let isSignupMode = false;
let uploadedImageBase64 = "";
let currentInsightEn = "";
let currentInsightHi = "";
let showingHindi = false; // For the AI Insight box

const translations = {
    "en": {
        "welcome_title": "New here? Let's take a 20-second look around.",
        "welcome_desc": "Two stops, one journey: enter check-up numbers to log data securely, and hand doctors a ready-made briefing with full AI insights and trend graphs the moment a mother reaches the hospital.",
        "welcome_btn": "Got it, let's start",
        "nav_village": "Village Check-In",
        "nav_village_sub": "Enter today's vitals",
        "nav_delivery": "Delivery Room",
        "nav_delivery_sub": "Emergency Retrieval Gateway",
        "p1_eyebrow": "Agent 2 · Smart Ingestion",
        "p1_title": "Upload report or enter data manually.",
        "p1_desc": "Upload a photo of the medical report, and we will extract the data. Anything missing? You can fill the gaps below.",
        "btn_ocr": "Upload ID/Report (OCR)",
        "btn_manual": "Enter Manually",
        "upload_hint": "Take a picture of the ID or browse for an image.",
        "btn_process": "Process Document",
        "btn_save": "Save Data",
        "p2_eyebrow": "Agent 4 · Emergency Searcher",
        "p2_title": "Emergency Retrieval Gateway",
        "p2_desc": "Select an option below to securely pull the patient's medical history when they arrive at the delivery room.",
        "tab_scan": "📷 Scan Card",
        "tab_manual": "🔢 Manual ID",
        "tab_demo": "🔍 Demographic Search",
        "scan_hint": "Point camera to scan the physical Card.",
        "btn_open_scan": "Open Camera Scanner",
        "man_hint": "Enter the Patient ID manually.",
        "btn_search": "Search Database",
        "demo_hint": "Search by Patient Name and Village.",
        "btn_search_rec": "Search Records",
        "insight_head": "Agent 3 · AI Clinical Insights",
        "chart_title": "42-Week Vitals Trend",
        "footer": "Built for front-line health workers · JananiSetu"
    },
    "hi": {
        "welcome_title": "यहाँ नए हैं? आइए 20-सेकंड में एक नज़र डालें।",
        "welcome_desc": "दो पड़ाव, एक यात्रा: डेटा सुरक्षित रूप से दर्ज करने के लिए चेक-अप नंबर दर्ज करें, और अस्पताल पहुँचते ही डॉक्टरों को पूर्ण AI अंतर्दृष्टि और ट्रेंड ग्राफ़ के साथ एक तैयार ब्रीफिंग सौंपें।",
        "welcome_btn": "समझ गया, शुरू करें",
        "nav_village": "गांव चेक-इन",
        "nav_village_sub": "आज के वाइटल्स दर्ज करें",
        "nav_delivery": "डिलीवरी रूम",
        "nav_delivery_sub": "आपातकालीन पुनर्प्राप्ति गेटवे",
        "p1_eyebrow": "एजेंट 2 · स्मार्ट इनजेशन",
        "p1_title": "रिपोर्ट अपलोड करें या मैन्युअल रूप से डेटा दर्ज करें।",
        "p1_desc": "मेडिकल रिपोर्ट की एक तस्वीर अपलोड करें, और हम डेटा निकाल लेंगे। कुछ छूट गया? आप नीचे दिए गए रिक्त स्थान भर सकते हैं।",
        "btn_ocr": "आईडी/रिपोर्ट अपलोड करें (OCR)",
        "btn_manual": "मैन्युअल रूप से दर्ज करें",
        "upload_hint": "आईडी की तस्वीर लें या छवि ब्राउज़ करें।",
        "btn_process": "दस्तावेज़ प्रोसेस करें",
        "btn_save": "डेटा सहेजें",
        "p2_eyebrow": "एजेंट 4 · आपातकालीन खोजकर्ता",
        "p2_title": "आपातकालीन पुनर्प्राप्ति गेटवे",
        "p2_desc": "डिलीवरी रूम में पहुँचने पर मरीज का मेडिकल इतिहास सुरक्षित रूप से निकालने के लिए नीचे एक विकल्प चुनें।",
        "tab_scan": "📷 कार्ड स्कैन करें",
        "tab_manual": "🔢 मैन्युअल आईडी",
        "tab_demo": "🔍 जनसांख्यिकीय खोज",
        "scan_hint": "भौतिक कार्ड को स्कैन करने के लिए कैमरा पॉइंट करें।",
        "btn_open_scan": "कैमरा स्कैनर खोलें",
        "man_hint": "मरीज की आईडी मैन्युअल रूप से दर्ज करें।",
        "btn_search": "डेटाबेस खोजें",
        "demo_hint": "मरीज के नाम और गांव से खोजें।",
        "btn_search_rec": "रिकॉर्ड खोजें",
        "insight_head": "एजेंट 3 · एआई क्लिनिकल इनसाइट्स",
        "chart_title": "42-सप्ताह वाइटल्स ट्रेंड",
        "footer": "फ्रंट-लाइन स्वास्थ्य कार्यकर्ताओं के लिए निर्मित · जननीसेतु"
    }
};

