# nuclei counter: local version
import os
import glob
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import subprocess
import statistics as st
import pandas as pd

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

# Establish the base directory as the script's location
base_dir = Path(__file__).resolve().parent

# Establish the GUI
## Allows selection of folder with images for analysis
def select_image_dir():
    global image_dir
    image_dir = filedialog.askdirectory()
    print(image_dir)

## Create main window
root = ThemedTk(theme="black", themebg=True)

## Create buttons for selecting directories and files
image_dir_button = ttk.Button(root, text="Select Image Directory", command=select_image_dir)
image_dir_button.pack()

## Start main loop
root.mainloop()

# Define required CellProfiler paths, then run CellProfiler
## Define the path to the CellProfiler executable (.exe)
cp_path = Path(r"C:\Program Files (x86)\CellProfiler\CellProfiler.exe")

## Define the path to the pipeline (.cppipe)
cppipe_path = base_dir / "CellPyAbility.cppipe"

## Define the folder where CellProfiler will output the .csv results
output_dir = base_dir / "cp_output"

# Run CellProfiler from the command line
subprocess.run([cp_path, "-c", "-r", "-p", cppipe_path, "-i", image_dir, "-o", output_dir])

# Define the path to the CellProfiler counting output
cp_csv = output_dir / "CellPyAbilityImage.csv"

# Load the CellProfiler counts into a DataFrame
df = pd.read_csv(cp_csv)
print(df)