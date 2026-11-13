# stats_tab.py

from datetime import date
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from base_tab import BaseTab
from exporter import export_report
from theme import WHITE, BLUE, MUTED, CHART_COLORS
from utils import format_duration, get_date_range, setup_table


class StatsTab(BaseTab):

    def __init__(self, parent, db, on_goal_changed=None):
        super().__init__(parent, db)

        # Được gọi mỗi lần load xong, để tab Mục tiêu cập nhật theo
        # (tránh StatsTab phải biết trực tiếp về GoalsTab)
        self.on_goal_changed = on_goal_changed

        self.build_ui()
        self.refresh()

    # =========================================
    # GIAO DIỆN
    # =========================================

    def build_ui(self):

        self.page_title(
            "Thống kê học tập",
            "Theo dõi kết quả và thời gian học của bạn"
        )

        filter_card = self.create_card("Bộ lọc thời gian")

        filter_frame = ttk.Frame(filter_card, style="Card.TFrame")
        filter_frame.pack(anchor="w")

        ttk.Label(
            filter_frame, text="Khoảng thời gian:", background=WHITE
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
            filter_frame, text="Cập nhật", command=self.refresh
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            filter_frame, text="Xuất báo cáo", style="Secondary.TButton",
            command=self.export_statistics
        ).grid(row=0, column=3, padx=5)

        summary_card = self.create_card("Tổng quan học tập")

        summary_grid = ttk.Frame(summary_card, style="Card.TFrame")
        summary_grid.pack(fill="x")

        self.total_time_label = ttk.Label(
            summary_grid, text="0 giây", style="Value.TLabel"
        )
        self.total_time_label.grid(row=0, column=0, padx=35, pady=8)

        self.session_count_label = ttk.Label(
            summary_grid, text="0 buổi", style="Value.TLabel"
        )
        self.session_count_label.grid(row=0, column=1, padx=35, pady=8)

        self.subject_count_label = ttk.Label(
            summary_grid, text="0 môn", style="Value.TLabel"
        )
        self.subject_count_label.grid(row=0, column=2, padx=35, pady=8)

        for column, title in enumerate(
            ["Tổng thời gian học", "Số buổi học", "Số môn đã học"]
        ):
            ttk.Label(
                summary_grid, text=title, background=WHITE, foreground=MUTED
            ).grid(row=1, column=column, padx=35)

        subject_card = self.create_card("Thống kê theo môn học")

        self.statistics_subject_table = ttk.Treeview(
            subject_card,
            columns=("subject", "sessions", "duration"),
            show="headings",
            height=4
        )

        setup_table(
            self.statistics_subject_table,
            [
                ("subject", "Môn học", 250, "w"),
                ("sessions", "Số buổi", 120, "center"),
                ("duration", "Tổng thời gian", 220, "center")
            ]
        )

        self.statistics_subject_table.pack(fill="both", expand=True)

        # ===== BIỂU ĐỒ CỘT: THỜI GIAN HỌC THEO NGÀY =====
        bar_card = self.create_card("Biểu đồ thời gian học theo ngày")

        self.daily_figure = Figure(figsize=(8, 3.4), dpi=100)
        self.daily_ax = self.daily_figure.add_subplot(111)

        self.daily_canvas = FigureCanvasTkAgg(
            self.daily_figure, master=bar_card
        )
        self.daily_canvas.get_tk_widget().pack(fill="both", expand=True)

        # ===== BIỂU ĐỒ TRÒN: TỶ LỆ THEO MÔN HỌC =====
        pie_card = self.create_card("Tỷ lệ thời gian học theo môn")

        self.subject_figure = Figure(figsize=(8, 3.6), dpi=100)
        self.subject_ax = self.subject_figure.add_subplot(111)

        self.subject_pie_canvas = FigureCanvasTkAgg(
            self.subject_figure, master=pie_card
        )
        self.subject_pie_canvas.get_tk_widget().pack(fill="both", expand=True)

        daily_card = self.create_card("Thống kê theo ngày")

        self.statistics_daily_table = ttk.Treeview(
            daily_card,
            columns=("date", "sessions", "duration"),
            show="headings",
            height=4
        )

        setup_table(
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
            ha="center", va="center", fontsize=11,
            color=MUTED, transform=ax.transAxes
        )
        canvas.draw_idle()

    def update_daily_chart(self, daily_data):

        from datetime import datetime

        ax = self.daily_ax
        ax.clear()

        if not daily_data:
            self.draw_empty_chart(self.daily_figure, ax, self.daily_canvas)
            return

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
                self.subject_figure, ax, self.subject_pie_canvas
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
        self.subject_pie_canvas.draw_idle()

    # =========================================
    # XUẤT BÁO CÁO
    # =========================================

    def export_statistics(self):

        start_date, end_date = get_date_range(self.period_combo.get())

        rows = self.db.get_sessions_for_export(start_date, end_date)

        if not rows:
            messagebox.showwarning(
                "Thông báo",
                "Không có buổi học nào trong khoảng thời gian này!"
            )
            return

        default_name = f"bao_cao_hoc_tap_{date.today().strftime('%Y%m%d')}"

        path = filedialog.asksaveasfilename(
            title="Lưu báo cáo học tập",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[
                ("Excel (*.xlsx)", "*.xlsx"),
                ("CSV (*.csv)", "*.csv")
            ]
        )

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
                "Thiếu thư viện openpyxl.\nHãy chạy: pip install openpyxl"
            )
            return

        except (OSError, ValueError) as error:
            messagebox.showerror("Lỗi", str(error))
            return

        messagebox.showinfo("Thành công", f"Đã xuất báo cáo:\n{path}")

    # =========================================
    # TẢI / LÀM MỚI THỐNG KÊ
    # Gọi public method này từ main.py bất cứ khi nào có dữ liệu mới
    # =========================================

    def refresh(self):

        start_date, end_date = get_date_range(self.period_combo.get())

        summary, subject_data, daily_data = (
            self.db.get_statistics(start_date, end_date)
        )

        self.total_time_label.config(text=format_duration(summary[0]))
        self.session_count_label.config(text=f"{summary[1]} buổi")
        self.subject_count_label.config(text=f"{summary[2]} môn")

        for table in [
            self.statistics_subject_table,
            self.statistics_daily_table
        ]:
            for item in table.get_children():
                table.delete(item)

        for subject in subject_data:
            self.statistics_subject_table.insert(
                "", "end",
                values=(subject[0], subject[1], format_duration(subject[2]))
            )

        for daily in daily_data:
            self.statistics_daily_table.insert(
                "", "end",
                values=(daily[0], daily[1], format_duration(daily[2]))
            )

        self.update_daily_chart(daily_data)
        self.update_subject_chart(subject_data)

        if self.on_goal_changed is not None:
            self.on_goal_changed()