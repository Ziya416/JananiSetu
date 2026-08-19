# JananiSetu
JananiSetu is an intelligent maternal health system designed to support frontline health workers (ANMs) in rural areas and institutional centres. It addresses the critical challenge of missing patient records by providing a centralized, AI-driven digital hub for maternal health data, ensuring that mother's health is monitored throughout the pregnancy.

# Features
- Centralized Maternal Registry : A digital repository that tracks patient health vitals securely over the 42-week gestational period.
- AI Orchestrator Agent : A central controller that performs the tasks like analyzing health vitals, triggering clinical alerts, and managing language translation services.
- AI Clinical Insight : Real-time processing of blood pressure, hemoglobin, and blood sugar levels to provide actionable health insights.
- Accessibility : Dynamic translation features to assist health workers in localizing medical guidance.
  
# Technical Stack
- Backend : Python (Flask)
- AI Logic : LLM-powered Orchestrator Agent & Analytical Models
- Data Infrastructure : Google BigQuery
- Deployment : Google Cloud Platform

# 🚀 What's New in v2.0 (Simulated Real-World Environment)
JananiSetu has been upgraded from a proof-of-concept to a simulated production environment:
* **Architecture Shift:** Migrated from a Python/Flask & GCP Vertex AI backend to a lightweight **Node.js & Express** architecture.
* **Synthetic Data Pipeline:** Integrated a custom Python generator creating 50+ realistic 42-week patient timelines, including injected high-risk edge cases (Preeclampsia, Gestational Diabetes, Anemia).
* **Interactive Analytics:** Replaced static image generation with dynamic, interactive frontend charts using **Chart.js**.
* **Zero-Cloud Dependency:** Replaced BigQuery with a local SQLite database for seamless, zero-cost deployment.

