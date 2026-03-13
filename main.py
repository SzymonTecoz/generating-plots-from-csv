import threading

import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import watchdog
import time

from seaborn import heatmap
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CSVHandler(FileSystemEventHandler):
    def __init__(self, csv_file, log):
        self.csv_file = csv_file
        self.log = log

    def on_modified(self, event):
        if event.src_path == self.csv_file:
            print("File changed. Updating plots...")
            analize_csv(self.csv_file, self.log)

def watch_csv(csv_file, log):

    event_handler = CSVHandler(csv_file, log)
    observer = Observer()
    directory = os.path.dirname(csv_file)
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    print("Watching for changes in " + csv_file)

def analize_csv(csv_file, log = None, hist = True, box = True, scatter = True, heatmap = True, pairplot = True):
    generated_plots = []
    os.makedirs("plots", exist_ok=True)
    df = pd.read_csv(csv_file, sep = None, engine = "python", on_bad_lines="skip")
    if log:
        log("Data loaded")

        log("Shape of dataset:")
        log(str(df.shape))

        log("Columns of dataset:")
        log(str(df.columns))

        log("Dataset preview:")
        log(str(df.head()))

        log("Numeric columns detected:")
        numeric_columns = df.select_dtypes(include="number").columns
        log(str(list(numeric_columns)))
        correlation_matrix = df[numeric_columns].corr()
        if heatmap:
            heatmap_file = "plots/correlation_matrix.png"
            if not os.path.exists(heatmap_file):
                plt.figure(figsize=(10,8))
                sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt = ".2f")
                plt.savefig(heatmap_file)
                plt.close()
                log("Heatmap saved as correlation_matrix.png")
                generated_plots.append(heatmap_file)
            else:
                log("Heatmap already exists")


        if hist:
            for column in numeric_columns:
                plt.figure()
                df[column].hist()
                plt.title(f"Histogram of {column}")
                plt.xlabel(column)
                plt.ylabel("Frequency")
                file_name = f"plots/{column}_histogram.png"
                if not os.path.exists(file_name):
                    plt.savefig(file_name)
                    log(f"Saved {file_name}")
                    generated_plots.append(file_name)
                else:
                    log(f"File {file_name} already exists")
                plt.close()
            if box:
                boxplot_file = f"plots/{column}_boxplot.png"

                if not os.path.exists(boxplot_file):
                    plt.figure()

                    sns.boxplot(x=df[column])

                    plt.title(f"Boxplot of {column}")

                    plt.savefig(boxplot_file)

                    plt.close()

                    print(f"Saved {boxplot_file}")
                    generated_plots.append(boxplot_file)

        if scatter:
            for i in range(len(numeric_columns)):
                for j in range(i+1, len(numeric_columns)):
                    col1 = numeric_columns[i]
                    col2 = numeric_columns[j]
                    scatter_file = f"plots/{col1}_vs_{col2}_scatter.png"
                    if not os.path.exists(scatter_file):
                        plt.figure()
                        sns.scatterplot(x=df[col1], y=df[col2])
                        plt.title(f"{col1} vs {col2}")
                        plt.xlabel(col1)
                        plt.ylabel(col2)
                        plt.savefig(scatter_file)
                        plt.close()
                        log(f"Saved {scatter_file}")
                        generated_plots.append(scatter_file)

        if pairplot:
            pairplot_file = "plots/pairplot.png"
            if not os.path.exists(pairplot_file):
                pairplot = sns.pairplot(df[numeric_columns])
                pairplot.savefig(pairplot_file)
                generated_plots.append(pairplot_file)
                plt.close()
                log("Saved pairplot.")

    return generated_plots



def select_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title = "Select file",filetypes = (("csv files","*.csv"),))

    return file_path


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Plot Generator")
        self.center_window()
        self.root.state("zoomed")
        self.root.resizable(True, True)
        self.csv_file = None
        self.setup_style()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_program)

    def center_window(self, width=700, height=500):

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_style(self):
        style = ttk.Style()
        style.configure("TButton", font = ("Helvetica", 12), padding = 10)
        style.configure("Blue.TButton", font = ("Helvetica", 12, "bold"), padding = 10)

    def create_widgets(self):
        title = ttk.Label(self.root, text="CSV Plot Generator", font=("Helvetica",12,"bold"))
        title.pack(pady=20)
        select_button = ttk.Button(self.root, text="Select CSV file...", command=self.select_file)
        select_button.pack(pady = 5)
        self.file_label = ttk.Label(self.root, text="No file selected", foreground="gray")
        self.file_label.pack(pady = 5)
        start_button = ttk.Button(self.root, text="Start monitoring", style="Blue.TButton", command=self.start_monitoring)
        start_button.pack(pady = 5)
        quit_button = ttk.Button(self.root, text="Quit", command=self.quit_program)
        quit_button.pack(pady=5)
        self.log_box = tk.Text(self.root, height=12, width=70, bg="#f5f5f7")
        self.log_box.pack(fill="both", expand=True, padx=20, pady=15)
        plots_label = ttk.Label(self.root, text="Generated plots:")
        plots_label.pack()
        self.plots_list = tk.Listbox(self.root, height=6)
        self.plots_list.pack()
        self.plots_list.bind("<Double-Button-1>", self.open_plot)

        plots_frame = ttk.LabelFrame(self.root, text="Select plots to generate:")
        plots_frame.pack(padx=20, pady=10, fill = "x")
        self.hist_var = tk.BooleanVar(value=True)
        self.box_var = tk.BooleanVar(value=True)
        self.scatter_var = tk.BooleanVar(value=True)
        self.heatmap_var = tk.BooleanVar(value=True)
        self.pairplot_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(plots_frame, text="Histogram", variable=self.hist_var).pack(anchor="w")
        ttk.Checkbutton(plots_frame, text="Boxplot", variable=self.box_var).pack(anchor="w")
        ttk.Checkbutton(plots_frame, text="Scatterplot", variable=self.scatter_var).pack(anchor="w")
        ttk.Checkbutton(plots_frame,text="Heatmap", variable=self.heatmap_var).pack(anchor="w")
        ttk.Checkbutton(plots_frame, text="Pairplot", variable=self.pairplot_var).pack(anchor="w")

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def refresh_plots(self):
        self.plots_list.delete(0, tk.END)
        if not os.path.exists("plots"):
            return
        for file in os.listdir("plots"):
            if file.endswith(".png"):
                self.plots_list.insert(tk.END, file)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=(("CSV files", "*.csv"),))
        if file_path:
            self.csv_file = file_path
            self.file_label.config(text=file_path)

    def start_monitoring(self):
        if not self.csv_file:
            self.log("Select a CSV file first.")
            return
        self.log("Analyzing CSV...")
        plots = analize_csv(self.csv_file, self.log, hist = self.hist_var.get(), box=self.box_var.get(), scatter=self.scatter_var.get(), heatmap=self.heatmap_var.get(), pairplot=self.pairplot_var.get())
        self.update_plots_list(plots)
        thread = threading.Thread(target=watch_csv, args=(self.csv_file, self.log), daemon=True)
        thread.start()

    def open_plot(self, event):
        selection = self.plots_list.curselection()
        if not selection:
            return
        file_name = self.plots_list.get(selection[0])
        path = os.path.join("plots", file_name)
        os.system(f"open '{path}'")

    def quit_program(self):
        answer = messagebox.askyesno("Quit", "Do you want to quit the application?")
        if answer:
            self.root.destroy()

    def update_plots_list(self, plots):

        self.plots_list.delete(0, tk.END)

        for plot in plots:
            name = os.path.basename(plot)

            self.plots_list.insert(tk.END, name)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()