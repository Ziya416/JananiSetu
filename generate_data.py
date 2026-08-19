# Genrating 60 Synthetic patient records of multiple timelines for demo case scenarios
# The records are from patient ID MOM-2001 to MOM-2060
import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect('jananisetu_simulated.db')
c = conn.cursor()

# 1. Create the table if it doesn't exist yet
c.execute('''
    CREATE TABLE IF NOT EXISTS registry_table (
        Patient_ID TEXT, Name TEXT, Husband_Name TEXT, Village TEXT,
        LMP TEXT, EDD TEXT, Obstetric_History TEXT, Visit_Week INTEGER,
        Blood_Pressure TEXT, Hemoglobin_Hb REAL, Blood_Sugar TEXT,
        Seizure_History TEXT, HHH_Status TEXT, Comorbidities_Remarks TEXT
    )
''')

# 2. Clear existing data so we start fresh
c.execute('DELETE FROM registry_table')

# Localized demographic data
first_names = ["Radha", "Sunita", "Kavita", "Priya", "Anjali", "Meera", "Sita", "Gita", "Neha", "Pooja", "Rekha"]
last_names = ["Patel", "Shah", "Desai", "Rathod", "Parmar", "Solanki", "Chauhan"]
husbands = ["Shyam", "Ramesh", "Suresh", "Amit", "Rahul", "Vikram", "Sanjay", "Mahesh"]
villages = ["Surat", "Navsari", "Bardoli", "Vyara", "Kamrej", "Olpad", "Mandvi"]

for i in range(1, 61):  # Generate 60 patients
    patient_id = f"MOM-{2000 + i}"
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    husband = random.choice(husbands)
    village = random.choice(villages)
    
    # Generate realistic pregnancy timelines
    lmp_date = datetime(2025, random.randint(1, 10), random.randint(1, 28))
    edd_date = lmp_date + timedelta(days=280)
    lmp = lmp_date.strftime("%d/%m/%Y")
    edd = edd_date.strftime("%d/%m/%Y")
    
    obs_history = f"G{random.randint(1,3)} P{random.randint(0,2)} A{random.randint(0,1)} L{random.randint(0,2)}"
    
    # INJECT REAL-WORLD EDGE CASES FOR THE AI TO CATCH
    profile = random.choices(["Normal", "Preeclampsia", "GDM", "Anemia"], weights=[70, 10, 10, 10])[0]
    
    seizure = "none"
    hhh = "No"
    notes = "Routine checkup. Mother feeling normal."
    
    if profile == "Preeclampsia":
        notes = "High risk: Monitor for sudden BP spikes and preeclampsia."
        seizure = random.choice(["none", "past"])
    elif profile == "GDM":
        notes = "Gestational Diabetes flagged in family history."
    elif profile == "Anemia":
        notes = "Severe anemia, prescribed iron supplements."
        
    # Generate 3 to 5 historical visits per patient
    num_visits = random.randint(3, 6)
    visit_weeks = sorted(random.sample([12, 16, 20, 24, 28, 32, 36, 38, 40], num_visits))
    
    for week in visit_weeks:
        # Baseline normal vitals
        sys_bp = random.randint(110, 125)
        dia_bp = random.randint(70, 80)
        hb = round(random.uniform(11.0, 13.5), 1)
        sugar = random.randint(80, 100)
        
        # Apply risk profile modifiers
        if profile == "Preeclampsia" and week >= 24:
            sys_bp = random.randint(145, 185)
            dia_bp = random.randint(95, 115)
        elif profile == "GDM" and week >= 24:
            sugar = random.randint(140, 210)
        elif profile == "Anemia":
            hb = round(random.uniform(7.0, 9.5), 1)
            
        bp_str = f"{sys_bp}/{dia_bp}"
        
        # Insert timeline node into database
        c.execute('''
            INSERT INTO registry_table 
            (Patient_ID, Name, Husband_Name, Village, LMP, EDD, Obstetric_History, 
            Visit_Week, Blood_Pressure, Hemoglobin_Hb, Blood_Sugar, Seizure_History, 
            HHH_Status, Comorbidities_Remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, name, husband, village, lmp, edd, obs_history, 
              week, bp_str, hb, sugar, seizure, hhh, notes))

conn.commit()
conn.close()
print("🔥 Successfully generated and injected simulated timelines for 60 patients!")



















