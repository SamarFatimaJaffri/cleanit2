from data_buffer import Data


class BadDataTool:
    @staticmethod
    def replace_bad_data(column: str, index: int, predicted_value: int | float | str | bool | None) -> str:
        """Use to correct a value."""
        Data.data.loc[int(index), column] = predicted_value
        return f'{column}\'s value at position {index} is replaced with {predicted_value}!'

    @staticmethod
    def remove_bad_data(index: int) -> str:
        """Use to remove a value that can't be corrected."""
        Data.data = Data.data.drop(int(index))
        return f'Row no {index} has been removed!'

    @staticmethod
    def value_correction(column: str, substrings: dict):
        """Use to correct column values i.e., by removing/replacing substrings"""
        old, new = substrings.keys(), substrings.values()
        Data.data[column] = Data.data[column].replace(old, new, regex=True)

        return f"{', '.join(old)} in {column} values got successfully replaced with {', '.join(new)} respectively"
