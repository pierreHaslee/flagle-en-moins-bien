import os, random
import pandas as pd
import numpy as np
import matplotlib
import PIL, PIL.Image
import streamlit as st

DEFAULT_SIZE = (2560, 1707)
MATRIX_DEFAULT_SIZE = (1707, 2560)
FLAG_PATH = os.path.join('flagle_app', 'data', 'w2560', '{}.png')
ISO_NAMES_PATH = os.path.join('flagle_app', 'data', 'country_iso2_names.csv')
ISO_NAMES = pd.read_csv(ISO_NAMES_PATH)

COUNTRIES_LIST = ISO_NAMES['Name'].to_list()

MAX_GUESS = 6


# LOADING

def get_png_name(name):
    return os.path.join(FLAG_PATH.format(ISO_NAMES.loc[ISO_NAMES.Name == name].Code.item().lower()))

def resize_image(img: PIL.Image.Image):
    img_size = img.size

    if img_size[1] > DEFAULT_SIZE[1]:
        div_factor = img_size[1] / DEFAULT_SIZE[1]
        new_x = int(np.round(img_size[0] / div_factor))
        left = (DEFAULT_SIZE[0] - new_x) // 2

        resized_img = PIL.Image.new('RGBA', DEFAULT_SIZE, (0, 0, 0, 0))
        resized_img.paste(img.resize((new_x, DEFAULT_SIZE[1])), (left, 0))

    elif img_size[1] < DEFAULT_SIZE[1]:
        top = (DEFAULT_SIZE[1] - img_size[1]) // 2

        resized_img = PIL.Image.new('RGBA', DEFAULT_SIZE, (0, 0, 0, 0))
        resized_img.paste(img, (0, top))
    
    else:
        return img.convert(mode='RGBA')

    return resized_img

def get_blank_flag():
    return PIL.Image.new('RGBA', DEFAULT_SIZE, (0, 0, 0, 0))

def get_flag_image(country_name):
    image = PIL.Image.open(get_png_name(country_name))
    resized_img = resize_image(image)
    return resized_img

def select_random_flag():
    n_countries = len(ISO_NAMES)
    i_sel = random.randint(0, n_countries)

    country_name = ISO_NAMES.iloc[i_sel]['Name']
    flag = get_flag_image(country_name)
    return flag, country_name

# PLAY FUNCTIONS

def get_processed_flag(flag):
    hsv_flag = matplotlib.colors.rgb_to_hsv(flag[:,:,:3] / 255)
    processed_flag = np.zeros(list(hsv_flag.shape[:2])+[3], dtype=np.uint8)

    (h,s,v) = (0,1,2)    

    # Hue
    processed_flag[:,:,h] = hsv_flag[:,:,h] * 10

    # Saturation
    processed_flag[:,:,s] = hsv_flag[:,:,s] * 0

    # Value
    processed_flag[:,:,v] = hsv_flag[:,:,v] * 1

    np.round(processed_flag)
    return processed_flag


def get_flag_mask(flag_1, flag_2):

    processed_flag_1 = get_processed_flag(flag_1)
    processed_flag_2 = get_processed_flag(flag_2)

    flag_mask = np.where((processed_flag_1 == processed_flag_2).all(axis=2), np.ones(MATRIX_DEFAULT_SIZE, dtype=np.uint8), np.zeros(MATRIX_DEFAULT_SIZE, dtype=np.uint8))
    return flag_mask

def get_union_flag(country_name_true, country_name_guess):

    flag_true = np.array(get_flag_image(country_name_true))
    flag_guess = np.array(get_flag_image(country_name_guess))

    flag_mask = get_flag_mask(flag_true, flag_guess)
    flag_mask_rgb = np.stack([flag_mask]*4, axis=2)

    union_flag = np.where(flag_mask_rgb==1, flag_true, np.zeros_like(flag_true))
    return union_flag

def combine_union_flags(union_original, union_to_combine):
    union_original = np.array(union_original)
    union_to_combine = np.array(union_to_combine)
    new_union = union_original.copy()
    new_union[union_to_combine[:,:,3] != 0] = union_to_combine[union_to_combine[:,:,3] != 0]
    return new_union

def np_flag_to_img(union_flag):
    return PIL.Image.fromarray(union_flag, 'RGBA')

def reset_game():
    flag, name = select_random_flag()
    st.session_state['union_flag'] = get_blank_flag()
    st.session_state['name'] = name
    st.session_state['guess_counter'] = 0
    st.session_state['guesses'] = ['']*MAX_GUESS