import os
import json
import time
import logging
import requests
from base64 import b64encode

import cv2
import emoji
import numpy as np
from PIL import Image
from easydict import EasyDict as edict

import streamlit as st

from src.constants import *
from src.utils import (read_yaml, open_image, query_file_kb,
                       resize_to_aspect_ratio_and_limit_length, resize_img_bytes)


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()
app_cfg = edict(read_yaml(CONFIG_FILE))

st.beta_set_page_config(page_title = 'Tweak Story', page_icon = app_cfg.page_icon)
st.set_option('deprecation.showfileUploaderEncoding', False)


# user input on sidebar
st.sidebar.header('Step 1: Upload Image')
img_buffer = st.sidebar.file_uploader(
    '',
    type = ['png', 'jpg', 'jpeg']
)
st.sidebar.text(" \n")
st.sidebar.text(" \n")

st.sidebar.header('Step 2: Select Your Flavors')
st.sidebar.text(" \n")
len_choices = tuple([k for k in SENTENCE_CLASS_MAP.keys()])
sentence_class_str = st.sidebar.selectbox( '', len_choices)
emoji_choices = tuple([k for k in EMOJI_CLASS_MAP.keys()])
emoji_class_str = st.sidebar.selectbox('', emoji_choices)
st.sidebar.text(" \n")
st.sidebar.text(" \n")

st.sidebar.header('Step 3: Generate Caption!')
st.sidebar.text(" \n")
is_run = st.sidebar.button('RUN')


# propagate user input to model run
if img_buffer is not None:
    demo_flag = False
else:
    img_buffer = open(app_cfg.demo_image, 'rb')
    demo_flag = True

img_bytes = img_buffer.read()
if query_file_kb(img_bytes) >= app_cfg.max_img_kb:
    img_bytes = resize_img_bytes(img_bytes, app_cfg.img_display)

caption = emoji.emojize(f"{DEFAULT_PADDING} :backhand_index_pointing_left: {PADDING_CODE} Press RUN Button to Generate Caption")

if is_run:
    sentence_class = SENTENCE_CLASS_MAP[sentence_class_str]
    emoji_class = EMOJI_CLASS_MAP[emoji_class_str]
    b64_img_str = b64encode(img_bytes).decode('ascii')
    
    body = dict(
            sentence_class = sentence_class,
            emoji_class = emoji_class,
            b64_img_str = b64_img_str
        )

    try:
        # TODO: toggle different host for local mode v.s. docker mode
        res = requests.post(
                url = f'{HOST}:{PORT}{ROUTE}',
                data = json.dumps(body)
            )
                
        caption = emoji.emojize(res.json()['output'])
        caption = f'{DEFAULT_PADDING} <b>CAPTION</b> {caption}'
    except:
        logger.info('error occured when sending requests to API')
        caption = f'{DEFAULT_PADDING} <b>ERROR</b> Request Error. Retry Again!'


# display image (preserve aspect ratio)
np_img = open_image(img_bytes, demo_flag)
np_img = resize_to_aspect_ratio_and_limit_length(np_img, app_cfg.img_display)

st.image(Image.fromarray(np_img), use_column_width = False)
st.write('')
st.markdown(f""" <h3> {caption} </h3> """, 
            unsafe_allow_html = True)

