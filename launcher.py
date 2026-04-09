#!/usr/bin/env python3
"""
Second Brain T — GUI Launcher
Double-click this file to open the launcher window.
No terminal needed.
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import threading
import sys
import os
from pathlib import Path

SCRIPT = Path(__file__).parent / 'build.py'
BG = '#0d1117'
FG = '#e6edf3'
ACCENT = '#388bfd'
CARD = '#161b22'
BORDER = '#30363d'
MUTED = '#8b949e'
GREEN = '#3fb950'
RED = '#f85149'


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Second Brain T')
        self.configure(bg=BG)
        self.resizable(False, False)
        self.geometry('540x480')
        self._center()
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        w, h = 540, 480
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG, pady=24)
        hdr.pack(fill='x')
        tk.Label(hdr, text='🧠', font=('System', 32), bg=BG, fg=FG).pack()
        tk.Label(hdr, text='Second Brain T', font=('Helvetica Neue', 18, 'bold'),
                 bg=BG, fg=FG).pack()
        tk.Label(hdr, text='Turn any folder into a knowledge base',
                 font=('Helvetica Neue', 11), bg=BG, fg=MUTED).pack(pady=(4, 0))

        # Folder picker
        folder_frame = tk.Frame(self, bg=CARD, bd=0, padx=16, pady=14)
        folder_frame.pack(fill='x', padx=24, pady=(0, 12))
        tk.Label(folder_frame, text='Folder', font=('Helvetica Neue', 11, 'bold'),
                 bg=CARD, fg=FG).pack(anchor='w')

        pick_row = tk.Frame(folder_frame, bg=CARD)
        pick_row.pack(fill='x', pady=(6, 0))

        self.folder_var = tk.StringVar(value='No folder selected')
        self.folder_label = tk.Label(pick_row, textvariable=self.folder_var,
                                      font=('Helvetica Neue', 11), bg=CARD, fg=MUTED,
                                      anchor='w', width=38, cursor='hand2')
        self.folder_label.pack(side='left')

        tk.Button(pick_row, text='Browse', font=('Helvetica Neue', 11),
                  bg=ACCENT, fg='white', relief='flat', padx=12, pady=4,
                  cursor='hand2', command=self._pick_folder).pack(side='right')

        # Options
        opts_frame = tk.Frame(self, bg=CARD, padx=16, pady=14)
        opts_frame.pack(fill='x', padx=24, pady=(0, 12))
        tk.Label(opts_frame, text='Options', font=('Helvetica Neue', 11, 'bold'),
                 bg=CARD, fg=FG).pack(anchor='w', pady=(0, 8))

        row1 = tk.Frame(opts_frame, bg=CARD)
        row1.pack(fill='x')
        tk.Label(row1, text='Title (optional)', font=('Helvetica Neue', 11),
                 bg=CARD, fg=MUTED, width=18, anchor='w').pack(side='left')
        self.title_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.title_var, font=('Helvetica Neue', 11),
                 bg='#21262d', fg=FG, insertbackground=FG, relief='flat',
                 highlightthickness=1, highlightbackground=BORDER, width=24).pack(side='left', padx=(8, 0))

        row2 = tk.Frame(opts_frame, bg=CARD)
        row2.pack(fill='x', pady=(8, 0))
        self.cache_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row2, text='Use cache (faster for repeated runs)',
                       variable=self.cache_var, font=('Helvetica Neue', 11),
                       bg=CARD, fg=FG, selectcolor=CARD, activebackground=CARD,
                       activeforeground=FG).pack(anchor='w')

        # Log output
        log_frame = tk.Frame(self, bg=CARD, padx=16, pady=10)
        log_frame.pack(fill='both', expand=True, padx=24, pady=(0, 12))
        self.log = tk.Text(log_frame, height=6, font=('Menlo', 10),
                           bg='#010409', fg=FG, relief='flat', wrap='word',
                           state='disabled', pady=4)
        self.log.pack(fill='both', expand=True)
        self.log.tag_config('ok', foreground=GREEN)
        self.log.tag_config('err', foreground=RED)
        self.log.tag_config('info', foreground=ACCENT)

        # Run button
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=(0, 20))
        self.run_btn = tk.Button(btn_row, text='▶  Run Second Brain T',
                                  font=('Helvetica Neue', 13, 'bold'),
                                  bg=ACCENT, fg='white', relief='flat',
                                  padx=28, pady=10, cursor='hand2',
                                  command=self._run)
        self.run_btn.pack()

        self.status_var = tk.StringVar(value='Ready')
        tk.Label(self, textvariable=self.status_var,
                 font=('Helvetica Neue', 10), bg=BG, fg=MUTED).pack()

    def _pick_folder(self):
        folder = filedialog.askdirectory(title='Select your folder')
        if folder:
            self.folder_var.set(folder)
            self.folder_label.config(fg=FG)

    def _log(self, msg: str, tag: str = ''):
        self.log.config(state='normal')
        self.log.insert('end', msg + '\n', tag)
        self.log.see('end')
        self.log.config(state='disabled')

    def _run(self):
        folder = self.folder_var.get()
        if folder == 'No folder selected' or not os.path.isdir(folder):
            messagebox.showerror('Error', 'Please select a valid folder first.')
            return

        self.run_btn.config(state='disabled', text='Running...')
        self.status_var.set('Building knowledge base...')
        self.log.config(state='normal')
        self.log.delete('1.0', 'end')
        self.log.config(state='disabled')

        def worker():
            cmd = [sys.executable, str(SCRIPT), folder]
            title = self.title_var.get().strip()
            if title:
                cmd += ['--title', title]
            if not self.cache_var.get():
                cmd.append('--no-cache')

            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                for line in proc.stdout:
                    line = line.rstrip()
                    if not line:
                        continue
                    tag = 'ok' if '✓' in line or 'Done' in line else \
                          'err' if 'error' in line.lower() else \
                          'info' if line.startswith(' ') else ''
                    self.after(0, self._log, line, tag)
                proc.wait()
                if proc.returncode == 0:
                    self.after(0, self._on_success, folder)
                else:
                    self.after(0, self._on_error)
            except Exception as e:
                self.after(0, self._log, f'Error: {e}', 'err')
                self.after(0, self._on_error)

        threading.Thread(target=worker, daemon=True).start()

    def _on_success(self, folder: str):
        self.run_btn.config(state='normal', text='▶  Run Second Brain T')
        self.status_var.set('✓ Done!')
        self._log('✓ Knowledge base ready!', 'ok')
        out = Path(__file__).parent / 'output' / 'index.html'
        if out.exists():
            import webbrowser
            webbrowser.open(str(out))
            self._log('→ Opening dashboard in browser...', 'info')

    def _on_error(self):
        self.run_btn.config(state='normal', text='▶  Run Second Brain T')
        self.status_var.set('Something went wrong — check the log above')


if __name__ == '__main__':
    app = Launcher()
    app.mainloop()
