from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
import re
import matplotlib
matplotlib.use('Agg') # Safe graph generation for servers
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import base64
from io import BytesIO

# Try loading BigQuery safely
try:
    from google.cloud import bigquery
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
    bq_client = bigquery.Client(location="asia-south1")
    BQ_AVAILABLE = True
except Exception as e:
    print(f"BigQuery init failed: {e}")
    BQ_AVAILABLE = False

from deep_translator import GoogleTranslator

app = Flask(__name__)
FILE_PATH = "maternal_health_registry.csv"

# Schema uses Visit_Week and includes HHH_Status
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

    # --- FETCH DATA ---
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
    
    # --- GRAPH GENERATION ---
    try:
        weeks = patient_data['Visit_Week'].fillna(0).astype(int).tolist()
        def extract_num(val, default=0):
            nums = re.findall(r'\d+', str(val))
            return int(nums[0]) if nums else default

        # 1. BP
        plt.figure(figsize=(6, 2.5))
        vals = [int(str(bp).split('/')[0]) if '/' in str(bp) else extract_num(bp) for bp in patient_data['Blood_Pressure']]
        plt.plot(weeks, vals, marker='o', color='#C1483D', linewidth=2)
        plt.title("Systolic BP Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 200)
        plt.gca().yaxis.set_major_locator(MultipleLocator(20)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_bp = base64.b64encode(buf.getvalue()).decode(); plt.close()

        # 2. Hb
        plt.figure(figsize=(6, 2.5))
        vals = pd.to_numeric(patient_data['Hemoglobin_Hb'], errors='coerce').fillna(0).tolist()
        plt.plot(weeks, vals, marker='o', color='#3E6FB0', linewidth=2)
        plt.title("Hemoglobin (Hb) Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 20)
        plt.gca().yaxis.set_major_locator(MultipleLocator(2)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_hb = base64.b64encode(buf.getvalue()).decode(); plt.close()
        
        # 3. Sugar
        plt.figure(figsize=(6, 2.5))
        vals = [extract_num(s) for s in patient_data['Blood_Sugar']]
        plt.plot(weeks, vals, marker='o', color='#E8A33D', linewidth=2)
        plt.title("Blood Sugar Trend"); plt.xlabel("Gestational Week"); plt.ylim(0, 300)
        plt.gca().yaxis.set_major_locator(MultipleLocator(20)); plt.grid(axis='y', linestyle='--', alpha=0.5)
        buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); graph_sugar = base64.b64encode(buf.getvalue()).decode(); plt.close()

    except Exception as e:
        print(f"Graph error: {e}")

    # --- AI INSIGHT ALERTS ---
    latest = patient_data.iloc[-1]
    
    def extract_num(val, default=0):
        nums = re.findall(r'\d+', str(val))
        return int(nums[0]) if nums else default
        
    bp_val = str(latest.get('Blood_Pressure', '0'))
    sbp = int(bp_val.split('/')[0]) if '/' in bp_val else extract_num(bp_val)
    dbp = int(bp_val.split('/')[1]) if '/' in bp_val else 0
    
    try:
        hb = float(latest.get('Hemoglobin_Hb', 0))
    except:
        hb = 0.0
        
    sugar = extract_num(latest.get('Blood_Sugar', '0'))
    
    alerts = []
    if sbp > 140 or dbp > 90: alerts.append("⚠️ ALERT: Systolic BP above 140/90 mmHg.")
    if hb < 11: alerts.append("⚠️ ALERT: Hemoglobin critically low (< 11 g/dL).")
    if sugar > 140: alerts.append("⚠️ ALERT: Blood Sugar above 140 mg/dL.")
    if str(latest.get('HHH_Status', 'No')).lower() == 'yes': alerts.append("🚨 ALERT: HHH Status concerning - Escalate care promptly.")

    insight = f"""Clinical Analysis for {patient_id}:
- Last Checkup Vitals: BP: {latest.get('Blood_Pressure', 'N/A')}, Hb: {hb}, Sugar: {latest.get('Blood_Sugar', 'N/A')}.
- Comorbidities: {latest.get('Comorbidities_Remarks', 'None')}
- Seizure History: {latest.get('Seizure_History', 'None')}
- HHH Status: {latest.get('HHH_Status', 'No')}
    
ALERTS:
{chr(10).join(alerts) if alerts else "- All vitals within monitored safe range."}
- Maintain detailed records for future reference."""

    # ALL DATA RETURNED AT THE END
    return jsonify({
        "status": "success",
        "graph_bp": graph_bp,
        "graph_hb": graph_hb,
        "graph_sugar": graph_sugar,
        "insight": insight
    })


@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get("text", "").strip()
    
    if not text or text in ["Agent 3 is analyzing...", "Loading...", "Analyzing..."]:
        return jsonify({"status": "error", "message": "Generate an insight first."})

    try:
        translated = GoogleTranslator(source='auto', target='hi').translate(text)
        return jsonify({"status": "success", "translated_text": translated})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Translation failed: {str(e)}"})


if __name__ == '__main__':
    app.run(debug=True)