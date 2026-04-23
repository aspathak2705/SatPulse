import pandas as pd
import os

def load_selected_parameters(data_path, selected_params):
    dfs = []

    for param in selected_params:
        file_path = os.path.join(data_path, f"{param}_stats_10min.parquet")

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        df = pd.read_parquet(file_path)
        df = df.add_prefix(f"{param}_")

        dfs.append(df)

    if len(dfs) == 0:
        print("No data loaded!")
        return None

    combined_df = pd.concat(dfs, axis=1)

    return combined_df