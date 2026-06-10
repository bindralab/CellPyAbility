"""Windows GUI wrapper for GDA analysis using shared CLI backend logic."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import CellPyAbility_toolbox_app as tb_gui
from cellpyability import gda_analysis
from cellpyability.toolbox import logger


def run():
    def gda_gui():
        image_dir = ''

        def select_image_dir():
            nonlocal image_dir
            image_dir = filedialog.askdirectory()

        root = tk.Tk()
        root.title('GDA input')

        entries = {}
        fields = [
            ('title_name', 'Enter the title of the experiment:'),
            ('upper_name', 'Enter the name for the upper cell condition (rows B-D):'),
            ('lower_name', 'Enter the name for the lower cell condition (rows E-G):'),
            ('top_conc', 'Enter the top concentration of drug used (column 11):'),
            ('dilution', 'Enter the drug dilution factor (x-fold):'),
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

    gui_inputs = gda_gui()
    required_fields = ['title_name', 'upper_name', 'lower_name', 'top_conc', 'dilution', 'image_dir']
    missing_fields = [field for field in required_fields if not gui_inputs.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required input(s): {', '.join(missing_fields)}")

    output_base = tb_gui.configure_cli_backend()
    logger.debug('Configured shared CLI backend for GDA GUI run.')

    gda_analysis.run_gda(
        title_name=gui_inputs['title_name'],
        upper_name=gui_inputs['upper_name'],
        lower_name=gui_inputs['lower_name'],
        top_conc=float(gui_inputs['top_conc']),
        dilution=float(gui_inputs['dilution']),
        image_dir=gui_inputs['image_dir'],
        show_plot=False,
        output_dir=str(output_base)
    )


if __name__ == '__main__':
    run()
