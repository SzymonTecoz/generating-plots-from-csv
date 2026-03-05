from tkinter import filedialog

import pandas as pd
import sys
import seaborn as sns
import tkinter as tk

def analize_csv(csv_file):
    df = pd.read_csv(csv_file)
    print("Data loaded\n")

    print("Shape of dataset:\n")
    print(df.shape)

    print("Columns of dataset:\n")
    print(df.columns)

    print("Dataset preview:\n")
    print(df.head())

    numeric_columns = df.select_dtypes(include="number").columns
    print("Numeric columns detected:\n")
    print(list(numeric_columns))


def select_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title = "Select file",filetypes = (("csv files","*.csv"),))

    return file_path


if __name__ == "__main__":
    csv_file = select_file()
    if csv_file:
        analize_csv(csv_file)
    else:
        print("No file selected")