# nuclei counter: local version
import numpy as np
import subprocess
import statistics as st
import pandas as pd
from pathlib import Path

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.optimize import root as scipy_root
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

## Establish the GUI
# Define GUI functions and assign variables to inputs
def submit():
    global doses, title_name, upper_name, lower_name
    # Get input from entry field
    input_doses = entry.get()
    title_name = entry1.get()
    upper_name = entry2.get()
    lower_name = entry3.get()

    # Split input into list of strings
    doses_str = input_doses.split('\t')

    # Check if there are 9 values
    if len(doses_str) != 9:
        messagebox.showerror("Error", "Please enter 9 values.")
        return

    # Convert list of strings to list of floats
    try:
        doses = [float(dose) for dose in doses_str]
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
        return doses
    root.after(100, root.destroy)

# Allows selection of folder with images for analysis
def select_image_dir():
    global image_dir
    image_dir = filedialog.askdirectory()
    print(image_dir)

# Create main window
root = ThemedTk(theme="black", themebg=True)

# Create entry fields for inputs
label1 = ttk.Label(root, text = "Enter the title of the graph (include drug used):")
label1.pack()
entry1 = ttk.Entry(root)
entry1.pack()
label2 = ttk.Label(root, text = "Enter the name of the cell condition in rows B-D:")
label2.pack()
entry2 = ttk.Entry(root)
entry2.pack()
label3 = ttk.Label(root, text = "Enter the name of the cell condition in rows E-G:")
label3.pack()
entry3 = ttk.Entry(root)
entry3.pack()
label = ttk.Label(root, text="Enter nine doses (M), separated by tab:")
label.pack()
entry = ttk.Entry(root)
entry.pack()

# Create buttons for selecting directories and files
image_dir_button = ttk.Button(root, text="Select Image Directory", command=select_image_dir)
image_dir_button.pack()

# Create submit button
submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.pack()

# Start main loop
root.mainloop()

# Establish the base directory as the script's location
base_dir = Path(__file__).resolve().parent

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

