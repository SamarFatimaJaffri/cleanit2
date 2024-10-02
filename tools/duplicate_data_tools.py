from data_buffer import Data


class DuplicateDataTools:
    @staticmethod
    def remove_duplicates() -> str:
        """Use to remove all duplicate rows."""
        Data.data = Data.data.drop_duplicates()
        return 'All the duplicate rows have been removed!'
