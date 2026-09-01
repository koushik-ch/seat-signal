import datetime
import importlib.util
import json
import unittest


MCP_AVAILABLE = importlib.util.find_spec("mcp") is not None


@unittest.skipUnless(MCP_AVAILABLE, "install requirements.txt to run MCP integration tests")
class MCPRecommendationTests(unittest.TestCase):
    def test_recommendation_tool_accepts_pvr_seats_json_list(self):
        import mcp_server

        future_date = (
            mcp_server.core.today_ist() + datetime.timedelta(days=1)
        ).isoformat()

        originals = (
            mcp_server.core.city_is_serviced,
            mcp_server.core.find_cinema,
            mcp_server.core.day_sessions,
            mcp_server.core.seat_report,
        )
        try:
            mcp_server.core.city_is_serviced = lambda _city: True
            mcp_server.core.find_cinema = lambda _city, cinema_id: {"cinema_id": cinema_id}
            mcp_server.core.day_sessions = lambda *args, **kwargs: ([
                {
                    "film": "TEST FILM",
                    "time": "07:45 PM",
                    "status": "Available",
                    "token": "opaque",
                    "screen": "IMAX",
                    "experience": "imax",
                    "language": "en",
                    "booking_url": "https://example.invalid/book",
                }
            ], None)
            mcp_server.core.seat_report = lambda *args, **kwargs: ({
                "total": 100,
                "free": 20,
                "zone_total": 20,
                "zone_free": 4,
                "zone_held": 0,
                "best_run": 4,
                "best_where": "D13-D16",
                "zone_rows": ["D"],
                "widened_to": [],
                "meets_party_size": True,
                "free_outside_zone": 16,
                "recommendation": {
                    "seats": ["D14", "D15"],
                    "span": "D14-D15",
                    "score": 0.96,
                    "in_zone": True,
                    "score_breakdown": {"centre": 0.98},
                    "reasons": ["inside the preferred zone"],
                },
                "recommendations": [],
                "exact_alternatives": [],
                "rows_seen": ["D"],
                "all_labels": [],
                "free_labels": [],
                "zone_labels": [],
                "zone_free_labels": [],
                "status_codes": {"1": 20, "2": 80},
            }, None)
            raw = mcp_server.pvr_recommend_seats(
                city="Chennai",
                cinema_id="1",
                date=future_date,
                party_size=2,
                format="json",
            )
            payload = json.loads(raw)
            self.assertEqual(
                payload["recommendations"][0]["recommendation"]["span"],
                "D14-D15",
            )
        finally:
            (
                mcp_server.core.city_is_serviced,
                mcp_server.core.find_cinema,
                mcp_server.core.day_sessions,
                mcp_server.core.seat_report,
            ) = originals


if __name__ == "__main__":
    unittest.main()
