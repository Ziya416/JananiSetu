let currentLang = 'en';
let savedInsightEn = '';
let savedInsightHi = '';
let chartInstances = {}; // Keep track of charts so we can destroy them on new searches

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
    // ... (Keep all your existing translation keys here, omitted for brevity)
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

function handleImageSelect(input) {
    if (input.files && input.files[0]) document.getElementById('processBtn').style.display = 'block';
}

function processOCR() {
    const btn = document.getElementById('processBtn');
    btn.innerText = "Analyzing Document...";
    setTimeout(() => {
        alert("OCR Complete! Switch to manual to verify details.");
        btn.innerText = "Process Document";
        setEntryMode('manual', document.querySelectorAll('#entryToggleGroup button')[1]);
    }, 1200);
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
            
            // Generate beautiful frontend charts
            renderChart('chart_bp', 'Systolic BP', data.history.bp, data.history.weeks, '#C1483D', 200);
            renderChart('chart_hb', 'Hemoglobin (Hb)', data.history.hb, data.history.weeks, '#3E6FB0', 20);
            renderChart('chart_sugar', 'Blood Sugar', data.history.sugar, data.history.weeks, '#E8A33D', 300);
        }
    }).catch(err => {
        document.getElementById('clinical-insight-text').innerText = "Error connecting to backend.";
    });
}