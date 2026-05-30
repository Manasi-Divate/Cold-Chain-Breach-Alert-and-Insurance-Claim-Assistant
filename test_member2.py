from utils.data_loader import load_data
from utils.data_cleaner import clean_data
from utils.data_cleaner import create_features
from utils.data_cleaner import get_summary

df = load_data(
    "data/healthcare_iot_target_dataset.csv"
)

df = clean_data(df)

df = create_features(df)

summary = get_summary(df)

print(summary)

print(df.head())