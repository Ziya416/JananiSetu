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
import google.generativeai as genai
import json
from google.oauth2 import service_account
from google.cloud import bigquery

# Load environment variables
load_dotenv()

# Initialize AI Orchestrator
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None
    print("WARNING: Gemini API key not found in .env")

matplotlib.use('Agg') 

# Cloud Run native credential setup
json_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if json_creds:
    import json
    from google.oauth2 import service_account
    creds_dict = json.loads(json_creds)
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    bq_client = bigquery.Client(credentials=creds, project=creds_dict["project_id"])
    BQ_AVAILABLE = True

# BigQuery Client Initialization
try:
    from google.cloud import bigquery
    # Render handles credentials via environment variables, but keeping this for local testing if needed
    if os.path.exists("service_account.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
    bq_client = bigquery.Client(location="asia-south1")
    BQ_AVAILABLE = True
except Exception as e:
    print(f"BigQuery init failed: {e}")
    BQ_AVAILABLE = False

app = Flask(__name__)
FILE_PATH = "maternal_health_registry.csv"

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
        clean_data = {col: data.get(col, "") for col in EXPECTED_COLUMNS}
        df = pd.DataFrame([clean_data], columns=EXPECTED_COLUMNS)

        if os.path.exists(FILE_PATH):
            df.to_csv(FILE_PATH, mode='a', header=False, index=False)
        else:
            df.to_csv(FILE_PATH, mode='w', header=True, index=False)

        return jsonify({"status": "success", "message": "Saved to Registry. Data aligned correctly."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/search', methods=['GET'])
def search_patient():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({"status": "error", "message": "Patient ID required"})

    patient_data = pd.DataFrame()

    # FETCH DATA 
    if BQ_AVAILABLE:
        try:
            query = f"SELECT * FROM `big-query-codelab-497213.maternal_health_data.registry-table` WHERE CAST(Patient_ID AS STRING) = '{patient_id}'"
            patient_data = bq_client.query(query).to_dataframe()
        except Exception as e:
            print(f"BQ failed: {e}")

    if patient_data.empty and os.path.exists(FILE_PATH):
        try:
            df = pd.read_csv(FILE_PATH)
            patient_data = df[df['Patient_ID'].astype(str) == str(patient_id)]
        except Exception as e:
            print(f"CSV read failed: {e}")

    if patient_data.empty:
        return jsonify({"status": "error", "message": "Patient not found."})

    graph_bp = None
    graph_hb = None
    graph_sugar = None
    
    # GRAPH GENERATION
    try:
        weeks = patient_data['Visit_Week'].fillna(0).astype(int).tolist()
        def extract_num(val, default=0):
            nums = re.findall(r'\d+', str(val))
            return int(nums[0]) if nums else default

        # BP Graph
        plt.figure(figsize=(6, 2.5))
        vals = [int(str(bp).split('/')[0]) if '/' in str(bp) else extract_num(bp) for bp in patient_data['Blood_Pressure']]
        plt.plot(weeks, vals, marker='o', color='#C1483D', linewidth=2)
        plt.title("Systolic BP Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 200)
        plt.gca().yaxis.set_major_locator(MultipleLocator(20)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_bp = base64.b64encode(buf.getvalue()).decode(); plt.close()

        # Hb Graph
        plt.figure(figsize=(6, 2.5))
        vals = pd.to_numeric(patient_data['Hemoglobin_Hb'], errors='coerce').fillna(0).tolist()
        plt.plot(weeks, vals, marker='o', color='#3E6FB0', linewidth=2)
        plt.title("Hemoglobin (Hb) Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 20)
        plt.gca().yaxis.set_major_locator(MultipleLocator(2)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_hb = base64.b64encode(buf.getvalue()).decode(); plt.close()
        
        # Sugar Graph
        plt.figure(figsize=(6, 2.5))
        vals = [extract_num(s) for s in patient_data['Blood_Sugar']]
        plt.plot(weeks, vals, marker='o', color='#E8A33D', linewidth=2)
        plt.title("Blood Sugar Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 300)
        plt.gca().yaxis.set_major_locator(MultipleLocator(20)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_sugar = base64.b64encode(buf.getvalue()).decode(); plt.close()

    except Exception as e:
        print(f"Graph error: {e}")

    # LATEST VITALS FOR ORCHESTRATOR
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
    
    insight_en = "AI Model not configured. Vitals require manual review."
    insight_hi = "एआई मॉडल कॉन्फ़िगर नहीं किया गया है।"

    if model:
        prompt = f"""Act as a maternal health orchestrator. 
        Task 1: Analyze these vitals for patient {patient_id}: BP {bp_val}, Hb {hb}, Sugar {sugar}. 
        Task 2: Generate a concise clinical insight (2-3 sentences) for the health worker based on medical guidelines and just show the alerts and last visit's vitals and also give the Comorbidities_&_Remarks also show alerts and last visit's vitals with some paragraph spacing.
        Task 3: Translate your exact insight into Hindi.
        
        Format your response EXACTLY like this, with no extra text or markdown:
        ENGLISH: [Your English text here]
        HINDI: [Your Hindi text here]"""

        try:
            response = model.generate_content(prompt)
            raw_text = response.text
            
            # Parse the dual-language response
            if "HINDI:" in raw_text:
                parts = raw_text.split("HINDI:")
                insight_en = parts[0].replace("ENGLISH:", "").strip()
                insight_hi = parts[1].strip()
            else:
                insight_en = raw_text
                insight_hi = "Translation error."
        except Exception as e:
            print(f"LLM Error: {e}")
            insight_en = "Error generating AI insight."
            insight_hi = "त्रुटि उत्पन्न हुई।"

    return jsonify({
        "status": "success",
        "graph_bp": graph_bp,
        "graph_hb": graph_hb,
        "graph_sugar": graph_sugar,
        "insight_en": insight_en,
        "insight_hi": insight_hi
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
