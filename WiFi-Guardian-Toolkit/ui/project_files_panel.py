"""ProjectFilesPanel UI mixin."""

import os
import tkinter as tk
from tkinter import ttk

from .theme import CYAN, PANEL_BG


class ProjectFilesPanelMixin:
    def open_project_files_window(self):
        if self.project_files_window and self.project_files_window.winfo_exists():
            self.project_files_window.lift()
            self._position_project_files_window()
            return

        win = tk.Toplevel(self.root)
        win.title("WiFi-Guardian-Toolkit Files")
        win.configure(bg=PANEL_BG)
        win.transient(self.root)
        self.project_files_window = win

        panel = self._create_project_files_panel(win)
        panel.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._position_project_files_window()

        def on_close():
            self.project_files_window = None
            self.project_files_tree = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

    def _position_project_files_window(self):
        if not self.project_files_window or not self.project_files_window.winfo_exists():
            return

        self.root.update_idletasks()
        width = 360
        height = max(self.root.winfo_height(), 540)
        x = self.root.winfo_rootx() + self.root.winfo_width() + 8
        y = self.root.winfo_rooty()
        self.project_files_window.geometry(f"{width}x{height}+{x}+{y}")

    def _create_project_files_panel(self, parent):
        panel = tk.Frame(parent, bg=PANEL_BG, bd=1, relief=tk.SOLID)

        tk.Label(
            panel,
            text="Project Files",
            fg=CYAN,
            bg=PANEL_BG,
            font=("Consolas", 12, "bold"),
            anchor="w",
        ).pack(fill=tk.X, padx=10, pady=(10, 6))

        tree_frame = tk.Frame(panel, bg=PANEL_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.project_files_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.project_files_tree.yview)
        self.project_files_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.project_files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder_name = os.path.basename(project_dir)
        root_item = self.project_files_tree.insert("", "end", text=folder_name, open=True)
        self._populate_project_files_tree(root_item, project_dir)

        return panel


    def _populate_project_files_tree(self, parent_item, folder_path):
        excluded_dirs = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}

        try:
            entries = sorted(
                os.scandir(folder_path),
                key=lambda item: (not item.is_dir(), item.name.lower()),
            )
        except OSError:
            return

        for entry in entries:
            if entry.name in excluded_dirs:
                continue

            node = self.project_files_tree.insert(parent_item, "end", text=entry.name, open=False)
            if entry.is_dir():
                self._populate_project_files_tree(node, entry.path)

