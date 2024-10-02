from pipeline.stage import Stage


class Pipeline:
    @staticmethod
    def kickoff():
        stage = Stage()
        stage.execute_jobs()
