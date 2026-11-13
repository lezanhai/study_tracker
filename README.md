#  STUDY TRACKER

**Ứng dụng theo dõi và quản lý thời gian học tập được xây dựng bằng Python, Tkinter và SQLite.**

Study Tracker là ứng dụng desktop hỗ trợ người dùng quản lý quá trình học tập, theo dõi thời gian học, thiết lập mục tiêu và nâng cao hiệu quả tự học thông qua giao diện trực quan, dễ sử dụng.

---

##  1. Giới thiệu

Study Tracker được phát triển nhằm hỗ trợ người học tổ chức và quản lý hoạt động học tập một cách khoa học.

Ứng dụng sử dụng Python với thư viện Tkinter để xây dựng giao diện đồ họa và SQLite để lưu trữ dữ liệu cục bộ. Dự án áp dụng lập trình hướng đối tượng (OOP), đồng thời tổ chức mã nguồn thành các module riêng biệt để thuận tiện cho việc phát triển và bảo trì.

## 2. Các chức năng chính

Ứng dụng bao gồm 6 khu vực chức năng:

  - Quản lý môn học: Thêm, xem và quản lý danh sách môn học. 
  - Theo dõi phiên học: Ghi nhận thời gian học, ngày học và ghi chú cho từng phiên. 
  - Pomodoro: Hỗ trợ học tập theo phương pháp Pomodoro với bộ đếm thời gian. 
  - Thống kê học tập: Tổng hợp và theo dõi thời gian học tập. 
  - Mục tiêu học tập: Thiết lập và theo dõi mục tiêu thời gian học. 
  - Quản lý công việc: Theo dõi bài tập, nhiệm vụ và thời hạn hoàn thành. 

## 3. Công nghệ sử dụng

- **Ngôn ngữ:** Python
- **Giao diện đồ họa:** Tkinter
- **Cơ sở dữ liệu:** SQLite
- **Lập trình:** Object-Oriented Programming (OOP)
- **Quản lý mã nguồn:** Git và GitHub
- **Môi trường phát triển:** Visual Studio Code

## 4. Cấu trúc dự án

```text
Study-Tracker/
│
├── main.py
│
├── database.py
│
├── subject_tab.py
├── session_tab.py
├── pomodoro_tab.py
├── statistics_tab.py
├── goal_tab.py
├── task_tab.py
│
├── study_tracker.db
│
├── README.md
└── .gitignore
```

> Lưu ý: Tên các file trong sơ đồ trên là cấu trúc minh họa. Hãy điều chỉnh lại theo đúng tên file thực tế trong dự án.

## 5. Cài đặt và chạy chương trình

### Yêu cầu hệ thống

- Windows 10 trở lên.
- Python 3.x.
- Visual Studio Code (khuyến nghị).

### Bước 1: Clone repository

```bash
git clone https://github.com/lezanhai/Study-Tracker.git
```

### Bước 2: Mở thư mục dự án

```bash
cd Study-Tracker
```

### Bước 3: Chạy chương trình

```bash
python main.py
```

Ứng dụng sẽ khởi chạy với giao diện desktop.

## 💾 6. Cơ sở dữ liệu

Study Tracker sử dụng SQLite để lưu trữ dữ liệu trực tiếp trên máy tính.

Cơ sở dữ liệu được tổ chức thành các bảng phục vụ việc quản lý môn học, phiên học, mục tiêu học tập và công việc.

File cơ sở dữ liệu chính:

```text
study_tracker.db
```

## 7. Định hướng phát triển

Một số hướng phát triển trong tương lai:

- Hoàn thiện và mở rộng hệ thống thống kê học tập.
- Cải thiện trải nghiệm giao diện người dùng.
- Bổ sung các tính năng hỗ trợ quản lý học tập.
- Tối ưu hóa việc lưu trữ và truy xuất dữ liệu.
- Nâng cao khả năng sao lưu và khôi phục dữ liệu.

## 8. Tác giả

**Tên dự án:** Study Tracker  
**Loại dự án:** Ứng dụng desktop cá nhân  
**Lĩnh vực:** Quản lý và hỗ trợ học tập  
**Ngôn ngữ lập trình:** Python

---

*Study Tracker – Plan your study, track your progress, improve every day.*
