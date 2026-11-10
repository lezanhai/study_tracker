# pomodoro_tab.py

import time
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from base_tab import BaseTab
from pomodoro_timer import PomodoroTimer
from theme import WHITE, BLUE, TEAL, TEXT, NAVY, MUTED


class PomodoroTab(BaseTab):

    def __init__(self, parent, db, root, on_session_saved):
        super().__init__(parent, db)

        self.root = root
        self.on_session_saved = on_session_saved

        self.pomodoro = PomodoroTimer()
        self.pomodoro_job = None

        self.subject_map = {}

        self.pomodoro_notice = ""
        self.pomodoro_notice_until = 0

        self.build_ui()
        self.refresh_subjects()

    # =========================================
    # GIAO DIỆN
    # =========================================

    def build_ui(self):

        self.page_title(
            "Pomodoro Focus",
            "Tập trung theo phiên, nghỉ ngơi hợp lý và duy trì hiệu suất học tập"
        )

        config_card = self.create_card("Thiết lập phiên học")

        config = ttk.Frame(config_card, style="Card.TFrame")
        config.pack(fill="x")

        ttk.Label(config, text="Môn học", background=WHITE).grid(
            row=0, column=0, sticky="w", padx=5
        )

        self.pomodoro_subject_combo = ttk.Combobox(
            config, width=22, state="readonly"
        )
        self.pomodoro_subject_combo.grid(row=1, column=0, padx=5, pady=8)

        ttk.Label(config, text="Nội dung học", background=WHITE).grid(
            row=0, column=1, sticky="w", padx=5
        )

        self.pomodoro_note_entry = ttk.Entry(config, width=25)
        self.pomodoro_note_entry.grid(row=1, column=1, padx=5, pady=8)

        ttk.Label(config, text="Tập trung (phút)", background=WHITE).grid(
            row=0, column=2, padx=5
        )

        self.focus_spin = ttk.Spinbox(config, from_=1, to=120, width=8)
        self.focus_spin.set("25")
        self.focus_spin.grid(row=1, column=2, padx=5)

        ttk.Label(config, text="Nghỉ ngắn", background=WHITE).grid(
            row=0, column=3, padx=5
        )

        self.short_spin = ttk.Spinbox(config, from_=1, to=60, width=8)
        self.short_spin.set("5")
        self.short_spin.grid(row=1, column=3, padx=5)

        ttk.Label(config, text="Nghỉ dài", background=WHITE).grid(
            row=0, column=4, padx=5
        )

        self.long_spin = ttk.Spinbox(config, from_=1, to=90, width=8)
        self.long_spin.set("15")
        self.long_spin.grid(row=1, column=4, padx=5)

        ttk.Label(
            config, text="Sau bao nhiêu phiên", background=WHITE
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.long_after_spin = ttk.Spinbox(config, from_=2, to=10, width=8)
        self.long_after_spin.set("4")
        self.long_after_spin.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        timer_card = self.create_card("Đồng hồ tập trung")

        self.pomodoro_phase_label = tk.Label(
            timer_card, text="SẴN SÀNG TẬP TRUNG",
            bg=WHITE, fg=BLUE, font=("Segoe UI", 13, "bold")
        )
        self.pomodoro_phase_label.pack(pady=(5, 10))

        self.pomodoro_time_label = tk.Label(
            timer_card, text="25:00",
            bg=WHITE, fg=BLUE, font=("Segoe UI", 52, "bold")
        )
        self.pomodoro_time_label.pack(pady=5)

        self.pomodoro_progress = ttk.Progressbar(
            timer_card, maximum=100, mode="determinate"
        )
        self.pomodoro_progress.pack(fill="x", padx=45, pady=15)

        self.pomodoro_status_label = ttk.Label(
            timer_card, text="Chọn môn học và nhấn Bắt đầu.",
            background=WHITE, foreground=MUTED
        )
        self.pomodoro_status_label.pack(pady=5)

        self.pomodoro_cycle_label = tk.Label(
            timer_card, text="Số phiên tập trung hoàn thành: 0",
            bg=WHITE, fg=NAVY, font=("Segoe UI", 11, "bold")
        )
        self.pomodoro_cycle_label.pack(pady=10)

        button_frame = ttk.Frame(timer_card, style="Card.TFrame")
        button_frame.pack(pady=15)

        self.pomodoro_start_button = ttk.Button(
            button_frame, text="▶ Bắt đầu", command=self.start_pomodoro
        )
        self.pomodoro_start_button.grid(row=0, column=0, padx=5)

        self.pomodoro_pause_button = ttk.Button(
            button_frame, text="Ⅱ Tạm dừng", command=self.pause_pomodoro,
            state="disabled", style="Secondary.TButton"
        )
        self.pomodoro_pause_button.grid(row=0, column=1, padx=5)

        self.pomodoro_resume_button = ttk.Button(
            button_frame, text="▶ Tiếp tục", command=self.resume_pomodoro,
            state="disabled"
        )
        self.pomodoro_resume_button.grid(row=0, column=2, padx=5)

        self.pomodoro_stop_button = ttk.Button(
            button_frame, text="■ Kết thúc", command=self.stop_pomodoro,
            state="disabled", style="Danger.TButton"
        )
        self.pomodoro_stop_button.grid(row=0, column=3, padx=5)

        guide = self.create_card("Quy trình Pomodoro")

        tk.Label(
            guide,
            text=(
                "1. Chọn môn học và nội dung cần học.\n"
                "2. Tập trung trong thời gian đã thiết lập.\n"
                "3. Nghỉ ngắn sau mỗi phiên học.\n"
                "4. Sau số phiên quy định, ứng dụng chuyển sang nghỉ dài.\n"
                "5. Chỉ thời gian tập trung được lưu vào lịch sử học tập."
            ),
            justify="left", bg=WHITE, fg=TEXT,
            font=("Segoe UI", 10), anchor="w"
        ).pack(fill="x")

    # =========================================
    # MÔN HỌC (được gọi lại mỗi khi danh sách môn học đổi)
    # =========================================

    def refresh_subjects(self):

        subjects = self.db.get_subjects()

        self.subject_map = {
            subject[1]: subject[0]
            for subject in subjects
        }

        names = list(self.subject_map.keys())

        self.pomodoro_subject_combo["values"] = names

        if self.pomodoro_subject_combo.get() not in names:
            self.pomodoro_subject_combo.set(names[0] if names else "")

    def set_pomodoro_controls(self, enabled):

        state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"

        self.pomodoro_subject_combo.config(state=combo_state)
        self.pomodoro_note_entry.config(state=state)

        self.focus_spin.config(state=state)
        self.short_spin.config(state=state)
        self.long_spin.config(state=state)
        self.long_after_spin.config(state=state)

    # =========================================
    # BẮT ĐẦU / TẠM DỪNG / TIẾP TỤC
    # =========================================

    def start_pomodoro(self):

        subject_name = self.pomodoro_subject_combo.get()

        if not subject_name:
            messagebox.showwarning(
                "Thông báo", "Vui lòng thêm và chọn môn học trước!"
            )
            return

        try:
            focus_minutes = int(self.focus_spin.get())
            short_minutes = int(self.short_spin.get())
            long_minutes = int(self.long_spin.get())
            long_after = int(self.long_after_spin.get())

            self.pomodoro.start(
                subject_id=self.subject_map[subject_name],
                note=self.pomodoro_note_entry.get().strip(),
                focus_minutes=focus_minutes,
                short_break_minutes=short_minutes,
                long_break_minutes=long_minutes,
                long_after=long_after
            )

            self.set_pomodoro_controls(False)

            self.pomodoro_start_button.config(state="disabled")
            self.pomodoro_pause_button.config(state="normal")
            self.pomodoro_resume_button.config(state="disabled")
            self.pomodoro_stop_button.config(state="normal")

            self.refresh_pomodoro_display()

        except ValueError:
            messagebox.showerror(
                "Lỗi", "Vui lòng nhập các thiết lập thời gian hợp lệ!"
            )

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    def pause_pomodoro(self):

        try:
            self.pomodoro.pause()

            self.pomodoro_pause_button.config(state="disabled")
            self.pomodoro_resume_button.config(state="normal")

            self.refresh_pomodoro_display()

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    def resume_pomodoro(self):

        try:
            self.pomodoro.resume()

            self.pomodoro_pause_button.config(state="normal")
            self.pomodoro_resume_button.config(state="disabled")

            self.refresh_pomodoro_display()

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    # =========================================
    # HIỂN THỊ / TICK
    # =========================================

    def show_pomodoro_notice(self, text, seconds=8):

        self.pomodoro_notice = text
        self.pomodoro_notice_until = time.monotonic() + seconds

    def refresh_pomodoro_display(self):

        if self.pomodoro_job is not None:
            self.root.after_cancel(self.pomodoro_job)
            self.pomodoro_job = None

        remaining = int(self.pomodoro.get_remaining() + 0.999)

        minutes = remaining // 60
        seconds = remaining % 60

        self.pomodoro_time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.pomodoro_progress["value"] = self.pomodoro.get_progress()

        self.pomodoro_cycle_label.config(
            text=f"Số phiên tập trung hoàn thành: {self.pomodoro.completed_cycles}"
        )

        if self.pomodoro.phase == "focus":

            self.pomodoro_phase_label.config(text="THỜI GIAN TẬP TRUNG", fg=BLUE)
            self.pomodoro_time_label.config(fg=BLUE)

            status = (
                "Đang tập trung học. Hãy cố gắng hoàn thành phiên này."
                if self.pomodoro.state == "running"
                else "Đang tạm dừng phiên học."
            )

        else:

            phase_text = "NGHỈ DÀI" if self.pomodoro.break_kind == "long" else "NGHỈ NGẮN"

            self.pomodoro_phase_label.config(text=phase_text, fg=TEAL)
            self.pomodoro_time_label.config(fg=TEAL)

            status = (
                "Hãy thư giãn và nghỉ ngơi."
                if self.pomodoro.state == "running"
                else "Thời gian nghỉ đang tạm dừng."
            )

        if self.pomodoro.state == "idle":
            status = "Chọn môn học và nhấn Bắt đầu."

        if (
            self.pomodoro.state != "idle"
            and time.monotonic() < self.pomodoro_notice_until
        ):
            status = self.pomodoro_notice

        self.pomodoro_status_label.config(text=status)

        if self.pomodoro.state == "running":
            self.pomodoro_job = self.root.after(250, self.pomodoro_tick)

    def pomodoro_tick(self):

        self.pomodoro_job = None

        event = self.pomodoro.tick()

        if event is not None:

            if event["type"] == "focus_complete":

                saved = self.save_pomodoro_session(event)

                self.root.bell()

                if saved:
                    self.show_pomodoro_notice(
                        "Hoàn thành phiên tập trung! Đến giờ nghỉ."
                    )
                else:
                    self.show_pomodoro_notice(
                        "Phiên tập trung đã xong nhưng CHƯA lưu được!"
                    )

            elif event["type"] == "break_complete":

                self.root.bell()
                self.show_pomodoro_notice(
                    "Đã hết giờ nghỉ. Bắt đầu phiên tập trung mới."
                )

        self.refresh_pomodoro_display()

    # =========================================
    # LƯU PHIÊN / KẾT THÚC
    # =========================================

    def save_pomodoro_session(self, event):

        try:
            self.db.add_timed_session(
                event["subject_id"],
                event["start_time"].isoformat(sep=" ", timespec="seconds"),
                event["end_time"].isoformat(sep=" ", timespec="seconds"),
                event["duration_seconds"],
                event["note"] or "Phiên học Pomodoro"
            )

        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Lỗi", f"Không lưu được phiên học: {error}")
            return False

        self.on_session_saved()

        return True

    def stop_pomodoro(self):

        confirm = messagebox.askyesno(
            "Xác nhận", "Bạn muốn kết thúc chế độ Pomodoro?"
        )

        if not confirm:
            return

        if self.pomodoro_job is not None:
            self.root.after_cancel(self.pomodoro_job)
            self.pomodoro_job = None

        event = self.pomodoro.peek_focus_event()

        if event is not None and not self.save_pomodoro_session(event):
            self.refresh_pomodoro_display()
            return

        self.pomodoro.stop()
        self.pomodoro_notice_until = 0

        self.set_pomodoro_controls(True)

        self.pomodoro_start_button.config(state="normal")
        self.pomodoro_pause_button.config(state="disabled")
        self.pomodoro_resume_button.config(state="disabled")
        self.pomodoro_stop_button.config(state="disabled")

        self.refresh_pomodoro_display()

        self.pomodoro_status_label.config(
            text="Pomodoro đã kết thúc. Bạn có thể bắt đầu phiên mới."
        )

        messagebox.showinfo("Thông báo", "Đã kết thúc chế độ Pomodoro.")

    # =========================================
    # DÙNG KHI ĐÓNG ỨNG DỤNG (gọi từ main.py)
    # =========================================

    def is_active(self):
        return self.pomodoro.state in ("running", "paused")

    def confirm_and_flush_on_exit(self):
        """
        Trả về True nếu được phép đóng ứng dụng, False nếu phải ở lại.
        """

        event = self.pomodoro.peek_focus_event()

        if event is not None:

            answer = messagebox.askyesnocancel(
                "Xác nhận",
                "Pomodoro đang ở phiên tập trung.\n"
                "Bạn có muốn lưu phần đã học trước khi thoát không?\n\n"
                "Có: lưu rồi thoát | Không: bỏ phiên và thoát | "
                "Hủy: ở lại"
            )

            if answer is None:
                return False

            if answer and not self.save_pomodoro_session(event):
                return False

        else:

            if not messagebox.askyesno(
                "Xác nhận",
                "Pomodoro đang trong giờ nghỉ. Bạn có muốn thoát không?"
            ):
                return False

        if self.pomodoro_job is not None:
            self.root.after_cancel(self.pomodoro_job)
            self.pomodoro_job = None

        return True