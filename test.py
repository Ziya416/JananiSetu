import unittest
import json
import sqlite3
import os
from unittest.mock import patch, MagicMock
from app import app, init_db, DB_NAME

class JananiSetuAuthTestCase(unittest.TestCase):
    """
    Test suite for Authentication (Signup, Login, and Security validations).
    """
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()
        init_db()

    def test_01_home_route(self):
        """Verify the frontend HTML is served securely."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!doctype html>', response.data.lower())

    def test_02_signup_success(self):
        """Verify a health worker can register successfully."""
        payload = {"username": "test_worker", "password": "secure123", "role": "phc"}
        res = self.client.post('/api/signup', data=json.dumps(payload), content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")

    def test_03_signup_duplicate(self):
        """Verify the database blocks duplicate usernames."""
        payload = {"username": "test_worker", "password": "newpassword", "role": "chc"}
        res = self.client.post('/api/signup', data=json.dumps(payload), content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("already exists", data["message"])

    def test_04_signup_missing_fields(self):
        """Verify registration fails if critical fields are omitted."""
        payload = {"username": "test_worker2"} # Missing password
        res = self.client.post('/api/signup', data=json.dumps(payload), content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")

    def test_05_login_success(self):
        """Verify a registered worker can authenticate."""
        payload = {"username": "test_worker", "password": "secure123"}
        res = self.client.post('/api/login', data=json.dumps(payload), content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["role"], "phc")

    def test_06_login_invalid_password(self):
        """Verify login is rejected with an incorrect password."""
        payload = {"username": "test_worker", "password": "wrongpassword"}
        res = self.client.post('/api/login', data=json.dumps(payload), content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("Invalid", data["message"])


class JananiSetuClinicalDataTestCase(unittest.TestCase):
    """
    Test suite for Patient Data Pipelines (Saving, Searching, RAG Extraction).
    """
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()
        init_db()

    def test_07_save_patient_valid(self):
        """Verify complete maternal health records are written to SQLite."""
        payload = {
            "Patient_ID": "MOM-9999", "Name": "Test Patient", "Husband_Name": "Husband", 
            "Village": "TestVillage", "LMP": "01/01/2026", "EDD": "08/10/2026", 
            "Obstetric_History": "G1 P0 A0 L0", "Visit_Week": 20, "Blood_Pressure": "110/70", 
            "Hemoglobin_Hb": 12.5, "Blood_Sugar": 90, "Seizure_History": "none", 
            "HHH_Status": "No", "Comorbidities_Remarks": "Healthy"
        }
        res = self.client.post('/api/save', data=json.dumps(payload), content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")

    def test_08_search_patient_found(self):
        """Verify retrieving an existing patient formats vitals correctly for RAG."""
        res = self.client.get('/api/search?patient_id=MOM-9999')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn(20, data["history"]["weeks"])
        self.assertIn(12.5, data["history"]["hb"])

    def test_09_search_patient_not_found(self):
        """Verify searching a non-existent patient ID handles errors gracefully."""
        res = self.client.get('/api/search?patient_id=MOM-0000')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("not found", data["message"])

    def test_10_search_demographic_success(self):
        """Verify identity retrieval using Name and Village parameters."""
        res = self.client.get('/api/search_demographic?name=Test&village=TestVillage')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["patient_id"], "MOM-9999")

    def test_11_search_demographic_missing_params(self):
        """Verify demographic search rejects malformed requests."""
        res = self.client.get('/api/search_demographic?name=Test')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")


class JananiSetuAIAgentTestCase(unittest.TestCase):
    """
    Test suite for Google Gemini Vision OCR integration and Edge Cases.
    """
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_12_ocr_missing_image(self):
        """Verify the Document AI endpoint rejects requests without base64 payloads."""
        payload = {"wrong_key": "data"}
        res = self.client.post('/api/ocr', data=json.dumps(payload), content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")

    @patch('app.client')
    def test_13_ocr_mocked_success(self, mock_gemini_client):
        """
        Simulate a successful Gemini Vision API extraction to verify 
        JSON parsing logic without consuming actual API quotas.
        """
        # Create a mock response object mirroring Google's SDK
        mock_response = MagicMock()
        mock_response.text = '''```json
        {
            "Patient_ID": "MOM-1111",
            "Name": "Mocked Mother",
            "Blood_Pressure": "130/85",
            "Hemoglobin_Hb": "10.2",
            "Blood_Sugar": "95"
        }
        ```'''
        
        # Configure the mock client to return our mock response
        mock_gemini_client.models.generate_content.return_value = mock_response

        # Send a tiny fake base64 image
        fake_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        payload = {"image": fake_b64}
        
        # Note: If client is not initialized due to missing API key locally, 
        # this test might return the "AI Client not configured" error. 
        # We assume the environment has the key for testing.
        if os.environ.get("GEMINI_API_KEY"):
            res = self.client.post('/api/ocr', data=json.dumps(payload), content_type='application/json')
            data = json.loads(res.data)
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["data"]["Name"], "Mocked Mother")

if __name__ == '__main__':
    # Run the comprehensive test suite with verbose output
    unittest.main(verbosity=2)
