🏥 JananiSetu

AI-Powered Maternal Health Intelligence Platform for Rural Healthcare Systems

📌 Overview

JananiSetu is an intelligent maternal healthcare system designed to address a critical challenge in rural medical ecosystems: lack of accessible patient history during emergencies.

In many rural areas, patients often arrive for delivery without medical records, forcing healthcare providers to repeat diagnostics and lose crucial time—delays that can become life-threatening in high-risk cases such as preeclampsia or gestational hypertension.

JananiSetu bridges this gap by transforming fragmented, paper-based records into a centralized, AI-driven decision support system, enabling real-time access to maternal health data across the full pregnancy timeline.

🚀 Key Capabilities
📂 Centralized Maternal Registry
Longitudinal tracking of patient health across 42 weeks of pregnancy
🤖 AI Clinical Insight Engine
Real-time analysis of vitals (BP, Hb, Sugar) with automated risk alerts
🔍 Intelligent Retrieval System
Access patient history via:
Unique Patient ID
Government-issued ID
Name + Village (fallback for low-resource scenarios)
🌐 Multilingual Accessibility
AI-generated clinical insights available in English + Hindi
📄 Vision-Based OCR (Document AI)
Digitizes handwritten medical reports to reduce manual data entry
🔐 Role-Based Authentication
Secure access for:
PHC workers
CHC staff
Institutional hospitals
🧠 System Evolution
🔹 Version 1.0 — AI-Orchestrated Cloud System

Built as a cloud-native AI platform, focusing on intelligent data retrieval and clinical reasoning.

Architecture Highlights:

Backend: Python (Flask)
AI Layer: LLM-powered Orchestrator (Gemini)
Data Storage: Google BigQuery
Retrieval: RAG-based contextual search
OCR: Gemini Vision-based document extraction

Key Innovation:

Transition from static record storage → context-aware AI decision system

Instead of simple queries, JananiSetu uses a Retrieval-Augmented Generation (RAG) pipeline to:

Retrieve longitudinal patient history
Generate real-time clinical insights
Highlight risk alerts for doctors
🔹 Version 2.0 — Simulated Production Environment

Redesigned to demonstrate real-world deployability and scalability.

Major Upgrades:

⚡ Migration to Node.js + Express architecture
🗄️ Transition from BigQuery → SQLite (zero-cost deployment)
📊 Interactive dashboards using Chart.js
🧪 Synthetic dataset generator simulating real-world patient timelines
🔄 Full-stack separation (frontend + backend)

Synthetic Data Pipeline:

Generates 50+ patient profiles
Covers 42-week pregnancy lifecycle
Injects real-world edge cases:
Preeclampsia
Gestational Diabetes
Anemia

Key Focus:

Demonstrating production readiness under resource constraints

⚙️ Technical Architecture
🧩 Backend (Flask API)
RESTful APIs for:
Authentication (/api/signup, /api/login)
OCR processing (/api/ocr)
Patient storage (/api/save)
Intelligent search (/api/search)
Secure password hashing (Werkzeug)
SQLite-based persistent storage
🧠 AI Layer
1. OCR Engine (Gemini Vision)
Extracts structured medical data from images
Converts unstructured reports → structured JSON
2. LLM Orchestrator
Analyzes:
Blood Pressure
Hemoglobin
Blood Sugar
Comorbidities
Generates:
Clinical risk alerts
Actionable summaries
Bilingual output (EN + HI)
3. Retrieval System (RAG-based)
Fetches complete patient timeline
Enables context-aware reasoning instead of keyword search
📊 Data Processing Pipeline
Time-series extraction of:
BP trends
Hb levels
Sugar levels
Numerical parsing from noisy inputs
Structured historical visualization
🔐 Authentication System
Role-based access control:
PHC (data entry)
CHC / Hospital (analysis & decision-making)
Secure credential storage with hashing
🌍 Real-World Impact

JananiSetu directly addresses:

❌ Missing maternal records in rural areas
❌ Delayed clinical decisions during emergencies
❌ Fragmented healthcare systems

By enabling:

✅ Faster diagnosis and response
✅ Reduced maternal mortality risks
✅ Data-driven healthcare delivery
🧪 Live Demo

🔗 https://jananisetu.onrender.com/

📸 Screenshots

<img width="948" height="470" alt="image" src="https://github.com/user-attachments/assets/a80bdb24-7546-42b0-9cdc-c92ac2e319a6" />

<img width="947" height="472" alt="image" src="https://github.com/user-attachments/assets/87c0cc4f-3a83-4345-a2be-a6faa7b3d54f" />

<img width="948" height="474" alt="image" src="https://github.com/user-attachments/assets/f3cedd9f-491f-4e02-b353-c1121b67d6b3" />

<img width="948" height="472" alt="image" src="https://github.com/user-attachments/assets/993c0539-c3ad-4ae5-96e8-d00a9628500a" />

<img width="948" height="472" alt="image" src="https://github.com/user-attachments/assets/ba3a1d7e-cfb2-4dc8-8017-924c55a886cc" />

<img width="950" height="471" alt="image" src="https://github.com/user-attachments/assets/71d92606-aadf-436d-825c-9086dda63cac" />

<img width="945" height="469" alt="image" src="https://github.com/user-attachments/assets/0cf69e80-0f80-4acf-a3c6-c036453d3695" />

<img width="949" height="470" alt="image" src="https://github.com/user-attachments/assets/38d31d25-a24d-4ce5-9de7-7cd52bf1aaa5" />

<img width="948" height="470" alt="image" src="https://github.com/user-attachments/assets/e763a4dc-0f7a-448f-a3d7-e496fc1d4bf6" />

https://github.com/user-attachments/assets/fd5ee1a7-7088-490c-90d9-61dc8110addd

✨ Features and Applications:
Dashboard view
OCR scanning interface
Risk analysis output
Patient history graph
🔮 Future Enhancements
🔗 Integration with national health IDs (ABHA)
☁️ Scalable cloud deployment (GCP / AWS)
📱 Mobile-first interface for ASHA workers
🧠 Predictive risk modeling using ML pipelines
🔐 Advanced healthcare data compliance (HIPAA-like standards)
