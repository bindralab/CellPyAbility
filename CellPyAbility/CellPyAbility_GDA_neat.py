import os
import statistics as st
import subprocess
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.optimize import root as scipy_root
from ttkthemes import ThemedTk

# Establish the base directory as the script's location
base_dir = Path(__file__).resolve().parent

# File where the CellProfiler path will be saved
config_file = base_dir / "cellprofiler_path.txt"

if not base_dir.exists():
    print(f"Base directory {base_dir} does not exist.")
    exit(1)
elif not os.access(base_dir, os.W_OK):
    print(f"Base directory {base_dir} is not writable.")
    exit(1)

def get_cellprofiler_path():
    # Check if the path has already been saved
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            saved_path = file.read().strip()
            if os.path.exists(saved_path):
                print(f"Using saved CellProfiler path: {saved_path}")
                return saved_path
            else:
                print("Saved path is invalid. Re-entering path ...")
    
    # Prompt the user for the path if not saved or invalid
    new_path = input("Enter the path to the CellProfiler program: ").strip()
    new_path = new_path.strip('"').strip("'")
    print(new_path)
    
    # Verify the path exists
    if not os.path.exists(new_path):
        print("Error: Path does not exist. Please try again.")
        return get_cellprofiler_path()  # Recursive call for valid input
    
    # Save the path to the file for future use
    with open(config_file, "w") as file:
        file.write(new_path)
    print(f"Path saved successfully: {new_path}")
    return new_path

# Get the CellProfiler path
cp_path = get_cellprofiler_path()

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
        messagebox.showerror('Error', 'Please enter 9 values.')
        return

    # Convert list of strings to list of floats
    try:
        doses = [float(dose) for dose in doses_str]
    except ValueError:
        messagebox.showerror('Error', 'Please enter valid numbers.')
        return doses
    root.after(100, root.destroy)

# Allows selection of folder with images for analysis
def select_image_dir():
    global image_dir
    image_dir = filedialog.askdirectory()
    print(image_dir)

# Create main window
root = ThemedTk(theme='black', themebg=True)

# Create entry fields for inputs
label1 = ttk.Label(root, text='Enter the title of the graph (include drug used):')
label1.pack()
entry1 = ttk.Entry(root)
entry1.pack()
label2 = ttk.Label(root, text='Enter the name of the cell condition in rows B-D:')
label2.pack()
entry2 = ttk.Entry(root)
entry2.pack()
label3 = ttk.Label(root, text='Enter the name of the cell condition in rows E-G:')
label3.pack()
entry3 = ttk.Entry(root)
entry3.pack()
label = ttk.Label(root, text='Enter nine doses in molar (exclude zero), separated by tab:')
label.pack()
entry = ttk.Entry(root)
entry.pack()

# Create buttons for selecting directories and files
image_dir_button = ttk.Button(root, text='Select Image Directory', command=select_image_dir)
image_dir_button.pack()

# Create submit button
submit_button = ttk.Button(root, text='Submit', command=submit)
submit_button.pack()

# Start main loop
root.mainloop()

## Define the path to the pipeline (.cppipe)
cppipe_path = base_dir / 'CellPyAbility.cppipe'

## Define the folder where CellProfiler will output the .csv results
cp_output_dir = base_dir / 'cp_output'

# Run CellProfiler from the command line
subprocess.run([cp_path, '-c', '-r', '-p', cppipe_path, '-i', image_dir, '-o', cp_output_dir])

# Define the path to the CellProfiler counting output
cp_csv = cp_output_dir / 'CellPyAbilityImage.csv'

# Define file path for GDA_output subfolder
gda_output_dir = base_dir / 'GDA_output'

print('Finished CellProfiler')

# Define function to search for and replace well names
def rename_to_any_target(entry, targets):
    for target in targets:
        if target in entry:
            return target
    return entry  # Keep original if no target matches

# List of targets to check
targets = [
    'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11',
    'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11',
    'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11',
    'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11',
    'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11',
    'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11',
    ]

print('Finished renaming wells')

# Load the CellProfiler counts into a DataFrame
df = pd.read_csv(cp_csv)
df.drop('ImageNumber', axis=1, inplace=True)
df.columns = ['nuclei', 'well']
df['well'] = df['well'].apply(lambda x: rename_to_any_target(x, targets))
df = df[['well', 'nuclei']]

