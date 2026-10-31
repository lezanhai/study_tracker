#task_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date


class TaskManagerView:

    def __init__(self, parent, db):

        self.parent = parent
        self.db = db
        self.subject_map = {}
        self.selected_task_id = None

        self.build_ui()
        self.refresh_subjects()
        self.load_tasks()

    # =================================
    # GIAO DIỆN
    # =================================

    def build_ui(self):

        ttk.Label(
            self.parent,
            text="Quản lý công việc",
            style="Title.TLabel"
        ).pack(anchor="w", padx=25, pady=(22, 3))

        ttk.Label(
            self.parent,
            text="Theo dõi bài tập, nhiệm vụ và thời hạn hoàn thành",
            style="Subtitle.TLabel"
        ).pack(anchor="w", padx=25, pady=(0, 18))

        card = ttk.Frame(
            self.parent,
            style="Card.TFrame",
            padding=18
        )

        card.pack(fill="x", padx=25, pady=8)

        ttk.Label(
            card,
            text="Thông tin công việc",
            style="CardTitle.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x")

        # Môn học
        ttk.Label(
            form,
            text="Môn học",
            background="white"
        ).grid(row=0, column=0, sticky="w", padx=5)

        self.subject_combo = ttk.Combobox(
            form,
            width=23,
            state="readonly"
        )

        self.subject_combo.grid(
            row=1, column=0, padx=5, pady=7
        )

        # Tên công việc
        ttk.Label(
            form,
            text="Tên công việc",
            background="white"
        ).grid(row=0, column=1, sticky="w", padx=5)

        self.title_entry = ttk.Entry(
            form,
            width=30
        )

        self.title_entry.grid(
            row=1, column=1, padx=5, pady=7
        )

        # Hạn hoàn thành
        ttk.Label(
            form,
            text="Hạn hoàn thành (dd/mm/yyyy)",
            background="white"
        ).grid(row=0, column=2, sticky="w", padx=5)

        self.date_entry = ttk.Entry(
            form,
            width=20
        )

        self.date_entry.grid(
            row=1, column=2, padx=5, pady=7
        )

        self.date_entry.insert(
            0,
            date.today().strftime("%d/%m/%Y")
        )

        # Mức độ ưu tiên
        ttk.Label(
            form,
            text="Mức độ ưu tiên",
            background="white"
        ).grid(
            row=2, column=0, sticky="w",
            padx=5, pady=(10, 0)
        )

        self.priority_combo = ttk.Combobox(
            form,
            values=["Thấp", "Trung bình", "Cao"],
            state="readonly",
            width=21
        )

        self.priority_combo.set("Trung bình")

        self.priority_combo.grid(
            row=3, column=0, padx=5, pady=7
        )

        # Mô tả
        ttk.Label(
            form,
            text="Mô tả công việc",
            background="white"
        ).grid(
            row=2, column=1, sticky="w",
            padx=5, pady=(10, 0)
        )

        self.description_entry = ttk.Entry(
            form,
            width=30
        )

        self.description_entry.grid(
            row=3, column=1, padx=5, pady=7
        )

        # Các nút
        button_frame = ttk.Frame(
            card,
            style="Card.TFrame"
        )

        button_frame.pack(anchor="w", pady=(12, 0))

        ttk.Button(
            button_frame,
            text="+ Thêm công việc",
            command=self.add_task
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            button_frame,
            text="Cập nhật",
            command=self.update_selected_task
        ).grid(row=0, column=1, padx=4)

        ttk.Button(
            button_frame,
            text="Làm mới",
            style="Secondary.TButton",
            command=self.clear_form
        ).grid(row=0, column=2, padx=4)

        # =================================
        # DANH SÁCH CÔNG VIỆC
        # =================================

        list_card = ttk.Frame(
            self.parent,
            style="Card.TFrame",
            padding=18
        )

        list_card.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=8
        )

        ttk.Label(
            list_card,
            text="Danh sách công việc",
            style="CardTitle.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        filter_frame = ttk.Frame(
            list_card,
            style="Card.TFrame"
        )

        filter_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            filter_frame,
            text="Lọc theo trạng thái:",
            background="white"
        ).pack(side="left", padx=5)

        self.filter_combo = ttk.Combobox(
            filter_frame,
            values=[
                "Tất cả",
                "Chưa bắt đầu",
                "Đang thực hiện",
                "Đã hoàn thành",
                "Quá hạn"
            ],
            state="readonly",
            width=20
        )

        self.filter_combo.set("Tất cả")

        self.filter_combo.pack(side="left", padx=5)

        self.filter_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.load_tasks()
        )

        ttk.Button(
            filter_frame,
            text="Làm mới",
            style="Secondary.TButton",
            command=self.load_tasks
        ).pack(side="left", padx=5)

        # Bảng công việc
        table_frame = ttk.Frame(
            list_card,
            style="Card.TFrame"
        )

        table_frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "id",
            "subject",
            "title",
            "due_date",
            "priority",
            "status"
        )

        self.task_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10
        )

        column_config = [
            ("id", "Mã", 45, "center"),
            ("subject", "Môn học", 130, "w"),
            ("title", "Công việc", 220, "w"),
            ("due_date", "Hạn hoàn thành", 120, "center"),
            ("priority", "Ưu tiên", 100, "center"),
            ("status", "Trạng thái", 145, "center")
        ]

        for column_id, title, width, anchor in column_config:
            self.task_table.heading(column_id, text=title, anchor=anchor)
            self.task_table.column(
                column_id,
                width=width,
                minwidth=width,
                anchor=anchor,
                stretch=True
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.task_table.yview
        )

        self.task_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.task_table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.task_table.tag_configure(
            "completed",
            foreground="#0F766E"
        )

        self.task_table.tag_configure(
            "overdue",
            foreground="#DC2626"
        )

        self.task_table.tag_configure(
            "high",
            foreground="#B45309"
        )

        self.task_table.bind(
            "<<TreeviewSelect>>",
            self.select_task
        )

        # Các nút trạng thái
        action_frame = ttk.Frame(
            list_card,
            style="Card.TFrame"
        )

        action_frame.pack(
            anchor="w",
            pady=(12, 0)
        )

        ttk.Button(
            action_frame,
            text="Đang thực hiện",
            style="Secondary.TButton",
            command=lambda: self.change_status("Đang thực hiện")
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            action_frame,
            text="Đánh dấu hoàn thành",
            command=lambda: self.change_status("Đã hoàn thành")
        ).grid(row=0, column=1, padx=4)

        ttk.Button(
            action_frame,
            text="Xóa công việc",
            style="Danger.TButton",
            command=self.delete_task
        ).grid(row=0, column=2, padx=4)

    # =================================
    # CẬP NHẬT MÔN HỌC
    # =================================

    def refresh_subjects(self):

        subjects = self.db.get_subjects()

        self.subject_map = {
            subject[1]: subject[0]
            for subject in subjects
        }

        names = list(self.subject_map.keys())

        self.subject_combo["values"] = names

        if self.subject_combo.get() not in names:
            self.subject_combo.set(
                names[0] if names else ""
            )

    # =================================
    # KIỂM TRA DỮ LIỆU
    # =================================

    def get_form_data(self):

        subject_name = self.subject_combo.get()
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        date_text = self.date_entry.get().strip()
        priority = self.priority_combo.get()

        if not subject_name:
            raise ValueError("Vui lòng chọn môn học!")

        if not title:
            raise ValueError("Vui lòng nhập tên công việc!")

        if len(title) > 150:
            raise ValueError(
                "Tên công việc không được quá 150 ký tự!"
            )

        try:
            due_date = datetime.strptime(
                date_text,
                "%d/%m/%Y"
            ).date()

        except ValueError:
            raise ValueError(
                "Ngày không hợp lệ. Hãy nhập dd/mm/yyyy!"
            )

        return (
            self.subject_map[subject_name],
            title,
            description,
            due_date.isoformat(),
            priority
        )

    # =================================
    # THÊM CÔNG VIỆC
    # =================================

    def add_task(self):

        try:
            data = self.get_form_data()

            self.db.add_task(*data)

            messagebox.showinfo(
                "Thành công",
                "Đã thêm công việc!"
            )

            self.clear_form()
            self.load_tasks()

        except ValueError as error:
            messagebox.showwarning(
                "Thông báo",
                str(error)
            )

    # =================================
    # CHỌN CÔNG VIỆC
    # =================================

    def select_task(self, event=None):

        selection = self.task_table.selection()

        if not selection:
            return

        values = self.task_table.item(
            selection[0],
            "values"
        )

        task_id = int(values[0])

        task = self.db.get_task(task_id)

        if task is None:
            return

        self.selected_task_id = task_id

        subject_id = task[1]
        title = task[2]
        description = task[3]
        due_date = task[4]
        priority = task[5]

        subject_name = next(
            (
                name
                for name, sid in self.subject_map.items()
                if sid == subject_id
            ),
            ""
        )

        self.subject_combo.set(subject_name)

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(
            0,
            description or ""
        )

        display_date = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).strftime("%d/%m/%Y")

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, display_date)

        self.priority_combo.set(priority)

    # =================================
    # CẬP NHẬT CÔNG VIỆC
    # =================================

    def update_selected_task(self):

        if self.selected_task_id is None:
            messagebox.showwarning(
                "Thông báo",
                "Hãy chọn công việc cần cập nhật!"
            )
            return

        try:
            data = self.get_form_data()

            self.db.update_task(
                self.selected_task_id,
                *data
            )

            messagebox.showinfo(
                "Thành công",
                "Đã cập nhật công việc!"
            )

            self.clear_form()
            self.load_tasks()

        except ValueError as error:
            messagebox.showwarning(
                "Thông báo",
                str(error)
            )

    # =================================
    # THAY ĐỔI TRẠNG THÁI
    # =================================

    def change_status(self, status):

        selection = self.task_table.selection()

        if not selection:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng chọn công việc trước!"
            )
            return

        task_id = int(
            self.task_table.item(
                selection[0],
                "values"
            )[0]
        )

        self.db.update_task_status(
            task_id,
            status
        )

        self.clear_form()
        self.load_tasks()

    # =================================
    # XÓA CÔNG VIỆC
    # =================================

    def delete_task(self):

        selection = self.task_table.selection()

        if not selection:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng chọn công việc cần xóa!"
            )
            return

        task_id = int(
            self.task_table.item(
                selection[0],
                "values"
            )[0]
        )

        confirm = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa công việc này?"
        )

        if not confirm:
            return

        self.db.delete_task(task_id)

        self.clear_form()
        self.load_tasks()

        messagebox.showinfo(
            "Thành công",
            "Đã xóa công việc!"
        )

    # =================================
    # LÀM MỚI BIỂU MẪU
    # =================================

    def clear_form(self):

        self.selected_task_id = None

        self.subject_combo.set(
            next(iter(self.subject_map.keys()), "")
        )

        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

        self.date_entry.insert(
            0,
            date.today().strftime("%d/%m/%Y")
        )

        self.priority_combo.set("Trung bình")

        for item in self.task_table.selection():
            self.task_table.selection_remove(item)

    # =================================
    # HIỂN THỊ DANH SÁCH
    # =================================

    def load_tasks(self):

        for item in self.task_table.get_children():
            self.task_table.delete(item)

        status_filter = self.filter_combo.get()

        tasks = self.db.get_tasks(status_filter)

        for task in tasks:

            task_id = task[0]
            subject = task[1]
            title = task[2]
            due_date = task[3]
            priority = task[4]
            status = task[5]

            display_date = datetime.strptime(
                due_date,
                "%Y-%m-%d"
            ).strftime("%d/%m/%Y")

            tag = ""

            if status == "Quá hạn":
                tag = "overdue"

            elif status == "Đã hoàn thành":
                tag = "completed"

            elif priority == "Cao":
                tag = "high"

            self.task_table.insert(
                "",
                tk.END,
                values=(
                    task_id,
                    subject,
                    title,
                    display_date,
                    priority,
                    status
                ),
                tags=(tag,) if tag else ()
            )
