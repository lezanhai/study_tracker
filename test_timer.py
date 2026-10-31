# test_timers.py
import unittest

from stopwatch import Stopwatch, TimerState
from study_timer import StudyTimer
from pomodoro_timer import PomodoroTimer, Phase, BreakKind


class FakeClock:
    """Đồng hồ giả: thời gian chỉ trôi khi ta gọi advance()."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class StopwatchTests(unittest.TestCase):

    def setUp(self):
        self.clock = FakeClock()
        self.watch = Stopwatch(self.clock)

    def test_counts_time_while_running(self):
        self.watch.start()
        self.clock.advance(10)
        self.assertEqual(self.watch.get_elapsed(), 10)

    def test_pause_stops_counting_and_resume_continues(self):
        self.watch.start()
        self.clock.advance(5)
        self.watch.pause()
        self.clock.advance(100)
        self.assertEqual(self.watch.get_elapsed(), 5)

        self.watch.resume()
        self.clock.advance(3)
        self.assertEqual(self.watch.get_elapsed(), 8)

    def test_invalid_transitions_raise_error(self):
        with self.assertRaises(RuntimeError):
            self.watch.pause()

        self.watch.start()

        with self.assertRaises(RuntimeError):
            self.watch.start()

        with self.assertRaises(RuntimeError):
            self.watch.resume()

    def test_stop_freezes_elapsed_time(self):
        self.watch.start()
        self.clock.advance(4)

        self.assertEqual(self.watch.stop(), 4)
        self.assertEqual(self.watch.state, TimerState.FINISHED)

        self.clock.advance(50)
        self.assertEqual(self.watch.get_elapsed(), 4)

    def test_reset_returns_to_idle(self):
        self.watch.start()
        self.clock.advance(7)
        self.watch.reset()

        self.assertEqual(self.watch.state, TimerState.IDLE)
        self.assertEqual(self.watch.get_elapsed(), 0)

    def test_state_compares_with_plain_string(self):
        # main.py vẫn so sánh trạng thái bằng chuỗi
        self.watch.start()
        self.assertTrue(self.watch.state == "running")
        self.assertTrue(self.watch.state in ("running", "paused"))


class StudyTimerTests(unittest.TestCase):

    def setUp(self):
        self.clock = FakeClock()
        self.timer = StudyTimer(self.clock)

    def test_finish_returns_rounded_duration(self):
        self.timer.start()
        self.clock.advance(90.4)

        started, ended, duration = self.timer.finish()

        self.assertEqual(duration, 90)
        self.assertIsNotNone(started)
        self.assertIsNotNone(ended)
        self.assertEqual(self.timer.state, TimerState.FINISHED)

    def test_get_summary_does_not_change_state(self):
        self.timer.start()
        self.clock.advance(30)

        _, _, duration = self.timer.get_summary()

        self.assertEqual(duration, 30)
        self.assertEqual(self.timer.state, TimerState.RUNNING)

    def test_reset_clears_session_times(self):
        self.timer.start()
        self.clock.advance(5)
        self.timer.finish()
        self.timer.reset()

        self.assertEqual(self.timer.state, TimerState.IDLE)
        self.assertIsNone(self.timer.started_at)
        self.assertIsNone(self.timer.ended_at)


class PomodoroTimerTests(unittest.TestCase):

    def setUp(self):
        self.clock = FakeClock()
        self.pomodoro = PomodoroTimer(self.clock)

        # Tập trung 1 phút, nghỉ ngắn 1 phút, nghỉ dài 2 phút, sau 2 phiên
        self.pomodoro.start(
            subject_id=1,
            note="test",
            focus_minutes=1,
            short_break_minutes=1,
            long_break_minutes=2,
            long_after=2
        )

    def test_nothing_happens_before_time_is_up(self):
        self.clock.advance(59)

        self.assertIsNone(self.pomodoro.tick())
        self.assertEqual(self.pomodoro.phase, Phase.FOCUS)

    def test_focus_completes_and_starts_short_break(self):
        self.clock.advance(60)

        event = self.pomodoro.tick()

        self.assertEqual(event["type"], "focus_complete")
        self.assertEqual(event["duration_seconds"], 60)
        self.assertEqual(event["subject_id"], 1)
        self.assertEqual(self.pomodoro.phase, Phase.BREAK)
        self.assertEqual(self.pomodoro.break_kind, BreakKind.SHORT)
        self.assertEqual(self.pomodoro.completed_cycles, 1)

    def test_break_complete_returns_to_focus(self):
        self.clock.advance(60)
        self.pomodoro.tick()

        self.clock.advance(60)
        event = self.pomodoro.tick()

        self.assertEqual(event["type"], "break_complete")
        self.assertEqual(self.pomodoro.phase, Phase.FOCUS)

    def test_long_break_after_configured_cycles(self):
        for _ in range(3):
            self.clock.advance(60)
            self.pomodoro.tick()

        self.assertEqual(self.pomodoro.completed_cycles, 2)
        self.assertEqual(self.pomodoro.phase, Phase.BREAK)
        self.assertEqual(self.pomodoro.break_kind, BreakKind.LONG)
        self.assertEqual(self.pomodoro.phase_duration, 120)

    def test_pause_does_not_consume_time(self):
        self.clock.advance(30)
        self.pomodoro.pause()
        self.clock.advance(1000)

        self.assertIsNone(self.pomodoro.tick())
        self.assertAlmostEqual(self.pomodoro.get_remaining(), 30)

        self.pomodoro.resume()
        self.clock.advance(30)
        event = self.pomodoro.tick()

        self.assertEqual(event["type"], "focus_complete")
        self.assertEqual(event["duration_seconds"], 60)

    def test_stop_during_focus_returns_partial_session(self):
        self.clock.advance(30)

        event = self.pomodoro.stop()

        self.assertEqual(event["duration_seconds"], 30)
        self.assertEqual(self.pomodoro.state, TimerState.IDLE)

    def test_stop_during_break_returns_nothing(self):
        self.clock.advance(60)
        self.pomodoro.tick()
        self.clock.advance(10)

        self.assertIsNone(self.pomodoro.stop())
        self.assertEqual(self.pomodoro.state, TimerState.IDLE)

    def test_cannot_start_twice(self):
        with self.assertRaises(RuntimeError):
            self.pomodoro.start(subject_id=1, note="")

    def test_invalid_settings_rejected(self):
        self.pomodoro.stop()

        with self.assertRaises(ValueError):
            self.pomodoro.start(subject_id=1, note="", focus_minutes=0)


if __name__ == "__main__":
    unittest.main()