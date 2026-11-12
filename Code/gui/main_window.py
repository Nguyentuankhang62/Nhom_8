
import tkinter as tk
from tkinter import ttk, messagebox


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("UDM_11 - Download nhiều file")
        self.root.geometry("950x750")
        self.root.minsize(800, 550)

        self.connected = False
        self.is_downloading = False
        self.download_progress = 0
        self.current_file = None

        self.create_widgets()

    def create_widgets(self):
        # Tiêu đề
        title = ttk.Label(
            self.root,
            text="ỨNG DỤNG DOWNLOAD NHIỀU FILE",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=15)

        # Khu vực kết nối Server
        connection_frame = ttk.LabelFrame(
            self.root,
            text="Kết nối Server",
            padding=10
        )
        connection_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(connection_frame, text="Địa chỉ IP:").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.ip_entry = ttk.Entry(connection_frame, width=25)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1, padx=5)

        ttk.Label(connection_frame, text="Port:").grid(
            row=0, column=2, padx=5
        )

        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=0, column=3, padx=5)

        self.connect_button = ttk.Button(
            connection_frame,
            text="Kết nối",
            command=self.connect_server
        )
        self.connect_button.grid(row=0, column=4, padx=10)

        self.disconnect_button = ttk.Button(
            connection_frame,
            text="Ngắt kết nối",
            command=self.disconnect_server,
            state="disabled"
        )
        self.disconnect_button.grid(row=0, column=5, padx=5)

        # Trạng thái kết nối
        self.status_label = ttk.Label(
            connection_frame,
            text="Trạng thái: Chưa kết nối",
            foreground="red"
        )
        self.status_label.grid(
            row=1, column=0, columnspan=6, sticky="w", padx=5, pady=5
        )

        # Danh sách file trên Server
        server_frame = ttk.LabelFrame(
            self.root,
            text="Danh sách file trên Server",
            padding=10
        )
        server_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("filename", "size", "status")

        self.file_tree = ttk.Treeview(
            server_frame,
            columns=columns,
            show="headings",
            height=6
        )

        self.file_tree.heading("filename", text="Tên file")
        self.file_tree.heading("size", text="Dung lượng")
        self.file_tree.heading("status", text="Trạng thái")

        self.file_tree.column("filename", width=400)
        self.file_tree.column("size", width=150, anchor="center")
        self.file_tree.column("status", width=150, anchor="center")

        self.file_tree.pack(fill="both", expand=True)

        # Nút thêm file vào hàng chờ
        ttk.Button(
            server_frame,
            text="Thêm vào hàng chờ",
            command=self.add_to_queue
        ).pack(pady=8, anchor="e")

        # Danh sách chờ tải xuống
        queue_frame = ttk.LabelFrame(
            self.root,
            text="Danh sách chờ tải xuống",
            padding=10
        )
        queue_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.queue_listbox = tk.Listbox(
            queue_frame,
            height=4,
            font=("Arial", 10)
        )
        #Hiển thị danh sách hàng chờ
        self.queue_listbox.pack(fill="both", expand=True)
        #Các nút chức năng
        queue_button_frame = ttk.Frame(queue_frame)
        queue_button_frame.pack(fill="x", pady=8)

        ttk.Button(
            queue_button_frame,
            text="Bắt đầu tải",
            command=self.start_download
        ).pack(side="left", padx=5)

        ttk.Button(
            queue_button_frame,
            text="Xóa khỏi hàng chờ",
            command=self.remove_from_queue
        ).pack(side="left", padx=5)

        # Tiến trình tải file
        progress_frame = ttk.LabelFrame(
            self.root,
            text="Tiến trình tải xuống",
            padding=10
        )
        progress_frame.pack(fill="x", padx=15, pady=10)

        self.progress = ttk.Progressbar(
            progress_frame,
            length=500,
            mode="determinate"
        )
        self.progress.pack(fill="x", pady=5)

        self.progress_label = ttk.Label(
            progress_frame,
            text="Chưa có file đang tải"
        )
        self.progress_label.pack(anchor="w")
        self.download_button = ttk.Button(
            progress_frame,
            text="",
            state="disabled"
        )

    def connect_server(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()

        if not ip or not port:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng nhập IP và Port!"
            )
            return

        try:
            port_number = int(port)

            if not 1 <= port_number <= 65535:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Lỗi",
                "Port phải là số từ 1 đến 65535!"
            )
            return

        # Tạm thời mô phỏng kết nối để kiểm tra giao diện
        self.connected = True

        self.status_label.config(
            text=f"Trạng thái: Đã kết nối (mô phỏng) - {ip}:{port_number}",
            foreground="green"
        )

        self.connect_button.config(state="disabled")
        self.disconnect_button.config(state="normal")

        # Dữ liệu mẫu để kiểm tra bảng
        self.file_tree.delete(*self.file_tree.get_children())

        sample_files = [
            ("tai_lieu.pdf", "2.5 MB", "Sẵn sàng"),
            ("hinh_anh.png", "1.2 MB", "Sẵn sàng"),
            ("video.mp4", "15 MB", "Sẵn sàng"),
        ]

        for file_info in sample_files:
            self.file_tree.insert("", "end", values=file_info)

    def disconnect_server(self):
        self.connected = False

        self.status_label.config(
            text="Trạng thái: Chưa kết nối",
            foreground="red"
        )

        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")

    def add_to_queue(self):
        selected_items = self.file_tree.selection()

        if not selected_items:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng chọn file cần thêm!"
            )
            return

        for item in selected_items:
            file_info = self.file_tree.item(item, "values")
            filename = file_info[0]

            current_items = self.queue_listbox.get(0, tk.END)

            if filename not in current_items:
                self.queue_listbox.insert(tk.END, filename)

