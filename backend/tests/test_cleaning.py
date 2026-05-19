import unittest

from app.services.cleaning import clean_records, normalize_name, parse_date


class CleaningServiceTest(unittest.TestCase):
    def test_normalize_name_removes_accents_and_extra_spaces(self):
        self.assertEqual(normalize_name("  Ácido   acetilsalicílico  "), "ACIDO ACETILSALICILICO")

    def test_parse_date_standardizes_iso_datetime(self):
        self.assertEqual(parse_date("2026-05-19T10:20:30Z"), "2026-05-19T10:20:30+00:00")

    def test_parse_date_accepts_java_nanosecond_timestamp(self):
        self.assertEqual(
            parse_date("2026-05-19T14:54:06.717387180Z"),
            "2026-05-19T14:54:06.717387+00:00",
        )

    def test_clean_records_removes_duplicates_and_reports_iterator_input(self):
        raw_records = iter(
            [
                {
                    "product_id": 1,
                    "product_code": "MED-001",
                    "product_name": "Ibuprofeno 400 mg",
                    "movement_type": "Exit",
                    "amount": 4,
                    "stock": 24,
                    "minimum_stock": 10,
                    "movement_date": "2026-05-01",
                    "batch_code": "B-001",
                },
                {
                    "product_id": 1,
                    "product_code": "MED-001",
                    "product_name": "Ibuprofeno 400 mg",
                    "movement_type": "Exit",
                    "amount": 4,
                    "stock": 24,
                    "minimum_stock": 10,
                    "movement_date": "2026-05-01",
                    "batch_code": "B-001",
                },
                {
                    "product_id": 2,
                    "product_code": "MED-002",
                    "product_name": "Vitamina C",
                    "movement_type": "Exit",
                    "amount": -3,
                    "stock": 12,
                    "minimum_stock": 8,
                    "movement_date": "2026-05-02",
                },
            ]
        )

        cleaned, metrics = clean_records(raw_records)

        self.assertEqual(metrics["input_records"], 3)
        self.assertEqual(metrics["cleaned_records"], 2)
        self.assertEqual(metrics["duplicates_removed"], 1)
        self.assertEqual(metrics["invalid_records"], 1)
        self.assertEqual(cleaned[0]["normalized_product_name"], "IBUPROFENO 400 MG")
        self.assertEqual(cleaned[1]["quality_flags"], ["negative_amount"])


if __name__ == "__main__":
    unittest.main()
