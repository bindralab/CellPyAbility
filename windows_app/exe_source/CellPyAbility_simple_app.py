import tkinter as tk
from tkinter import filedialog, ttk

import CellPyAbility_toolbox_app as tb

def run():
    # Initialize toolbox
    logger, base_dir = tb.logger, tb.base_dir

    # Establish the GUI for experiment info
    def simple_gui():
        root = tk.Tk()
        root.title('GDA input')

        ttk.Label(root, text='Experiment title:').pack()
        title_entry = ttk.Entry(root); title_entry.pack()

        image_dir = ''
        def select_dir(): 
            nonlocal image_dir
            image_dir = filedialog.askdirectory()
        ttk.Button(root, text='Select images…', command=select_dir).pack()

        inputs = {}
        def on_submit():
            inputs['title'] = title_entry.get()
            inputs['image_dir'] = image_dir
            root.destroy()
        ttk.Button(root, text='Submit', command=on_submit).pack()
        root.mainloop()
        return inputs

    # Run the GUI and assign inputs to variables
    gui = simple_gui()
    title = gui['title']
    imgdir = gui['image_dir']

    # Run CellProfiler via the command line
    df_cp, cp_csv = tb.run_cellprofiler(imgdir)
    df_cp.drop(columns='ImageNumber', inplace=True)
    df_cp.columns = ['nuclei','well']

    # Rename wells and define row/column names
    df_cp['well'] = df_cp['well'].apply(lambda x: tb.rename_wells(x, tb.wells))
    df_cp[['Row','Column']] = df_cp['well'].str.extract(r'^([B-G])(\d+)$')

    # Pivot df_cp so it matches a 96-well layout (nuclei count matrix)
    row_labels = ['B','C','D','E','F','G']
    column_labels = [str(i) for i in range(2,12)]
    count_matrix = (
        df_cp
        .pivot(index='Row', columns='Column', values='nuclei')
        .reindex(index=row_labels, columns=column_labels)
    )

    # Define or create and define CellPyAbility/simple_output/ directory
    outdir = base_dir / 'simple_output'
    outdir.mkdir(exist_ok=True)

    # Save the count matrix to the simple_output directory
    count_matrix.to_csv(outdir / f'{title}_simple_CountMatrix.csv')
    logger.info(f"Saved count matrix for '{title}' to {outdir}")

if __name__ == '__main__':
    run()