// AUTHENTICATION & UI TOGGLES
function toggleAuthMode() {
    isSignupMode = !isSignupMode;
    document.getElementById('authTitle').innerText = isSignupMode ? "Sign Up for JananiSetu" : "Login to JananiSetu";
    document.getElementById('authActionBtn').innerText = isSignupMode ? "Create Account" : "Login";
    document.getElementById('authToggleHint').innerText = isSignupMode ? "Already have an account? Login" : "Don't have an account? Sign up";
    document.getElementById('roleSelection').style.display = isSignupMode ? "block" : "none";
}

function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
    } else {
        input.type = "password";
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
    }
}

function handleAuth() {
    const user = document.getElementById('authUsername').value;
    const pass = document.getElementById('authPassword').value;
    const role = document.getElementById('authRole').value;
    const endpoint = isSignupMode ? '/api/signup' : '/api/login';
    const payload = isSignupMode ? { username: user, password: pass, role: role } : { username: user, password: pass };

    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            if (isSignupMode) {
                alert("Account created successfully! Please login with your credentials.");
                document.getElementById('authPassword').value = '';
                toggleAuthMode(); 
            } else {
                document.getElementById('loginOverlay').style.display = 'none';
                let roleName = "Health Worker";
                if (data.role === 'phc') roleName = "PHC Worker";
                if (data.role === 'chc') roleName = "CHC Worker";
                if (data.role === 'institutional') roleName = "Institutional Worker";

                alert(`Welcome! Logged in as ${roleName}. Accessing full platform.`);
                document.querySelectorAll('.station').forEach(s => s.style.display = 'flex');
                goTo('p1');
            }
        } else {
            alert(data.message);
        }
    });
}

// GLOBAL TRANSLATION
function toggleLang(lang, btnElement) {
    document.querySelectorAll('.lang-toggle button').forEach(btn => btn.classList.remove('active'));
    if (btnElement) {
        btnElement.classList.add('active');
    }

    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });
}

// NAVIGATION & PANELS
function dismissWelcome() {
    document.getElementById('welcomeBanner').style.display = 'none';
}

function goTo(panelId) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.station').forEach(s => s.classList.remove('active'));
    
    document.getElementById(panelId).classList.add('active');
    document.querySelector(`button[data-panel="${panelId}"]`).classList.add('active');
}

function setEntryMode(mode, btn) {
    document.querySelectorAll('#entryToggleGroup button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    if(mode === 'ocr') {
        document.getElementById('uploadZone').style.display = 'block';
        document.getElementById('manualEntryZone').style.display = 'none';
    } else {
        document.getElementById('uploadZone').style.display = 'none';
        document.getElementById('manualEntryZone').style.display = 'block';
    }
}

function showIdentityMethod(method, btn) {
    document.querySelectorAll('#identityToggleGroup button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    document.getElementById('scannerZone').style.display = 'none';
    document.getElementById('manualSearchZone').style.display = 'none';
    document.getElementById('demoSearchZone').style.display = 'none';
    
    if(method === 'scan') document.getElementById('scannerZone').style.display = 'block';
    if(method === 'manual') document.getElementById('manualSearchZone').style.display = 'block';
    if(method === 'demo') document.getElementById('demoSearchZone').style.display = 'block';
}

// DOCUMENT AI & SAVING (PANEL 1)
function handleImageSelect(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            uploadedImageBase64 = e.target.result; 
            document.getElementById('processBtn').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function processOCR() {
    const btn = document.getElementById('processBtn');
    if (!uploadedImageBase64) return alert("Please select an image first.");
    
    btn.innerText = "Analyzing Document with AI...";
    
    fetch('/api/ocr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: uploadedImageBase64 })
    })
    .then(res => res.json())
    .then(data => {
        btn.innerText = "Process Document";
        if (data.status === "success" && data.data) {
            if(data.data.Patient_ID) document.getElementById('man_id').value = data.data.Patient_ID;
            if(data.data.Name) document.getElementById('man_name').value = data.data.Name;
            if(data.data.Blood_Pressure) document.getElementById('man_bp').value = data.data.Blood_Pressure;
            if(data.data.Hemoglobin_Hb) document.getElementById('man_hb').value = data.data.Hemoglobin_Hb;
            if(data.data.Blood_Sugar) document.getElementById('man_sugar').value = data.data.Blood_Sugar;
            
            alert("Document AI extraction complete! Please verify the details.");
            setEntryMode('manual', document.querySelectorAll('#entryToggleGroup button')[1]);
        } else {
            alert("Error: " + (data.message || "Failed to parse document."));
        }
    })
    .catch(err => {
        btn.innerText = "Process Document";
        alert("Connection error during OCR. Please wait a moment and try again.");
    });
}

function savePatientData() {
    const payload = {
        Patient_ID: document.getElementById('man_id').value,
        Name: document.getElementById('man_name').value,
        Husband_Name: document.getElementById('man_husband').value,
        Village: document.getElementById('man_village').value,
        Visit_Week: document.getElementById('man_week').value,
        LMP: document.getElementById('man_lmp').value,
        EDD: document.getElementById('man_edd').value,
        Obstetric_History: document.getElementById('man_obs').value,
        Blood_Pressure: document.getElementById('man_bp').value,
        Hemoglobin_Hb: document.getElementById('man_hb').value,
        Blood_Sugar: document.getElementById('man_sugar').value,
        Seizure_History: document.getElementById('man_seizure').value,
        HHH_Status: document.getElementById('man_hhh').value,
        Comorbidities_Remarks: document.getElementById('man_notes').value
    };

    if(!payload.Patient_ID) return alert("Patient ID is required.");

    fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            alert('Data saved securely to database!');
            document.querySelectorAll('#manualEntryZone input').forEach(i => i.value = '');
            document.getElementById('man_notes').value = '';
        } else {
            alert('Error: ' + data.message);
        }
    });
}

