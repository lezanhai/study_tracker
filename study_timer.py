# study_timer.py
import time
from datetime import datetime

from stopwatch import Stopwatch, TimerState


class StudyTimer(Stopwatch):
    """Đồng hồ cho một buổi học: thêm thời điểm bắt đầu và kết thúc."""

    def __init__(self, clock=time.monotonic):

        super().__init__(clock)

        self.started_at = None
        self.ended_at = None

    def start(self):

        super().start()
        self.started_at = datetime.now()

    # Lấy kết quả buổi học mà KHÔNG đổi trạng thái đồng hồ
    def get_summary(self):

        if self.state not in (TimerState.RUNNING, TimerState.PAUSED):
            raise RuntimeError("Không có buổi học đang diễn ra!")

        return (
            self.started_at,
            datetime.now(),
            int(round(self.get_elapsed()))
        )

    # Kết thúc buổi học và đóng băng đồng hồ
    def finish(self):

        if self.state not in (TimerState.RUNNING, TimerState.PAUSED):
            raise RuntimeError("Không có buổi học đang diễn ra!")

        elapsed = self.stop()
        self.ended_at = datetime.now()

        return (
            self.started_at,
            self.ended_at,
            int(round(elapsed))
        )

    def reset(self):

        super().reset()

        self.started_at = None
        self.ended_at = None