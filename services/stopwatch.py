# stopwatch.py
import time
from enum import Enum


class TimerState(str, Enum):
    """Trạng thái đồng hồ. Kế thừa str nên so sánh được với chuỗi."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"

    def __str__(self):
        return self.value


class Stopwatch:
    """
    Đồng hồ bấm giờ có tạm dừng và tiếp tục.

    clock: hàm trả về thời gian hiện tại (giây). Mặc định là
    time.monotonic, khi kiểm thử có thể truyền đồng hồ giả.
    """

    def __init__(self, clock=time.monotonic):

        self._clock = clock
        self.state = TimerState.IDLE

        # Tổng thời gian đã chạy trước lượt hiện tại
        self._elapsed_before = 0.0

        # Mốc bắt đầu của lượt chạy hiện tại
        self._segment_started = None

    def start(self):

        if self.state != TimerState.IDLE:
            raise RuntimeError("Bộ đếm đang hoạt động!")

        self._elapsed_before = 0.0
        self._segment_started = self._clock()
        self.state = TimerState.RUNNING

    def pause(self):

        if self.state != TimerState.RUNNING:
            raise RuntimeError("Bộ đếm chưa chạy!")

        self._elapsed_before += self._clock() - self._segment_started
        self._segment_started = None
        self.state = TimerState.PAUSED

    def resume(self):

        if self.state != TimerState.PAUSED:
            raise RuntimeError("Bộ đếm chưa được tạm dừng!")

        self._segment_started = self._clock()
        self.state = TimerState.RUNNING

    def get_elapsed(self):

        if self.state == TimerState.RUNNING:
            return (
                self._elapsed_before
                + self._clock() - self._segment_started
            )

        return self._elapsed_before

    def stop(self):
        """Dừng hẳn, đóng băng thời gian và trả về tổng số giây."""

        if self.state not in (TimerState.RUNNING, TimerState.PAUSED):
            raise RuntimeError("Bộ đếm chưa chạy!")

        elapsed = self.get_elapsed()

        self._elapsed_before = elapsed
        self._segment_started = None
        self.state = TimerState.FINISHED

        return elapsed

    def reset(self):

        self.state = TimerState.IDLE
        self._elapsed_before = 0.0
        self._segment_started = None