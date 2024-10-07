import streamlit as st

from src.play_utils import select_random_flag, get_blank_flag, reset_game
from src.app_utils import display_difficulty

st.set_page_config(initial_sidebar_state='collapsed', layout='wide')

st.title('FLAGLE EN MOINS BIEN')

col1, col2 = st.columns([0.3, 0.7])

with col1:
    st.session_state['difficulty'] = st.radio('difficulty', [0, 1, 2, 3, 4], index=0, format_func=display_difficulty)

with st.container():
    if st.button(label='PLAY'):
        reset_game(difficulty=st.session_state.difficulty)
        st.switch_page('pages/play.py')