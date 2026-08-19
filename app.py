from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import base64
from io import BytesIO
from dotenv import load_dotenv
import sqlite3

# Import standard Generative AI instead of Vertex AI
import google.generativeai as genai

load_dotenv()
matplotlib.use('Agg')

# 1. Initialize Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# 2. Initialize SQLite Database (Replaces BigQuery)
DB_NAME = "jananisetu_simulated.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create the table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS registry_table (
            Patient_ID TEXT, Name TEXT, Husband_Name TEXT, Village TEXT,
            LMP TEXT, EDD TEXT, Obstetric_History TEXT, Visit_Week INTEGER,
            Blood_Pressure TEXT, Hemoglobin_Hb REAL, Blood_Sugar TEXT,
            Seizure_History TEXT, HHH_Status TEXT, Comorbidities_Remarks TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)

EXPECTED_COLUMNS = [
    "Patient_ID", "Name", "Husband_Name", "Village", "LMP", "EDD", 
    "Obstetric_History", "Visit_Week", "Blood_Pressure", 
    "Hemoglobin_Hb", "Blood_Sugar", "Seizure_History", "HHH_Status", "Comorbidities_Remarks"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/save', methods=['POST'])
def save_patient():
    data = request.json
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Prepare data tuple in the correct column order
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
        # Use pandas read_sql to keep it compatible with your existing graphing code
        query = "SELECT * FROM registry_table WHERE Patient_ID = ?"
        patient_data = pd.read_sql_query(query, conn, params=(patient_id,))
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database search failed: {e}"})

    if patient_data.empty:
        return jsonify({"status": "error", "message": "Patient not found in Database."})

    graph_bp = None
    graph_hb = None
    graph_sugar = None
    
    try:
        weeks = patient_data['Visit_Week'].replace("", 0).fillna(0).astype(int).tolist()
        def extract_num(val, default=0):
            nums = re.findall(r'\d+', str(val))
            return int(nums[0]) if nums else default

        plt.figure(figsize=(6, 2.5))
        vals = [int(str(bp).split('/')[0]) if '/' in str(bp) else extract_num(bp) for bp in patient_data['Blood_Pressure']]
        plt.plot(weeks, vals, marker='o', color='#C1483D', linewidth=2)
        plt.title("Systolic BP Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 200)
        plt.gca().yaxis.set_major_locator(MultipleLocator(20)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_bp = base64.b64encode(buf.getvalue()).decode(); plt.close()

        plt.figure(figsize=(6, 2.5))
        vals = pd.to_numeric(patient_data['Hemoglobin_Hb'], errors='coerce').fillna(0).tolist()
        plt.plot(weeks, vals, marker='o', color='#3E6FB0', linewidth=2)
        plt.title("Hemoglobin (Hb) Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 20)
        plt.gca().yaxis.set_major_locator(MultipleLocator(2)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_hb = base64.b64encode(buf.getvalue()).decode(); plt.close()
        
        plt.figure(figsize=(6, 2.5))
        vals = [extract_num(s) for s in patient_data['Blood_Sugar']]
        plt.plot(weeks, vals, marker='o', color='#E8A33D', linewidth=2)
        plt.title("Blood Sugar Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 300)
        plt.gca().yaxis.set_major_locator(MultipleLocator(20)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_sugar = base64.b64encode(buf.getvalue()).decode(); plt.close()

    except Exception as e:
        print(f"Graph error: {e}")

    latest = patient_data.iloc[-1]
    
    def extract_num(val, default=0):
        nums = re.findall(r'\d+', str(val))
        return int(nums[0]) if nums else default
        
    bp_val = str(latest.get('Blood_Pressure', '0'))
    try:
        hb = float(latest.get('Hemoglobin_Hb', 0))
    except:
        hb = 0.0
    sugar = extract_num(latest.get('Blood_Sugar', '0'))

    comorbidities = str(latest.get('Comorbidities_Remarks', 'None reported'))
    
    insight_en = "AI Model not configured. Vitals require manual review."
    insight_hi = "एआई मॉडल कॉन्फ़िगर नहीं किया गया है।"

    if model:
        prompt = f"""Act as a maternal health orchestrator. 
        
        PATIENT DATA:
        Patient ID: {patient_id}
        BP: {bp_val}
        Hb: {hb}
        Sugar: {sugar}
        Comorbidities & Remarks: {comorbidities}
        
        Task 1: Analyze the vitals based on standard maternal medical guidelines.
        Task 2: Generate a concise clinical insight (2-3 sentences) alerting the health worker to any risks.
        Task 3: Below your insight, explicitly list the vitals and comorbidities EXACTLY as provided in the PATIENT DATA above. Use paragraph spacing.
        Task 4: Translate the ENTIRE English response (including the vitals and comorbidities list) into Hindi.
        
        Format your response EXACTLY like this, with no extra text or markdown:
        ENGLISH: 
        [Your clinical insight here]
        
        Last Visit Vitals:
        BP: {bp_val}
        Hb: {hb}
        Sugar: {sugar}
        
        Comorbidities & Remarks:
        {comorbidities}
        
        HINDI: 
        [Hindi translation of the clinical insight]
        
        अंतिम विज़िट के वाइटल्स:
        BP: {bp_val}
        Hb: {hb}
        Sugar: {sugar}
        
        सहवर्ती रोग और टिप्पणियाँ:
        [Hindi translation of the Comorbidities & Remarks here]"""

        try:
            # Standard Gemini API safety settings syntax
            safety_settings = [
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}
            ]
            
            response = model.generate_content(prompt, safety_settings=safety_settings)
            raw_text = response.text
            
            if "HINDI:" in raw_text:
                parts = raw_text.split("HINDI:")
                insight_en = parts[0].replace("ENGLISH:", "").strip()
                insight_hi = parts[1].strip()
            else:
                insight_en = raw_text
                insight_hi = "Translation error."
                
        except Exception as e:
            print(f"LLM Error: {e}")
            insight_en = f"SYSTEM ERROR: {str(e)}"
            insight_hi = "त्रुटि उत्पन्न हुई।"

    return jsonify({
        "status": "success",
        "graph_bp": graph_bp,
        "graph_hb": graph_hb,
        "graph_sugar": graph_sugar,
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
        query = "SELECT Patient_ID FROM registry_table WHERE LOWER(Name) = LOWER(?) AND LOWER(Village) = LOWER(?) LIMIT 1"
        result = pd.read_sql_query(query, conn, params=(name, village))
        conn.close()
        
        if result.empty:
            return jsonify({"status": "error", "message": "No patient found with this name and village."})
            
        matched_id = str(result.iloc[0]['Patient_ID'])
        return jsonify({"status": "success", "patient_id": matched_id})
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database search failed: {e}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)