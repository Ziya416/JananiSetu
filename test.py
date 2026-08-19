import unittest
import json
import sqlite3
import os
from app import app, init_db, DB_NAME

class JananiSetuAPITestCase(unittest.TestCase):
    """
    Test suite for JananiSetu Flask API endpoints and SQLite database operations.
    Run this file to ensure all critical backend routes are functioning correctly.
    """

    @classmethod
    def setUpClass(cls):
        """Set up a fresh database before running any tests."""
        app.config['TESTING'] = True
        cls.client = app.test_client()
        init_db()

    def test_01_home_route(self):
        """Test if the main frontend serves correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_02_signup_success(self):
        """Test creating a new health worker account."""
        payload = {
            "username": "test_phc",
            "password": "securepassword123",
            "role": "phc"
        }
        response = self.client.post(
            '/api/signup',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_03_signup_duplicate(self):
        """Test that duplicate usernames are rejected."""
        payload = {
            "username": "test_phc",
            "password": "differentpassword",
            "role": "chc"
        }
        response = self.client.post(
            '/api/signup',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("already exists", data["message"])

    def test_04_login_success(self):
        """Test secure login with valid credentials."""
        payload = {
            "username": "test_phc",
            "password": "securepassword123"
        }
        response = self.client.post(
            '/api/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["role"], "phc")

    def test_05_login_failure(self):
        """Test login rejection with invalid credentials."""
        payload = {
            "username": "test_phc",
            "password": "wrongpassword"
        }
        response = self.client.post(
            '/api/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

    def test_06_save_patient_data(self):
        """Test insertion of new maternal health records into SQLite."""
        payload = {
            "Patient_ID": "TEST-001",
            "Name": "Aarti Sharma",
            "Husband_Name": "Ramesh",
            "Village": "Surat",
            "LMP": "01/01/2026",
            "EDD": "08/10/2026",
            "Obstetric_History": "G2 P1 A0 L1",
            "Visit_Week": 24,
            "Blood_Pressure": "120/80",
            "Hemoglobin_Hb": 11.5,
            "Blood_Sugar": 95,
            "Seizure_History": "none",
            "HHH_Status": "No",
            "Comorbidities_Remarks": "Normal"
        }
        response = self.client.post(
            '/api/save',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_07_search_demographic(self):
        """Test fetching a patient ID using Name and Village."""
        response = self.client.get('/api/search_demographic?name=Aarti&village=Surat')
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["patient_id"], "TEST-001")

if __name__ == '__main__':
    unittest.main()
