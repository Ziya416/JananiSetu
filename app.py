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
import json
from google.oauth2 import service_account
from google.cloud import bigquery

# Import Vertex AI instead of standard generativeai
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold

load_dotenv()
matplotlib.use('Agg')

# Cloud Run native credential setup for BigQuery and Vertex AI
json_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if json_creds:
    creds_dict = json.loads(json_creds)
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    
    # Initialize BigQuery
    bq_client = bigquery.Client(credentials=creds, project=creds_dict["project_id"])
    
    # Initialize Vertex AI using the same credentials and project
    vertexai.init(project=creds_dict["project_id"], location="us-central1", credentials=creds)
    model = GenerativeModel("gemini-2.5-flash")
    BQ_AVAILABLE = True
else:
    # Local fallback
    bq_client = bigquery.Client(location="asia-south1")
    vertexai.init(project="big-query-codelab-497213", location="us-central1")
    model = GenerativeModel("gemini-2.5-flash")
    BQ_AVAILABLE = True

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
        row_to_insert = {col: data.get(col, "") for col in EXPECTED_COLUMNS}
        table_id = "big-query-codelab-497213.maternal_health_data.registry-table"
        errors = bq_client.insert_rows_json(table_id, [row_to_insert])
        
        if errors == []:
            return jsonify({"status": "success", "message": "Saved to BigQuery."})
        else:
            return jsonify({"status": "error", "message": f"BigQuery errors: {errors}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/search', methods=['GET'])
def search_patient():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({"status": "error", "message": "Patient ID required"})

    try:
        query = f"""
            SELECT * FROM `big-query-codelab-497213.maternal_health_data.registry-table` 
            WHERE CAST(Patient_ID AS STRING) = '{patient_id}'
        """
        patient_data = bq_client.query(query).to_dataframe()
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database search failed: {e}"})

    if patient_data.empty:
        return jsonify({"status": "error", "message": "Patient not found in BigQuery."})

    graph_bp = None
    graph_hb = None
    graph_sugar = None
    
    try:
        weeks = patient_data['Visit_Week'].fillna(0).astype(int).tolist()
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
        {comorbidities}"""

        try:
            # Vertex AI specific safety settings syntax
            safety_settings = {
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
            
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
        # Query BigQuery for a matching patient
        query = f"""
            SELECT Patient_ID FROM `big-query-codelab-497213.maternal_health_data.registry-table` 
            WHERE LOWER(Name) = LOWER('{name}') AND LOWER(Village) = LOWER('{village}')
            LIMIT 1
        """
        result = bq_client.query(query).to_dataframe()
        
        if result.empty:
            return jsonify({"status": "error", "message": "No patient found with this name and village."})
            
        matched_id = str(result.iloc[0]['Patient_ID'])
        return jsonify({"status": "success", "patient_id": matched_id})
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database search failed: {e}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
