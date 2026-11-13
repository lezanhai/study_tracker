# tracking_tab.py

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from base_tab import BaseTab
from study_timer import StudyTimer
from theme import WHITE, BLUE, MUTED
from utils import format_duration, setup_table


class TrackingTab(BaseTab):

    def __init__(self, parent, db, root, on_session_change):
        super().__init__(parent, db)

        self.root = root
        self.on_session_change = on_session_change

        self.timer = StudyTimer()
        self.timer_job = None

        self.active_subject_id = None
        self.active_note = ""

        self.subject_map = {}

        self.build_ui()
        self.refresh_subjects()
        self.load_sessions()

    # =========================================
    # GIAO DIỆN
    # =========================================

    def build_ui(self):

        self.page_title(
            "Theo dõi thời gian học",
            "Tập trung học tập và ghi lại từng buổi học"
        )

        card = self.create_card("Thông tin buổi học")

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x")

        ttk.Label(form, text="Môn học", background=WHITE).grid(
            row=0, column=0, sticky="w"
        )

        self.subject_combo = ttk.Combobox(form, width=30, state="readonly")
        self.subject_combo.grid(row=1, column=0, padx=(0, 20), pady=8)

        ttk.Label(form, text="Nội dung học", background=WHITE).grid(
            row=0, column=1, sticky="w"
        )

        self.note_entry = ttk.Entry(form, width=40)
        self.note_entry.grid(row=1, column=1, pady=8)

        timer_card = self.create_card("Đồng hồ học tập")

        self.timer_label = tk.Label(
            timer_card, text="00:00:00",
            bg=WHITE, fg=BLUE, font=("Segoe UI", 42, "bold")
        )
        self.timer_label.pack(pady=15)

        button_frame = ttk.Frame(timer_card, style="Card.TFrame")
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame, text="Bắt đầu", command=self.start_timer
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(
            button_frame, text="Tạm dừng", command=self.pause_timer,
            state="disabled", style="Secondary.TButton"
        )
        self.pause_button.grid(row=0, column=1, padx=5)

        self.resume_button = ttk.Button(
            button_frame, text="Tiếp tục", command=self.resume_timer,
            state="disabled"
        )
        self.resume_button.grid(row=0, column=2, padx=5)

        self.finish_button = ttk.Button(
            button_frame, text="Kết thúc và lưu", command=self.finish_timer,
            state="disabled", style="Danger.TButton"
        )
        self.finish_button.grid(row=0, column=3, padx=5)

        history_card = self.create_card("Lịch sử học tập")

        self.session_table = ttk.Treeview(
            history_card,
            columns=("id", "subject", "date", "duration", "note"),
            show="headings",
            height=5
        )

        setup_table(
            self.session_table,
            [
                ("id", "Mã", 50, "center"),
                ("subject", "Môn học", 140, "w"),
                ("date", "Ngày học", 110, "center"),
                ("duration", "Thời gian", 140, "center"),
                ("note", "Nội dung", 300, "w")
            ]
        )

        self.session_table.pack(fill="both", expand=True)

        history_buttons = ttk.Frame(history_card, style="Card.TFrame")
        history_buttons.pack(anchor="w", pady=(12, 0))

        ttk.Button(
            history_buttons, text="Sửa buổi học đã chọn",
            style="Secondary.TButton", command=self.edit_selected_session
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            history_buttons, text="Xóa buổi học đã chọn",
            style="Danger.TButton", command=self.delete_selected_session
        ).grid(row=0, column=1, padx=4)

        ttk.Button(
            history_buttons, text="+ Nhập tay buổi học",
            command=self.add_manual_session
        ).grid(row=0, column=2, padx=4)

    # =========================================
    # MÔN HỌC (gọi lại mỗi khi danh sách môn học đổi)
    # =========================================

    def refresh_subjects(self):

        subjects = self.db.get_subjects()

        self.subject_map = {
            subject[1]: subject[0]
            for subject in subjects
        }

        names = list(self.subject_map.keys())

        self.subject_combo["values"] = names

        if self.subject_combo.get() not in names:
            self.subject_combo.set(names[0] if names else "")

    # =========================================
    # ĐỒNG HỒ HỌC THÔNG THƯỜNG
    # =========================================

    def start_timer(self):

        subject_name = self.subject_combo.get()

        if not subject_name:
            messagebox.showwarning(
                "Thông báo", "Vui lòng thêm và chọn môn học trước!"
            )
            return

        try:
            self.timer.start()

            self.active_subject_id = self.subject_map[subject_name]
            self.active_note = self.note_entry.get().strip()

            self.subject_combo.config(state="disabled")
            self.note_entry.config(state="disabled")

            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.resume_button.config(state="disabled")
            self.finish_button.config(state="normal")

            self.refresh_timer_display()

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    def pause_timer(self):

        try:
            self.timer.pause()

            self.pause_button.config(state="disabled")
            self.resume_button.config(state="normal")

            self.refresh_timer_display()

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    def resume_timer(self):

        try:
            self.timer.resume()

            self.pause_button.config(state="normal")
            self.resume_button.config(state="disabled")

            self.refresh_timer_display()

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    def refresh_timer_display(self):

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        total_seconds = int(self.timer.get_elapsed())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        self.timer_label.config(
            text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )

        if self.timer.state == "running":
            self.timer_job = self.root.after(1000, self.refresh_timer_display)

    def finish_timer(self):

        if self.timer.get_elapsed() < 1:
            messagebox.showwarning(
                "Thông báo",
                "Hãy học ít nhất 1 giây trước khi kết thúc!"
            )
            return

        try:
            start_time, end_time, duration = self.timer.get_summary()

            self.db.add_timed_session(
                self.active_subject_id,
                start_time.isoformat(sep=" ", timespec="seconds"),
                end_time.isoformat(sep=" ", timespec="seconds"),
                duration,
                self.active_note
            )

        except (RuntimeError, ValueError, sqlite3.Error) as error:
            messagebox.showerror(
                "Lỗi",
                f"Không lưu được buổi học: {error}\n"
                "Đồng hồ vẫn được giữ nguyên, bạn có thể thử lại."
            )
            return

        messagebox.showinfo("Thành công", "Đã lưu buổi học!")

        self.reset_timer_ui()
        self.load_sessions()
        self.on_session_change()

    def reset_timer_ui(self):

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.timer.reset()

        self.timer_label.config(text="00:00:00")

        self.subject_combo.config(state="readonly")
        self.note_entry.config(state="normal")

        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.resume_button.config(state="disabled")
        self.finish_button.config(state="disabled")

    # =========================================
    # LỊCH SỬ HỌC TẬP
    # =========================================

    def load_sessions(self):

        for item in self.session_table.get_children():
            self.session_table.delete(item)

        sessions = self.db.get_sessions()

        for session in sessions:

            session_id = session[0]
            subject = session[1]
            study_date = session[2]
            duration_seconds = session[3]
            note = session[4]

            self.session_table.insert(
                "",
                "end",
                values=(
                    session_id,
                    subject,
                    study_date,
                    format_duration(duration_seconds),
                    note
                )
            )

    def get_selected_session_id(self):

        selection = self.session_table.selection()

        if not selection:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng chọn một buổi học trong bảng trước!"
            )
            return None

        return int(self.session_table.item(selection[0], "values")[0])

    def edit_selected_session(self):

        session_id = self.get_selected_session_id()

        if session_id is None:
            return

        session = self.db.get_session(session_id)

        if session is None:
            return

        _, subject_id, study_date, duration_seconds, note = session

        dialog = tk.Toplevel(self.root)
        dialog.title("Sửa buổi học")
        dialog.configure(bg=WHITE)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        body = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        body.pack(fill="both", expand=True)

        ttk.Label(
            body, text=f"Ngày học: {study_date}",
            background=WHITE, foreground=MUTED
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(body, text="Môn học", background=WHITE).grid(
            row=1, column=0, sticky="w", pady=6
        )

        subject_box = ttk.Combobox(
            body,
            values=list(self.subject_map.keys()),
            state="readonly",
            width=28
        )

        current_name = next(
            (
                name
                for name, sid in self.subject_map.items()
                if sid == subject_id
            ),
            ""
        )

        subject_box.set(current_name)
        subject_box.grid(row=1, column=1, padx=(12, 0), pady=6)

        ttk.Label(body, text="Thời gian (phút)", background=WHITE).grid(
            row=2, column=0, sticky="w", pady=6
        )

        minutes_entry = ttk.Entry(body, width=30)
        minutes_entry.insert(0, f"{duration_seconds / 60:.1f}")
        minutes_entry.grid(row=2, column=1, padx=(12, 0), pady=6)

        ttk.Label(body, text="Nội dung học", background=WHITE).grid(
            row=3, column=0, sticky="w", pady=6
        )

        note_box = ttk.Entry(body, width=30)
        note_box.insert(0, note or "")
        note_box.grid(row=3, column=1, padx=(12, 0), pady=6)

        def save_changes():

            try:
                minutes = float(minutes_entry.get().replace(",", "."))

            except ValueError:
                messagebox.showwarning(
                    "Thông báo", "Thời gian phải là một số!", parent=dialog
                )
                return

            chosen_name = subject_box.get()

            if chosen_name not in self.subject_map:
                messagebox.showwarning(
                    "Thông báo", "Vui lòng chọn môn học!", parent=dialog
                )
                return

            try:
                self.db.update_session(
                    session_id,
                    self.subject_map[chosen_name],
                    minutes,
                    note_box.get().strip()
                )

            except ValueError as error:
                messagebox.showwarning("Thông báo", str(error), parent=dialog)
                return

            dialog.destroy()

            self.load_sessions()
            self.on_session_change()

        button_row = ttk.Frame(body, style="Card.TFrame")
        button_row.grid(row=4, column=0, columnspan=2, pady=(16, 0))

        ttk.Button(
            button_row, text="Lưu thay đổi", command=save_changes
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_row, text="Hủy", style="Secondary.TButton",
            command=dialog.destroy
        ).grid(row=0, column=1, padx=5)

    def delete_selected_session(self):

        session_id = self.get_selected_session_id()

        if session_id is None:
            return

        confirm = messagebox.askyesno(
            "Xác nhận", "Bạn có chắc chắn muốn xóa buổi học này?"
        )

        if not confirm:
            return

        self.db.delete_session(session_id)

        self.load_sessions()
        self.on_session_change()

        messagebox.showinfo("Thành công", "Đã xóa buổi học!")

    def add_manual_session(self):

        if not self.subject_map:
            messagebox.showwarning(
                "Thông báo", "Vui lòng thêm môn học trước!"
            )
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Nhập tay buổi học")
        dialog.configure(bg=WHITE)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        body = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Môn học", background=WHITE).grid(
            row=0, column=0, sticky="w", pady=6
        )

        names = list(self.subject_map.keys())

        subject_box = ttk.Combobox(
            body, values=names, state="readonly", width=28
        )
        subject_box.set(names[0])
        subject_box.grid(row=0, column=1, padx=(12, 0), pady=6)

        ttk.Label(body, text="Ngày học (dd/mm/yyyy)", background=WHITE).grid(
            row=1, column=0, sticky="w", pady=6
        )

        date_entry = ttk.Entry(body, width=30)
        date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        date_entry.grid(row=1, column=1, padx=(12, 0), pady=6)

        ttk.Label(body, text="Thời gian (phút)", background=WHITE).grid(
            row=2, column=0, sticky="w", pady=6
        )

        minutes_entry = ttk.Entry(body, width=30)
        minutes_entry.grid(row=2, column=1, padx=(12, 0), pady=6)

        ttk.Label(body, text="Nội dung học", background=WHITE).grid(
            row=3, column=0, sticky="w", pady=6
        )

        note_box = ttk.Entry(body, width=30)
        note_box.grid(row=3, column=1, padx=(12, 0), pady=6)

        def save_session():

            try:
                minutes = float(minutes_entry.get().replace(",", "."))

            except ValueError:
                messagebox.showwarning(
                    "Thông báo", "Thời gian phải là một số!", parent=dialog
                )
                return

            if minutes <= 0 or minutes > 1440:
                messagebox.showwarning(
                    "Thông báo",
                    "Thời gian phải lớn hơn 0 và không quá 1440 phút "
                    "(24 giờ)!",
                    parent=dialog
                )
                return

            try:
                study_date = datetime.strptime(
                    date_entry.get().strip(), "%d/%m/%Y"
                ).date()

            except ValueError:
                messagebox.showwarning(
                    "Thông báo",
                    "Ngày không hợp lệ. Hãy nhập dd/mm/yyyy!",
                    parent=dialog
                )
                return

            if study_date > date.today():
                messagebox.showwarning(
                    "Thông báo",
                    "Không thể nhập buổi học ở tương lai!",
                    parent=dialog
                )
                return

            try:
                self.db.add_session(
                    self.subject_map[subject_box.get()],
                    study_date.isoformat(),
                    minutes,
                    note_box.get().strip() or "Nhập tay"
                )

            except ValueError as error:
                messagebox.showwarning("Thông báo", str(error), parent=dialog)
                return

            dialog.destroy()

            self.load_sessions()
            self.on_session_change()

            messagebox.showinfo("Thành công", "Đã thêm buổi học!")

        button_row = ttk.Frame(body, style="Card.TFrame")
        button_row.grid(row=4, column=0, columnspan=2, pady=(16, 0))

        ttk.Button(
            button_row, text="Lưu buổi học", command=save_session
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_row, text="Hủy", style="Secondary.TButton",
            command=dialog.destroy
        ).grid(row=0, column=1, padx=5)

    # =========================================
    # DÙNG KHI ĐÓNG ỨNG DỤNG (gọi từ main.py)
    # =========================================

    def is_active(self):
        return self.timer.state in ("running", "paused")

    def confirm_and_flush_on_exit(self):
        """
        Trả về True nếu được phép đóng ứng dụng, False nếu phải ở lại.
        """

        answer = messagebox.askyesnocancel(
            "Xác nhận",
            "Buổi học đang diễn ra chưa được lưu.\n"
            "Bạn có muốn lưu phần đã học trước khi thoát không?\n\n"
            "Có: lưu rồi thoát | Không: bỏ buổi học và thoát | "
            "Hủy: ở lại"
        )

        if answer is None:
            return False

        if answer and self.timer.get_elapsed() >= 1:

            try:
                start_time, end_time, duration = self.timer.get_summary()

                self.db.add_timed_session(
                    self.active_subject_id,
                    start_time.isoformat(sep=" ", timespec="seconds"),
                    end_time.isoformat(sep=" ", timespec="seconds"),
                    duration,
                    self.active_note
                )

            except (RuntimeError, ValueError, sqlite3.Error) as error:
                messagebox.showerror(
                    "Lỗi",
                    f"Không lưu được buổi học: {error}\n"
                    "Ứng dụng chưa thoát để tránh mất dữ liệu."
                )
                return False

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        return True