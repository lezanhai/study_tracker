# goals_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

from ui.base_tab import BaseTab
from ui.theme import WHITE, BLUE, MUTED
from utils.utils import format_duration


class GoalsTab(BaseTab):

    def __init__(self, parent, db):
        super().__init__(parent, db)

        self.build_ui()
        self.load_goal_progress()

    # =========================================
    # GIAO DIỆN MỤC TIÊU
    # =========================================

    def build_ui(self):

        self.page_title(
            "Mục tiêu học tập",
            "Thiết lập mục tiêu và duy trì thói quen học tập"
        )

        card = self.create_card("Thiết lập mục tiêu tuần")

        self.goal_week_label = ttk.Label(
            card,
            text="",
            style="Subtitle.TLabel"
        )
        self.goal_week_label.pack(anchor="w", pady=5)

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(anchor="w", pady=12)

        ttk.Label(
            form,
            text="Mục tiêu (phút/tuần):",
            background=WHITE
        ).grid(row=0, column=0, padx=(0, 10))

        self.goal_entry = ttk.Entry(form, width=18)
        self.goal_entry.grid(row=0, column=1, padx=5)

        ttk.Button(
            form,
            text="Lưu mục tiêu",
            command=self.save_goal
        ).grid(row=0, column=2, padx=10)

        progress_card = self.create_card("Tiến độ học tập tuần này")

        self.goal_percent_label = tk.Label(
            progress_card,
            text="0%",
            bg=WHITE,
            fg=BLUE,
            font=("Segoe UI", 32, "bold")
        )
        self.goal_percent_label.pack(pady=10)

        self.goal_progress = ttk.Progressbar(
            progress_card,
            maximum=100,
            mode="determinate"
        )
        self.goal_progress.pack(fill="x", padx=15, pady=15)

        self.goal_status_label = ttk.Label(
            progress_card,
            text="Bạn chưa đặt mục tiêu cho tuần này.",
            background=WHITE,
            foreground=MUTED,
            font=("Segoe UI", 11)
        )
        self.goal_status_label.pack(pady=10)

    # =========================================
    # LƯU MỤC TIÊU
    # =========================================

    def save_goal(self):

        target_text = self.goal_entry.get().strip()

        if not target_text:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng nhập mục tiêu học tập!"
            )
            return

        try:
            target_minutes = int(target_text)

            if target_minutes <= 0:
                messagebox.showwarning(
                    "Thông báo",
                    "Mục tiêu phải lớn hơn 0!"
                )
                return

            today = date.today()
            week_start = today - timedelta(days=today.weekday())

            self.db.save_weekly_goal(
                week_start.isoformat(),
                target_minutes
            )

            messagebox.showinfo(
                "Thành công",
                "Đã lưu mục tiêu học tập!"
            )

            self.goal_entry.delete(0, tk.END)

            self.load_goal_progress()

        except ValueError:
            messagebox.showerror(
                "Lỗi",
                "Mục tiêu phải là số nguyên!"
            )

    # =========================================
    # TẢI TIẾN ĐỘ MỤC TIÊU
    # =========================================

    def load_goal_progress(self):

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        start_date = week_start.isoformat()
        end_date = today.isoformat()

        target_minutes = self.db.get_weekly_goal(start_date)

        total_seconds = self.db.get_weekly_study_seconds(
            start_date,
            end_date
        )

        week_end = week_start + timedelta(days=6)

        self.goal_week_label.config(
            text=(
                f"Tuần từ {start_date} "
                f"đến {week_end.isoformat()}"
            )
        )

        if target_minutes is None:
            self.goal_progress["value"] = 0
            self.goal_status_label.config(
                text="Bạn chưa đặt mục tiêu cho tuần này."
            )
            self.goal_percent_label.config(text="0%")
            return

        target_seconds = target_minutes * 60
        percent = total_seconds / target_seconds * 100

        self.goal_progress["value"] = min(percent, 100)

        remaining_seconds = max(target_seconds - total_seconds, 0)

        self.goal_status_label.config(
            text=(
                f"Đã học: {format_duration(total_seconds)}"
                f" / Mục tiêu: {format_duration(target_seconds)}"
                f"\nCòn thiếu: {format_duration(remaining_seconds)}"
            )
        )

        self.goal_percent_label.config(
            text=f"{percent:.1f}% hoàn thành"
        )