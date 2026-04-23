from data.loader import load_selected_parameters
from core.preprocess import clean_data,scale_data,create_sequences

DATA_PATH="data/raw"

selected_parameter = [
    "AMT00102",
    "AMT00103"
]

df = load_selected_parameters(DATA_PATH,selected_parameter)
df = clean_data(df)

scaled_data,scaler = scale_data(df)
sequences = create_sequences(scaled_data,window_size=20)

print("Data Shape:", df.shape)
print("Sequences shape:",sequences.shape)
print(df.head())

