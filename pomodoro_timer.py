# pomodoro_timer.py
import time
from datetime import datetime
from enum import Enum

from stopwatch import Stopwatch, TimerState


class Phase(str, Enum):
    FOCUS = "focus"
    BREAK = "break"


class BreakKind(str, Enum):
    SHORT = "short"
    LONG = "long"


class PomodoroTimer:
    """Pomodoro: xen kẽ giai đoạn tập trung và nghỉ, dùng một Stopwatch."""

    def __init__(self, clock=time.monotonic):

        # Quan hệ "chứa" (composition): mỗi giai đoạn là một lượt bấm giờ
        self._watch = Stopwatch(clock)

        self.phase = Phase.FOCUS
        self.break_kind = None

        self.focus_minutes = 25
        self.short_break_minutes = 5
        self.long_break_minutes = 15
        self.long_after = 4

        self.completed_cycles = 0

        self.subject_id = None
        self.note = ""

        self.phase_duration = self.focus_minutes * 60
        self.focus_started_at = None

    @property
    def state(self):
        return self._watch.state

    # =================================
    # BẮT ĐẦU POMODORO
    # =================================

    def start(
        self,
        subject_id,
        note,
        focus_minutes=25,
        short_break_minutes=5,
        long_break_minutes=15,
        long_after=4
    ):

        if self.state != TimerState.IDLE:
            raise RuntimeError("Pomodoro đang hoạt động!")

        values = [
            focus_minutes,
            short_break_minutes,
            long_break_minutes,
            long_after
        ]

        if any(value <= 0 for value in values):
            raise ValueError("Các thiết lập phải lớn hơn 0!")

        self.focus_minutes = focus_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.long_after = long_after

        self.subject_id = subject_id
        self.note = note

        self.completed_cycles = 0

        self.phase = Phase.FOCUS
        self.break_kind = None

        self._start_phase()

    # =================================
    # KHỞI TẠO MỘT GIAI ĐOẠN
    # =================================

    def _start_phase(self):

        if self.phase == Phase.FOCUS:

            self.phase_duration = self.focus_minutes * 60
            self.focus_started_at = datetime.now()
            self.break_kind = None

        elif self.break_kind == BreakKind.LONG:

            self.phase_duration = self.long_break_minutes * 60

        else:

            self.phase_duration = self.short_break_minutes * 60

        self._watch.reset()
        self._watch.start()

    # =================================
    # THỜI GIAN VÀ TIẾN ĐỘ
    # =================================

    def get_elapsed(self):
        return self._watch.get_elapsed()

    def get_remaining(self):
        return max(0, self.phase_duration - self.get_elapsed())

    def get_progress(self):

        if self.phase_duration <= 0:
            return 0

        progress = (self.get_elapsed() / self.phase_duration) * 100

        return min(100, max(0, progress))

    # =================================
    # TẠM DỪNG VÀ TIẾP TỤC
    # =================================

    def pause(self):

        if self.state != TimerState.RUNNING:
            raise RuntimeError("Pomodoro chưa chạy!")

        self._watch.pause()

    def resume(self):

        if self.state != TimerState.PAUSED:
            raise RuntimeError("Pomodoro chưa được tạm dừng!")

        self._watch.resume()

    # =================================
    # TẠO DỮ LIỆU PHIÊN HỌC
    # =================================

    def _create_focus_event(self):

        duration_seconds = int(round(self.get_elapsed()))

        if duration_seconds < 1:
            return None

        return {
            "subject_id": self.subject_id,
            "start_time": self.focus_started_at,
            "end_time": datetime.now(),
            "duration_seconds": duration_seconds,
            "note": self.note,
            "type": "focus_complete"
        }

    # Tạo dữ liệu phiên tập trung hiện tại mà KHÔNG đổi trạng thái
    def peek_focus_event(self):

        if self.phase != Phase.FOCUS:
            return None

        if self.state not in (TimerState.RUNNING, TimerState.PAUSED):
            return None

        return self._create_focus_event()

    # =================================
    # KIỂM TRA KHI HẾT GIỜ
    # =================================

    def tick(self):

        if self.state != TimerState.RUNNING:
            return None

        if self.get_remaining() > 0:
            return None

        # Kết thúc phiên tập trung
        if self.phase == Phase.FOCUS:

            event = self._create_focus_event()

            self.completed_cycles += 1

            # Sau mỗi số phiên quy định sẽ nghỉ dài
            if self.completed_cycles % self.long_after == 0:
                self.break_kind = BreakKind.LONG
            else:
                self.break_kind = BreakKind.SHORT

            self.phase = Phase.BREAK
            self._start_phase()

            return event

        # Kết thúc thời gian nghỉ
        self.phase = Phase.FOCUS
        self.break_kind = None
        self._start_phase()

        return {"type": "break_complete"}

    # =================================
    # KẾT THÚC POMODORO
    # =================================

    def stop(self):

        event = self.peek_focus_event()

        self._watch.reset()

        self.phase = Phase.FOCUS
        self.break_kind = None

        self.phase_duration = self.focus_minutes * 60
        self.focus_started_at = None

        return event