from jobs.agent import Agent
from data_buffer import Data
from tools import MissingValueTools as Tools, ObservationTools as OTools

import logging
import numpy as np
import yaml


class MissingDataCleaner(Agent):
    """clean missing values column by column"""
    def __init__(self):
        agent_config = yaml.full_load(open('jobs/config/agents.yaml'))
        super().__init__(agent_config['MissingValuesExpert'])

    def _clean_numeric_values(self, column):
        config = self.task_config['clean_numeric_values']
        prompt, examples = config['task'], config['examples']
        action = self.select_action(OTools.get_values(column), prompt, examples)
        try:
            exec(f'Tools.{action}(column)')
        except AttributeError:
            Tools.remove_nulls(column)

    def _clean_non_numeric_values(self, column):
        config = self.task_config['clean_non_numeric_values']
        prompt, examples = config['task'], config['examples']
        action = self.select_action(Data.data[column], prompt, examples)
        try:
            if action.startswith('fill_nulls'):
                action, value = action.split(', ')
                evaluated = None
                try:
                    evaluated = eval(value)
                except Exception as e:
                    logging.exception(f'Exception: {e}.\nValue {value} cannot be evaluated')
                Tools.fill_nulls(column, evaluated if evaluated else value)
            else:
                exec(f'Tools.{action}(column)')
        except AttributeError:
            Tools.remove_nulls(column)

    def execute(self):
        """clean missing values column by column"""
        null_columns = Tools.get_column_having_nulls()

        for column in null_columns:
            if np.issubdtype(Data.data[column].dtype, np.number):
                self._clean_numeric_values(column)
            else:
                self._clean_non_numeric_values(column)
