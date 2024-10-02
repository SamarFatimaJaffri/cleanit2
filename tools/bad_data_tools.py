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
