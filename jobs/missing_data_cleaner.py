from jobs.agent import Agent
from data_buffer import Data
from tools import MissingValueTools as Tools

import numpy as np
import pandas as pd


class MissingDataCleaner(Agent):
    """clean missing values column by column"""
    def __init__(self):
        config = {
            'designation': 'Missing Values Expert',
            'role': 'You are an data engineer, tasked to clean the missing data.',
            'goal': 'analyze the data and based on your expertise decide what action to take for null values.\n'
                    'For example, you can fill data with mean if it is a normal distribution, you can fill it with '
                    'median when the data is skewed, and with median if data is categorical or discrete, or you can '
                    'delete the record if you can\'t decide and there are very few missing values, or you can fill all '
                    'the nulls with some specific value, etc.'
        }
        super().__init__(config)

    def _clean_numeric_values(self, column):
        actions = """Analyze the data and select the action best suitable to perform on the missing values based on your analysis
        Available actions:
        - remove_nulls
        - fill_with_mean
        - fill_with_median
        - fill_with_mode
        
        For example,
        remove_nulls
        """
        examples = """User:
        0     56.0
        1     85.0
        2     48.0
        3     14.0
        4     87.0
        5     25.0
        6     86.0
        7      NaN
        8     46.0
        9     35.0
        10    47.0
        Name: sales, dtype: float64
        
        You:
        remove_nulls
        
        User:
        0     89.58
        1     95.59
        2    103.57
        3    115.64
        4    120.29
        5    114.37
        6     84.34
        7     82.78
        8    119.45
        9     93.59
        Name: height, dtype: float64
        
        You:
        fill_with_mean
        
        User:
        0    13
        1     4
        2     9
        3    26
        4     8
        5     6
        6    10
        7     7
        8     3
        9     8
        Name: in_stock, dtype: int64
        
        You:
        fill_with_median
        
        User:"""
        action = self.select_action(Data.data[column], actions, examples)
        try:
            exec(f'Tools.{action}(column)')
        except AttributeError:
            Tools.remove_nulls(column)

    def _clean_non_numeric_values(self, column):
        actions = """Analyze the data and select the action best suitable to perform on the missing values based on your analysis
        Available actions:
        - remove_nulls
        - fill_nulls, <value> (specify value to fill nulls with)
        - fill_with_mode
        
        For example,
        fill_nulls, regular_pack
        """
        examples = """User:
        0      Oliver
        1        None
        2        Noah
        3         Ava
        4        Liam
        5      Sophia
        6       Jacob
        7    Isabella
        8       Mason
        9      Olivia
        Name: name, dtype: object 
        
        You:
        remove_nulls
        
        User:
        0       Brazil
        1    Australia
        2       Canada
        3        Spain
        4        None
        Name: country, dtype: object 
        
        You:
        fill_nulls, unspecified
        
        User:
        0    cat
        1    dog
        2    cat
        3    cat
        4    cat
        Name: pet, dtype: object
        
        You:
        fill_with_mode
        
        User:"""
        action = self.select_action(Data.data[column], actions, examples)
        try:
            if action.startswith('fill_nulls'):
                action, value = action.split(', ')
                Tools.fill_nulls(column, eval(value))
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
