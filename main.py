from tkinter import filedialog
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
import seaborn as sns
import tkinter as tk
import hashlib

from seaborn import heatmap


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

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def file_changed(csv_file):
    hash_file = "data_hash.txt"
    current_hash = get_file_hash(csv_file)
    if not os.path.exists(hash_file):
        with open(hash_file, "w") as f:
            f.write(current_hash)
        return True
    with open(hash_file, "r") as f:
        saved_hash = f.read()

    if saved_hash != current_hash:
        with open(hash_file, "w") as f:
            f.write(current_hash)
        return True
    return False




if __name__ == "__main__":
    csv_file = select_file()
    if csv_file:
        if file_changed(csv_file):
            print("File changed")
            analize_csv(csv_file)
        else:
            print("\nData not changed. No update needed.")
    else:
        print("No file selected")