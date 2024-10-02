from data_buffer import Data


class MissingValueTools:
    @staticmethod
    def get_column_having_nulls() -> list:
        """Use to get names of the columns having null values"""
        cols = Data.data.columns[Data.data.isna().any()].to_list()
        if not cols:
            return []
        else:
            return cols

    @staticmethod
    def column_have_nulls(column: str) -> bool:
        """Use to check if particular column has null values"""
        return bool(Data.data[column].isna().any())

    @staticmethod
    def remove_all_nulls() -> str:
        """Use to remove all the empty cells from entire dataset."""
        Data.data = Data.data.dropna()
        return 'All the empty cells are removed!'

    @staticmethod
    def fill_all_nulls(value) -> str:
        """Use to replace all the empty cells with a particular value in entire dataset."""
        Data.data = Data.data.fillna(value)
        return f'All the null values are replaced with {value}!'

    @staticmethod
    def remove_nulls(column: str) -> str:
        """Use to remove the empty cells of a particular column."""
        Data.data = Data.data.dropna(subset=[column])
        return f'All the empty cells of {column} column are removed!'

    @staticmethod
    def fill_nulls(column: str, value) -> str:
        """Use to replace the empty cells of a particular column with a particular value."""
        Data.data[column] = Data.data[column].fillna(value)
        return f'All the empty cells of {column} column are replaced with {value}!'

    @staticmethod
    def fill_with_mean(column: str) -> str:
        """Use to replace the empty cells of a particular column with its mean value."""
        value = Data.data[column].mean()
        Data.data[column] = Data.data[column].fillna(value)
        return f'All the empty cells of {column} column are replaced with its mean value!'

    @staticmethod
    def fill_with_median(column: str) -> str:
        """Use to replace the empty cells of a particular column with its median value."""
        value = Data.data[column].median()
        Data.data[column] = Data.data[column].fillna(value)
        return f'All the empty cells of {column} column are replaced with its median!'

    @staticmethod
    def fill_with_mode(column: str) -> str:
        """Use to replace the empty cells of a particular column with its mode value."""
        value = Data.data[column].mode()[0]
        Data.data[column] = Data.data[column].fillna(value)
        return f'All the empty cells of {column} column are replaced with its mode value!'
