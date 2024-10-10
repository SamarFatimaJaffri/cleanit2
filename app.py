from pathlib import Path

import pandas as pd
import streamlit as st

from data_buffer import Data
from pipeline import Pipeline


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


@st.dialog('Provide API KEY')
def get_api_key():
    providers = {'OPENAI': 'OPENAI', 'AI/ML API': 'AIMLAPI'}

    # technology provider dropdown
    provider = st.selectbox(
        label='Choose your technology provider',
        options=providers.keys(),
        help='Your API KEY provider'
    )

    # api key text area
    api_key = st.text_input('Enter your API KEY')

    # refresh after the pictures have been uploaded
    if st.button('Done'):
        st.session_state.client = {
            'provider': providers[provider],
            'API_KEY': api_key
        }
        st.rerun()


class App:
    def main(self):
        def save_data(dataframe):
            Data.data = dataframe

        st.logo(image='images/logo.png', icon_image='images/icon.png')

        if 'is_expanded' not in st.session_state:
            st.session_state['is_expanded'] = True
        with st.expander('User Data', expanded=st.session_state['is_expanded']):
            # load data
            df = None
            with st.form('data', border=False):
                data = st.file_uploader('Upload the data', type=['csv', 'json'])

                # make pandas dataframe for processing
                if data:
                    df = get_dataframe(data)
                    st.dataframe(df, height=150)

                submitted = st.form_submit_button('Clean it →', on_click=save_data(df))
            st.session_state['is_expanded'] = False

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
    # initialize empty client
    if not st.session_state.get('client'):
        st.session_state.client = {'provider': None, 'API_KEY': None}

    # set client
    if not all(st.session_state.get('client').values()):
        get_api_key()

    app = App()
    app.main()