// SEARCH & AI INSIGHTS (PANEL 2)
function searchByDemographics() {
    const name = document.getElementById('demo_name').value;
    const village = document.getElementById('demo_village').value;
    
    if(!name || !village) return alert("Please enter both Name and Village.");
    
    fetch(`/api/search_demographic?name=${name}&village=${village}`)
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            document.getElementById('search_id').value = data.patient_id;
            alert(`Patient Found: ${data.patient_id}. Switching to manual search to pull records.`);
            showIdentityMethod('manual', document.querySelectorAll('#identityToggleGroup button')[1]);
            simulateSearch();
        } else {
            alert(data.message);
        }
    });
}

function simulateSearch() {
    const pid = document.getElementById('search_id').value;
    if (!pid) return alert("Enter Patient ID");
    
    document.getElementById('briefingBox').style.display = 'block';
    document.getElementById('patient_title').innerText = "Fetching securely...";
    document.getElementById('clinical-insight-text').innerText = "AI is analyzing medical history...";
    document.getElementById('lang-toggle-btn').style.display = 'none';
    document.getElementById('chart-wrap').style.display = 'none';

    fetch(`/api/search?patient_id=${pid}`)
    .then(res => res.json())
    .then(data => {
        if (data.status === 'error') {
            document.getElementById('patient_title').innerText = "Patient Not Found";
            document.getElementById('clinical-insight-text').innerText = data.message;
            return;
        }

        document.getElementById('patient_title').innerText = `Executive Labor Briefing: ${pid}`;
        
        // Setup AI Insight toggles
        currentInsightEn = data.insight_en;
        currentInsightHi = data.insight_hi;
        showingHindi = false;
        
        document.getElementById('clinical-insight-text').innerText = currentInsightEn;
        
        if (currentInsightEn && currentInsightHi) {
            document.getElementById('lang-toggle-btn').style.display = 'block';
            document.getElementById('lang-toggle-btn').innerText = "Translate Insight to Hindi";
        }
        
        renderCharts(data.history);
        document.getElementById('chart-wrap').style.display = 'block';
    })
    .catch(err => {
        document.getElementById('patient_title').innerText = "Connection Error";
        document.getElementById('clinical-insight-text').innerText = "Failed to connect to AI Core.";
    });
}

function toggleLanguage() {
    showingHindi = !showingHindi;
    const insightBox = document.getElementById('clinical-insight-text');
    const btn = document.getElementById('lang-toggle-btn');
    
    if (showingHindi) {
        insightBox.innerText = currentInsightHi;
        btn.innerText = "Translate Insight to English";
    } else {
        insightBox.innerText = currentInsightEn;
        btn.innerText = "Translate Insight to Hindi";
    }
}

// ==========================================
// 7. CHART.JS GRAPH RENDERING
// ==========================================
let charts = {};
function renderCharts(history) {
    const commonOptions = {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
            x: { title: { display: true, text: 'Week', font: {size: 10} } },
            y: { title: { display: true, font: {size: 10} } }
        }
    };

    const createChart = (id, label, data, color) => {
        const ctx = document.getElementById(id).getContext('2d');
        if (charts[id]) charts[id].destroy();
        charts[id] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: history.weeks,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: color,
                    backgroundColor: color + '33',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 4
                }]
            },
            options: { ...commonOptions, scales: { ...commonOptions.scales, y: { title: { display: true, text: label, font: {size: 10} } } } }
        });
    };

    createChart('chart_bp', 'Sys. BP (mmHg)', history.bp, '#d32f2f');
    createChart('chart_hb', 'Hemoglobin (g/dL)', history.hb, '#1976d2');
    createChart('chart_sugar', 'Blood Sugar (mg/dL)', history.sugar, '#ed6c02');
}
