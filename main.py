import pandas as pd
import sys
import seaborn as sns

def analize_csv(csv_file):
    df = pd.read_csv(csv_file)
    print("Data loaded\n")

    print("Shape of dataset:\n")
    print(df.shape)