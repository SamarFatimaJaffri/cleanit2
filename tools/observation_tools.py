import pandas as pd

from data_buffer import Data

pd.set_option('display.max_rows', None)


class ObservationTools:
    @staticmethod
    def get_all_values() -> pd.DataFrame:
        """Use for small dataset to get full data for observation"""
        return Data.data

    @staticmethod
    def get_values(column: str) -> pd.DataFrame:
        """Use to get data from a particular column for observation"""
        return Data.data[column]
