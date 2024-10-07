import os, random
import pandas as pd
import numpy as np
import matplotlib
import PIL, PIL.Image
import streamlit as st

DEFAULT_SIZE = (2560, 1707)
RESIZE_SIZE = (853, 569)
MATRIX_DEFAULT_SIZE = (RESIZE_SIZE[1], RESIZE_SIZE[0])
FLAG_PATH = os.path.join('flagle_app', 'data', 'w2560', '{}.png')
ISO_NAMES_PATH = os.path.join('flagle_app', 'data', 'country_info.csv')
ISO_NAMES = pd.read_csv(ISO_NAMES_PATH, delimiter=';').drop_duplicates(subset=['Impact Country'])

COUNTRIES_LIST = ISO_NAMES['Impact Country'].to_list()

MAX_GUESS = 6


# LOADING

def get_png_name(name):
    return os.path.join(FLAG_PATH.format(ISO_NAMES.loc[ISO_NAMES['Impact Country'] == name].ISO2.item().lower()))

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
        resized_img = img.convert(mode='RGBA')

    return resized_img.resize(RESIZE_SIZE)

def get_blank_flag():
    return PIL.Image.new('RGBA', RESIZE_SIZE, (0, 0, 0, 0))

def get_flag_image(country_name):
    image = PIL.Image.open(get_png_name(country_name))
    resized_img = resize_image(image)
    return resized_img

def diff_to_pop(diff):
    if diff==0:
        return 50000000
    if diff==1:
        return 100000
    if diff==2:
        return 30000
    if diff==3:
        return 5000
    if diff==4:
        return 0
    
def select_random_flag(difficulty=0):
    valid_difficulty_index = ISO_NAMES.loc[ISO_NAMES.Population >= diff_to_pop(difficulty)].index
    n_countries = len(valid_difficulty_index)
    i_sel = random.randint(0, n_countries)

    country_name = ISO_NAMES.loc[ISO_NAMES.index == valid_difficulty_index[i_sel]]['Impact Country'].item()
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


def get_flag_mask_deprecated(flag_1, flag_2):

    processed_flag_1 = get_processed_flag(flag_1)
    processed_flag_2 = get_processed_flag(flag_2)

    flag_mask = np.where((processed_flag_1 == processed_flag_2).all(axis=2), np.ones(MATRIX_DEFAULT_SIZE, dtype=np.uint8), np.zeros(MATRIX_DEFAULT_SIZE, dtype=np.uint8))
    return flag_mask

def get_hsv_flag(flag):
    return matplotlib.colors.rgb_to_hsv(flag[:,:,:3] / 255)

def filter_flag_mask(flag_mask):
    kernel_size = 4
    threshold_ratio = 0.1
    threshold = (kernel_size*2+1)**2*threshold_ratio

    max_i, max_j = flag_mask.shape
    flag_int = flag_mask.astype(np.uint8)
    for i in range(max_i):
        for j in range(max_j):
            slice_i = slice(max(0, i-kernel_size), min(max_i, i+1+kernel_size))
            slice_j = slice(max(0, j-kernel_size), min(max_j, j+1+kernel_size))
            if flag_int[slice_i, slice_j].sum() <= threshold:
                flag_mask[i, j] = False

    return flag_mask

def get_flag_mask(flag_1, flag_2):
    hsv_flag_1 = get_hsv_flag(flag_1)
    hsv_flag_2 = get_hsv_flag(flag_2)

    flag_diff_1 = np.abs(hsv_flag_1 - hsv_flag_2)
    flag_diff_2 = np.abs(flag_diff_1 - np.stack([np.ones(MATRIX_DEFAULT_SIZE)]+[np.zeros(MATRIX_DEFAULT_SIZE)]*2, axis=2))
    flag_diff = np.minimum(flag_diff_1, flag_diff_2)
    flag_mask = np.where((flag_diff[:,:,0] <= 0.06) & (flag_diff[:,:,1] <= 0.35) & (flag_diff[:,:,2] <= 0.35) & (flag_2[:,:,3] != 0), np.ones(MATRIX_DEFAULT_SIZE, dtype=np.uint8), np.zeros(MATRIX_DEFAULT_SIZE, dtype=np.uint8))
    return filter_flag_mask(flag_mask)

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

def reset_game(**kwargs):
    flag, name = select_random_flag(**kwargs)
    st.session_state['union_flag'] = get_blank_flag()
    st.session_state['name'] = name
    st.session_state['guess_counter'] = 0
    st.session_state['guesses'] = ['']*MAX_GUESS
    st.session_state['guesses_union_flag'] = [get_blank_flag()]*MAX_GUESS
    st.session_state['won'] = False

def country_info(name):
    row = ISO_NAMES.loc[ISO_NAMES['Impact Country'] == name]
    capital = row.Capital.item()
    population = row.Population.item()
    st.html(
        '''
        <details>
        <summary>Capital</summary>
        {}
        </details>
        '''.format(capital)
        )

    st.html(
        '''
        <details>
        <summary>Population</summary>
        {:,}
        </details>
        '''.format(population)
        )