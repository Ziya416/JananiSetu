let currentLang = 'en';
let savedInsightEn = '';
let savedInsightHi = '';
let chartInstances = {}; // Keep track of charts so we can destroy them on new searches

let isSignupMode = false;

function toggleAuthMode() {
    isSignupMode = !isSignupMode;
    document.getElementById('authTitle').innerText = isSignupMode ? "Create an Account" : "Login to JananiSetu";
    document.getElementById('authActionBtn').innerText = isSignupMode ? "Sign Up" : "Login";
    document.getElementById('authToggleHint').innerText = isSignupMode ? "Already have an account? Login" : "Don't have an account? Sign up";
    document.getElementById('roleSelection').style.display = isSignupMode ? "block" : "none";
}

function togglePasswordVisibility(inputId, btnElement) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        btnElement.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>'; 
    } else {
        input.type = "password";
        btnElement.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'; 
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
                document.getElementById('loginOverlay').style.display = 'none';      // Successful Login: Dismiss overlay and unlock full platform for everyone
                
                let roleName = "Health Worker";
                if (data.role === 'phc') roleName = "PHC Worker";
                if (data.role === 'chc') roleName = "CHC Worker";
                if (data.role === 'institutional') roleName = "Institutional Worker";

                alert(`Welcome! Logged in as ${roleName}. Accessing full platform.`);
                document.querySelectorAll('.station').forEach(s => s.style.display = 'flex');                // Ensuring both stations are visible to everyone
                goTo('p1');
            }
        } else {
            alert(data.message);
        }
    });
}

// --- JSON TRANSLATION DICTIONARY ---
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

// --- LANGUAGE TOGGLE FUNCTION ---
function toggleLang(lang, btnElement) {
    // 1. Update the button styles visually
    document.querySelectorAll('.lang-toggle button').forEach(btn => btn.classList.remove('active'));
    if (btnElement) {
        btnElement.classList.add('active');
    }

    // 2. Map through all HTML elements that have the data-translate attribute
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });
}

function toggleLang(lang, btn) {
    document.querySelectorAll('.lang-toggle button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if(translations[key]) {
            if(el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.placeholder = translations[key][lang];
            } else {
                el.innerText = translations[key][lang];
            }
        }
    });
}

function goTo(id){
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    document.querySelectorAll('.station').forEach((s, idx) => {
        s.classList.toggle('active', (id === 'p1' && idx === 0) || (id === 'p2' && idx === 1));
    });
}

function dismissWelcome(){ document.getElementById('welcomeBanner').classList.add('dismissed'); }

function setEntryMode(mode, clickedBtn) {
    document.querySelectorAll('#entryToggleGroup button').forEach(b => b.classList.remove('active'));
    clickedBtn.classList.add('active');
    document.getElementById('uploadZone').style.display = mode === 'ocr' ? 'block' : 'none';
    document.getElementById('manualEntryZone').style.display = mode === 'manual' ? 'block' : 'none';
}

function showIdentityMethod(type, btn) {
    document.querySelectorAll('#identityToggleGroup button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('scannerZone').style.display = type === 'scan' ? 'block' : 'none';
    document.getElementById('manualSearchZone').style.display = type === 'manual' ? 'block' : 'none';
    document.getElementById('demoSearchZone').style.display = type === 'demo' ? 'block' : 'none';
}

let uploadedImageBase64 = "";

function handleImageSelect(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            uploadedImageBase64 = e.target.result; // Save the base64 string for the API call
            document.getElementById('processBtn').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function processOCR() {
    const btn = document.getElementById('processBtn');
    if (!uploadedImageBase64) {
        return alert("Please select an image first.");
    }
    
    btn.innerText = "Analyzing Document with AI...";
    fetch('/api/ocr', {                  // Call the real Gemini Vision endpoint in app.py
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: uploadedImageBase64 })
    })
    .then(res => res.json())
    .then(data => {
        btn.innerText = "Process Document";
        
        if (data.status === "success" && data.data) {
            // Autofill the manual entry form with the AI extracted data
            if(data.data.Patient_ID) document.getElementById('man_id').value = data.data.Patient_ID;
            if(data.data.Name) document.getElementById('man_name').value = data.data.Name;
            if(data.data.Blood_Pressure) document.getElementById('man_bp').value = data.data.Blood_Pressure;
            if(data.data.Hemoglobin_Hb) document.getElementById('man_hb').value = data.data.Hemoglobin_Hb;
            if(data.data.Blood_Sugar) document.getElementById('man_sugar').value = data.data.Blood_Sugar;
            
            alert("Document AI extraction complete! Please verify the details.");
            
            setEntryMode('manual', document.querySelectorAll('#entryToggleGroup button')[1]);  // Automatically switch the UI to manual mode so the user can see the filled data
        } else {
            alert("Error: " + (data.message || "Failed to parse document."));
        }
    })
    .catch(err => {
        btn.innerText = "Process Document";
        alert("Connection error during OCR.");
    });
}

