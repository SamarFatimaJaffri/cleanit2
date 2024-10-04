import logging

from jobs.agent import Agent
from data_buffer import Data
from tools import FormatCorrectionTools as Tools, ObservationTools as OTools


class Formatter(Agent):
    def __init__(self):
        config = {
            'designation': 'Formating Expert',
            'role': 'You are a data engineer, tasked to correct columns format.',
            'goal': 'analyze the data and based on the data decide whether the column format needs to be corrected.\n'
                    'For example a salary column with integer values, with some or all in string format would need to '
                    'be correctly formatted as int, or a date column with some or all values formatted as strings '
                    'would need to be correctly formatted as datetime, etc.',
        }
        super().__init__(config)

    def _correct_data_format(self):
        actions = """Analyze the data and correct the column format if required by taking appropriate action and if no action is required choose NA.
        You are also supposed to correct values if so requires e.g., removing commas, or characters like %, $, etc from numeric columns so that data can be analyzed.
        For all the columns that contain numeric values e.g., salary, count, etc. change the type to numeric from object / strings.
        
        Available actions:
        - value_correction, <{'old1': 'new1', 'old2': 'new2'}> (specify the dict containing old and substrings along with new substrings you want to replace them with, use escape sequence where you would in regex e.g., \^)
        - format_to_int
        - format_to_datetime, <format> (specify the date format)
        - typecast_column, <type> (specify the correct datatype)
        - NA
        
        `value_correction` action can be user in combination with other actions
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
        format_to_int
        
        User:
        0     1234
        1    3,524
        2    1,643
        3       57
        4     2459
        
        You:
        format_to_int
        
        User:
        0     True
        1    False
        2    False
        3        1
        4     True
        5     True
        6        0
        
        You:
        typecast_column, bool
        
        User:"""
        for column in Data.columns():
            action = self.select_action(OTools.get_values(column), actions, examples)
            try:
                if action.startswith('value_correction'):
                    action = action.split('\n')
                    _, value = action[0].split(', ')
                    Tools.value_correction(column, value)
                    action = action[1:]

                if action == 'NA':
                    logging.info('No action required')
                    return
                elif action == 'format_to_int':
                    Tools.format_to_int(column)
                else:
                    action, value = action.split(', ')
                    exec(f'Tools.{action}(column, value)')
            except AttributeError:
                logging.error('Action not available')

    def execute(self):
        self._correct_data_format()
