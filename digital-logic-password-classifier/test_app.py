"""
test_app.py
Comprehensive unit and integration testing of the Flask application and routes.
"""

import unittest
import json
import io
from app import app


class DigitalLogicAppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_pages_render(self):
        pages = [
            "/",
            "/about",
            "/classifier",
            "/logic-analysis",
            "/test-cases",
            "/dataset",
            "/dashboard",
            "/report",
            "/deliverables",
            "/requirements.txt"
        ]
        for p in pages:
            response = self.client.get(p)
            self.assertEqual(response.status_code, 200, f"Page {p} returned status {response.status_code}")

    def test_api_classify(self):
        response = self.client.post("/api/classify", 
                                    data=json.dumps({"password": "Admin@2026Secure!"}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["score"], 5)
        self.assertEqual(data["category"], "Very Strong")
        self.assertEqual(data["attributes"]["A"], 1)
        self.assertEqual(data["attributes"]["B"], 1)
        self.assertEqual(data["attributes"]["C"], 1)
        self.assertEqual(data["attributes"]["D"], 1)
        self.assertEqual(data["attributes"]["E"], 1)
        self.assertEqual(data["minterm"], "m31")

    def test_api_truth_table(self):
        response = self.client.get("/api/truth-table")
        self.assertEqual(response.status_code, 200)
        table = response.get_json()
        self.assertEqual(len(table), 32)
        self.assertEqual(table[0]["minterm"], "m0")
        self.assertEqual(table[31]["minterm"], "m31")

    def test_api_test_cases(self):
        response = self.client.post("/api/test-cases/run")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["total"], 15)
        self.assertEqual(data["passed"], 15)
        self.assertEqual(data["failed"], 0)
        self.assertEqual(data["accuracy_rate"], 100.0)

    def test_api_dataset_generation(self):
        response = self.client.post("/api/dataset/generate",
                                    data=json.dumps({"count": 25}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["items"]), 25)

    def test_api_dashboard_stats(self):
        response = self.client.get("/api/dashboard/stats")
        self.assertEqual(response.status_code, 200)
        stats = response.get_json()
        self.assertIn("categories", stats)
        self.assertIn("scores_histogram", stats)
        self.assertIn("avg_length", stats)

    def test_api_downloads(self):
        # Sample CSV download
        res_csv = self.client.get("/api/download/sample-csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("text/csv", res_csv.content_type)

        # ZIP archive download
        res_zip = self.client.get("/api/download/project-zip")
        self.assertEqual(res_zip.status_code, 200)
        self.assertIn("application/zip", res_zip.content_type)


if __name__ == "__main__":
    unittest.main()
