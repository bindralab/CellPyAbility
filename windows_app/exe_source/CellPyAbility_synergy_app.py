"""Windows GUI wrapper for synergy analysis using shared CLI backend logic."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import CellPyAbility_toolbox_app as tb_gui
from cellpyability import synergy_analysis
from cellpyability.toolbox import logger


def run():
    def synergy_gui():
        image_dir = ''

        def select_image_dir():
            nonlocal image_dir
            image_dir = filedialog.askdirectory()

        root = tk.Tk()
        root.title('synergy input')

        entries = {}
        fields = [
            ('title_name', 'Enter the title of the experiment:'),
            ('x_drug', 'Enter the drug name for the horizontal gradient:'),
            ('x_top_conc', 'Enter the horizontal top concentration (M):'),
            ('x_dilution', 'Enter the horizontal dilution factor (x-fold):'),
            ('y_drug', 'Enter the drug name for the vertical gradient:'),
            ('y_top_conc', 'Enter the vertical top concentration (M):'),
            ('y_dilution', 'Enter the vertical dilution factor (x-fold):'),
        ]
        for key, text in fields:
            ttk.Label(root, text=text).pack()
            entry = ttk.Entry(root)
            entry.pack()
            entries[key] = entry

        ttk.Button(root, text='Select Image Directory', command=select_image_dir).pack()

        gui_inputs = {}

        def submit():
            for key, entry in entries.items():
                gui_inputs[key] = entry.get().strip()
            gui_inputs['image_dir'] = image_dir
            root.destroy()

        ttk.Button(root, text='Submit', command=submit).pack()
        root.mainloop()
        return gui_inputs

    gui_inputs = synergy_gui()
    required_fields = [
        'title_name', 'x_drug', 'x_top_conc', 'x_dilution',
        'y_drug', 'y_top_conc', 'y_dilution', 'image_dir'
    ]
    missing_fields = [field for field in required_fields if not gui_inputs.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required input(s): {', '.join(missing_fields)}")

    output_base = tb_gui.configure_cli_backend()
    logger.debug('Configured shared CLI backend for synergy GUI run.')

    synergy_analysis.run_synergy(
        title_name=gui_inputs['title_name'],
        x_drug=gui_inputs['x_drug'],
        x_top_conc=float(gui_inputs['x_top_conc']),
        x_dilution=float(gui_inputs['x_dilution']),
        y_drug=gui_inputs['y_drug'],
        y_top_conc=float(gui_inputs['y_top_conc']),
        y_dilution=float(gui_inputs['y_dilution']),
        image_dir=gui_inputs['image_dir'],
        show_plot=False,
        output_dir=str(output_base)
    )


if __name__ == '__main__':
    run()
