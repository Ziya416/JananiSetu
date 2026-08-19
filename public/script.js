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

function toggleLanguage() {
    const textElement = document.getElementById("clinical-insight-text");
    const btn = document.getElementById("lang-toggle-btn");
    
    if (currentLang === 'en') {
        textElement.innerText = savedInsightHi;
        btn.innerText = "View in English";
        currentLang = 'hi';
    } else {
        textElement.innerText = savedInsightEn;
        btn.innerText = "Translate to Hindi";
        currentLang = 'en';
    }
}

const translations = {
    welcome_title: { en: "New here? Let's take a 20-second look around.", hi: "यहाँ नए हैं? आइए 20 सेकंड में चारों ओर देखें।" }
};

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
