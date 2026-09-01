import unittest

import core


def make_row(name, numbers, free=None, aisle_before=None):
    free = set(numbers if free is None else free)
    seats = []
    aisle_before = set(aisle_before or [])
    for number in numbers:
        if number in aisle_before:
            seats.append({"sn": None, "displaynumber": None, "s": 0})
        seats.append(
            {
                "sn": "%s%d" % (name, number),
                "displaynumber": number,
                "s": 1 if number in free else 2,
            }
        )
    return {"n": name, "t": "seats", "s": seats}


class SeatRecommendationTests(unittest.TestCase):
    def test_recommendation_never_crosses_an_aisle(self):
        row = make_row("D", list(range(1, 6)) + list(range(10, 15)), aisle_before={10})
        recommendations = core.recommend_seats(
            [row], {"D": set(range(1, 6)) | set(range(10, 15))}, party_size=2
        )
        self.assertTrue(recommendations)
        for recommendation in recommendations:
            seats = recommendation["seats"]
            self.assertEqual(len(seats), 2)
            self.assertFalse({5, 10}.issubset({core._seat_no(label) for label in seats}))

    def test_recommendation_prefers_the_centre_of_the_preferred_block(self):
        row = make_row("D", range(1, 22))
        recommendations = core.recommend_seats(
            [row], {"D": set(range(1, 22))}, party_size=2, limit=5
        )
        self.assertEqual(recommendations[0]["span"], "D10-D11")
        self.assertTrue(recommendations[0]["in_zone"])
        self.assertIn("near the horizontal centre", recommendations[0]["reasons"])

    def test_seat_report_contains_exact_pick_and_alternatives(self):
        original = core._post
        try:
            core._post = lambda _path, _body: {
                "status": 200,
                "output": {
                    "cinemaName": "Test Cinema",
                    "rows": [make_row("D", range(1, 12))],
                },
            }
            report, error = core.seat_report(
                "opaque", zone_rows=["D"], zone_seats=[1, 11], party_size=2
            )
        finally:
            core._post = original
        self.assertIsNone(error)
        self.assertEqual(report["recommendation"]["span"], "D5-D6")
        self.assertTrue(report["recommendations"])
        self.assertIn("score_breakdown", report["recommendation"])


if __name__ == "__main__":
    unittest.main()
