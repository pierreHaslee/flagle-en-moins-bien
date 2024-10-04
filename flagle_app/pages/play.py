import streamlit as st

from src.play_utils import get_union_flag, combine_union_flags, np_flag_to_img, select_random_flag, get_blank_flag, reset_game, get_flag_image
from src.play_utils import COUNTRIES_LIST, MAX_GUESS

st.set_page_config(initial_sidebar_state='collapsed', layout='wide')

if 'play_again' in st.session_state.keys() and st.session_state.play_again:
    reset_game()

with st.container():
    st.title('Find the secret flag')

col1, col2 = st.columns([0.7, 0.3])

with col1:
    with st.container():

        if 'selected_country' in st.session_state.keys() and st.session_state.selected_country != 'Select a Country':
            st.session_state.guesses[st.session_state.guess_counter] = st.session_state.selected_country
            st.session_state['guess_counter'] += 1
            new_union_flag = combine_union_flags(st.session_state['union_flag'], get_union_flag(st.session_state.name, st.session_state.selected_country))
            st.session_state['union_flag'] = np_flag_to_img(new_union_flag)
            
            if st.session_state.selected_country.strip().lower() == st.session_state['name'].strip().lower():
                st.header('YOU WON!!')
                st.subheader('The flag was {}'.format(st.session_state['name']))
                st.button('PLAY AGAIN', key='play_again')

            st.session_state.selected_country = 'Select a Country'

        st.image(st.session_state['union_flag'])

        

    with st.container():
        if st.session_state.guess_counter < MAX_GUESS:
            st.selectbox(label='',
                        options=['Select a Country']+COUNTRIES_LIST,
                        index=0,
                        key='selected_country')
        else:
            st.header('You lost.')
            st.subheader('The flag was {}'.format(st.session_state['name']))
            st.image(get_flag_image(st.session_state['name']))
            st.button('PLAY AGAIN', key='play_again')

with col2:
    with st.container():
        st.header('{} guesses left.'.format(MAX_GUESS-st.session_state['guess_counter']))
        for i in range(MAX_GUESS):
            st.subheader('{}.   {}'.format(i, st.session_state['guesses'][i]))
            if st.session_state.guesses[i] != '':
                st.image(get_flag_image(st.session_state['guesses'][i]), width=35)