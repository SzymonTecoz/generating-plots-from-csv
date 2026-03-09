from tkinter import filedialog
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import tkinter as tk
import watchdog
import time

from seaborn import heatmap
from watchdog.observers import Observer


class CSVHandler():
    def __init__(self, csv_file):
        self.csv_file = csv_file

    def on_modified(self, event):
        if event.src_path == self.csv_file:
            print("File changed. Updating plots...")
            analize_csv(self.csv_file)

def watch_csv(csv_file):
    event_handler = CSVHandler(csv_file)
    observer = Observer()
    directory = os.path.dirname(csv_file)
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    print("Watching for changes in " + csv_file)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def analize_csv(csv_file):
    os.makedirs("plots", exist_ok=True)
    df = pd.read_csv(csv_file, on_bad_lines="skip")
    print("Data loaded\n")

    print("Shape of dataset:\n")
    print(df.shape)

    print("Columns of dataset:\n")
    print(df.columns)

    print("Dataset preview:\n")
    print(df.head())

    print("Numeric columns detected:\n")
    numeric_columns = df.select_dtypes(include="number").columns
    print(list(numeric_columns))
    correlation_matrix = df[numeric_columns].corr()
    heatmap_file = "plots/correlation_matrix.png"
    if not os.path.exists(heatmap_file):
        plt.figure(figsize=(10,8))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt = ".2f")
        plt.savefig(heatmap_file)
        plt.close()
        print("\nHeatmap saved as correlation_matrix.png\n")
    else:
        print("Heatmap already exists\n")



    for column in numeric_columns:
        plt.figure()
        df[column].hist()
        plt.title(f"Histogram of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        file_name = f"plots/{column}_histogram.png"
        if not os.path.exists(file_name):
            plt.savefig(file_name)
            print(f"Saved {file_name}")
        else:
            print(f"File {file_name} already exists")
        plt.figure()
        plt.close()



def select_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title = "Select file",filetypes = (("csv files","*.csv"),))

    return file_path





if __name__ == "__main__":
    csv_file = select_file()
    if csv_file:
        analize_csv(csv_file)
        watch_csv(csv_file)
    else:
        print("No file selected")