# Calculate the average nuclei per condition for the upper three rows
upper_vehicle_wells = ['B2','C2','D2']
upper_vehicle_mean = df[df['well'].isin(upper_vehicle_wells)]['nuclei'].mean()

upper_dose1_wells = ['B3','C3','D3']
upper_dose1_mean = df[df['well'].isin(upper_dose1_wells)]['nuclei'].mean()

upper_dose2_wells = ['B4','C4','D4']
upper_dose2_mean = df[df['well'].isin(upper_dose2_wells)]['nuclei'].mean()

upper_dose3_wells = ['B5','C5','D5']
upper_dose3_mean = df[df['well'].isin(upper_dose3_wells)]['nuclei'].mean()

upper_dose4_wells = ['B6', 'C6', 'D6']
upper_dose4_mean = df[df['well'].isin(upper_dose4_wells)]['nuclei'].mean()

upper_dose5_wells = ['B7', 'C7', 'D7']
upper_dose5_mean = df[df['well'].isin(upper_dose5_wells)]['nuclei'].mean()

upper_dose6_wells = ['B8', 'C8', 'D8']
upper_dose6_mean = df[df['well'].isin(upper_dose6_wells)]['nuclei'].mean()

upper_dose7_wells = ['B9', 'C9', 'D9']
upper_dose7_mean = df[df['well'].isin(upper_dose7_wells)]['nuclei'].mean()

upper_dose8_wells = ['B10','C10','D10']
upper_dose8_mean = df[df['well'].isin(upper_dose8_wells)]['nuclei'].mean()

upper_dose9_wells = ['B11', 'C11', 'D11']
upper_dose9_mean = df[df['well'].isin(upper_dose9_wells)]['nuclei'].mean()

# Calculate the average nuclei per condition for the lower three rows
lower_vehicle_wells = ['E2', 'F2', 'G2']
lower_vehicle_mean = df[df['well'].isin(lower_vehicle_wells)]['nuclei'].mean()

lower_dose1_wells = ['E3', 'F3', 'G3']
lower_dose1_mean = df[df['well'].isin(lower_dose1_wells)]['nuclei'].mean()

lower_dose2_wells = ['E4', 'F4', 'G4']
lower_dose2_mean = df[df['well'].isin(lower_dose2_wells)]['nuclei'].mean()

lower_dose3_wells = ['E5','F5','G5']
lower_dose3_mean = df[df['well'].isin(lower_dose3_wells)]['nuclei'].mean()

lower_dose4_wells = ['E6','F6','G6']
lower_dose4_mean = df[df['well'].isin(lower_dose4_wells)]['nuclei'].mean()

lower_dose5_wells = ['E7','F7','G7']
lower_dose5_mean = df[df['well'].isin(lower_dose5_wells)]['nuclei'].mean()

lower_dose6_wells = ['E8','F8','G8']
lower_dose6_mean = df[df['well'].isin(lower_dose6_wells)]['nuclei'].mean()

lower_dose7_wells = ['E9','F9','G9']
lower_dose7_mean = df[df['well'].isin(lower_dose7_wells)]['nuclei'].mean()

lower_dose8_wells = ['E10','F10','G10']
lower_dose8_mean = df[df['well'].isin(lower_dose8_wells)]['nuclei'].mean()

lower_dose9_wells = ['E11','F11','G11']
lower_dose9_mean = df[df['well'].isin(lower_dose9_wells)]['nuclei'].mean()

# Define the conditions for the upper and lower groups so we can normalize within groups
upper_conditions = [
    upper_vehicle_wells,
    upper_dose1_wells,
    upper_dose2_wells,
    upper_dose3_wells,
    upper_dose4_wells,
    upper_dose5_wells,
    upper_dose6_wells,
    upper_dose7_wells,
    upper_dose8_wells,
    upper_dose9_wells,
]
lower_conditions = [
    lower_vehicle_wells,
    lower_dose1_wells,
    lower_dose2_wells,
    lower_dose3_wells,
    lower_dose4_wells,
    lower_dose5_wells,
    lower_dose6_wells,
    lower_dose7_wells,
    lower_dose8_wells,
    lower_dose9_wells,
]

