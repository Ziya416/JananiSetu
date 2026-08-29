## JananiSetu
This is a maternal healthcare web application designed to provide crucial health tracking and resources. Built with Python and integrated with Google Cloud tools, the system ensures scalable and reliable access to maternal healthcare information.

## Tech Stack
Python, Google Cloud Platform (GCP), Web Framework (e.g., Flask/FastAPI), HTML/CSS/JS.

## How does this work?
This project operates as a full-stack web application with cloud-backed services.

 *Version 1 to Version 2 Improvements:*

*Architecture Overhaul*: V2 features an updated, more robust architecture deployed entirely on Google Cloud, ensuring better scalability compared to the localized V1.

*Live Deployment*: Transitioned from a local/development environment in V1 to a fully live production deployment in August 2026.

*Enhanced Data Pipeline*: Improved integration with GCP tools for more secure and efficient handling of maternal health data.

## How do I run this?
You need to have Python and the Google Cloud CLI installed.

Clone the repository and navigate into the project folder.

Run python -m venv venv to create a virtual environment, then activate it (source venv/bin/activate on Mac/Linux or venv\Scripts\activate on Windows).

Run pip install -r requirements.txt to install all necessary Python dependencies.

Authenticate with Google Cloud by running gcloud auth application-default login.

Run python app.py (or your specific start command) to launch the local development server.

You can check the UI at http://localhost:5000.

## Custom Usage & Interaction
To test the cloud integration locally, ensure your GCP project ID is correctly set in your .env file.

You can interact with the API endpoints directly using tools like Postman by hitting http://localhost:5000/api/v1/... to simulate data entry and retrieval.

## I am done experimenting with this project
Run deactivate in your terminal to exit the Python virtual environment.

If you spun up any paid GCP resources for testing (like Cloud SQL or specific Cloud Run instances), make sure to spin them down via the GCP Console or CLI to avoid unexpected charges.

## Live Demo

🔗 https://jananisetu.onrender.com/

## Screenshots

*Signups*
<img width="948" height="470" alt="image" src="https://github.com/user-attachments/assets/a80bdb24-7546-42b0-9cdc-c92ac2e319a6" />

*Login Page*
<img width="947" height="472" alt="image" src="https://github.com/user-attachments/assets/87c0cc4f-3a83-4345-a2be-a6faa7b3d54f" />

*Homepage*
<img width="948" height="474" alt="image" src="https://github.com/user-attachments/assets/f3cedd9f-491f-4e02-b353-c1121b67d6b3" />

*Manual or by Document AI data insertion* 
<img width="948" height="472" alt="image" src="https://github.com/user-attachments/assets/993c0539-c3ad-4ae5-96e8-d00a9628500a" />
<img width="948" height="472" alt="image" src="https://github.com/user-attachments/assets/ba3a1d7e-cfb2-4dc8-8017-924c55a886cc" />

*Alert & Graphs*
<img width="950" height="471" alt="image" src="https://github.com/user-attachments/assets/71d92606-aadf-436d-825c-9086dda63cac" />
<img width="945" height="469" alt="image" src="https://github.com/user-attachments/assets/0cf69e80-0f80-4acf-a3c6-c036453d3695" />

*Bilingual web app*
<img width="949" height="470" alt="image" src="https://github.com/user-attachments/assets/38d31d25-a24d-4ce5-9de7-7cd52bf1aaa5" />
<img width="948" height="470" alt="image" src="https://github.com/user-attachments/assets/e763a4dc-0f7a-448f-a3d7-e496fc1d4bf6" />

## Demo Video
https://github.com/user-attachments/assets/fd5ee1a7-7088-490c-90d9-61dc8110addd
