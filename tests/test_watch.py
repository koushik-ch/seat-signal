import datetime
import unittest

import core
import watch


class WatchPolicyTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "kind": "new_date",
            "date": "2026-08-23",
            "shows": [{"time": "07:45 PM", "screen": "IMAX", "film": "Test"}],
        }

    def test_quiet_hours_defer_and_then_release_event(self):
        config = {"name": "test", "quiet_hours": ["23:00", "07:00"]}
        state = {}
        late = datetime.datetime(2026, 8, 20, 23, 30, tzinfo=core.IST)
        self.assertTrue(watch.in_quiet_hours(config, late))
        self.assertEqual(watch.prepare_events(state, config, [self.event], late), [])
        self.assertTrue(state[watch.PENDING_ALERTS_KEY]["test"])

        morning = datetime.datetime(2026, 8, 21, 8, 0, tzinfo=core.IST)
        released = watch.prepare_events(state, config, [], morning)
        self.assertEqual(len(released), 1)

    def test_duplicate_suppression_only_after_success(self):
        config = {"name": "test", "dedup_minutes": 30}
        state = {}
        first = watch.prepare_events(state, config, [self.event])
        self.assertEqual(len(first), 1)
        # Without marking delivery, a failed notification is retryable.
        self.assertEqual(len(watch.prepare_events(state, config, [self.event])), 1)
        watch.mark_events_delivered(state, config, first)
        self.assertEqual(watch.prepare_events(state, config, [self.event]), [])

    def test_failure_alert_requires_repeated_problem(self):
        state = {}
        problem = {
            "key": "poll|test|2026-08-23",
            "kind": "poll",
            "watch": "test",
            "detail": "timeout",
        }
        self.assertEqual(watch.update_failure_state(state, [problem]), [])
        self.assertEqual(len(watch.update_failure_state(state, [problem])), 1)

    def test_priority_is_capped_and_clamped(self):
        self.assertEqual(watch.watch_priority({"priority": 1}), 1)
        self.assertEqual(watch.watch_priority({"priority": 99}), 5)
        title, body, url, priority = watch.format_alert(
            {
                "name": "test",
                "priority": 2,
                "city": "Chennai",
                "cinema_id": "1",
                "cinema_slug": "test",
            },
            [self.event],
        )
        self.assertEqual(priority, 2)


if __name__ == "__main__":
    unittest.main()
