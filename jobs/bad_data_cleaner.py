from jobs.agent import Agent
from data_buffer import Data
import re
from tools import BadDataTool as Tools, ObservationTools as OTools

import logging


class BadDataCleaner(Agent):
    def __init__(self):
        config = {
            'designation': 'Bad Data Expert',
            'role': 'You are an experienced data engineer, tasked to clean the bad-data.',
            'goal': 'analyze the data and based on your expertise find the bad data from given values.\n'
                    'A value can be called as bad data if it is a misspelled name, wrongly formatted value as compared '
                    'to other values such as a temperature containing all values in celsius, but few in fahrenheit, '
                    'then fahrenheit values will be considered as bad data, A bad data can either be corrected or '
                    # 'then fahrenheit values will be considered as bad data, or an outlier i.e., excessively large or '
                    # 'a very small value as compared to other listed values. A bad data can either be corrected or '
                    'removed if it is not possible to predict the correct value.'
        }
        super().__init__(config)

    def _find_bad_data_columns(self, column) -> tuple[list[int], str]:
        """
        Ask llm to locate bad data
        :param column: column name
        :return: list of bad data indexes
        """
        prompt = """Analyze the data and locate bad data from all the values, return the indexes of all the bad data values, and if there is no bad data return []
        """
        examples = """User:
        0         0.000042
        1        83.000000
        2        75.000000
        3        38.000000
        4        56.000000
        5        64.000000
        6        74.000000
        7        23.000000
        8    757483.000000
        9        75.000000
        
        You:
        [0, 8]
        
        User:
        0       Red
        1      Blue
        2    Yellow
        3     Green
        4    Opaque
        
        You:
        []
        
        User:"""

        res = self.respond(OTools.get_values(column), prompt, examples)
        indexes = re.findall(r'\[[^]]*]', res)[0]
        res = res.replace(indexes, '')

        indexes = eval(indexes)
        if not isinstance(indexes, list):
            logging.error('Indexes not returned as list', indexes)
            return [], ''
        return indexes, res

    def _clean_bad_data(self, column, indexes, explanation):
        actions = """Analyze the data and select the action best suitable to perform on the bad-data values based on your analysis
        Available actions:
        - replace_bad_data, <value> (specify value to replace the previous value with)
        - remove_bad_data
        - NA
        """
        examples = """User:
        INdia
        
        You:
        replace_bad_data, India
        
        User:
        0&4659
        
        You:
        remove_bad_data
        
        User:"""
        for index in indexes:
            user = f'index: {index}, Data: {Data.data.loc[index, column]}\n{explanation}'
            action = self.select_action(
                user, actions, examples
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
                logging.error('No action required' if action == 'NA' else 'Action not available')

    def _replace_substrings(self, column):
        prompt = """Analyze the data and make corrections in the data if required by removing unwanted substrings from values such as commas, or characters like %, $, etc from numeric columns so that data can be analyzed and if no correction is required choose NA.

        You must remove all non-numeric substring from the numeric columns like salary, count, etc.

        Available actions:
        - value_correction, <{'old1': 'new1', 'old2': 'new2'}> (specify the python dictionary containing old substrings you want to replace, with new substrings you want to replace them with. You must use escape sequence where you would in python regex like \^)
        - NA
        """
        examples = """User:
        0      $362
        1      8300
        2     7,597
        3     $3820
        4       565
        5      6472
        6     7,425
        7    $232.0
        8       733

        You:
        value_correction, {'\$': '', ',': ''}

        User:"""
        action = self.respond(
            OTools.get_values(column), prompt, examples
        )
        if action.startswith('value_correction'):
            value = action[action.index(',')+2:]
            evaluated = None
            try:
                evaluated = eval(value)
            except Exception as e:
                logging.exception(f'Exception: {e}.\nValue {value} is not a dictionary')
            Tools.value_correction(column, evaluated if evaluated else value)

    def execute(self):
        for column in Data.columns():
            indexes, response = self._find_bad_data_columns(column)
            self._clean_bad_data(column, indexes, response)
            self._replace_substrings(column)
