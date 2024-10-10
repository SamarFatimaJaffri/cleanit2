import pandas as pd

from data_buffer import Data


class FormatCorrectionTools:
    @staticmethod
    def format_to_int(column: str) -> str:
        """Use to format all the values of a particular column as numeric"""
        while True:
            try:
                Data.data[column] = pd.to_numeric(Data.data[column])
                return f'{column} formatted to int!'
            except ValueError as err:
                index = str(err).split('at position ')[-1]
                Data.data.loc[int(index), column] = None

    @staticmethod
    def format_to_datetime(column: str, dateformat: str) -> str:
        """Use to format all the values of a particular column as datetime"""
        while True:
            try:
                Data.data[column] = pd.to_datetime(Data.data[column], dateformat)
                return f'{column} formatted to datetime in {dateformat} format!'
            except ValueError as err:
                index = str(err).split('at position ')[-1]
                Data.data.loc[int(index), column] = None

    @staticmethod
    def typecast_column(column: str, datatype: str) -> str:
        """Use to typecast the values of a particular column to a particular type"""
        while True:
            try:
                Data.data[column] = Data.data[column].astype(datatype)
                return f'{column} type-casted to {datatype}!'
            except ValueError as err:
                index = str(err).split('at position ')[-1]
                Data.data.loc[int(index), column] = None