# Define the upper and lower mean groups
upper_means = [
    upper_vehicle_mean,
    upper_dose1_mean,
    upper_dose2_mean,
    upper_dose3_mean,
    upper_dose4_mean,
    upper_dose5_mean,
    upper_dose6_mean,
    upper_dose7_mean,
    upper_dose8_mean,
    upper_dose9_mean,
]
lower_means = [
    lower_vehicle_mean,
    lower_dose1_mean,
    lower_dose2_mean,
    lower_dose3_mean,
    lower_dose4_mean,
    lower_dose5_mean,
    lower_dose6_mean,
    lower_dose7_mean,
    lower_dose8_mean,
    lower_dose9_mean,
]

# Normalize individual wells to their group vehicle control
normalized_upper_wells = [[df[df['well'] == well]['nuclei'].mean() / upper_vehicle_mean for well in condition] 
                          for condition in upper_conditions]
normalized_lower_wells = [[df[df['well'] == well]['nuclei'].mean() / lower_vehicle_mean for well in condition]
                          for condition in lower_conditions]

# Calculate standard deviation of each condition's normalized
upper_sd = [st.stdev(condition) for condition in normalized_upper_wells]
lower_sd = [st.stdev(condition) for condition in normalized_lower_wells]

# Calculate the mean nucleiCount for each condition and normalize it
upper_normalized_means = [sum(condition) / len(condition) for condition in normalized_upper_wells]
lower_normalized_means = [sum(condition) / len(condition) for condition in normalized_lower_wells]

# Pair column number with drug dose
column_concentrations = {
    '2': 0,  # Control
    '3': doses[0],
    '4': doses[1],
    '5': doses[2],
    '6': doses[3],
    '7': doses[4],
    '8': doses[5],
    '9': doses[6],
    '10': doses[7],
    '11': doses[8],
}

# Consolidate analytics into a .csv file
df2 = pd.DataFrame(columns=column_concentrations)
df2.index.name = '96-Well Column'
df2.loc['Drug Concentration'] = list(column_concentrations.values())
df2.loc[f'Relative Cell Viability {upper_name}'] = upper_normalized_means
df2.loc[f'Relative Cell Viability {lower_name}'] = lower_normalized_means
df2.loc[f'Relative Standard Deviation {upper_name}'] = upper_sd
df2.loc[f'Relative Standard Deviation {lower_name}'] = lower_sd
df2.to_csv(gda_output_dir / f'{title_name}_GDA_Stats.csv')

# Normalize nuclei counts for each well individually
df['normalized_nuclei'] = df.apply(
    lambda row: row['nuclei'] / upper_vehicle_mean 
    if row['well'][0] in ['B', 'C', 'D'] else row['nuclei'] / lower_vehicle_mean,
    axis=1
)

# Extract rows and columns for the matrix
row_letters = ['B', 'C', 'D', 'E', 'F', 'G']
column_labels = list(column_concentrations.values())

# Create an empty matrix
viability_matrix = pd.DataFrame(
    index=row_letters,
    columns=column_labels,
    dtype=float
)

# Fill the matrix with normalized data
for letter in row_letters:
    for column_label, dose in column_concentrations.items():
        # Find the well(s) matching the current row and column
        well_pattern = letter + column_label  # e.g., 'B2'
        matching_wells = df[df['well'] == well_pattern]

        # Compute mean normalized viability for this well (in case there are duplicates)
        viability_matrix.at[letter, dose] = matching_wells['normalized_nuclei'].mean()

# Rename the rows based on the cell line names given by the user
row_labels = [f'{upper_name} rep 1', f'{upper_name} rep 2', f'{upper_name} rep 3', 
              f'{lower_name} rep 1', f'{lower_name} rep 2', f'{lower_name} rep 3']

viability_matrix.index = row_labels

# Save the matrix to a file or continue analysis
viability_matrix.to_csv(gda_output_dir / f'{title_name}_GDA_ViabilityMatrix.csv')

print('Finished analyzing data')

# Assign doses to the x-axis
x = np.array(doses)

# Assign average normalized nuclei counts to the y-axis for each condition
y1 = np.array(upper_normalized_means[1:])
y2 = np.array(lower_normalized_means[1:])

## Define non-linear regression for the xy-plot and estimate IC50s
# Define the 5PL function
def fivePL(x, A, B, C, D, G):  # (x = doses, A = min y, B = Hill slope, C = inflection, D = max y, G = asymetry):
    return ((A - D) / (1.0 + (x / C) ** B) ** G) + D

