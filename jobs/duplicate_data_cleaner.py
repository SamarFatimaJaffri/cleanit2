from tools import DuplicateDataTools as Tools


class DuplicateDataCleaner:
    """remove duplicate records"""
    def execute(self):
        Tools.remove_duplicates()
