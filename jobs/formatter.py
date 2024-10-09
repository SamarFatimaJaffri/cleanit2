from jobs.agent import Agent
from data_buffer import Data
from tools import FormatCorrectionTools as Tools, ObservationTools as OTools

import logging
import yaml


class Formatter(Agent):
    """correct datatype of columns"""
    def __init__(self):
        agent_config = yaml.full_load(open('jobs/config/agents.yaml'))
        super().__init__(agent_config['FormatExpert'])

    def _correct_data_format(self):
        """
        correct column datatype
        :return:
        """
        config = self.task_config['correct_data_format']
        prompt, examples = config['task'], config['examples']
        for column in Data.columns():
            action = self.select_action(OTools.get_values(column), prompt, examples)
            try:
                if action == 'NA':
                    logging.info('No action required')
                elif action == 'format_to_int':
                    Tools.format_to_int(column)
                else:
                    # every other action is returned with a value i.e., `typecast_column, <type>`
                    action, value = action.split(', ')
                    # execute selected tool
                    exec(f'Tools.{action}(column, value)')
            except AttributeError:
                # if wrong tool is selected (other than enlisted ones), log error message
                logging.error('Action not available')

    def execute(self):
        self._correct_data_format()