# Initial guesses for parameters
params_init_5PL_y1 = [y1[np.argmin(y1)], 1, x[np.abs(y1 - 0.5).argmin()], y1[np.argmax(y1)], 1]  # [A, B, C, D, G]
params_init_5PL_y2 = [y2[np.argmin(y2)], 1, x[np.abs(y2 - 0.5).argmin()], y2[np.argmax(y2)], 1]  # [A, B, C, D, G]

# Generate x values for the fitted curves
x_plot = np.linspace(min(x), max(x), 1000)

# Use curve_fit to fit the data for y1 and y2
## Identify initial maxfev along with higher maxfev in case optimal parameters not found
maxfev_initial = int(1e4)
maxfev_retry = int(1e6)

try:
    # First attempt with initial maxfev
    popt_5PL_y1, pcov_5PL_y1 = curve_fit(fivePL, x, y1, p0=params_init_5PL_y1, maxfev=maxfev_initial)
except RuntimeError:
    print(f'RuntimeError encountered with maxfev={maxfev_initial} for {upper_name}. Retrying with maxfev={maxfev_retry}...')
    try:
        # Second attempt with higher maxfev
        popt_5PL_y1, pcov_5PL_y1 = curve_fit(fivePL, x, y1, p0=params_init_5PL_y1, maxfev=maxfev_retry)
    except RuntimeError:
        # These are some ugly data ... let them know
        print(f'RuntimeError encountered with maxfev={maxfev_retry} for {upper_name}. A logistic model does not appear to fit these data.')
        
try:
    # First attempt with initial maxfev
    popt_5PL_y2, pcov_5PL_y2 = curve_fit(fivePL, x, y2, p0=params_init_5PL_y2, maxfev=maxfev_initial)
except RuntimeError:
    print(f'RuntimeError encountered with maxfev={maxfev_initial} for {lower_name}. Retrying with maxfev={maxfev_retry}...')
    try:
        # Second attempt with higher maxfev
        popt_5PL_y2, pcov_5PL_y2 = curve_fit(fivePL, x, y2, p0=params_init_5PL_y2, maxfev=maxfev_retry)
    except:
        # These are some ugly data ... let them know
        print(f'RunTimeError encountered with maxfev={maxfev_retry} for {lower_name}. A logistic model does not apeear to fit these data.')

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
plt.style.use('default')
plt.xscale('log')
plt.scatter(x, y1, color='blue', label=str(upper_name))
plt.scatter(x, y2, color='red', label=str(lower_name))
plt.errorbar(x, y1, yerr=upper_sd[1:], fmt='o', color='blue', capsize=3)
plt.errorbar(x, y2, yerr=lower_sd[1:], fmt='o', color='red', capsize=3)

# Annotate the plot
plt.xlabel('Concentration (M)')
plt.ylabel('Relative Cell Survival')
plt.title(str(title_name))
plt.text(0.05, 0.09, f'IC50 = {IC50_y1.x[0]:.2e}',
    color='blue',
    fontsize=10,
    transform=plt.gca().transAxes
)
plt.text(
    0.05, 0.05, f'IC50 = {IC50_y2.x[0]:.2e}',
    color='red',
    fontsize=10,
    transform=plt.gca().transAxes
)
plt.text(
    0.05, 0.01, f'IC50 ratio = {IC50_ratio:.1f}',
    color='black',
    fontsize=10,
    transform=plt.gca().transAxes
)
plt.legend()
plt.savefig(gda_output_dir / f'{title_name}_GDA_plot.png', dpi=200, bbox_inches='tight')
print('Finished graphing data. Please close plot when ready to continue.')
plt.show()

# Rename the CellProfiler output using the provided title name
counts_csv = gda_output_dir / f'{title_name}_GDA_counts.csv'

try:
    os.rename(cp_csv, counts_csv)
    print(f'{cp_csv} succesfully renamed to {counts_csv}')
except FileNotFoundError:
    print(f'{cp_csv} not found')
except PermissionError:
    print(f'Permission denied. {cp_csv} may be open or in use.')
except Exception as e:
    print(f'While renaming {cp_csv}, an error occurred: {e}')

print('Analysis complete. Please find the results in the GDA_output folder.')