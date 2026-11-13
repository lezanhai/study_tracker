# main.py
import tkinter as tk
from tkinter import ttk
from datetime import date

from ui.goals_tab import GoalsTab
from ui.stats_tab import StatsTab
from ui.task_manager import TaskManagerView
from ui.subject_tab import SubjectTab
from database import DatabaseManager
from ui.tracking_tab import TrackingTab
from ui.pomodoro_tab import PomodoroTab
from ui.theme import BG, WHITE, NAVY, apply_style

class StudyTrackerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Study Tracker")
        self.root.geometry("1150x800")
        self.root.minsize(950, 680)
        self.root.configure(bg=BG)

        self.db = DatabaseManager()

        apply_style()
        self.build_header()
        self.build_notebook()

        # Khởi tạo tab quản lý môn học từ subject_tab.py
        self.subject_view = SubjectTab(
            self.subject_frame,
            self.db,
            self.refresh_subject_data,
            self.subject_operations_busy
        )

        # Khởi tạo các tab còn lại
        self.tracking_view = TrackingTab(
            self.session_frame,
            self.db,
            self.root,
            self.on_tracking_session_saved
        )

        self.pomodoro_view = PomodoroTab(
            self.pomodoro_frame,
            self.db,
            self.root,
            self.on_pomodoro_session_saved
        )


        self.goals_view = GoalsTab(self.goal_frame, self.db)

        self.stats_view = StatsTab(
            self.statistics_frame,
            self.db,
            on_goal_changed=self.goals_view.load_goal_progress
        )

        # Khởi tạo giao diện quản lý công việc
        self.task_view = TaskManagerView(
            self.task_frame,
            self.db
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
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
    # TAB 1: QUẢN LÝ MÔN HỌC
    # Đã tách giao diện sang subject_tab.py
    # =========================================

    def subject_operations_busy(self):
        return (
        self.tracking_view.is_active()
        or self.pomodoro_view.is_occupied()
    )

    def refresh_subject_data(self):
        self.load_subjects()
        self.tracking_view.load_sessions()
        self.stats_view.refresh()

    def on_tracking_session_saved(self):
        self.stats_view.refresh()

    def on_pomodoro_session_saved(self):
        self.tracking_view.load_sessions()
        self.stats_view.refresh()

    def load_subjects(self):

        # Tải danh sách môn học trong tab riêng
        self.subject_view.load_subjects()

        # Cập nhật danh sách môn học ở tab Theo dõi học tập
        self.tracking_view.refresh_subjects()

        # Cập nhật danh sách môn học ở tab Pomodoro
        self.pomodoro_view.refresh_subjects()

        # Cập nhật danh sách môn học ở tab Công việc
        if hasattr(self, "task_view"):
            self.task_view.refresh_subjects()

    # =========================================
    # ĐÓNG ỨNG DỤNG
    # =========================================

    def close_app(self):

                # ----- Buổi học thông thường đang chạy -----
        if self.tracking_view.is_active():
            if not self.tracking_view.confirm_and_flush_on_exit():
                return

        # ----- Pomodoro đang chạy -----
        if self.pomodoro_view.is_active():
            if not self.pomodoro_view.confirm_and_flush_on_exit():
                return


        self.db.close()
        self.root.destroy()

# =========================================
# CHẠY CHƯƠNG TRÌNH
# =========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = StudyTrackerApp(root)

    root.mainloop()