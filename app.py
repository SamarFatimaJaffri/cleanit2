from pathlib import Path

import pandas as pd
import streamlit as st

from data_buffer import Data
from pipeline import Pipeline
from session import Session

st.set_page_config(layout="wide")


@st.cache_data
def get_dataframe(data) -> pd.DataFrame | None:
    if not data:
        return

    suffix = Path(data.name).suffix
    if suffix == '.csv':
        df = pd.read_csv(data)
    else:
        df = pd.DataFrame(data)
    return df


def get_api_key():
    providers = {'OPENAI': 'OPENAI', 'AI/ML API': 'AIMLAPI'}

    # get technology provider and api key
    provider = st.selectbox(
        label='Choose your technology provider',
        options=providers.keys(),
        help='Your API KEY provider'
    )
    api_key = st.text_input('Enter your API KEY')

    return providers[provider], api_key


class App:
    def style(self):
        # load style
        with open('.streamlit/style.css') as css:
            st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

        # set app logo
        st.logo(image='images/logo.png', icon_image='images/icon.png')

        with st.container():
            _, col1, col2 = st.columns([0.05, 0.55, 0.4], gap='large', vertical_alignment='center')
            with _:
                pass

            with col1:
                st.header('Clean It')
                st.markdown('- Tired of cleaning bad data?' + '  \n'
                            '- Unable to perform analysis because data is not clean?' + '  \n'
                            '- Don\'t want to clean data but have to, as who else will?')

                st.markdown('We will, Yup!' + '  \n' + 'Give your bad-data worries to us, and let us clean it for you!')

                # set client provider
                with st.popover('Setup Client', help='Specify your provider and API key'):
                    Session.provider, Session.api_key = get_api_key()

            with col2:
                st.image('./images/o1-mini-img.png', width=230)

    def main(self):
        self.style()

        def save_data(dataframe):
            Data.data = dataframe

        st.container(height=50, border=0)

        col1, col2 = st.columns(2, gap='medium', vertical_alignment='center')
        with col1:
            # load data
            df = None
            with st.form('data'):
                data = st.file_uploader('Upload the data', type=['csv', 'json'])

                # make pandas dataframe for processing
                if data:
                    df = get_dataframe(data)
                    st.dataframe(df, height=150)

                submitted = st.form_submit_button('Clean it →', on_click=save_data(df))

        with col2:
            st.subheader('Insert you data\n\n')
            st.markdown('Insert you data into the system so that we can fix' + '  \n'
                        '- the misspelled names' + '  \n'
                        '- the outliers' + '  \n'
                        '- null values' + '  \n'
                        'and many other issue that make your data bad')
            st.markdown('_Make sure you have setup the client before inserting data_')

        # clean and analyze data
        if isinstance(df, pd.DataFrame) and submitted:
            with st.status('🤖 **Agents at work...**', state='running', expanded=True) as status:
                with st.container(height=500, border=False):
                    pipeline = Pipeline()
                    pipeline.kickoff()
                status.update(label='✅ Data Cleaned!', state='complete', expanded=False)

            st.subheader('Here is your cleaned data', anchor=False, divider='rainbow')
            Data.data = Data.data.reset_index(drop=True)
            st.write(Data.data)


if __name__ == '__main__':
    app = App()
    app.main()
