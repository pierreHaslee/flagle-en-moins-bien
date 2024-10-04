import streamlit as st

from src.play_utils import select_random_flag, get_blank_flag, reset_game

st.set_page_config(initial_sidebar_state='collapsed', layout='wide')

if st.button(label='PLAY'):
    reset_game()

    st.switch_page('pages/play.py')