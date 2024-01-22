import pandas as pd


class Airport:
    def __init__(self, df: pd.Series):
        self.airport_ref = df["airport_ref"]
        self.latitude = df["latitude_deg"]
        self.longitude = df["longitude_deg"]
        self.elevation = df["elevation_ft"]
        self.runway_length = df["length_ft"]
