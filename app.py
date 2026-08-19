from flask import Flask, request, jsonify
import pandas as pd
import os
import re
from dotenv import load_dotenv
import sqlite3
import PIL.Image
import base64
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

# Use the NEW SDK to fix the warning
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini Client
client = None
if os.environ.get("GEMINI_API_KEY"):
    client = genai.Client()
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

DB_NAME = "jananisetu_simulated.db"

app = Flask(__name__, static_folder='public', static_url_path='')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registry_table (
            Patient_ID TEXT, Name TEXT, Husband_Name TEXT, Village TEXT,
            LMP TEXT, EDD TEXT, Obstetric_History TEXT, Visit_Week INTEGER,
            Blood_Pressure TEXT, Hemoglobin_Hb REAL, Blood_Sugar TEXT,
            Seizure_History TEXT, HHH_Status TEXT, Comorbidities_Remarks TEXT
        )
    ''')
    # Create the users table for secure login/signup
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

EXPECTED_COLUMNS = [
    "Patient_ID", "Name", "Husband_Name", "Village", "LMP", "EDD", 
    "Obstetric_History", "Visit_Week", "Blood_Pressure", 
    "Hemoglobin_Hb", "Blood_Sugar", "Seizure_History", "HHH_Status", "Comorbidities_Remarks"
]

@app.route('/')
def home():
    return app.send_static_file('index.html')

# --- USER AUTHENTICATION ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "phc")

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required."})

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        hashed_pw = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Account created successfully."})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Username already exists."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            return jsonify({"status": "success", "role": user[1]})
        else:
            return jsonify({"status": "error", "message": "Invalid username or password."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- DOCUMENT AI (GEMINI VISION) ---
@app.route('/api/ocr', methods=['POST'])
def process_ocr():
    if not client:
        return jsonify({"status": "error", "message": "AI Client not configured."})
        
    try:
        data = request.json
        img_data = base64.b64decode(data['image'].split(',')[1])
        img = PIL.Image.open(BytesIO(img_data))
        
        prompt = """
        Extract the following maternal health data from this medical report image. 
        Return ONLY a valid JSON object with these exact keys:
        "Patient_ID", "Name", "Blood_Pressure", "Hemoglobin_Hb", "Blood_Sugar".
        If a value is not found, leave the string empty. Do not include markdown formatting.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        
        raw_json = response.text.replace("```json", "").replace("```", "").strip()
        import json
        extracted_data = json.loads(raw_json)
        return jsonify({"status": "success", "data": extracted_data})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/save', methods=['POST'])
def save_patient():
    data = request.json
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        values = tuple(data.get(col, "") for col in EXPECTED_COLUMNS)
        placeholders = ",".join(["?"] * len(EXPECTED_COLUMNS))
        c.execute(f"INSERT INTO registry_table VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Saved to Local Database."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/search', methods=['GET'])
def search_patient():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({"status": "error", "message": "Patient ID required"})

    try:
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT * FROM registry_table WHERE Patient_ID = ?"
        patient_data = pd.read_sql_query(query, conn, params=(patient_id,))
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database search failed: {e}"})

    if patient_data.empty:
        return jsonify({"status": "error", "message": "Patient not found in Database."})

    history = {"weeks": [], "bp": [], "hb": [], "sugar": []}
    
    def extract_num(val, default=0):
        nums = re.findall(r'\d+', str(val))
        return int(nums[0]) if nums else default

    for _, row in patient_data.iterrows():
        week = extract_num(row.get('Visit_Week', 0))
        history["weeks"].append(week)
        
        bp_val = row.get('Blood_Pressure', '')
        sys_bp = int(str(bp_val).split('/')[0]) if '/' in str(bp_val) else extract_num(bp_val)
        history["bp"].append(sys_bp)
        
        try:
            hb_val = float(row.get('Hemoglobin_Hb', 0))
        except:
            hb_val = 0.0
        history["hb"].append(hb_val)
        
        sugar_val = extract_num(row.get('Blood_Sugar', 0))
        history["sugar"].append(sugar_val)

    latest = patient_data.iloc[-1]
    bp_val = str(latest.get('Blood_Pressure', '0'))
    try:
        hb = float(latest.get('Hemoglobin_Hb', 0))
    except:
        hb = 0.0
    sugar = extract_num(latest.get('Blood_Sugar', '0'))
    comorbidities = str(latest.get('Comorbidities_Remarks', 'None reported'))

    insight_en = "AI Model not configured."
    insight_hi = "एआई मॉडल कॉन्फ़िगर नहीं किया गया है।"

    if client:
        prompt = f"""Act as a maternal health orchestrator. 
        PATIENT DATA: Patient ID: {patient_id}, BP: {bp_val}, Hb: {hb}, Sugar: {sugar}, Comorbidities: {comorbidities}.
        Task 1: Analyze vitals based on standard guidelines.
        Task 2: Generate a concise clinical insight (2-3 sentences) alerting risks.
        Task 3: Below your insight, explicitly list the vitals exactly as provided.
        Task 4: Translate the entire response into Hindi.
        Format EXACTLY like this:
        ENGLISH:
        [Insight]
        Last Visit Vitals:
        BP: {bp_val} | Hb: {hb} | Sugar: {sugar}
        Comorbidities: {comorbidities}
        HINDI:
        [Hindi Insight]
        अंतिम विज़िट के वाइटल्स:
        BP: {bp_val} | Hb: {hb} | Sugar: {sugar}
        सहवर्ती रोग: [Hindi Comorbidities]"""

        try:
            config = types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                ]
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )
            raw_text = response.text
            if "HINDI:" in raw_text:
                parts = raw_text.split("HINDI:")
                insight_en = parts[0].replace("ENGLISH:", "").strip()
                insight_hi = parts[1].strip()
            else:
                insight_en = raw_text
        except Exception as e:
            print(f"LLM Error: {e}")
            insight_en = f"SYSTEM ERROR: {str(e)}"
            insight_hi = "त्रुटि उत्पन्न हुई।"

    return jsonify({
        "status": "success",
        "history": history,
        "insight_en": insight_en,
        "insight_hi": insight_hi
    })

@app.route('/api/search_demographic', methods=['GET'])
def search_demographic():
    name = request.args.get('name', '').strip()
    village = request.args.get('village', '').strip()
    if not name or not village:
        return jsonify({"status": "error", "message": "Name and Village are required."})
    
    try:
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT Patient_ID FROM registry_table WHERE LOWER(Name) LIKE LOWER(?) AND LOWER(Village) = LOWER(?) LIMIT 1"
        result = pd.read_sql_query(query, conn, params=(f"%{name}%", village))
        conn.close()
        
        if result.empty:
            return jsonify({"status": "error", "message": "No patient found."})
        return jsonify({"status": "success", "patient_id": str(result.iloc[0]['Patient_ID'])})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database search failed: {e}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print("=========================================")
    print(f"Flask Server running at http://localhost:{port}")
    print("=========================================")
    app.run(host='0.0.0.0', port=port, debug=True)

















