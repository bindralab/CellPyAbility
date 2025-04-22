import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import sys

import CellPyAbility_GDA_app
import CellPyAbility_simple_app
import CellPyAbility_synergy_app

# Define temporary directory so logo can be accessed later
if getattr(sys, 'frozen', False):
    temp_dir = Path(sys._MEIPASS) # PyInstaller's temporary folder
else:
    temp_dir = Path.cwd()

# Gives user info on scripts when hovering over GUI buttons
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        # Calculate position for the tooltip window
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        # Create a top-level window that appears above other windows
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#ffffe0", relief=tk.SOLID, borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def launch_gui():
    # Establish GUI window
    global root
    root = tk.Tk()
    root.title("CellPyAbility Analysis Menu")
    root.geometry("500x700") # If it fits, it ships

    # Load logo bundled in application
    try:
        logo_image = tk.PhotoImage(file= temp_dir / "CellPyAbilityLogo.png")
        logo_label = tk.Label(root, image=logo_image)
    except Exception as e: # if it doesn't work, load in text title
        print("Could not load logo image:", e)
        logo_label = tk.Label(root, text="CellPyAbility\nBindra Lab", font=("tahoma", 24))

    logo_label.pack(pady=10)

    # Create buttons for each script option, along with tooltip dialogue
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    btn_gda = tk.Button(button_frame, text="GDA", width=12,
                        command=lambda: run_script(1))
    btn_gda.grid(row=0, column=0, padx=5, pady=5)
    ToolTip(btn_gda, "Dose-response analysis of two cell lines in response to one treatment")

    btn_synergy = tk.Button(button_frame, text="synergy", width=12,
                            command=lambda: run_script(2))
    btn_synergy.grid(row=0, column=1, padx=5, pady=5)
    ToolTip(btn_synergy, "Dose-response analysis of one cell line in response to two treatments in combination")

    btn_simple = tk.Button(button_frame, text="simple", width=12,
                           command=lambda: run_script(3))
    btn_simple.grid(row=0, column=2, padx=5, pady=5)
    ToolTip(btn_simple, "Raw nuclei count matrix")

    btn_exit = tk.Button(root, text="Exit", command=root.quit)
    ToolTip(btn_exit, "Close the program")
    btn_exit.pack(pady=10)

    root.mainloop()

# Runs script based on user input from GUI
def run_script(script_number):
    global root
    root.destroy() # Close window after choosing script
    
    if script_number == 1:
        CellPyAbility_GDA_app.run()
    elif script_number == 2:
        CellPyAbility_synergy_app.run()
    elif script_number == 3:
        CellPyAbility_simple_app.run()
    else:
        print("Invalid script selection.") # Vestigial given the GUI but will leave it for now
    
    # Ask user if they wish to perform an additonal analysis
    temp_root = tk.Tk()
    temp_root.withdraw()
    response = messagebox.askyesno("Would you like to perform another analysis?")
    temp_root.destroy()

    if response:
        launch_gui() # If yes, re-launch GUI
    else:
        sys.exit() # Else, exit application
    
launch_gui()