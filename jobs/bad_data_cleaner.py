from jobs.agent import Agent
from data_buffer import Data
import re
from tools import BadDataTool as Tools, ObservationTools as OTools

import logging
import yaml


class BadDataCleaner(Agent):
    def __init__(self):
        agent_config = yaml.full_load(open('jobs/config/agents.yaml'))
        super().__init__(agent_config['BadDataExpert'])

    def _find_bad_data_values(self, column) -> tuple[list[int], str]:
        """
        Ask llm to locate bad data
        :param column: column name
        :return: list of bad data indexes
        """
        config = self.task_config['find_bad_data_values']
        prompt, examples = config['task'], config['examples']

        res = self.respond(OTools.get_values(column), prompt, examples)
        indexes = re.findall(r'\[[^]]*]', res)[0]
        res = res.replace(indexes, '')

        indexes = eval(indexes)
        if not isinstance(indexes, list):
            logging.error('Indexes not returned as list', indexes)
            return [], ''
        return indexes, res

    def _clean_bad_data(self, column, indexes, explanation):
        config = self.task_config['clean_bad_data']
        prompt, examples = config['task'], config['examples']
        for index in indexes:
            user = f'{explanation}\n\nindex: {index}, Data: {Data.data.loc[index, column]}'
            action = self.select_action(
                user, prompt, examples
            )
            try:
                if action == 'NA':
                    logging.info('No action required')
                elif action.startswith('replace_bad_data'):
                    action, value = action.split(', ')
                    evaluated = None
                    try:
                        evaluated = eval(value)
                    except Exception as e:
                        logging.exception(f'Exception: {e}.\nValue {value} cannot be evaluated')
                    Tools.replace_bad_data(column, index, evaluated if evaluated else value)
                else:
                    exec(f'Tools.{action}(index)')
            except AttributeError:
                logging.error('Action not available')

    def _replace_substrings(self, column):
        config = self.task_config['replace_substrings']
        prompt, examples = config['task'], config['examples']
        action = self.respond(
            OTools.get_values(column), prompt, examples
        )
        if action.startswith('value_correction'):
            value = action[action.index(',')+2:]

            try:
                evaluated = eval(value)
                Tools.value_correction(column, evaluated)
            except Exception as e:
                logging.exception(f'Exception: {e}.\nValue {value} is not a dictionary')

    def execute(self):
        for column in Data.columns():
            indexes, response = self._find_bad_data_values(column)
            self._clean_bad_data(column, indexes, response)
            self._replace_substrings(column)
