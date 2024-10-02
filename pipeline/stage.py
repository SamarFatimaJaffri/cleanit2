from jobs import BadDataCleaner, DuplicateDataCleaner, Formatter, MissingDataCleaner


class Stage:
    def __init__(self):
        self.stages = (
            BadDataCleaner(),
            Formatter(),
            MissingDataCleaner(),
            DuplicateDataCleaner(),
        )

    def execute_jobs(self):
        """perform the sequential procedure of cleaning data"""
        for stage in self.stages:
            stage.execute()
