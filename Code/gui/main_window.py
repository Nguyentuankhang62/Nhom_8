"""Giao diện Tkinter cho ứng dụng tải nhiều tệp từ TCP Server."""

from __future__ import annotations

import queue
import socket
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import TkinterDnD

from Code.gui.drag_drop_handler import DragDropHandler
from Code.gui.queue_manager import DownloadQueueManager, DownloadTask


class MainWindow:
    """Tạo giao diện, điều phối TCP worker và cập nhật Tkinter an toàn luồng."""

    def __init__(self, root):
        """Khởi tạo trạng thái, hàng đợi cập nhật và các widget của cửa sổ."""
        self.root = root
        self.root.title("UDM_11 - Download nhiều file")
        self.root.geometry("1100x720")
        self.root.minsize(850, 560)
        self.connected = False
        self._closing = False
        self._ui_events = queue.Queue()
        self._file_sizes = {}
        self._destination_names = set()

        self.create_widgets()
        self.queue_manager = DownloadQueueManager(
            self.update_download_item, max_concurrent=2
        )
        self.drag_drop_handler = DragDropHandler(self)
        self.drag_drop_handler.register()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(100, self._process_ui_events)

    def create_widgets(self):
        """Dựng các vùng kết nối, danh sách Server, hàng đợi và cấu hình tải."""
        ttk.Label(
            self.root,
            text="ỨNG DỤNG DOWNLOAD NHIỀU FILE",
            font=("Arial", 18, "bold"),
        ).pack(pady=(12, 4))

        connection_frame = ttk.LabelFrame(
            self.root, text="Kết nối Server", padding=8
        )
        connection_frame.pack(fill="x", padx=12, pady=5)

        ttk.Label(connection_frame, text="IP:").grid(row=0, column=0, padx=4)
        self.ip_entry = ttk.Entry(connection_frame, width=20)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1, padx=4)
        ttk.Label(connection_frame, text="Port:").grid(row=0, column=2, padx=4)
        self.port_entry = ttk.Entry(connection_frame, width=8)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=0, column=3, padx=4)

        self.connect_button = ttk.Button(
            connection_frame, text="Kết nối", command=self.connect_server
        )
        self.connect_button.grid(row=0, column=4, padx=4)
        self.refresh_button = ttk.Button(
            connection_frame,
            text="Làm mới danh sách",
            command=self.refresh_server_files,
            state="disabled",
        )
        self.refresh_button.grid(row=0, column=5, padx=4)
        self.status_label = ttk.Label(
            connection_frame,
            text="Trạng thái: Chưa kết nối",
            foreground="#a11",
        )
        self.status_label.grid(
            row=0, column=6, padx=10, sticky="w"
        )
        connection_frame.columnconfigure(6, weight=1)

        settings_frame = ttk.LabelFrame(
            self.root, text="Cấu hình tải xuống", padding=8
        )
        settings_frame.pack(fill="x", padx=12, pady=5)
        ttk.Label(
            settings_frame, text="Giới hạn tải cùng lúc:"
        ).pack(side="left", padx=(0, 4))
        self.concurrency_var = tk.IntVar(value=2)
        self.concurrency_spinbox = ttk.Spinbox(
            settings_frame,
            from_=1,
            to=DownloadQueueManager.MAX_WORKERS,
            width=4,
            textvariable=self.concurrency_var,
            command=self._set_concurrency,
        )
        self.concurrency_spinbox.pack(side="left")
        self.concurrency_spinbox.bind(
            "<FocusOut>", lambda _event: self._set_concurrency()
        )
        self.concurrency_spinbox.bind(
            "<Return>", lambda _event: self._set_concurrency()
        )
        ttk.Label(settings_frame, text="file").pack(side="left", padx=(3, 16))

        ttk.Label(settings_frame, text="Nếu tệp đích đã tồn tại:").pack(
            side="left", padx=(0, 4)
        )
        self.conflict_var = tk.StringVar(value="Hỏi xác nhận (Ask)")
        self.conflict_combobox = ttk.Combobox(
            settings_frame,
            textvariable=self.conflict_var,
            state="readonly",
            width=25,
            values=(
                "Hỏi xác nhận (Ask)",
                "Tự động đổi tên (Auto-rename)",
                "Ghi đè (Overwrite)",
                "Bỏ qua (Skip)",
            ),
        )
        self.conflict_combobox.pack(side="left", padx=4)

        destination_frame = ttk.Frame(settings_frame)
        destination_frame.pack(side="left", fill="x", expand=True, padx=(14, 0))
        ttk.Label(destination_frame, text="Thư mục lưu:").pack(side="left")
        self.destination_var = tk.StringVar(
            value=str(Path.home() / "Downloads")
        )
        self.destination_entry = ttk.Entry(
            destination_frame, textvariable=self.destination_var
        )
        self.destination_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(
            destination_frame, text="Chọn...", command=self._choose_destination
        ).pack(side="left")

        self.server_frame = ttk.LabelFrame(
            self.root,
            text="Khu vực 1 - Danh sách file trên Server (kéo thả để tải)",
            padding=8,
        )
        self.server_frame.pack(fill="both", expand=True, padx=12, pady=5)
        self.server_table_frame = ttk.Frame(self.server_frame)
        self.server_table_frame.pack(fill="both", expand=True)
        self.server_tree = ttk.Treeview(
            self.server_table_frame,
            columns=("filename", "size"),
            show="headings",
            selectmode="extended",
            height=7,
        )
        self.server_tree.heading("filename", text="Tên file")
        self.server_tree.heading("size", text="Kích thước")
        self.server_tree.column("filename", width=650, anchor="w")
        self.server_tree.column("size", width=150, anchor="center")
        self._add_tree_scrollbars(self.server_table_frame, self.server_tree)
        ttk.Button(
            self.server_frame,
            text="Thêm file đã chọn vào Download",
            command=self._add_selected_files,
        ).pack(anchor="e", pady=(6, 0))

        self.download_frame = ttk.LabelFrame(
            self.root, text="Khu vực 2 - Danh sách file cần download", padding=8
        )
        self.download_frame.pack(fill="both", expand=True, padx=12, pady=5)
        self.download_table_frame = ttk.Frame(self.download_frame)
        self.download_table_frame.pack(fill="both", expand=True)
        columns = ("filename", "size", "progress", "speed", "eta", "status")
        self.download_tree = ttk.Treeview(
            self.download_table_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
            height=8,
        )
        headings = {
            "filename": ("Tên file", 330, "w"),
            "size": ("Kích thước", 100, "center"),
            "progress": ("Tiến trình", 90, "center"),
            "speed": ("Tốc độ", 110, "center"),
            "eta": ("ETA", 110, "center"),
            "status": ("Trạng thái", 150, "center"),
        }
        for column, (heading, width, anchor) in headings.items():
            self.download_tree.heading(column, text=heading)
            self.download_tree.column(column, width=width, anchor=anchor)
        self.download_tree.tag_configure("waiting", foreground="#805600")
        self.download_tree.tag_configure("processing", foreground="#145a9e")
        self.download_tree.tag_configure("success", foreground="#18743a")
        self.download_tree.tag_configure("failure", foreground="#b00020")
        self.download_scrollbar = self._add_tree_scrollbars(
            self.download_table_frame, self.download_tree
        )

    @staticmethod
    def _add_tree_scrollbars(parent, tree):
        """Đặt Treeview và scrollbar trong đúng parent để widget được vẽ ổn định."""
        scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tree.configure(yscrollcommand=scrollbar.set)
        return scrollbar

    def connect_server(self):
        """Kiểm tra địa chỉ nhập vào rồi tải danh sách file ở một luồng nền."""
        address = self._server_address()
        if address is None:
            return
        self.connect_button.configure(state="disabled")
        self._start_list_request(*address)

    def refresh_server_files(self):
        """Yêu cầu danh sách mới mà không chặn vòng lặp sự kiện Tkinter."""
        address = self._server_address()
        if address is None:
            return
        self.refresh_button.configure(state="disabled")
        self._start_list_request(*address)

    def _server_address(self):
        """Đọc và xác thực IP/Port; lỗi nhập liệu được báo ngay trên giao diện."""
        host = self.ip_entry.get().strip()
        raw_port = self.port_entry.get().strip()
        if not host or not raw_port:
            messagebox.showwarning("Thông báo", "Vui lòng nhập IP và Port!")
            return None
        try:
            port = int(raw_port)
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Port phải là số từ 1 đến 65535!")
            return None
        return host, port

    def _start_list_request(self, host, port):
        """Mở TCP kết nối và gửi LIST_FILES trong worker, không gọi Tk từ worker."""
        threading.Thread(
            target=self._request_server_files,
            args=(host, port),
            name="server-file-list",
            daemon=True,
        ).start()

    def _request_server_files(self, host, port):
        """Đọc phản hồi FILE_LIST theo giao thức hiện tại của TCPServer."""
        try:
            with socket.create_connection((host, port), timeout=5) as client:
                client.settimeout(10)
                client.sendall(b"LIST_FILES\n")
                client.shutdown(socket.SHUT_WR)
                response = bytearray()
                while True:
                    chunk = client.recv(4096)
                    if not chunk:
                        break
                    response.extend(chunk)
            lines = response.decode("utf-8", errors="replace").splitlines()
            if not lines or not lines[0].startswith("FILE_LIST||"):
                raise OSError("Phản hồi danh sách file từ Server không hợp lệ.")
            count = int(lines[0].split("||", 1)[1])
            filenames = lines[1 : count + 1]
            self.update_connection_status("Đã kết nối", f"{host}:{port}")
            self.populate_server_files(filenames)
        except (OSError, ValueError, UnicodeError) as exc:
            self.update_connection_status("Lỗi kết nối", str(exc))

    def update_connection_status(self, status, details=""):
        """Gửi trạng thái kết nối vào hàng đợi để chỉ luồng giao diện sửa widget."""
        self._ui_events.put(("connection", status, details))

    def populate_server_files(self, file_list):
        """Chuyển danh sách Server từ bất kỳ luồng nào sang hàng đợi cập nhật GUI."""
        self._ui_events.put(("server_files", list(file_list)))

    def update_download_item(
        self,
        filename,
        progress_pct,
        speed_str,
        eta_str,
        status_str,
        size_str=None,
    ):
        """Đưa tiến trình một tệp vào hàng đợi thread-safe, không chạm trực tiếp Tk."""
        self._ui_events.put(
            (
                "download_update",
                filename,
                progress_pct,
                speed_str,
                eta_str,
                status_str,
                size_str,
            )
        )

    def _process_ui_events(self):
        """Rút các sự kiện từ worker và cập nhật widget trên luồng Tk chính."""
        if self._closing:
            return
        # Giới hạn số sự kiện mỗi lượt để tiến trình tải dồn dập không chiếm UI.
        for _ in range(250):
            try:
                event = self._ui_events.get_nowait()
            except queue.Empty:
                break

            event_type = event[0]
            if event_type == "connection":
                self._apply_connection_status(event[1], event[2])
            elif event_type == "server_files":
                self._apply_server_files(event[1])
            elif event_type == "download_update":
                self._apply_download_update(*event[1:])

        self.root.after(100, self._process_ui_events)

    def _apply_connection_status(self, status, details):
        """Hiển thị một trong ba trạng thái kết nối bắt buộc và điều chỉnh nút."""
        if status == "Đã kết nối":
            self.connected = True
            color = "#18743a"
            self.connect_button.configure(state="normal")
            self.refresh_button.configure(state="normal")
        elif status == "Lỗi kết nối":
            self.connected = False
            color = "#b00020"
            self.connect_button.configure(state="normal")
            self.refresh_button.configure(state="disabled")
        else:
            self.connected = False
            color = "#a11"
            self.connect_button.configure(state="normal")
            self.refresh_button.configure(state="disabled")
        suffix = f" - {details}" if details else ""
        self.status_label.configure(
            text=f"Trạng thái: {status}{suffix}", foreground=color
        )

    def _apply_server_files(self, file_list):
        """Hiển thị tên và kích thước có sẵn; kích thước chưa được server công bố ghi rõ."""
        self.server_tree.delete(*self.server_tree.get_children())
        self._file_sizes.clear()
        for item in file_list:
            if isinstance(item, dict):
                filename = str(item["filename"])
                size = item.get("size")
            elif isinstance(item, (tuple, list)):
                filename = str(item[0])
                size = item[1] if len(item) > 1 else None
            else:
                filename = str(item)
                size = None
            size_text = self._format_size(size)
            self._file_sizes[filename] = size_text
            self.server_tree.insert(
                "", "end", iid=filename, values=(filename, size_text)
            )

    def enqueue_server_files(self, filenames):
        """Kiểm tra quy tắc trùng tên, tạo từng dòng và đẩy tác vụ vào QueueManager."""
        if not self.connected:
            messagebox.showwarning(
                "Thông báo", "Vui lòng kết nối Server trước khi tải!"
            )
            return
        destination = Path(self.destination_var.get()).expanduser()
        if not destination.is_dir():
            messagebox.showerror(
                "Lỗi", "Thư mục lưu không tồn tại. Vui lòng chọn thư mục hợp lệ."
            )
            return

        for filename in filenames:
            target = self._resolve_destination(filename, destination)
            if target is None:
                continue
            self._destination_names.add(self._destination_key(target))
            self.download_tree.insert(
                "",
                "end",
                iid=filename,
                values=(
                    filename,
                    self._file_sizes.get(filename, "Chờ Server gửi"),
                    "0%",
                    "—",
                    "—",
                    "Đang chờ",
                ),
                tags=("waiting",),
            )
            try:
                self.queue_manager.add_task(
                    DownloadTask(
                        filename=filename,
                        destination=target,
                        host=self.ip_entry.get().strip(),
                        port=int(self.port_entry.get().strip()),
                    )
                )
            except RuntimeError as exc:
                self._apply_download_update(
                    filename, 0, "—", "—", f"Thất bại: {exc}", None
                )

    def _resolve_destination(self, filename, directory):
        """Áp dụng Ask, Auto-rename, Overwrite hoặc Skip trước khi tạo tác vụ."""
        if self.download_tree.exists(filename):
            return None

        target = directory / filename
        conflict = (
            target.exists()
            or self._destination_key(target) in self._destination_names
        )
        if not conflict:
            return target

        policy = self.conflict_var.get()
        if policy == "Bỏ qua (Skip)":
            return None
        if policy == "Tự động đổi tên (Auto-rename)":
            return self._auto_rename(target)
        if policy == "Ghi đè (Overwrite)":
            return target
        if messagebox.askyesno(
            "Tệp đã tồn tại",
            f"{target.name} đã tồn tại. Bạn có muốn ghi đè không?",
        ):
            return target
        return None

    def _auto_rename(self, target):
        """Tìm tên chưa tồn tại cả trên đĩa lẫn trong các tác vụ đang chờ."""
        stem, suffix = target.stem, target.suffix
        number = 1
        while True:
            candidate = target.with_name(f"{stem} ({number}){suffix}")
            if (
                not candidate.exists()
                and self._destination_key(candidate) not in self._destination_names
            ):
                return candidate
            number += 1

    @staticmethod
    def _destination_key(path):
        """Chuẩn hóa đường dẫn đích để nhận diện đúng tệp đã được giữ chỗ."""
        return str(path.resolve()).casefold()

    def _add_selected_files(self):
        """Đưa các dòng đang chọn trên Server vào tải bằng cùng quy tắc với kéo-thả."""
        filenames = [
            self.server_tree.item(item_id, "values")[0]
            for item_id in self.server_tree.selection()
        ]
        if not filenames:
            messagebox.showwarning("Thông báo", "Vui lòng chọn file cần tải!")
            return
        self.enqueue_server_files(filenames)

    def _apply_download_update(
        self, filename, progress_pct, speed_str, eta_str, status_str, size_str
    ):
        """Cập nhật riêng dòng được báo, tô màu theo trạng thái và giữ GUI hoạt động."""
        if not self.download_tree.exists(filename):
            return
        values = list(self.download_tree.item(filename, "values"))
        values[2] = f"{max(0.0, min(100.0, float(progress_pct))):.1f}%"
        values[3] = speed_str
        values[4] = eta_str
        values[5] = status_str
        if size_str:
            values[1] = size_str
        status_lower = status_str.casefold()
        if status_lower.startswith("thất bại"):
            tag = "failure"
        elif status_str == "Thành công":
            tag = "success"
        elif status_str == "Đang xử lý":
            tag = "processing"
        else:
            tag = "waiting"
        self.download_tree.item(filename, values=values, tags=(tag,))

    def _set_concurrency(self):
        """Xác thực giá trị Spinbox rồi áp dụng giới hạn mới cho hàng đợi."""
        try:
            value = int(self.concurrency_var.get())
            self.queue_manager.set_max_concurrent(value)
        except (ValueError, tk.TclError):
            self.concurrency_var.set(self.queue_manager.max_concurrent)
            messagebox.showerror(
                "Lỗi",
                f"Giới hạn tải phải là số từ 1 đến "
                f"{DownloadQueueManager.MAX_WORKERS}.",
            )

    def _choose_destination(self):
        """Cho người dùng chọn thư mục lưu tệp bằng hộp thoại hệ điều hành."""
        selected = filedialog.askdirectory(
            initialdir=self.destination_var.get() or str(Path.home())
        )
        if selected:
            self.destination_var.set(selected)

    @staticmethod
    def _format_size(size):
        """Định dạng kích thước byte; trả về trạng thái rõ ràng nếu chưa biết."""
        if size is None:
            return "Chưa biết"
        try:
            remaining = float(size)
        except (TypeError, ValueError):
            return str(size)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if remaining < 1024 or unit == "TB":
                return f"{remaining:.1f} {unit}"
            remaining /= 1024
        return f"{remaining:.1f} TB"

    def _on_close(self):
        """Yêu cầu các worker dừng chờ rồi đóng cửa sổ, không chờ tải trên UI."""
        self._closing = True
        self.queue_manager.shutdown()
        self.root.destroy()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    MainWindow(root)
    root.mainloop()
