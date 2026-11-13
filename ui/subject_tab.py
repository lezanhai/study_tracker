
import tkinter as tk
from tkinter import ttk, messagebox

from ui.base_tab import BaseTab
from ui.theme import WHITE
from utils.utils import setup_table


class SubjectTab(BaseTab):
    def __init__(self, parent, db, on_change, is_busy):
        super().__init__(parent, db)

        self.on_change = on_change
        self.is_busy = is_busy
        self.selected_subject_id = None

        self.build_ui()
        self.load_subjects()

    # =========================================
    # GIAO DIỆN QUẢN LÝ MÔN HỌC
    # =========================================

    def build_ui(self):
        self.page_title(
            "Quản lý môn học",
            "Thêm, sửa và xóa các môn học của bạn"
        )

        card = self.create_card("Thông tin môn học")

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x")

        ttk.Label(
            form,
            text="Tên môn học",
            background=WHITE
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.name_entry = ttk.Entry(form, width=30)
        self.name_entry.grid(
            row=1, column=0, padx=(0, 15), pady=5
        )

        ttk.Label(
            form,
            text="Mô tả",
            background=WHITE
        ).grid(row=0, column=1, sticky="w", pady=5)

        self.description_entry = ttk.Entry(form, width=35)
        self.description_entry.grid(
            row=1, column=1, padx=(0, 15), pady=5
        )

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
            "Danh sách môn học (chọn một dòng để sửa hoặc xóa)",
            fill="both",
            expand=True
        )

        self.subject_table = ttk.Treeview(
            table_card,
            columns=("id", "name", "description"),
            show="headings"
        )

        setup_table(
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

    # =========================================
    # THÊM MÔN HỌC
    # =========================================

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

        except ValueError as error:
            messagebox.showerror("Lỗi", str(error))
            return

        messagebox.showinfo("Thành công", "Đã thêm môn học!")

        self.clear_subject_form()
        self.on_change()

    # =========================================
    # CHỌN MÔN HỌC
    # =========================================

    def select_subject(self, event=None):
        selection = self.subject_table.selection()

        if not selection:
            return

        values = self.subject_table.item(
            selection[0], "values"
        )

        self.selected_subject_id = int(values[0])

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, str(values[1]))

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, str(values[2]))

    # =========================================
    # LÀM MỚI FORM
    # =========================================

    def clear_subject_form(self):
        self.selected_subject_id = None

        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

        for item in self.subject_table.selection():
            self.subject_table.selection_remove(item)

    # =========================================
    # CẬP NHẬT MÔN HỌC
    # =========================================

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

        messagebox.showinfo(
            "Thành công",
            "Đã cập nhật môn học!"
        )

        self.clear_subject_form()
        self.on_change()

    # =========================================
    # XÓA MÔN HỌC
    # =========================================

    def delete_selected_subject(self):
        if self.selected_subject_id is None:
            messagebox.showwarning(
                "Thông báo",
                "Hãy chọn môn học cần xóa trong bảng!"
            )
            return

        if self.is_busy():
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

        messagebox.showinfo(
            "Thành công",
            "Đã xóa môn học!"
        )

        self.clear_subject_form()
        self.on_change()

    # =========================================
    # TẢI DANH SÁCH MÔN HỌC
    # =========================================

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
