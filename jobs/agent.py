import streamlit as st
import yaml
from openai import OpenAI


class Agent:
    def __init__(self, agent_config, model_name='o1-mini'):
        self.agent_config = agent_config
        self.task_config = yaml.full_load(open('jobs/config/tasks.yaml'))
        if st.session_state.client['provider'] == 'OPENAI':
            self._client = OpenAI(
                api_key=st.session_state.client['API_KEY'],
            )
        else:
            self._client = OpenAI(
                api_key=st.session_state.client['API_KEY'],
                base_url=st.secrets[f"{st.session_state.client['provider']}_URL"],
            )
        self._model_name = model_name
        self.messages = []

    def respond(self, data, task: str, additional_info: str) -> str:
        """
        Get response from agent
        :param data: data as specified by user
        :param task: task description
        :param additional_info: extra information like explanation of why data is marked as bad data
        :return:
        """
        if not self.messages:
            st.subheader(self.agent_config['designation'], divider='gray')

            self.messages = [{
                'role': 'system',
                'content': f"{self.agent_config['role']}\n\nYour goal is to {self.agent_config['goal']}",
            }]
            st.markdown(f":red[**System:**]\n\n{self.messages[0]['content']}")

        messages = [
            self.messages[0],
            {
                'role': 'user',
                'content': f'{task}\n\n{additional_info}\n{data}\n\nYou:',
            },
        ]

        st.markdown(':orange[**User:**]')
        st.markdown(f'\n{task}\n\n{additional_info}')
        st.write(data)

        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
        )
        response = response.choices[0].message.content
        st.write(f':green[**Response:**]\n\n{response}')

        return response

    def select_action(self, data, task: str, examples: str) -> str:
        """
        Ask agent to choose an action based on data observation
        :param data: data as specified by user
        :param task: task description
        :param examples: for few shot prompting
        :return:
        """
        action = self.respond(data, task, examples)
        return action
