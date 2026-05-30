import pandas as pd

df = pd.read_csv("healthcare_iot_target_dataset.csv")

print(df.columns.tolist())
print()
print(df.head())