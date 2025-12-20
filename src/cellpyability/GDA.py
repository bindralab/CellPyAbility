"""
GDA.py is a standalone GUI script for dose-response experiments of two conditions with 9 concs and a vehicle.
This script should remain in the same directory as the other CellPyAbility scripts.
For more information, please see the README at https://github.com/bindralab/CellPyAbility.
"""
import tkinter as tk
from tkinter import filedialog, ttk

import toolbox as tb
from gda_analysis import run_gda

# Initialize toolbox
logger = tb.logger

# Establish the GUI for experiment info
def gda_gui():
    image_dir = ''
    def select_image_dir():
        nonlocal image_dir
        image_dir = filedialog.askdirectory()

    # Create main window
    root = tk.Tk()
    root.title('GDA input')

    # Create entry fields for inputs
    entries = {}
    fields = [
        ('title_name', 'Enter the title of the experiment:'),
        ('upper_name', 'Enter the name for the upper cell condition (rows B-D):'),
        ('lower_name', 'Enter the name for the lower cell condition (rows E-G):'),
        ('top_conc', 'Enter the top concentration of drug used (column 11) in molar:'),
        ('dilution', 'Enter the drug dilution factor (x-fold):'),
    ]
    for key, text in fields:
        ttk.Label(root, text=text).pack()
        entry = ttk.Entry(root)
        entry.pack()
        entries[key] = entry

    # Adds button for image directory file select
    image_dir_button = ttk.Button(root, text='Select Image Directory', command=select_image_dir)
    image_dir_button.pack()
    
    # This dictionary will hold the result
    gui_inputs = {}
    
    # Callback function to use when the form is submitted
    def submit():
        for key, entry in entries.items():
            gui_inputs[key] = entry.get()
        gui_inputs['image_dir'] = image_dir
        root.destroy()
    
    # Create button to submit form
    submit_button = ttk.Button(root, text='Submit', command=submit)
    submit_button.pack()
    
    root.mainloop()
    logger.debug('GUI submitted.')
    return gui_inputs

# Assign the gda_gui output to script variable
gui_inputs = gda_gui()

# Run GDA analysis using the refactored module
run_gda(
    title_name=gui_inputs['title_name'],
    upper_name=gui_inputs['upper_name'],
    lower_name=gui_inputs['lower_name'],
    top_conc=float(gui_inputs['top_conc']),
    dilution=float(gui_inputs['dilution']),
    image_dir=gui_inputs.get('image_dir'),
    show_plot=True
)
