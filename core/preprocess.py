import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def load_data(path):
    return pd.read_parquet(path)

def scale_data(df):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    return scaled,scaler

def create_sequences(data, window_size=20):
    sequences=[]
    
    for i in range(len(data)-window_size):
        sequences.append(data[i:i+window_size])

    return np.array(sequences)

def clean_data(df):
    df = df.ffill()
    df = df.dropna()

    return df


    