import logging
import re

import yaml

from data_buffer import Data
from jobs.agent import Agent
from tools import BadDataTool as Tools
from tools import ObservationTools as OTools


class BadDataCleaner(Agent):
    """locate and fix bad data one by one from each column,
    check if column need sub-string removal and modify the values"""
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
        # get the indexes array from the response
        indexes = re.findall(r'\[[^]]*]', res)[0]
        # remove the array from the response to keep the explanation for cleaning task
        res = res.replace(indexes, '')

        indexes = eval(indexes)  # evaluate string to get list i.e., '[1, 2]' > [1, 2]
        if not isinstance(indexes, list):
            logging.error('Indexes not returned as list', indexes)
            return [], ''
        return indexes, res

    def _clean_bad_data(self, column, indexes, explanation):
        """
        Clean the values at indexes marked as bad data
        :param column: column name
        :param indexes: bad data indexes
        :param explanation: explanation returned by llm of why indexes are bad data
        :return:
        """
        config = self.task_config['clean_bad_data']
        prompt, examples = config['task'], config['examples']
        for index in indexes:
            # send explanation, index and bad data to llm
            user = f'{explanation}\n\nindex: {index}, Data: {Data.data.loc[index, column]}'
            action = self.select_action(
                user, prompt, examples
            )

            try:
                if action == 'NA':
                    logging.info('No action required')
                elif action.startswith('replace_bad_data'):
                    # replace_bad_data is returned with a value i.e., `replace_bad_data, <value>`
                    action, value = action.split(', ')

                    # evaluate the given string to get value in actual datatype i.e., 'False' > False
                    evaluated = None
                    try:
                        evaluated = eval(value)
                    except Exception as e:
                        logging.exception(f'Exception: {e}.\nValue {value} cannot be evaluated')

                    # if a values can't be evaluated i.e., is string use it as it is
                    Tools.replace_bad_data(column, index, evaluated if evaluated else value)
                else:
                    # execute selected tool
                    exec(f'Tools.{action}(index)')
            except AttributeError:
                # if wrong tool is selected (other than enlisted ones), log error message
                logging.error('Action not available')

    def _replace_substrings(self, column):
        """
        Check if column need further modification and replace substrings if specified
        :param column: column name
        :return:
        """
        config = self.task_config['replace_substrings']
        prompt, examples = config['task'], config['examples']
        action = self.respond(
            OTools.get_values(column), prompt, examples
        )
        if action.startswith('value_correction'):
            # value_correction action is returned with a dict i.e., value_correction, <{'old1': 'new1'}>
            #   get the dict from the string value
            value = action[action.index(',') + 2:]

            # evaluate the given string to get dictionary i.e., '{'e1': ''}' > {'e1': ''}
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
