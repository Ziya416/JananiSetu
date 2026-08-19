# Genrating 60 Synthetic patient records of multiple timelines for demo case scenarios
# The records are from patient ID MOM-2001 to MOM-2060
import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "jananisetu_simulated.db"

FIRST_NAMES = [
    "Radha", "Sunita", "Priya", "Aarti", "Meena", "Kavita", "Anjali", 
    "Pooja", "Neha", "Ritu", "Sita", "Geeta", "Rekha", "Kiran", "Mamta"
]
LAST_NAMES = [
    "Devi", "Sharma", "Patel", "Singh", "Verma", 
    "Gupta", "Das", "Kumari", "Shah", "Desai"
]
HUSBAND_NAMES = [
    "Ramesh", "Suresh", "Amit", "Rahul", "Anil", 
    "Sunil", "Rajesh", "Vijay", "Sanjay", "Dinesh", "Mahesh"
]
VILLAGES = [
    "Olpad", "Kamrej", "Bardoli", "Mandvi", 
    "Mangrol", "Palsana", "Mahuva", "Choryasi", "Umarpada"
]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS registry_table')
    c.execute('''
        CREATE TABLE registry_table (
            Patient_ID TEXT, Name TEXT, Husband_Name TEXT, Village TEXT,
            LMP TEXT, EDD TEXT, Obstetric_History TEXT, Visit_Week INTEGER,
            Blood_Pressure TEXT, Hemoglobin_Hb REAL, Blood_Sugar TEXT,
            Seizure_History TEXT, HHH_Status TEXT, Comorbidities_Remarks TEXT
        )
    ''')
    conn.commit()
    return conn

def seed_data():
    conn = init_db()
    c = conn.cursor()
    
    today = datetime.now()
    records_added = 0
    
    for i in range(1, 66):
        patient_id = f"MOM-{2000 + i}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        husband = random.choice(HUSBAND_NAMES)
        village = random.choice(VILLAGES)
        
        g = random.randint(1, 4)
        p = g - 1 if g > 1 else 0
        obs_hist = f"G{g} P{p} A{random.randint(0, 1) if g > 1 else 0} L{p}"
        
        weeks_pregnant = random.randint(12, 38)
        lmp_date = today - timedelta(weeks=weeks_pregnant)
        edd_date = lmp_date + timedelta(days=280)
        
        lmp_str = lmp_date.strftime("%d/%m/%Y")
        edd_str = edd_date.strftime("%d/%m/%Y")
        
        risk_profile = random.choices(
            ["normal", "anemic", "hypertensive", "emergency"], 
            weights=[60, 20, 15, 5], k=1
        )[0]
        
        visit_schedule = [w for w in [12, 24, 32, 36] if w <= weeks_pregnant]
        if not visit_schedule: 
            visit_schedule = [weeks_pregnant]
            
        for week in visit_schedule:
            sys_bp = random.randint(110, 120)
            dia_bp = random.randint(70, 80)
            hb = round(random.uniform(11.0, 13.5), 1)
            sugar = random.randint(85, 110)
            seizure = "none"
            hhh = "No"
            notes = "Routine checkup normal."
            
            if risk_profile == "anemic":
                hb = round(random.uniform(7.5, 10.0), 1)
                notes = "Prescribed IFA supplements and dietary monitoring."
                
            elif risk_profile == "hypertensive":
                sys_bp = random.randint(140, 160)
                dia_bp = random.randint(90, 100)
                notes = "Elevated BP detected. Regular monitoring required."
                
            elif risk_profile == "emergency" and week == visit_schedule[-1]:
                sys_bp = random.randint(160, 180)
                dia_bp = random.randint(100, 115)
                hb = round(random.uniform(6.5, 8.5), 1)
                seizure = "active"
                hhh = "Yes"
                notes = "CRITICAL: Eclampsia symptoms. Immediate referral initiated."
            
            bp_str = f"{sys_bp}/{dia_bp}"
            
            c.execute('''
                INSERT INTO registry_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, name, husband, village, lmp_str, edd_str, obs_hist, 
                  week, bp_str, hb, str(sugar), seizure, hhh, notes))
            
            records_added += 1
            
    conn.commit()
    conn.close()
    print(f"Generated {records_added} records across 65 patients.")

if __name__ == "__main__":
    seed_data()



















