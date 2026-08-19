require('dotenv').config();
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { GoogleGenerativeAI } = require('@google/generative-ai');
const path = require('path');

const app = express();
app.use(express.json());

// Serve HTML, CSS, JS from the 'public' folder
app.use(express.static(path.join(__dirname, 'public')));

// Initialize SQLite Database
const db = new sqlite3.Database('./jananisetu_simulated.db', (err) => {
    if (err) console.error(err.message);
    console.log('Connected to SQLite database.');
});

db.run(`CREATE TABLE IF NOT EXISTS registry_table (
    Patient_ID TEXT, Name TEXT, Husband_Name TEXT, Village TEXT,
    LMP TEXT, EDD TEXT, Obstetric_History TEXT, Visit_Week INTEGER,
    Blood_Pressure TEXT, Hemoglobin_Hb REAL, Blood_Sugar TEXT,
    Seizure_History TEXT, HHH_Status TEXT, Comorbidities_Remarks TEXT
)`);

// Initialize Gemini API
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });

const EXPECTED_COLUMNS = [
    "Patient_ID", "Name", "Husband_Name", "Village", "LMP", "EDD", 
    "Obstetric_History", "Visit_Week", "Blood_Pressure", 
    "Hemoglobin_Hb", "Blood_Sugar", "Seizure_History", "HHH_Status", "Comorbidities_Remarks"
];

// Save Data Route
app.post('/api/save', (req, res) => {
    const data = req.body;
    const values = EXPECTED_COLUMNS.map(col => data[col] || "");
    const placeholders = EXPECTED_COLUMNS.map(() => "?").join(",");

    db.run(`INSERT INTO registry_table VALUES (${placeholders})`, values, function(err) {
        if (err) return res.json({ status: "error", message: err.message });
        res.json({ status: "success", message: "Saved to Local Database." });
    });
});

// Search Route
app.get('/api/search', (req, res) => {
    const patient_id = req.query.patient_id;
    if (!patient_id) return res.json({ status: "error", message: "Patient ID required" });

    db.all(`SELECT * FROM registry_table WHERE Patient_ID = ?`, [patient_id], async (err, rows) => {
        if (err) return res.json({ status: "error", message: err.message });
        if (rows.length === 0) return res.json({ status: "error", message: "Patient not found." });

        // Process historical data for frontend charts
        const history = { weeks: [], bp: [], hb: [], sugar: [] };
        rows.forEach(row => {
            history.weeks.push(row.Visit_Week || 0);
            
            // Extract numbers from strings for graphs
            let bp = 0;
            if (row.Blood_Pressure && String(row.Blood_Pressure).includes('/')) {
                bp = parseInt(String(row.Blood_Pressure).split('/')[0]);
            } else if (row.Blood_Pressure) {
                const match = String(row.Blood_Pressure).match(/\d+/);
                bp = match ? parseInt(match[0]) : 0;
            }
            history.bp.push(bp);
            
            history.hb.push(parseFloat(row.Hemoglobin_Hb) || 0);
            
            let sugar = 0;
            if (row.Blood_Sugar) {
                const match = String(row.Blood_Sugar).match(/\d+/);
                sugar = match ? parseInt(match[0]) : 0;
            }
            history.sugar.push(sugar);
        });

        const latest = rows[rows.length - 1];
        const bp_val = latest.Blood_Pressure || "0";
        const hb = latest.Hemoglobin_Hb || 0;
        const sugar_match = String(latest.Blood_Sugar || "0").match(/\d+/);
        const sugar = sugar_match ? parseInt(sugar_match[0]) : 0;
        const comorbidities = latest.Comorbidities_Remarks || "None reported";

        let insight_en = "Error generating AI response.";
        let insight_hi = "त्रुटि उत्पन्न हुई।";

        try {
            const prompt = `Act as a maternal health orchestrator. 
            PATIENT DATA: Patient ID: ${patient_id}, BP: ${bp_val}, Hb: ${hb}, Sugar: ${sugar}, Comorbidities: ${comorbidities}.
            Task 1: Analyze vitals based on standard guidelines.
            Task 2: Generate a concise clinical insight (2-3 sentences) alerting risks.
            Task 3: Below your insight, explicitly list the vitals exactly as provided.
            Task 4: Translate the entire response into Hindi.
            Format EXACTLY like this:
            ENGLISH:
            [Insight]
            Last Visit Vitals:
            BP: ${bp_val} | Hb: ${hb} | Sugar: ${sugar}
            Comorbidities: ${comorbidities}
            HINDI:
            [Hindi Insight]
            अंतिम विज़िट के वाइटल्स:
            BP: ${bp_val} | Hb: ${hb} | Sugar: ${sugar}
            सहवर्ती रोग: [Hindi Comorbidities]`;

            const response = await model.generateContent(prompt);
            const raw_text = response.response.text();

            if (raw_text.includes("HINDI:")) {
                const parts = raw_text.split("HINDI:");
                insight_en = parts[0].replace("ENGLISH:", "").trim();
                insight_hi = parts[1].trim();
            } else {
                insight_en = raw_text;
            }
        } catch (e) {
            console.error("LLM Error:", e);
        }

        res.json({
            status: "success",
            history: history, // Send raw data to frontend
            insight_en: insight_en,
            insight_hi: insight_hi
        });
    });
});

// Demographic Search Route
app.get('/api/search_demographic', (req, res) => {
    const { name, village } = req.query;
    if (!name || !village) return res.json({ status: "error", message: "Name and Village required." });

    // Using LIKE to allow partial name matches
    db.get(`SELECT Patient_ID FROM registry_table WHERE LOWER(Name) LIKE LOWER(?) AND LOWER(Village) = LOWER(?) LIMIT 1`, 
    [`%${name}%`, village], (err, row) => {
        if (err) return res.json({ status: "error", message: err.message });
        if (!row) return res.json({ status: "error", message: "No patient found." });
        res.json({ status: "success", patient_id: row.Patient_ID });
    });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log('=========================================');
    console.log(`🚀 Server is successfully running!`);
    console.log(`👉 Click here or open in browser: http://localhost:${PORT}`);
    console.log('=========================================');
});