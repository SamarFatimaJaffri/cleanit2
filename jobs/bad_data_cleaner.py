from jobs.agent import Agent
from data_buffer import Data
import re
from tools import BadDataTool as Tools

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

    def _find_bad_data_columns(self, column) -> list[int]:
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
        res = re.findall(
            r'\[[^]]*]',
            self.respond(Data.data[column], prompt, examples)
        )[0]
        indexes = eval(res)
        if not isinstance(indexes, list):
            logging.error('Indexes not returned as list', indexes)
            return []
        return indexes

    def _clean_bad_data(self, column, indexes):
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
            action = self.select_action(
                Data.data.loc[index, column], actions, examples
            )
            try:
                if action == 'NA':
                    logging.info('No action required')
                    return
                elif action.startswith('replace_bad_data'):
                    action, value = action.split(', ')
                    Tools.replace_bad_data(column, index, eval(value))
                else:
                    exec(f'Tools.{action}(index)')
            except AttributeError:
                logging.error('No action required' if action == 'NA' else 'Action not available')

    def execute(self):
        for column in Data.columns():
            indexes = self._find_bad_data_columns(column)
            self._clean_bad_data(column, indexes)
