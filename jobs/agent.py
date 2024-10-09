from langchain_groq import ChatGroq

import streamlit as st
import yaml


class Agent:
    def __init__(self, agent_config, model_name='llama3-70b-8192'):
        self.agent_config = agent_config
        self.task_config = yaml.full_load(open('jobs/config/tasks.yaml'))
        self._llm = ChatGroq(
            temperature=0,
            groq_api_key=st.secrets['GROQ_API_KEY'],
            model_name=model_name,
        )
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

            self.messages = [
                ('system', f"{self.agent_config['role']}\n\nYour goal is to {self.agent_config['goal']}"),
            ]
            st.markdown(f':red[**System:**]\n\n{self.messages[0][1]}')

        messages = [
            self.messages[0],
            ('user', f"{task}\n\n{additional_info}\n{data}\n\nYou:")
        ]

        st.markdown(':orange[**User:**]')
        st.markdown(f'\n{task}\n\n{additional_info}')
        st.write(data)

        res = self._llm.invoke(messages)
        st.write(f':green[**Response:**]\n\n{res.content}')

        return res.content

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
