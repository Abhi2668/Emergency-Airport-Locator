import argparse
import pandas as pd


class DataWorker:
    def __init__(self, data_1, data_2):
        self.d1: pd.DataFrame = pd.read_csv(data_1)
        self.d2: pd.DataFrame = pd.read_csv(data_2)
        self.merged_data: pd.DataFrame = None

    def clean_raws(self, cols_1: list, cols_2: list):

        # This removes extraneous qualitative data from the raws as well as almost fully
        # incomplete columns of data (mostly for lat/long with runways, which are already
        # matched to an airport's lat/long.

        self.d1 = self.d1.drop(cols_1, axis=1)
        self.d2 = self.d2.drop(cols_2, axis=1)

    def merge(self):

        # Matches airports with runways based off airport_ref. Multiple runways are saved as multiple rows of data
        # with the same airport_ref. Any airports or runways with unmatched airport_refs are dropped.

        self.merged_data: pd.DataFrame = self.d1.merge(self.d2, on="airport_ref", how="inner")

        # Checks for missing values in any row of the matched airport_refs. Drops any rows containing incomplete
        # information. In this case, filling values from estimations is not viable as this could produce disastrous
        # results via misleading information being sent to the pilots.

        print("VALIDATING...")
        if self.merged_data.isnull().values.any():
            print("ERROR: Missing data in DF. Killing rows containing missing data.")
            self.merged_data.dropna(axis=0, how="any", inplace=True)
        else:
            print("PASSED")

        # So far, we are only working with airplanes and operational airports. Therefore, we remove any airports
        # classified as 'heliport' and 'closed.'

        self.merged_data.drop(self.merged_data[self.merged_data["type"] == "heliport"].index, inplace=True)
        self.merged_data.drop(self.merged_data[self.merged_data["type"] == "closed"].index, inplace=True)
