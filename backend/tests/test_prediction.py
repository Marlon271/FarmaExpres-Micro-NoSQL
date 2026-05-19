import unittest

from app.services.prediction import build_predictions


class PredictionServiceTest(unittest.TestCase):
    def test_build_predictions_prioritizes_high_risk_demand(self):
        cleaned_records = [
            {
                "product_id": "MED-001",
                "product_code": "MED-001",
                "product_name": "Ibuprofeno 400 mg",
                "category": "Analgesico",
                "movement_type": "Exit",
                "amount": 10,
                "movement_date": "2026-05-01",
                "stock": 12,
                "minimum_stock": 5,
                "is_valid": True,
            },
            {
                "product_id": "MED-001",
                "product_code": "MED-001",
                "product_name": "Ibuprofeno 400 mg",
                "category": "Analgesico",
                "movement_type": "Exit",
                "amount": 10,
                "movement_date": "2026-05-02",
                "stock": 12,
                "minimum_stock": 5,
                "is_valid": True,
            },
            {
                "product_id": "MED-002",
                "product_code": "MED-002",
                "product_name": "Loratadina 10 mg",
                "category": "Antihistaminico",
                "movement_type": "Snapshot",
                "amount": 0,
                "movement_date": "2026-05-02",
                "stock": 40,
                "minimum_stock": 10,
                "is_valid": True,
            },
        ]
        snapshots = [
            {
                "product_id": "MED-001",
                "product_code": "MED-001",
                "product_name": "Ibuprofeno 400 mg",
                "category": "Analgesico",
                "current_stock": 12,
                "minimum_stock": 5,
            },
            {
                "product_id": "MED-002",
                "product_code": "MED-002",
                "product_name": "Loratadina 10 mg",
                "category": "Antihistaminico",
                "current_stock": 40,
                "minimum_stock": 10,
            },
        ]

        predictions, metrics = build_predictions(cleaned_records, snapshots, horizon_days=30)

        self.assertEqual(metrics["method"], "30_day_moving_average")
        self.assertEqual(metrics["products_evaluated"], 2)
        self.assertEqual(metrics["valid_records_used"], 3)
        self.assertEqual(predictions[0]["product_id"], "MED-001")
        self.assertEqual(predictions[0]["risk_level"], "HIGH")
        self.assertEqual(predictions[0]["predicted_demand_units"], 21)
        self.assertEqual(predictions[1]["risk_level"], "LOW")


if __name__ == "__main__":
    unittest.main()
