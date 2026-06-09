"""Windows GUI wrapper for simple analysis using shared CLI backend logic."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import CellPyAbility_toolbox_app as tb

if not getattr(sys, "frozen", False):
    repo_src = Path(__file__).resolve().parents[2] / "src"
    if str(repo_src) not in sys.path:
        sys.path.insert(0, str(repo_src))

from cellpyability import simple_analysis


def run():
    logger = tb.logger

    def simple_gui():
        root = tk.Tk()
        root.title('Simple input')

        ttk.Label(root, text='Experiment title:').pack()
        title_entry = ttk.Entry(root)
        title_entry.pack()

        image_dir = ''

        def select_dir():
            nonlocal image_dir
            image_dir = filedialog.askdirectory()

        ttk.Button(root, text='Select images…', command=select_dir).pack()

        inputs = {}

        def on_submit():
            inputs['title'] = title_entry.get().strip()
            inputs['image_dir'] = image_dir
            root.destroy()

        ttk.Button(root, text='Submit', command=on_submit).pack()
        root.mainloop()
        return inputs

    gui = simple_gui()
    required_fields = ['title', 'image_dir']
    missing_fields = [field for field in required_fields if not gui.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required input(s): {', '.join(missing_fields)}")

    output_base = tb.configure_cli_backend()
    logger.debug('Configured shared CLI backend for simple GUI run.')

    simple_analysis.run_simple(
        title=gui['title'],
        image_dir=gui['image_dir'],
        output_dir=str(output_base)
    )


if __name__ == '__main__':
    run()