# Calculate the average nuclei per condition for the upper three rows
upper_vehicle_wells = ['B2_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C2_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D2_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_vehicle_mean = df[df['FileName_DAPI'].isin(upper_vehicle_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose1_wells = ['B3_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C3_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D3_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose1_mean = df[df['FileName_DAPI'].isin(upper_dose1_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose2_wells = ['B4_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C4_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D4_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose2_mean = df[df['FileName_DAPI'].isin(upper_dose2_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose3_wells = ['B5_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C5_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D5_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose3_mean = df[df['FileName_DAPI'].isin(upper_dose3_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose4_wells = ['B6_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C6_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D6_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose4_mean = df[df['FileName_DAPI'].isin(upper_dose4_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose5_wells = ['B7_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C7_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D7_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose5_mean = df[df['FileName_DAPI'].isin(upper_dose5_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose6_wells = ['B8_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C8_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D8_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose6_mean = df[df['FileName_DAPI'].isin(upper_dose6_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose7_wells = ['B9_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C9_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D9_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose7_mean = df[df['FileName_DAPI'].isin(upper_dose7_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose8_wells = ['B10_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C10_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D10_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose8_mean = df[df['FileName_DAPI'].isin(upper_dose8_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

upper_dose9_wells = ['B11_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'C11_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'D11_-1_1_1_Stitched[DAPI 377,447]_001.tif']
upper_dose9_mean = df[df['FileName_DAPI'].isin(upper_dose9_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

# Calculate the average nuclei per condition for the lower three rows
lower_vehicle_wells = ['E2_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F2_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G2_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_vehicle_mean = df[df['FileName_DAPI'].isin(lower_vehicle_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose1_wells = ['E3_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F3_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G3_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose1_mean = df[df['FileName_DAPI'].isin(lower_dose1_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose2_wells = ['E4_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F4_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G4_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose2_mean = df[df['FileName_DAPI'].isin(lower_dose2_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose3_wells = ['E5_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F5_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G5_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose3_mean = df[df['FileName_DAPI'].isin(lower_dose3_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose4_wells = ['E6_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F6_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G6_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose4_mean = df[df['FileName_DAPI'].isin(lower_dose4_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose5_wells = ['E7_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F7_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G7_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose5_mean = df[df['FileName_DAPI'].isin(lower_dose5_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose6_wells = ['E8_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F8_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G8_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose6_mean = df[df['FileName_DAPI'].isin(lower_dose6_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose7_wells = ['E9_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F9_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G9_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose7_mean = df[df['FileName_DAPI'].isin(lower_dose7_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose8_wells = ['E10_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F10_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G10_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose8_mean = df[df['FileName_DAPI'].isin(lower_dose8_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

lower_dose9_wells = ['E11_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'F11_-1_1_1_Stitched[DAPI 377,447]_001.tif', 'G11_-1_1_1_Stitched[DAPI 377,447]_001.tif']
lower_dose9_mean = df[df['FileName_DAPI'].isin(lower_dose9_wells)]['Count_LargeBlockCorrectedNucleiDAPI'].mean()

# Define the conditions for the upper and lower groups
upper_conditions = [upper_vehicle_wells, upper_dose1_wells, upper_dose2_wells, upper_dose3_wells, upper_dose4_wells, upper_dose5_wells, upper_dose6_wells, upper_dose7_wells, upper_dose8_wells, upper_dose9_wells]
lower_conditions = [lower_vehicle_wells, lower_dose1_wells, lower_dose2_wells, lower_dose3_wells, lower_dose4_wells, lower_dose5_wells, lower_dose6_wells, lower_dose7_wells, lower_dose8_wells, lower_dose9_wells]

# Define the upper and lower mean groups
upper_means = [upper_dose1_mean, upper_dose2_mean, upper_dose3_mean, upper_dose4_mean, upper_dose5_mean, upper_dose6_mean, upper_dose7_mean, upper_dose8_mean, upper_dose9_mean]
lower_means = [lower_dose1_mean, lower_dose2_mean, lower_dose3_mean, lower_dose4_mean, lower_dose5_mean, lower_dose6_mean, lower_dose7_mean, lower_dose8_mean, lower_dose9_mean]

# Normalize individual wells
normalized_upper_wells = [[df[df['FileName_DAPI'] == well]['Count_LargeBlockCorrectedNucleiDAPI'].mean() / upper_vehicle_mean for well in condition] for condition in upper_conditions]
normalized_lower_wells = [[df[df['FileName_DAPI'] == well]['Count_LargeBlockCorrectedNucleiDAPI'].mean() / lower_vehicle_mean for well in condition] for condition in lower_conditions]

# Calculate standard deviation of each condition
upper_sd = [st.stdev(condition) for condition in normalized_upper_wells[1:]]
lower_sd = [st.stdev(condition) for condition in normalized_lower_wells[1:]]

# Calculate the mean NucleiCount for each condition and normalize it
upper_normalized_means = upper_means / upper_vehicle_mean
lower_normalized_means = lower_means / lower_vehicle_mean

# Assign doses to the x-axis
x = np.array(doses)

# Assign average normalized nuclei counts to the y-axis for each condition
y1 = np.array(upper_normalized_means)
y2 = np.array(lower_normalized_means)

## Define non-linear regression for the xy-plot and estimate IC50s
# Define the 5PL function
def fivePL(x, A, B, C, D, G): # (x = doses, A = min y, B = Hill slope, C = inflection, D = max y, G = asymetry):
    return ((A-D) / (1.0 + (x / C)**B)**G) + D

# Initial guesses for parameters
params_init_5PL_y1 = [y1[np.argmin(y1)], 1, x[np.abs(y1-0.5).argmin()], y1[np.argmax(y1)], 1]  # [A, B, C, D, G]
params_init_5PL_y2 = [y2[np.argmin(y2)], 1, x[np.abs(y2-0.5).argmin()], y2[np.argmax(y2)], 1]  # [A, B, C, D, G]

# Generate x values for the fitted curves
x_plot = np.linspace(min(x), max(x), 1000)

# Use curve_fit to fit the data for y1 and y2
popt_5PL_y1, pcov_5PL_y1 = curve_fit(fivePL, x, y1, p0=params_init_5PL_y1, maxfev=10000)
popt_5PL_y2, pcov_5PL_y2 = curve_fit(fivePL, x, y2, p0=params_init_5PL_y2, maxfev=10000)

# Calculate y values for the fitted curves for y1 and y2
y_plot_5PL_y1 = fivePL(x_plot, *popt_5PL_y1)
y_plot_5PL_y2 = fivePL(x_plot, *popt_5PL_y2)

# Plot the fitted curves for y1 and y2
plt.plot(x_plot, y_plot_5PL_y1, 'b-')
plt.plot(x_plot, y_plot_5PL_y2, 'r-')

# Define the function to estimate IC50 for y1 and y2
def root_func_y1(x):
    return fivePL(x, *popt_5PL_y1) - 0.5
def root_func_y2(x):
    return fivePL(x, *popt_5PL_y2) - 0.5

# Use the dose (x) closest to y=0.5 as initials for IC50 estimates
initial_guess_y1 = x[np.abs(y1 - 0.5).argmin()]
initial_guess_y2 = x[np.abs(y2 - 0.5).argmin()]
print(initial_guess_y1)
print(initial_guess_y2)

# Estimate the IC50 for y1 and y2
IC50_y1 = scipy_root(root_func_y1, initial_guess_y1)
IC50_y2 = scipy_root(root_func_y2, initial_guess_y2)

# Calculate the ratio of IC50 estimates
IC50_value_y1 = IC50_y1.x[0]
IC50_value_y2 = IC50_y2.x[0]
IC50_ratio = IC50_value_y1 / IC50_value_y2

## Create scatter plot
# Create basic structure
plt.style.use('ggplot')
plt.xscale('log')
plt.scatter(x, y1, color = 'blue', label = str(upper_name))
plt.scatter(x, y2, color = 'red', label = str(lower_name))
plt.errorbar(x, y1, yerr = upper_sd, fmt='o', color='blue', capsize= 3)
plt.errorbar(x, y2, yerr = lower_sd, fmt='o', color='red', capsize=3)

# Annotate the plot
plt.xlabel('Concentration (M)')
plt.ylabel('Relative Cell Survival')
plt.title(str(title_name))
plt.text(0.05, 0.09, f'IC50 = {IC50_y1.x[0]:.2e}', color='blue', fontsize=10, transform=plt.gca().transAxes)
plt.text(0.05, 0.05, f'IC50 = {IC50_y2.x[0]:.2e}', color='red', fontsize=10, transform=plt.gca().transAxes)
plt.text(0.05, 0.01, f'IC50 ratio = {IC50_ratio:.1f}', color='black', fontsize=10, transform=plt.gca().transAxes)
plt.legend()
plt.show()