function savePatientData() {
    const payload = {
        Patient_ID: document.getElementById('man_id').value,
        Name: document.getElementById('man_name').value, 
        Husband_Name: document.getElementById('man_husband').value,
        Village: document.getElementById('man_village').value,
        LMP: document.getElementById('man_lmp').value,
        EDD: document.getElementById('man_edd').value,
        Obstetric_History: document.getElementById('man_obs').value,
        Visit_Week: document.getElementById('man_week').value,
        Blood_Pressure: document.getElementById('man_bp').value,
        Hemoglobin_Hb: document.getElementById('man_hb').value,
        Blood_Sugar: document.getElementById('man_sugar').value,
        Seizure_History: document.getElementById('man_seizure').value,
        HHH_Status: document.getElementById('man_hhh').value,
        Comorbidities_Remarks: document.getElementById('man_notes').value
    };

    if (!payload.Patient_ID || !payload.Visit_Week) return alert("Patient ID and Visit Week are required!");
    fetch('/api/save', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify(payload) 
    }).then(res => res.json()).then(data => alert(data.message));
}

async function searchByDemographics() {
    const name = document.getElementById('demo_name').value.trim();
    const village = document.getElementById('demo_village').value.trim();
    if (!name || !village) return alert("Please enter both Name and Village.");

    try {
        const res = await fetch(`/api/search_demographic?name=${encodeURIComponent(name)}&village=${encodeURIComponent(village)}`);
        const data = await res.json();
        if (data.status === "success") {
            alert("Patient found! Loading records for ID: " + data.patient_id);
            document.getElementById('search_id').value = data.patient_id;
            simulateSearch(); 
        } else {
            alert("Error: " + data.message);
        }
    } catch (e) { alert("Failed to connect to the server."); }
}

function renderChart(canvasId, label, dataArray, labelsArray, color, maxVal) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (chartInstances[canvasId]) chartInstances[canvasId].destroy();
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labelsArray,
            datasets: [{
                label: label,
                data: dataArray,
                borderColor: color,
                backgroundColor: color,
                tension: 0.3,
                borderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0, max: maxVal },
                x: { title: { display: true, text: 'Gestational Week' } }
            }
        }
    });
}

function simulateSearch() {
    const input = document.getElementById('search_id');
    if (!input || input.value.trim() === "") return alert("Please enter a Patient ID.");
    document.getElementById('briefingBox').style.display = 'block';
    document.getElementById('clinical-insight-text').innerText = "Agent 3 is analyzing database...";
    const chartWrap = document.getElementById('chart-wrap');

    if (chartWrap) chartWrap.style.display = 'none';
    fetch('/api/search?patient_id=' + input.value)
    .then(res => res.json())
    .then(data => {
        if (data.status === "error") {
            alert(data.message);
            document.getElementById('briefingBox').style.display = 'none';
            return;
        }

        document.getElementById('patient_title').innerText = "Briefing for " + input.value;
        savedInsightEn = data.insight_en;
        savedInsightHi = data.insight_hi;
        currentLang = 'en'; 
        
        document.getElementById('clinical-insight-text').innerText = savedInsightEn;
        document.getElementById('lang-toggle-btn').style.display = "block";
        document.getElementById('lang-toggle-btn').innerText = "Translate to Hindi";

        if (chartWrap && data.history) {
            chartWrap.style.display = 'block'; 
            renderChart('chart_bp', 'Systolic BP', data.history.bp, data.history.weeks, '#C1483D', 200);
            renderChart('chart_hb', 'Hemoglobin (Hb)', data.history.hb, data.history.weeks, '#3E6FB0', 20);
            renderChart('chart_sugar', 'Blood Sugar', data.history.sugar, data.history.weeks, '#E8A33D', 300);
        }
    }).catch(err => {
        document.getElementById('clinical-insight-text').innerText = "Error connecting to backend.";
    });
}    
