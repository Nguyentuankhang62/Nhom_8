"""Kéo các mục đã chọn từ bảng Server sang bảng tải xuống."""

import os
import tkinter as tk
from tkinter import messagebox, ttk

from tkinterdnd2 import DND_FILES


class DragDropHandler:
    """Quản lý kéo-thả nội bộ và file Explorer vào vùng Download."""

    def __init__(self, main_window):
        """Lưu cửa sổ cha và khởi tạo trạng thái của một phiên kéo."""
        self.main_window = main_window
        self.server_tree = main_window.server_tree
        self.drag_items = ()
        self.press_x = 0
        self.press_y = 0
        self.drag_started = False
        self.drag_window = None
        self.drag_label = None

    def register(self):
        """Đăng ký kéo-thả chuột nội bộ và native drop trên vùng Download.

        TkinterDnD.Tk cung cấp các phương thức drop_target_register/dnd_bind;
        đăng ký cả Treeview lẫn frame để widget con không làm mất drop target.
        """
        self.server_tree.configure(selectmode="extended")
        self.server_tree.bind("<ButtonPress-1>", self._on_press, add="+")
        self.server_tree.bind("<B1-Motion>", self._on_motion, add="+")
        self.main_window.root.bind_all(
            "<ButtonRelease-1>", self._on_release, add="+"
        )
        for widget in (
            self.main_window.download_tree,
            self.main_window.download_table_frame,
            self.main_window.download_scrollbar,
            self.main_window.download_frame,
        ):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<DropEnter>>", self._on_drop_enter)
            widget.dnd_bind("<<DropPosition>>", self._on_drop_position)
            widget.dnd_bind("<<Drop>>", self._on_external_drop)

    @staticmethod
    def _accepted_action(event):
        """Trả action hợp lệ để Explorer biết widget hiện tại nhận thao tác COPY."""
        return getattr(event, "action", None) or "copy"

    def _on_drop_enter(self, event):
        """Báo hệ điều hành rằng vùng Download có thể nhận danh sách file."""
        return self._accepted_action(event)

    def _on_drop_position(self, event):
        """Giữ nguyên action được thương lượng khi con trỏ di chuyển trên vùng nhận."""
        return self._accepted_action(event)

    def _on_external_drop(self, event):
        """Tách đường dẫn Explorer, chỉ nhận file hợp lệ trùng tên với file Server."""
        try:
            # splitlist hiểu đúng các đường dẫn Tcl có khoảng trắng được bọc trong {}.
            file_paths = event.widget.tk.splitlist(event.data)
        except tk.TclError as exc:
            messagebox.showerror(
                "Lỗi kéo thả", f"Không đọc được danh sách đường dẫn: {exc}"
            )
            return "refuse"

        server_files = {}
        for item_id in self.main_window.server_tree.get_children():
            filename = self.main_window.server_tree.item(
                item_id, "values"
            )[0]
            server_files[os.path.normcase(filename)] = filename

        matched_names = []
        rejected_paths = []
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                rejected_paths.append(file_path)
                continue

            filename = os.path.basename(file_path)
            server_filename = server_files.get(os.path.normcase(filename))
            if server_filename is None:
                rejected_paths.append(file_path)
                continue
            matched_names.append(server_filename)

        if matched_names:
            self.main_window.enqueue_server_files(matched_names)
        if rejected_paths:
            preview = "\n".join(rejected_paths[:5])
            if len(rejected_paths) > 5:
                preview += f"\n... và {len(rejected_paths) - 5} tệp khác"
            messagebox.showwarning(
                "Một số tệp không được thêm",
                "Chỉ nhận file có tên khớp danh sách trên Server. "
                "Thư mục hoặc file không khớp đã được bỏ qua:\n\n"
                f"{preview}",
            )
        return self._accepted_action(event)

    def _on_press(self, event):
        """Giữ nguyên vùng chọn nhiều dòng khi bắt đầu kéo từ một dòng đã chọn."""
        self.press_x = event.x_root
        self.press_y = event.y_root
        self.drag_started = False
        row_id = self.server_tree.identify_row(event.y)
        selected_items = self.server_tree.selection()
        if row_id and row_id in selected_items:
            self.drag_items = selected_items
            return "break"
        # Với dòng chưa chọn, để Treeview xử lý click rồi lấy vùng chọn mới khi kéo.
        self.drag_items = ()
        return None

    def _on_motion(self, event):
        """Tạo và cập nhật cửa sổ nổi khi chuột kéo đủ xa khỏi điểm nhấn."""
        if not self.drag_items:
            self.drag_items = self.server_tree.selection()
        if not self.drag_items:
            return

        distance = abs(event.x_root - self.press_x) + abs(
            event.y_root - self.press_y
        )
        if not self.drag_started and distance < 5:
            return

        self.drag_started = True
        self._show_drag_window(event.x_root, event.y_root)
        self.server_tree.configure(cursor="hand2")

    def _show_drag_window(self, x_root, y_root):
        """Hiện nhãn nhỏ bám theo con trỏ để báo số tệp đang kéo."""
        text = f"📥 Kéo {len(self.drag_items)} file sang vùng Download..."
        if self.drag_window is None or not self.drag_window.winfo_exists():
            self.drag_window = tk.Toplevel(self.main_window.root)
            self.drag_window.overrideredirect(True)
            self.drag_label = ttk.Label(
                self.drag_window,
                text=text,
                padding=(10, 6),
                relief="solid",
            )
            self.drag_label.pack()
            try:
                self.drag_window.attributes("-alpha", 0.85)
            except tk.TclError:
                pass
        else:
            self.drag_label.configure(text=text)

        self.drag_window.geometry(f"+{x_root + 14}+{y_root + 14}")

    def _on_release(self, event):
        """Chỉ chuyển tệp vào hàng đợi khi thả trong vùng Download."""
        try:
            if not self.drag_started:
                return

            target = self.main_window.root.winfo_containing(
                event.x_root, event.y_root
            )
            if self._is_download_target(target):
                filenames = [
                    self.server_tree.item(item_id, "values")[0]
                    for item_id in self.drag_items
                    if self.server_tree.exists(item_id)
                ]
                if filenames:
                    self.main_window.enqueue_server_files(filenames)
        finally:
            self._finish_drag()

    def _is_download_target(self, widget):
        """Nhận diện bảng Download và mọi widget con nằm trong khung của nó."""
        target_widgets = {
            self.main_window.download_tree,
            self.main_window.download_table_frame,
            self.main_window.download_scrollbar,
            self.main_window.download_frame,
        }
        while widget is not None:
            if widget in target_widgets:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _finish_drag(self):
        """Đóng cửa sổ kéo và dọn trạng thái để lần kéo sau hoạt động độc lập."""
        self.server_tree.configure(cursor="")
        if self.drag_window is not None and self.drag_window.winfo_exists():
            self.drag_window.destroy()
        self.drag_window = None
        self.drag_label = None
        self.drag_items = ()
        self.drag_started = False
