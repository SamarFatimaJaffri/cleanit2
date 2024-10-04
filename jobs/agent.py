from data_buffer import Data
from langchain_groq import ChatGroq

import numpy as np
import pandas as pd
import streamlit as st


class Agent:
    def __init__(self, config, model_name='llama3-70b-8192'):
        self._config = config
        self._task_config = None
        self._llm = ChatGroq(
            temperature=0,
            groq_api_key=st.secrets['GROQ_API_KEY'],
            model_name=model_name,
        )
        self.messages = []

    def task(self, config):
        self._task_config = config

        def decorator_inner(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)

            return wrapper

        return decorator_inner

    def respond(self, data, task: str, additional_info: str) -> str:
        """Get response from agent"""
        if not self.messages:
            st.subheader(self._config['designation'], divider='gray')

            self.messages = [
                ('system', f"{self._config['role']}\n\nYour goal is to {self._config['goal']}"),
            ]
            st.markdown(f':red[**System:**]\n\n{self.messages[0][1]}')

        messages = [
            self.messages[0],
            ('user', f"{task}\n\n{additional_info}\n{data}\n\nYou:")
        ]

        st.markdown(':orange[**User:**]')
        st.write(f'\n{messages[-1][1]}')

        res = self._llm.invoke(messages)
        st.write(f':green[**Response:**]\n\n{res.content}')

        return res.content

    def select_action(self, data, task: str, examples: str) -> str:
        """Ask agent to choose an action based on data observation"""
        action = self.respond(data, task, examples)
        return action
