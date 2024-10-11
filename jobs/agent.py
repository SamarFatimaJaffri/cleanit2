import logging

import streamlit as st
import yaml
from openai import OpenAI

from session import Session


class Agent:
    def __init__(self, agent_config, model_name='o1-mini'):
        self.agent_config = agent_config
        self.task_config = yaml.full_load(open('jobs/config/tasks.yaml'))
        self._model_name = model_name
        self.messages = []

        params = {}
        if Session.api_key and Session.provider:
            params['api_key'] = Session.api_key
            if Session.provider != 'OPENAI':
                params['base_url'] = st.secrets[f'{Session.provider}_URL']
        self._client = OpenAI(**params)

    def respond(self, data, task: str, extra_info: str) -> str:
        """
        Get response from agent
        :param data: data as specified by user
        :param task: task description
        :param extra_info: examples for few short prompting or info like why data is marked as bad data
        :return:
        """
        messages = [{
            'role': 'user',
            'content': f"{self.messages[0]['content']}\n\n{task}\n\n{extra_info}\n{data}\n\nYou:",
        }]

        st.markdown(':orange[**User:**]')
        st.markdown(f'\n{task}\n\n{extra_info}')
        st.write(data)

        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            max_completion_tokens=25000,
        )
        response = response.choices[0].message.content
        st.write(f':green[**Response:**]\n\n{response}')

        return response

    def get_response(self, data, task: str, extra_info: str) -> str:
        """
        Ask agent to choose an action based on data observation
        :param data: data as specified by user
        :param task: task description
        :param extra_info: examples for few shot prompting or context of last action(s)
        :return:
        """
        if not self.messages:
            st.subheader(self.agent_config['designation'], divider='gray')

            self.messages = [{
                'role': 'system',
                'content': f"{self.agent_config['role']}\n\nYour goal is to {self.agent_config['goal']}",
            }]
            st.markdown(f":red[**System:**]\n\n{self.messages[0]['content']}")

        response = self.respond(data, task, extra_info)
        if not response:
            self.messages['content'] = ''
            logging.debug('No response from the model; retrying without system prompt')
            response = self.respond(data, task, extra_info)
        if not response:
            response = self.respond(data, task, '')
            logging.debug('No response from the model; retrying without examples / prev action context')
            response = self.respond(data, task, extra_info)
        if not response:
            logging.debug('No response from the model; taking no action')

        return response
