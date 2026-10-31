# main.py
import tkinter as tk
import sqlite3
import time
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta, datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from task_manager import TaskManagerView
from database import DatabaseManager
from study_timer import StudyTimer
from pomodoro_timer import PomodoroTimer
from exporter import export_report


# =========================================
# CẤU HÌNH MÀU SẮC
# =========================================

BG = "#F1F5F9"
WHITE = "#FFFFFF"
NAVY = "#172554"
BLUE = "#2563EB"
BLUE_HOVER = "#1D4ED8"
TEAL = "#0F766E"
TEXT = "#1E293B"
MUTED = "#64748B"
BORDER = "#E2E8F0"
RED = "#DC2626"

# Bảng màu cho biểu đồ
CHART_COLORS = [
    "#2563EB", "#0F766E", "#F59E0B", "#DC2626",
    "#7C3AED", "#0891B2", "#65A30D", "#DB2777"
]

class StudyTrackerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Study Tracker")
        self.root.geometry("1150x800")
        self.root.minsize(950, 680)
        self.root.configure(bg=BG)

        self.db = DatabaseManager()

        # Đồng hồ học thông thường
        self.timer = StudyTimer()

        # Đồng hồ Pomodoro
        self.pomodoro = PomodoroTimer()

        self.timer_job = None
        self.pomodoro_job = None

        self.active_subject_id = None
        self.active_note = ""
        self.selected_subject_id = None
        self.pomodoro_notice = ""
        self.pomodoro_notice_until = 0

        self.subject_map = {}

        self.setup_style()
        self.build_header()
        self.build_notebook()

        self.build_subject_tab()
        self.build_session_tab()
        self.build_pomodoro_tab()
        self.build_statistics_tab()
        self.build_goal_tab()

        # Khởi tạo giao diện quản lý công việc
        self.task_view = TaskManagerView(
            self.task_frame,
            self.db
        )

        self.load_subjects()
        self.load_sessions()
        self.load_statistics()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

    # =========================================
    # STYLE
    # =========================================

    def setup_style(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", font=("Segoe UI", 10))

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=WHITE)

        style.configure(
            "TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Title.TLabel",
            background=BG,
            foreground=NAVY,
            font=("Segoe UI", 20, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=BG,
            foreground=MUTED
        )

        style.configure(
            "CardTitle.TLabel",
            background=WHITE,
            foreground=NAVY,
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Value.TLabel",
            background=WHITE,
            foreground=BLUE,
            font=("Segoe UI", 19, "bold")
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            background=BLUE,
            foreground=WHITE,
            borderwidth=0
        )

        style.map(
            "TButton",
            background=[
                ("active", BLUE_HOVER),
                ("disabled", "#CBD5E1")
            ],
            foreground=[
                ("disabled", "#64748B")
            ]
        )

        style.configure(
            "Secondary.TButton",
            background="#E2E8F0",
            foreground=NAVY
        )

        style.configure(
            "Danger.TButton",
            background=RED,
            foreground=WHITE
        )

        style.configure(
            "TNotebook",
            background=BG,
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background="#E2E8F0",
            foreground=MUTED,
            padding=(15, 12),
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", WHITE),
                ("active", "#DBEAFE")
            ],
            foreground=[
                ("selected", BLUE),
                ("active", NAVY)
            ]
        )

        style.configure(
            "Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            foreground=TEXT,
            rowheight=32,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground=NAVY,
            font=("Segoe UI", 10, "bold"),
            padding=10,
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", NAVY)]
        )

        style.configure("TEntry", padding=8, fieldbackground=WHITE)
        style.configure("TCombobox", padding=7, fieldbackground=WHITE)

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#E2E8F0",
            background=TEAL,
            thickness=16
        )

    # =========================================
    # HÀM CĂN CỘT CHO BẢNG (SỬA LỆCH CỘT)
    # =========================================

    def setup_table(self, table, columns):
        """
        columns: danh sách (mã_cột, tiêu_đề, độ_rộng, căn_lề)
        Tiêu đề và dữ liệu dùng CHUNG một kiểu căn lề
        nên luôn thẳng hàng với nhau.
        """

        for column_id, title, width, anchor in columns:

            table.heading(
                column_id,
                text=title,
                anchor=anchor
            )

            table.column(
                column_id,
                width=width,
                minwidth=width,
                anchor=anchor,
                stretch=True
            )

    # =========================================
    # HEADER
    # =========================================

    def build_header(self):

        header = tk.Frame(self.root, bg=NAVY, height=85)
        header.pack(fill="x")
        header.pack_propagate(False)

        left = tk.Frame(header, bg=NAVY)
        left.pack(side="left", padx=28, pady=15)

        tk.Label(
            left,
            text="STUDY TRACKER",
            bg=NAVY,
            fg=WHITE,
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Quản lý và nâng cao hiệu quả học tập",
            bg=NAVY,
            fg="#BFDBFE",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        tk.Label(
            header,
            text=date.today().strftime("%d/%m/%Y"),
            bg=NAVY,
            fg=WHITE,
            font=("Segoe UI", 11, "bold")
        ).pack(side="right", padx=30)

    # =========================================
    # NOTEBOOK CÓ 6 TAB CUỘN ĐƯỢC
    # =========================================

    def build_notebook(self):

        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        # Tạo 6 tab
        self.subject_tab, self.subject_frame, self.subject_canvas = (
            self.create_scrollable_tab()
        )

        self.session_tab, self.session_frame, self.session_canvas = (
            self.create_scrollable_tab()
        )

        self.pomodoro_tab, self.pomodoro_frame, self.pomodoro_canvas = (
            self.create_scrollable_tab()
        )

        self.statistics_tab, self.statistics_frame, self.statistics_canvas = (
            self.create_scrollable_tab()
        )

        self.goal_tab, self.goal_frame, self.goal_canvas = (
            self.create_scrollable_tab()
        )

        self.task_tab, self.task_frame, self.task_canvas = (
            self.create_scrollable_tab()
        )

        # Thêm tab
        self.notebook.add(self.subject_tab, text="  Môn học  ")
        self.notebook.add(self.session_tab, text="  Theo dõi học tập  ")
        self.notebook.add(self.pomodoro_tab, text="  Pomodoro  ")
        self.notebook.add(self.statistics_tab, text="  Thống kê  ")
        self.notebook.add(self.goal_tab, text="  Mục tiêu  ")
        self.notebook.add(self.task_tab, text="  Công việc  ")

        # Danh sách canvas để cuộn bằng chuột
        self.tab_canvases = [
            self.subject_canvas,
            self.session_canvas,
            self.pomodoro_canvas,
            self.statistics_canvas,
            self.goal_canvas,
            self.task_canvas
        ]

        self.root.bind_all("<MouseWheel>", self.on_mousewheel)
        self.root.bind_all("<Button-4>", self.on_mousewheel_linux)
        self.root.bind_all("<Button-5>", self.on_mousewheel_linux)

    # =========================================
    # TẠO MỘT TAB CÓ THANH CUỘN
    # =========================================

    def create_scrollable_tab(self):

        outer_frame = ttk.Frame(self.notebook)

        canvas = tk.Canvas(
            outer_frame,
            bg=BG,
            highlightthickness=0,
            borderwidth=0
        )

        scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",
            command=canvas.yview
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content_frame = ttk.Frame(canvas)

        window_id = canvas.create_window(
            (0, 0),
            window=content_frame,
            anchor="nw"
        )

        # Tự cập nhật vùng cuộn khi nội dung thay đổi
        content_frame.bind(
            "<Configure>",
            lambda event, c=canvas:
            c.configure(scrollregion=c.bbox("all"))
        )

        # Chiều rộng nội dung theo cửa sổ
        canvas.bind(
            "<Configure>",
            lambda event, c=canvas, w=window_id:
            c.itemconfigure(w, width=event.width)
        )

        return outer_frame, content_frame, canvas

    # =========================================
    # CUỘN BẰNG CHUỘT WINDOWS
    # =========================================

    def on_mousewheel(self, event):

        # Lăn chuột trên bảng thì để bảng tự cuộn
        if isinstance(event.widget, ttk.Treeview):
            return

        selected_tab = self.notebook.index(self.notebook.select())
        canvas = self.tab_canvases[selected_tab]

        if abs(event.delta) >= 120:
            units = int(-event.delta / 120)
        else:
            units = -1 if event.delta > 0 else 1

        canvas.yview_scroll(units, "units")

        return "break"

    # =========================================
    # CUỘN TRÊN LINUX
    # =========================================

    def on_mousewheel_linux(self, event):

        # Lăn chuột trên bảng thì để bảng tự cuộn
        if isinstance(event.widget, ttk.Treeview):
            return

        selected_tab = self.notebook.index(self.notebook.select())
        canvas = self.tab_canvases[selected_tab]

        if event.num == 4:
            canvas.yview_scroll(-1, "units")

        elif event.num == 5:
            canvas.yview_scroll(1, "units")

        return "break"

    # =========================================
    # HÀM GIAO DIỆN DÙNG CHUNG
    # =========================================

    def page_title(self, parent, title, subtitle):

        ttk.Label(
            parent,
            text=title,
            style="Title.TLabel"
        ).pack(anchor="w", padx=25, pady=(22, 3))

        ttk.Label(
            parent,
            text=subtitle,
            style="Subtitle.TLabel"
        ).pack(anchor="w", padx=25, pady=(0, 18))

    def create_card(self, parent, title=None):

        card = ttk.Frame(
            parent,
            style="Card.TFrame",
            padding=18
        )

        card.pack(fill="x", padx=25, pady=8)

        if title:
            ttk.Label(
                card,
                text=title,
                style="CardTitle.TLabel"
            ).pack(anchor="w", pady=(0, 12))

        return card

    # =========================================
    # TAB 1: QUẢN LÝ MÔN HỌC
    # =========================================

    def build_subject_tab(self):

        self.page_title(
            self.subject_frame,
            "Quản lý môn học",
            "Thêm, sửa và xóa các môn học của bạn"
        )

        card = self.create_card(
            self.subject_frame,
            "Thông tin môn học"
        )

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x")

        ttk.Label(
            form,
            text="Tên môn học",
            background=WHITE
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.name_entry = ttk.Entry(form, width=30)
        self.name_entry.grid(row=1, column=0, padx=(0, 15), pady=5)

        ttk.Label(
            form,
            text="Mô tả",
            background=WHITE
        ).grid(row=0, column=1, sticky="w", pady=5)

        self.description_entry = ttk.Entry(form, width=35)
        self.description_entry.grid(row=1, column=1, padx=(0, 15), pady=5)

        button_frame = ttk.Frame(card, style="Card.TFrame")
        button_frame.pack(anchor="w", pady=(12, 0))

        ttk.Button(
            button_frame,
            text="+ Thêm môn học",
            command=self.add_subject
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            button_frame,
            text="Cập nhật",
            command=self.update_selected_subject
        ).grid(row=0, column=1, padx=4)

        ttk.Button(
            button_frame,
            text="Xóa môn học",
            style="Danger.TButton",
            command=self.delete_selected_subject
        ).grid(row=0, column=2, padx=4)

        ttk.Button(
            button_frame,
            text="Làm mới",
            style="Secondary.TButton",
            command=self.clear_subject_form
        ).grid(row=0, column=3, padx=4)

        table_card = self.create_card(
            self.subject_frame,
            "Danh sách môn học (chọn một dòng để sửa hoặc xóa)"
        )

        self.subject_table = ttk.Treeview(
            table_card,
            columns=("id", "name", "description"),
            show="headings"
        )

        self.setup_table(
            self.subject_table,
            [
                ("id", "Mã môn", 80, "center"),
                ("name", "Tên môn học", 220, "w"),
                ("description", "Mô tả", 400, "w")
            ]
        )

        self.subject_table.bind(
            "<<TreeviewSelect>>",
            self.select_subject
        )

        self.subject_table.pack(fill="both", expand=True)
    def add_subject(self):

        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng nhập tên môn học!"
            )
            return

        try:
            self.db.add_subject(name, description)

            messagebox.showinfo("Thành công", "Đã thêm môn học!")

            self.clear_subject_form()
            self.load_subjects()

        except ValueError as error:
            messagebox.showerror("Lỗi", str(error))

    def select_subject(self, event=None):

        selection = self.subject_table.selection()

        if not selection:
            return

        values = self.subject_table.item(selection[0], "values")

        self.selected_subject_id = int(values[0])

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, str(values[1]))

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, str(values[2]))

    def clear_subject_form(self):

        self.selected_subject_id = None

        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

        for item in self.subject_table.selection():
            self.subject_table.selection_remove(item)

    def update_selected_subject(self):

        if self.selected_subject_id is None:
            messagebox.showwarning(
                "Thông báo",
                "Hãy chọn môn học cần cập nhật trong bảng!"
            )
            return

        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Thông báo",
                "Tên môn học không được để trống!"
            )
            return

        try:
            self.db.update_subject(
                self.selected_subject_id,
                name,
                description
            )

        except ValueError as error:
            messagebox.showerror("Lỗi", str(error))
            return

        messagebox.showinfo("Thành công", "Đã cập nhật môn học!")

        self.clear_subject_form()

        # Tên môn đổi thì lịch sử, thống kê, công việc đều phải làm mới
        self.load_subjects()
        self.load_sessions()
        self.load_statistics()
        self.task_view.load_tasks()

    def delete_selected_subject(self):

        if self.selected_subject_id is None:
            messagebox.showwarning(
                "Thông báo",
                "Hãy chọn môn học cần xóa trong bảng!"
            )
            return

        if (
            self.timer.state in ("running", "paused")
            or self.pomodoro.state != "idle"
        ):
            messagebox.showwarning(
                "Thông báo",
                "Hãy kết thúc đồng hồ học tập hoặc Pomodoro "
                "đang chạy trước khi xóa môn học!"
            )
            return

        session_count, task_count = self.db.count_subject_usage(
            self.selected_subject_id
        )

        if session_count > 0 or task_count > 0:
            messagebox.showwarning(
                "Không thể xóa",
                f"Môn học này đang có {session_count} buổi học "
                f"và {task_count} công việc.\n"
                "Hãy xóa các dữ liệu đó trước rồi xóa môn học."
            )
            return

        confirm = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa môn học này?"
        )

        if not confirm:
            return

        try:
            self.db.delete_subject(self.selected_subject_id)

        except ValueError as error:
            messagebox.showerror("Lỗi", str(error))
            return

        messagebox.showinfo("Thành công", "Đã xóa môn học!")

        self.clear_subject_form()
        self.load_subjects()
    def load_subjects(self):

        for item in self.subject_table.get_children():
            self.subject_table.delete(item)

        subjects = self.db.get_subjects()

        for subject in subjects:
            self.subject_table.insert(
                "",
                tk.END,
                values=subject
            )

        self.load_subject_options()
        self.load_pomodoro_subject_options()

        # Cập nhật môn học cho tab Công việc
        if hasattr(self, "task_view"):
            self.task_view.refresh_subjects()

    # =========================================
    # TAB 2: THEO DÕI THỜI GIAN HỌC
    # =========================================

    def build_session_tab(self):

        self.page_title(
            self.session_frame,
            "Theo dõi thời gian học",
            "Tập trung học tập và ghi lại từng buổi học"
        )

        card = self.create_card(
            self.session_frame,
            "Thông tin buổi học"
        )

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x")

        ttk.Label(
            form,
            text="Môn học",
            background=WHITE
        ).grid(row=0, column=0, sticky="w")

        self.subject_combo = ttk.Combobox(
            form,
            width=30,
            state="readonly"
        )
        self.subject_combo.grid(row=1, column=0, padx=(0, 20), pady=8)

        ttk.Label(
            form,
            text="Nội dung học",
            background=WHITE
        ).grid(row=0, column=1, sticky="w")

        self.note_entry = ttk.Entry(form, width=40)
        self.note_entry.grid(row=1, column=1, pady=8)

        timer_card = self.create_card(
            self.session_frame,
            "Đồng hồ học tập"
        )

        self.timer_label = tk.Label(
            timer_card,
            text="00:00:00",
            bg=WHITE,
            fg=BLUE,
            font=("Segoe UI", 42, "bold")
        )
        self.timer_label.pack(pady=15)

        button_frame = ttk.Frame(timer_card, style="Card.TFrame")
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="Bắt đầu",
            command=self.start_timer
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(
            button_frame,
            text="Tạm dừng",
            command=self.pause_timer,
            state="disabled",
            style="Secondary.TButton"
        )
        self.pause_button.grid(row=0, column=1, padx=5)

        self.resume_button = ttk.Button(
            button_frame,
            text="Tiếp tục",
            command=self.resume_timer,
            state="disabled"
        )
        self.resume_button.grid(row=0, column=2, padx=5)

        self.finish_button = ttk.Button(
            button_frame,
            text="Kết thúc và lưu",
            command=self.finish_timer,
            state="disabled",
            style="Danger.TButton"
        )
        self.finish_button.grid(row=0, column=3, padx=5)

        history_card = self.create_card(
            self.session_frame,
            "Lịch sử học tập"
        )

        self.session_table = ttk.Treeview(
            history_card,
            columns=("id", "subject", "date", "duration", "note"),
            show="headings",
            height=5
        )

        self.setup_table(
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
            history_buttons,
            text="Sửa buổi học đã chọn",
            style="Secondary.TButton",
            command=self.edit_selected_session
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            history_buttons,
            text="Xóa buổi học đã chọn",
            style="Danger.TButton",
            command=self.delete_selected_session
        ).grid(row=0, column=1, padx=4)

        ttk.Button(
            history_buttons,
            text="+ Nhập tay buổi học",
            command=self.add_manual_session
        ).grid(row=0, column=2, padx=4)

    def load_subject_options(self):

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
                "Thông báo",
                "Vui lòng thêm và chọn môn học trước!"
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
            self.timer_job = self.root.after(
                1000,
                self.refresh_timer_display
            )

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
        self.load_statistics()
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
                    self.format_duration(duration_seconds),
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
            body,
            text=f"Ngày học: {study_date}",
            background=WHITE,
            foreground=MUTED
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(
            body,
            text="Môn học",
            background=WHITE
        ).grid(row=1, column=0, sticky="w", pady=6)

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

        ttk.Label(
            body,
            text="Thời gian (phút)",
            background=WHITE
        ).grid(row=2, column=0, sticky="w", pady=6)

        minutes_entry = ttk.Entry(body, width=30)
        minutes_entry.insert(0, f"{duration_seconds / 60:.1f}")
        minutes_entry.grid(row=2, column=1, padx=(12, 0), pady=6)

        ttk.Label(
            body,
            text="Nội dung học",
            background=WHITE
        ).grid(row=3, column=0, sticky="w", pady=6)

        note_box = ttk.Entry(body, width=30)
        note_box.insert(0, note or "")
        note_box.grid(row=3, column=1, padx=(12, 0), pady=6)

        def save_changes():

            try:
                minutes = float(minutes_entry.get().replace(",", "."))

            except ValueError:
                messagebox.showwarning(
                    "Thông báo",
                    "Thời gian phải là một số!",
                    parent=dialog
                )
                return

            chosen_name = subject_box.get()

            if chosen_name not in self.subject_map:
                messagebox.showwarning(
                    "Thông báo",
                    "Vui lòng chọn môn học!",
                    parent=dialog
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
                messagebox.showwarning(
                    "Thông báo",
                    str(error),
                    parent=dialog
                )
                return

            dialog.destroy()

            self.load_sessions()
            self.load_statistics()

        button_row = ttk.Frame(body, style="Card.TFrame")
        button_row.grid(row=4, column=0, columnspan=2, pady=(16, 0))

        ttk.Button(
            button_row,
            text="Lưu thay đổi",
            command=save_changes
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_row,
            text="Hủy",
            style="Secondary.TButton",
            command=dialog.destroy
        ).grid(row=0, column=1, padx=5)

    def delete_selected_session(self):

        session_id = self.get_selected_session_id()

        if session_id is None:
            return

        confirm = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa buổi học này?"
        )

        if not confirm:
            return

        self.db.delete_session(session_id)

        self.load_sessions()
        self.load_statistics()

        messagebox.showinfo("Thành công", "Đã xóa buổi học!")

    def add_manual_session(self):

        if not self.subject_map:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng thêm môn học trước!"
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

        ttk.Label(
            body,
            text="Môn học",
            background=WHITE
        ).grid(row=0, column=0, sticky="w", pady=6)

        names = list(self.subject_map.keys())

        subject_box = ttk.Combobox(
            body,
            values=names,
            state="readonly",
            width=28
        )
        subject_box.set(names[0])
        subject_box.grid(row=0, column=1, padx=(12, 0), pady=6)

        ttk.Label(
            body,
            text="Ngày học (dd/mm/yyyy)",
            background=WHITE
        ).grid(row=1, column=0, sticky="w", pady=6)

        date_entry = ttk.Entry(body, width=30)
        date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        date_entry.grid(row=1, column=1, padx=(12, 0), pady=6)

        ttk.Label(
            body,
            text="Thời gian (phút)",
            background=WHITE
        ).grid(row=2, column=0, sticky="w", pady=6)

        minutes_entry = ttk.Entry(body, width=30)
        minutes_entry.grid(row=2, column=1, padx=(12, 0), pady=6)

        ttk.Label(
            body,
            text="Nội dung học",
            background=WHITE
        ).grid(row=3, column=0, sticky="w", pady=6)

        note_box = ttk.Entry(body, width=30)
        note_box.grid(row=3, column=1, padx=(12, 0), pady=6)

        def save_session():

            # Kiểm tra số phút
            try:
                minutes = float(minutes_entry.get().replace(",", "."))

            except ValueError:
                messagebox.showwarning(
                    "Thông báo",
                    "Thời gian phải là một số!",
                    parent=dialog
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

            # Kiểm tra ngày
            try:
                study_date = datetime.strptime(
                    date_entry.get().strip(),
                    "%d/%m/%Y"
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
                messagebox.showwarning(
                    "Thông báo",
                    str(error),
                    parent=dialog
                )
                return

            dialog.destroy()

            self.load_sessions()
            self.load_statistics()

            messagebox.showinfo("Thành công", "Đã thêm buổi học!")

        button_row = ttk.Frame(body, style="Card.TFrame")
        button_row.grid(row=4, column=0, columnspan=2, pady=(16, 0))

        ttk.Button(
            button_row,
            text="Lưu buổi học",
            command=save_session
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_row,
            text="Hủy",
            style="Secondary.TButton",
            command=dialog.destroy
        ).grid(row=0, column=1, padx=5)
    # =========================================
    # TAB 3: POMODORO
    # =========================================

    def build_pomodoro_tab(self):

        self.page_title(
            self.pomodoro_frame,
            "Pomodoro Focus",
            "Tập trung theo phiên, nghỉ ngơi hợp lý và duy trì hiệu suất học tập"
        )

        # Cấu hình Pomodoro
        config_card = self.create_card(
            self.pomodoro_frame,
            "Thiết lập phiên học"
        )

        config = ttk.Frame(config_card, style="Card.TFrame")
        config.pack(fill="x")

        ttk.Label(
            config,
            text="Môn học",
            background=WHITE
        ).grid(row=0, column=0, sticky="w", padx=5)

        self.pomodoro_subject_combo = ttk.Combobox(
            config,
            width=22,
            state="readonly"
        )
        self.pomodoro_subject_combo.grid(row=1, column=0, padx=5, pady=8)

        ttk.Label(
            config,
            text="Nội dung học",
            background=WHITE
        ).grid(row=0, column=1, sticky="w", padx=5)

        self.pomodoro_note_entry = ttk.Entry(config, width=25)
        self.pomodoro_note_entry.grid(row=1, column=1, padx=5, pady=8)

        ttk.Label(
            config,
            text="Tập trung (phút)",
            background=WHITE
        ).grid(row=0, column=2, padx=5)

        self.focus_spin = ttk.Spinbox(config, from_=1, to=120, width=8)
        self.focus_spin.set("25")
        self.focus_spin.grid(row=1, column=2, padx=5)

        ttk.Label(
            config,
            text="Nghỉ ngắn",
            background=WHITE
        ).grid(row=0, column=3, padx=5)

        self.short_spin = ttk.Spinbox(config, from_=1, to=60, width=8)
        self.short_spin.set("5")
        self.short_spin.grid(row=1, column=3, padx=5)

        ttk.Label(
            config,
            text="Nghỉ dài",
            background=WHITE
        ).grid(row=0, column=4, padx=5)

        self.long_spin = ttk.Spinbox(config, from_=1, to=90, width=8)
        self.long_spin.set("15")
        self.long_spin.grid(row=1, column=4, padx=5)

        ttk.Label(
            config,
            text="Sau bao nhiêu phiên",
            background=WHITE
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.long_after_spin = ttk.Spinbox(
            config,
            from_=2,
            to=10,
            width=8
        )
        self.long_after_spin.set("4")
        self.long_after_spin.grid(
            row=2,
            column=1,        # SỬA: trước đây là column=0 nên bị đè lên nhãn
            sticky="w",
            padx=5,
            pady=5
        )

        # Khu vực đồng hồ
        timer_card = self.create_card(
            self.pomodoro_frame,
            "Đồng hồ tập trung"
        )

        self.pomodoro_phase_label = tk.Label(
            timer_card,
            text="SẴN SÀNG TẬP TRUNG",
            bg=WHITE,
            fg=BLUE,
            font=("Segoe UI", 13, "bold")
        )
        self.pomodoro_phase_label.pack(pady=(5, 10))

        self.pomodoro_time_label = tk.Label(
            timer_card,
            text="25:00",
            bg=WHITE,
            fg=BLUE,
            font=("Segoe UI", 52, "bold")
        )
        self.pomodoro_time_label.pack(pady=5)

        self.pomodoro_progress = ttk.Progressbar(
            timer_card,
            maximum=100,
            mode="determinate"
        )
        self.pomodoro_progress.pack(fill="x", padx=45, pady=15)

        self.pomodoro_status_label = ttk.Label(
            timer_card,
            text="Chọn môn học và nhấn Bắt đầu.",
            background=WHITE,
            foreground=MUTED
        )
        self.pomodoro_status_label.pack(pady=5)

        self.pomodoro_cycle_label = tk.Label(
            timer_card,
            text="Số phiên tập trung hoàn thành: 0",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 11, "bold")
        )
        self.pomodoro_cycle_label.pack(pady=10)

        # Các nút
        button_frame = ttk.Frame(timer_card, style="Card.TFrame")
        button_frame.pack(pady=15)

        self.pomodoro_start_button = ttk.Button(
            button_frame,
            text="▶ Bắt đầu",
            command=self.start_pomodoro
        )
        self.pomodoro_start_button.grid(row=0, column=0, padx=5)

        self.pomodoro_pause_button = ttk.Button(
            button_frame,
            text="Ⅱ Tạm dừng",
            command=self.pause_pomodoro,
            state="disabled",
            style="Secondary.TButton"
        )
        self.pomodoro_pause_button.grid(row=0, column=1, padx=5)

        self.pomodoro_resume_button = ttk.Button(
            button_frame,
            text="▶ Tiếp tục",
            command=self.resume_pomodoro,
            state="disabled"
        )
        self.pomodoro_resume_button.grid(row=0, column=2, padx=5)

        self.pomodoro_stop_button = ttk.Button(
            button_frame,
            text="■ Kết thúc",
            command=self.stop_pomodoro,
            state="disabled",
            style="Danger.TButton"
        )
        self.pomodoro_stop_button.grid(row=0, column=3, padx=5)

        # Hướng dẫn
        guide = self.create_card(
            self.pomodoro_frame,
            "Quy trình Pomodoro"
        )

        tk.Label(
            guide,
            text=(
                "1. Chọn môn học và nội dung cần học.\n"
                "2. Tập trung trong thời gian đã thiết lập.\n"
                "3. Nghỉ ngắn sau mỗi phiên học.\n"
                "4. Sau số phiên quy định, ứng dụng chuyển sang nghỉ dài.\n"
                "5. Chỉ thời gian tập trung được lưu vào lịch sử học tập."
            ),
            justify="left",
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 10),
            anchor="w"
        ).pack(fill="x")

    # Cập nhật danh sách môn học của Pomodoro
    def load_pomodoro_subject_options(self):

        subjects = self.db.get_subjects()

        subject_names = [subject[1] for subject in subjects]

        self.pomodoro_subject_combo["values"] = subject_names

        if self.pomodoro_subject_combo.get() not in subject_names:
            self.pomodoro_subject_combo.set(
                subject_names[0] if subject_names else ""
            )

    # Khóa hoặc mở cấu hình Pomodoro
    def set_pomodoro_controls(self, enabled):

        state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"

        self.pomodoro_subject_combo.config(state=combo_state)
        self.pomodoro_note_entry.config(state=state)

        self.focus_spin.config(state=state)
        self.short_spin.config(state=state)
        self.long_spin.config(state=state)
        self.long_after_spin.config(state=state)

    # Bắt đầu Pomodoro
    def start_pomodoro(self):

        subject_name = self.pomodoro_subject_combo.get()

        if not subject_name:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng thêm và chọn môn học trước!"
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
                "Lỗi",
                "Vui lòng nhập các thiết lập thời gian hợp lệ!"
            )

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    # Tạm dừng
    def pause_pomodoro(self):

        try:
            self.pomodoro.pause()

            self.pomodoro_pause_button.config(state="disabled")
            self.pomodoro_resume_button.config(state="normal")

            self.refresh_pomodoro_display()

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    # Tiếp tục
    def resume_pomodoro(self):

        try:
            self.pomodoro.resume()

            self.pomodoro_pause_button.config(state="normal")
            self.pomodoro_resume_button.config(state="disabled")

            self.refresh_pomodoro_display()

        except RuntimeError as error:
            messagebox.showerror("Lỗi", str(error))

    # Hiển thị đồng hồ Pomodoro
    def refresh_pomodoro_display(self):

        if self.pomodoro_job is not None:
            self.root.after_cancel(self.pomodoro_job)
            self.pomodoro_job = None

        remaining = int(self.pomodoro.get_remaining() + 0.999)

        minutes = remaining // 60
        seconds = remaining % 60

        self.pomodoro_time_label.config(
            text=f"{minutes:02d}:{seconds:02d}"
        )

        self.pomodoro_progress["value"] = self.pomodoro.get_progress()

        self.pomodoro_cycle_label.config(
            text=(
                "Số phiên tập trung hoàn thành: "
                f"{self.pomodoro.completed_cycles}"
            )
        )

        if self.pomodoro.phase == "focus":

            self.pomodoro_phase_label.config(
                text="THỜI GIAN TẬP TRUNG",
                fg=BLUE
            )

            self.pomodoro_time_label.config(fg=BLUE)

            status = (
                "Đang tập trung học. Hãy cố gắng hoàn thành phiên này."
                if self.pomodoro.state == "running"
                else "Đang tạm dừng phiên học."
            )

        else:

            if self.pomodoro.break_kind == "long":
                phase_text = "NGHỈ DÀI"
            else:
                phase_text = "NGHỈ NGẮN"

            self.pomodoro_phase_label.config(
                text=phase_text,
                fg=TEAL
            )

            self.pomodoro_time_label.config(fg=TEAL)

            status = (
                "Hãy thư giãn và nghỉ ngơi."
                if self.pomodoro.state == "running"
                else "Thời gian nghỉ đang tạm dừng."
            )

        if self.pomodoro.state == "idle":
            status = "Chọn môn học và nhấn Bắt đầu."

        # Thông báo tạm thời (hiện vài giây) được ưu tiên hơn trạng thái thường
        if (
            self.pomodoro.state != "idle"
            and time.monotonic() < self.pomodoro_notice_until
        ):
            status = self.pomodoro_notice
        self.pomodoro_status_label.config(text=status)

        if self.pomodoro.state == "running":
            self.pomodoro_job = self.root.after(
                250,
                self.pomodoro_tick
            )

    # Kiểm tra quá trình đếm ngược
        # Hiện thông báo tạm thời trên nhãn trạng thái Pomodoro
    def show_pomodoro_notice(self, text, seconds=8):

        self.pomodoro_notice = text
        self.pomodoro_notice_until = time.monotonic() + seconds

    # Kiểm tra quá trình đếm ngược
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

    # Lưu phiên tập trung vào SQLite. Trả về True nếu lưu thành công
    def save_pomodoro_session(self, event):

        try:
            self.db.add_timed_session(
                event["subject_id"],
                event["start_time"].isoformat(
                    sep=" ",
                    timespec="seconds"
                ),
                event["end_time"].isoformat(
                    sep=" ",
                    timespec="seconds"
                ),
                event["duration_seconds"],
                event["note"] or "Phiên học Pomodoro"
            )

        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror(
                "Lỗi",
                f"Không lưu được phiên học: {error}"
            )
            return False

        self.load_sessions()
        self.load_statistics()

        return True

    # Kết thúc Pomodoro
    def stop_pomodoro(self):

        confirm = messagebox.askyesno(
            "Xác nhận",
            "Bạn muốn kết thúc chế độ Pomodoro?"
        )

        if not confirm:
            return

        if self.pomodoro_job is not None:
            self.root.after_cancel(self.pomodoro_job)
            self.pomodoro_job = None

        # Lưu TRƯỚC, nếu lỗi thì giữ nguyên đồng hồ để thử lại
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

        messagebox.showinfo(
            "Thông báo",
            "Đã kết thúc chế độ Pomodoro."
        )
    # =========================================
    # TAB 4: THỐNG KÊ
    # =========================================

    def build_statistics_tab(self):

        self.page_title(
            self.statistics_frame,
            "Thống kê học tập",
            "Theo dõi kết quả và thời gian học của bạn"
        )

        filter_card = self.create_card(
            self.statistics_frame,
            "Bộ lọc thời gian"
        )

        filter_frame = ttk.Frame(filter_card, style="Card.TFrame")
        filter_frame.pack(anchor="w")

        ttk.Label(
            filter_frame,
            text="Khoảng thời gian:",
            background=WHITE
        ).grid(row=0, column=0, padx=5)

        self.period_combo = ttk.Combobox(
            filter_frame,
            values=["Hôm nay", "Tuần này", "Tháng này", "Tất cả"],
            state="readonly",
            width=20
        )
        self.period_combo.set("Tuần này")
        self.period_combo.grid(row=0, column=1, padx=10)

        ttk.Button(
            filter_frame,
            text="Cập nhật",
            command=self.load_statistics
        ).grid(row=0, column=2, padx=5)

        summary_card = self.create_card(
            self.statistics_frame,
            "Tổng quan học tập"
        )

        ttk.Button(
            filter_frame,
            text="Xuất báo cáo",
            style="Secondary.TButton",
            command=self.export_statistics
        ).grid(row=0, column=3, padx=5)

        summary_grid = ttk.Frame(summary_card, style="Card.TFrame")
        summary_grid.pack(fill="x")

        self.total_time_label = ttk.Label(
            summary_grid,
            text="0 giây",
            style="Value.TLabel"
        )
        self.total_time_label.grid(row=0, column=0, padx=35, pady=8)

        self.session_count_label = ttk.Label(
            summary_grid,
            text="0 buổi",
            style="Value.TLabel"
        )
        self.session_count_label.grid(row=0, column=1, padx=35, pady=8)

        self.subject_count_label = ttk.Label(
            summary_grid,
            text="0 môn",
            style="Value.TLabel"
        )
        self.subject_count_label.grid(row=0, column=2, padx=35, pady=8)

        for column, title in enumerate(
            ["Tổng thời gian học", "Số buổi học", "Số môn đã học"]
        ):
            ttk.Label(
                summary_grid,
                text=title,
                background=WHITE,
                foreground=MUTED
            ).grid(row=1, column=column, padx=35)

        subject_card = self.create_card(
            self.statistics_frame,
            "Thống kê theo môn học"
        )

        self.statistics_subject_table = ttk.Treeview(
            subject_card,
            columns=("subject", "sessions", "duration"),
            show="headings",
            height=4
        )

        self.setup_table(
            self.statistics_subject_table,
            [
                ("subject", "Môn học", 250, "w"),
                ("sessions", "Số buổi", 120, "center"),
                ("duration", "Tổng thời gian", 220, "center")
            ]
        )

        self.statistics_subject_table.pack(fill="both", expand=True)
                # ===== BIỂU ĐỒ CỘT: THỜI GIAN HỌC THEO NGÀY =====
        bar_card = self.create_card(
            self.statistics_frame,
            "Biểu đồ thời gian học theo ngày"
        )

        self.daily_figure = Figure(figsize=(8, 3.4), dpi=100)
        self.daily_ax = self.daily_figure.add_subplot(111)

        self.daily_canvas = FigureCanvasTkAgg(
            self.daily_figure,
            master=bar_card
        )
        self.daily_canvas.get_tk_widget().pack(fill="both", expand=True)

        # ===== BIỂU ĐỒ TRÒN: TỶ LỆ THEO MÔN HỌC =====
        pie_card = self.create_card(
            self.statistics_frame,
            "Tỷ lệ thời gian học theo môn"
        )

        self.subject_figure = Figure(figsize=(8, 3.6), dpi=100)
        self.subject_ax = self.subject_figure.add_subplot(111)

        self.subject_canvas = FigureCanvasTkAgg(
            self.subject_figure,
            master=pie_card
        )
        self.subject_canvas.get_tk_widget().pack(fill="both", expand=True)

        daily_card = self.create_card(
            self.statistics_frame,
            "Thống kê theo ngày"
        )

        self.statistics_daily_table = ttk.Treeview(
            daily_card,
            columns=("date", "sessions", "duration"),
            show="headings",
            height=4
        )

        self.setup_table(
            self.statistics_daily_table,
            [
                ("date", "Ngày học", 250, "w"),
                ("sessions", "Số buổi", 120, "center"),
                ("duration", "Tổng thời gian", 220, "center")
            ]
        )

        self.statistics_daily_table.pack(fill="both", expand=True)

    # =========================================
    # BIỂU ĐỒ
    # =========================================

    def draw_empty_chart(self, figure, ax, canvas):

        ax.clear()
        ax.axis("off")
        ax.text(
            0.5, 0.5,
            "Chưa có dữ liệu trong khoảng thời gian này",
            ha="center",
            va="center",
            fontsize=11,
            color=MUTED,
            transform=ax.transAxes
        )
        canvas.draw_idle()

    def update_daily_chart(self, daily_data):

        ax = self.daily_ax
        ax.clear()

        if not daily_data:
            self.draw_empty_chart(
                self.daily_figure, ax, self.daily_canvas
            )
            return

        # daily_data đang xếp ngày mới nhất trước -> đảo lại,
        # chỉ lấy tối đa 14 ngày gần nhất cho khỏi chật
        rows = list(reversed(daily_data))[-14:]

        labels = [
            datetime.strptime(row[0], "%Y-%m-%d").strftime("%d/%m")
            for row in rows
        ]
        minutes = [row[2] / 60 for row in rows]

        bars = ax.bar(labels, minutes, color=BLUE, width=0.6)
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=9)

        ax.set_ylabel("Phút")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=9)
        ax.set_ylim(0, max(minutes) * 1.2)

        self.daily_figure.tight_layout()
        self.daily_canvas.draw_idle()

    def update_subject_chart(self, subject_data):

        ax = self.subject_ax
        ax.clear()

        if not subject_data:
            self.draw_empty_chart(
                self.subject_figure, ax, self.subject_canvas
            )
            return

        names = [row[0] for row in subject_data]
        minutes = [row[2] / 60 for row in subject_data]
        colors = [
            CHART_COLORS[i % len(CHART_COLORS)]
            for i in range(len(names))
        ]

        ax.pie(
            minutes,
            colors=colors,
            autopct="%1.0f%%",
            startangle=90,
            pctdistance=0.75,
            textprops={"color": "white", "fontsize": 10},
            wedgeprops={"edgecolor": "white"}
        )
        ax.axis("equal")

        legend_labels = [
            f"{name} ({int(m)} phút)"
            for name, m in zip(names, minutes)
        ]

        ax.legend(
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            frameon=False,
            fontsize=10
        )

        self.subject_figure.tight_layout()
        self.subject_canvas.draw_idle()

    def export_statistics(self):

        start_date, end_date = self.get_date_range()

        rows = self.db.get_sessions_for_export(start_date, end_date)

        if not rows:
            messagebox.showwarning(
                "Thông báo",
                "Không có buổi học nào trong khoảng thời gian này!"
            )
            return

        default_name = (
            f"bao_cao_hoc_tap_{date.today().strftime('%Y%m%d')}"
        )

        path = filedialog.asksaveasfilename(
            title="Lưu báo cáo học tập",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[
                ("Excel (*.xlsx)", "*.xlsx"),
                ("CSV (*.csv)", "*.csv")
            ]
        )

        # Người dùng bấm Hủy
        if not path:
            return

        try:
            export_report(rows, path)

        except PermissionError:
            messagebox.showerror(
                "Lỗi",
                "Không ghi được file. Nếu file đang mở trong Excel "
                "hãy đóng lại rồi thử lại."
            )
            return

        except ImportError:
            messagebox.showerror(
                "Lỗi",
                "Thiếu thư viện openpyxl.\n"
                "Hãy chạy: pip install openpyxl"
            )
            return

        except (OSError, ValueError) as error:
            messagebox.showerror("Lỗi", str(error))
            return

        messagebox.showinfo(
            "Thành công",
            f"Đã xuất báo cáo:\n{path}"
        )

    def get_date_range(self):

        today = date.today()
        period = self.period_combo.get()

        if period == "Hôm nay":
            start_date = today

        elif period == "Tuần này":
            start_date = today - timedelta(days=today.weekday())

        elif period == "Tháng này":
            start_date = today.replace(day=1)

        else:
            start_date = date(1, 1, 1)

        return start_date.isoformat(), today.isoformat()

    def format_duration(self, total_seconds):

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours} giờ {minutes} phút"

        elif minutes > 0:
            return f"{minutes} phút {seconds} giây"

        return f"{seconds} giây"

    def load_statistics(self):

        start_date, end_date = self.get_date_range()

        summary, subject_data, daily_data = (
            self.db.get_statistics(start_date, end_date)
        )

        self.total_time_label.config(
            text=self.format_duration(summary[0])
        )

        self.session_count_label.config(
            text=f"{summary[1]} buổi"
        )

        self.subject_count_label.config(
            text=f"{summary[2]} môn"
        )

        for table in [
            self.statistics_subject_table,
            self.statistics_daily_table
        ]:
            for item in table.get_children():
                table.delete(item)

        for subject in subject_data:
            self.statistics_subject_table.insert(
                "",
                tk.END,
                values=(
                    subject[0],
                    subject[1],
                    self.format_duration(subject[2])
                )
            )

        for daily in daily_data:
            self.statistics_daily_table.insert(
                "",
                tk.END,
                values=(
                    daily[0],
                    daily[1],
                    self.format_duration(daily[2])
                )
            )
        self.update_daily_chart(daily_data)
        self.update_subject_chart(subject_data)

        self.load_goal_progress()

    # =========================================
    # TAB 5: MỤC TIÊU
    # =========================================

    def build_goal_tab(self):

        self.page_title(
            self.goal_frame,
            "Mục tiêu học tập",
            "Thiết lập mục tiêu và duy trì thói quen học tập"
        )

        card = self.create_card(
            self.goal_frame,
            "Thiết lập mục tiêu tuần"
        )

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

        progress_card = self.create_card(
            self.goal_frame,
            "Tiến độ học tập tuần này"
        )

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
                f"Đã học: {self.format_duration(total_seconds)}"
                f" / Mục tiêu: {self.format_duration(target_seconds)}"
                f"\nCòn thiếu: {self.format_duration(remaining_seconds)}"
            )
        )

        self.goal_percent_label.config(
            text=f"{percent:.1f}% hoàn thành"
        )

    # =========================================
    # ĐÓNG ỨNG DỤNG
    # =========================================

    def close_app(self):

        # ----- Buổi học thông thường đang chạy -----
        if self.timer.state in ("running", "paused"):

            answer = messagebox.askyesnocancel(
                "Xác nhận",
                "Buổi học đang diễn ra chưa được lưu.\n"
                "Bạn có muốn lưu phần đã học trước khi thoát không?\n\n"
                "Có: lưu rồi thoát | Không: bỏ buổi học và thoát | "
                "Hủy: ở lại"
            )

            if answer is None:
                return

            if answer and self.timer.get_elapsed() >= 1:

                try:
                    start_time, end_time, duration = (
                        self.timer.get_summary()
                    )

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
                    return

        # ----- Pomodoro đang chạy -----
        if self.pomodoro.state in ("running", "paused"):

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
                    return

                if answer and not self.save_pomodoro_session(event):
                    return

            else:

                if not messagebox.askyesno(
                    "Xác nhận",
                    "Pomodoro đang trong giờ nghỉ. Bạn có muốn thoát không?"
                ):
                    return

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)

        if self.pomodoro_job is not None:
            self.root.after_cancel(self.pomodoro_job)

        self.db.close()
        self.root.destroy()

# =========================================
# CHẠY CHƯƠNG TRÌNH
# =========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = StudyTrackerApp(root)

    root.mainloop()