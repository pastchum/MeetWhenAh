import unittest
from datetime import datetime
from scheduler import Scheduler

### NOT UPDATED FOR NEW TIMING WEIGHTS

class SchedulerTest(unittest.TestCase):
    def test_create_availability_map(self):
        scheduler = Scheduler()
        availability_blocks = [
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T10:30:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T11:00:00+08:00", "end_time": "2025-01-01T11:30:00+08:00", "event_id": "1", "user_uuid": "2"},
        ]
        availability_map = scheduler._create_availability_map(availability_blocks)
        self.assertEqual(len(availability_map), 2)
        self.assertIsInstance(availability_map, dict)
        self.assertEqual(availability_map, {datetime.strptime("2025-01-01T10:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["1"], datetime.strptime("2025-01-01T11:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["2"]})

        avail_blocks_test_2 = [
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T10:30:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T11:00:00+08:00", "end_time": "2025-01-01T11:30:00+08:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "3"},
            {"start_time": "2025-01-01T11:30:00+08:00", "end_time": "2025-01-01T12:00:00+08:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01T12:00:00+08:00", "end_time": "2025-01-01T12:30:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T12:30:00+08:00", "end_time": "2025-01-01T13:00:00+08:00", "event_id": "1", "user_uuid": "3"},
            {"start_time": "2025-01-01T13:00:00+08:00", "end_time": "2025-01-01T13:30:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T12:30:00+08:00", "end_time": "2025-01-01T13:00:00+08:00", "event_id": "1", "user_uuid": "2"},
        ]
        availability_map_test_2 = scheduler._create_availability_map(avail_blocks_test_2)
        print({
                             datetime.strptime("2025-01-01T10:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z").isoformat(): ["1"],
                             datetime.strptime("2025-01-01T10:30:00+08:00", "%Y-%m-%dT%H:%M:%S%z").isoformat(): ["1", "3"],
                             datetime.strptime("2025-01-01T11:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z").isoformat(): ["2"],
                             datetime.strptime("2025-01-01T11:30:00+08:00", "%Y-%m-%dT%H:%M:%S%z").isoformat(): ["2"],
                             datetime.strptime("2025-01-01T12:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z").isoformat(): ["1"],
                             datetime.strptime("2025-01-01T12:30:00+08:00", "%Y-%m-%dT%H:%M:%S%z").isoformat(): ["2", "3"],
                             datetime.strptime("2025-01-01T13:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z").isoformat(): ["1"],
                         })
        self.assertEqual(len(availability_map_test_2), 7)
        self.assertIsInstance(availability_map_test_2, dict)
        self.assertEqual(availability_map_test_2, 
                         {
                             datetime.strptime("2025-01-01T10:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["1"],
                             datetime.strptime("2025-01-01T10:30:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["1", "3"],
                             datetime.strptime("2025-01-01T11:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["2"],
                             datetime.strptime("2025-01-01T11:30:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["2"],
                             datetime.strptime("2025-01-01T12:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["1"],
                             datetime.strptime("2025-01-01T12:30:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["2", "3"],
                             datetime.strptime("2025-01-01T13:00:00+08:00", "%Y-%m-%dT%H:%M:%S%z"): ["1"],
                         })

    def test_create_event_blocks(self):
        scheduler = Scheduler()
        availability_blocks = [
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T10:30:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T10:30:00+08:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "2"},
        ]
        availability_map = scheduler._create_availability_map(availability_blocks)
        event_blocks = scheduler._create_event_blocks(availability_map)
        self.assertEqual(event_blocks, [{"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1","2"], "duration": 60, "participant_count": 2}])

        avail_blocks_test_2 = [
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01T11:00:00+08:00", "end_time": "2025-01-01T11:30:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T11:00:00+08:00", "end_time": "2025-01-01T11:30:00+08:00", "event_id": "1", "user_uuid": "2"},
        ]
        availability_map_test_2 = scheduler._create_availability_map(avail_blocks_test_2)
        event_blocks_test_2 = scheduler._create_event_blocks(availability_map_test_2)

        self.assertEqual(event_blocks_test_2, [{"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:30:00+08:00", "participants": ["1","2"], "duration": 60, "participant_count": 2}])

    def test_is_within_sleep_hours(self):
        scheduler = Scheduler()
        event_block = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"]}
        self.assertTrue(scheduler._is_within_sleep_hours(event_block))

    def test_is_within_sensitivity_threshold(self):
        scheduler = Scheduler()
        event_block = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"]}
        self.assertTrue(scheduler._is_within_sensitivity_threshold(event_block))

    def test_is_within_minimum_block_size(self):
        scheduler = Scheduler()
        event_block = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"]}
        self.assertTrue(scheduler._is_within_minimum_block_size(event_block))

    def test_is_within_minimum_participants(self):
        scheduler = Scheduler()
        event_block = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"]}
        self.assertTrue(scheduler._is_within_minimum_participants(event_block))

    def test_is_valid_event_block(self):
        scheduler = Scheduler()
        event_block = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"]}
        self.assertTrue(scheduler._is_valid_event_block(event_block))

    def test_score_event_block(self):
        scheduler = Scheduler()
        event_block = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"]}
        self.assertGreater(scheduler._score_event_block(event_block), 0)
        event_block_2 = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2", "3"]}
        self.assertGreater(scheduler._score_event_block(event_block_2), scheduler._score_event_block(event_block))
        event_block_3 = {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:30:00+08:00", "participants": ["1", "2", "3"]}
        self.assertGreater(scheduler._score_event_block(event_block_3), scheduler._score_event_block(event_block_2))


    def test_get_best_event_block(self):
        scheduler = Scheduler()
        event_blocks = [
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"], "duration": 60, "participant_count": 2},
            {"start_time": "2025-01-01T11:00:00+08:00", "end_time": "2025-01-01T12:00:00+08:00", "participants": ["1", "2"], "duration": 60, "participant_count": 2},
        ]
        self.assertEqual(scheduler._get_best_event_block(event_blocks), event_blocks)
        event_blocks_2 = [
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1", "2"], "duration": 60, "participant_count": 2},
            {"start_time": "2025-01-01T11:00:00+08:00", "end_time": "2025-01-01T12:00:00+08:00", "participants": ["1", "2"], "duration": 60, "participant_count": 2},
            {"start_time": "2025-01-01T12:30:00+08:00", "end_time": "2025-01-01T14:00:00+08:00", "participants": ["1", "2"], "duration": 90, "participant_count": 2},
        ]
        self.assertEqual(scheduler._get_best_event_block(event_blocks_2), 
                         [{"start_time": "2025-01-01T12:30:00+08:00", "end_time": "2025-01-01T14:00:00+08:00", "participants": ["1", "2"], "duration": 90, "participant_count": 2}])
        event_blocks_3 = []
        self.assertEqual(scheduler._get_best_event_block(event_blocks_3), [])


    def test_process_availability_blocks(self):
        scheduler = Scheduler()
        availability_blocks = [
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T10:30:00+08:00", "event_id": "1", "user_uuid": "1"},
        ]
        self.assertEqual(scheduler._process_availability_blocks(availability_blocks), [])

        avail_blocks_test_2 = [
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T10:30:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T10:30:00+08:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01T10:30:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "event_id": "1", "user_uuid": "2"},
        ]
        self.assertEqual(scheduler._process_availability_blocks(avail_blocks_test_2), 
                         [{"start_time": "2025-01-01T10:00:00+08:00", "end_time": "2025-01-01T11:00:00+08:00", "participants": ["1","2"], "duration": 60, "participant_count": 2}])

if __name__ == "__main__":
    unittest.main()