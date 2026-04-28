import pandas as pd

DATA_PATH = "data/Dogs Pedigree.csv"


def clean_id(value):
    if pd.isna(value):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return str(int(float(value)))


def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    return [
        {
            "id": str(int(float(row["ID"]))),
            "name": row["Name"].strip() if isinstance(row["Name"], str) else row["Name"],
            "breed": row["Breed"].strip() if isinstance(row["Breed"], str) else row["Breed"],
            "sex": row["Sex"].strip() if isinstance(row["Sex"], str) else row["Sex"],
            "height_cm": row["Height_cm"],
            "weight_kg": row["Weight_kg"],
            "sire_id": clean_id(row["Sire_ID"]),
            "dam_id": clean_id(row["Dam_ID"]),
        }
        for _, row in df.iterrows()
    ]


def build_index(data):
    return {dog["id"]: dog for dog in data}