#
    def remove_from_queue(self):
        selected = self.queue_listbox.curselection()

        if not selected:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng chọn file cần xóa!"
            )
            return

        if self.is_downloading and 0 in selected:
            messagebox.showwarning(
                "Thông báo",
                "Không thể xóa file đang được xử lý!"
            )
            return

        for index in reversed(selected):
            self.queue_listbox.delete(index)

    def start_download(self):
        if not self.connected:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng kết nối Server trước!"
            )
            return

        if self.is_downloading:
            messagebox.showinfo(
                "Thông báo",
                "Đang có file được xử lý!"
            )
            return

        if self.queue_listbox.size() == 0:
            messagebox.showwarning(
                "Thông báo",
                "Hàng chờ chưa có file!"
            )
            return

        self.current_file = self.queue_listbox.get(0)
        self.download_progress = 0
        self.is_downloading = True

        self.progress["value"] = 0
        self.progress_label.config(
            text=f"Đang tải: {self.current_file} - 0%"
        )

        self.update_progress()

    def update_progress(self):
        if not self.is_downloading:
            return

        self.download_progress += 5

        self.progress["value"] = self.download_progress

        self.progress_label.config(
            text=(
                f"Đang tải: {self.current_file} "
                f"- {self.download_progress}%"
            )
        )

        if self.download_progress >= 100:
            self.finish_download()
        else:
            self.root.after(200, self.update_progress)

    def finish_download(self):
        finished_file = self.current_file
        if (
            self.queue_listbox.size() > 0
            and self.queue_listbox.get(0) == finished_file
        ):
            self.queue_listbox.delete(0)

        self.progress["value"] = 100
        self.progress_label.config(
            text=f"Hoàn thành: {finished_file}"
        )

        self.is_downloading = False
        self.current_file = None

        if self.queue_listbox.size() > 0:
            self.root.after(500, self.start_next_download)

    def start_next_download(self):
        if not self.is_downloading and self.queue_listbox.size() > 0:
            self.current_file = self.queue_listbox.get(0)
            self.download_progress = 0
            self.is_downloading = True

            self.progress["value"] = 0
            self.progress_label.config(
                text=f"Đang tải: {self.current_file} - 0%"
            )

            self.update_progress()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
