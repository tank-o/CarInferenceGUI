import time

import extcolors
import pandas as pd
from matplotlib.colors import rgb2hex
from colormap import rgb2hex
from skimage.color import rgb2lab
from image_utils import center_of_image

colour_dict = {
    'red': '#FF0000',
    'green': '#008000',
    'blue': '#0000FF',
    'dark blue': '#00008B',
    'dark green': '#006400',
    'light_yellow': '#FFFF00',
    'yellow': '#DBC742',
    'orange': '#FFA500',
    'purple': '#800080',
    'pink': '#FFC0CB',
    'black': '#000000',
    'white': '#FFFFFF',
    'grey': '#808080',
    'gray': '#808080',
    'silver': '#C0C0C0',
}


def get_colour_pallette(image, tolerance=25, limit=8):
    colors_x = extcolors.extract_from_image(image, tolerance=tolerance, limit=limit)
    color_df = color_to_df(colors_x)
    return color_df


def hex_to_rgb(hex_string: str):
    hex_string = hex_string.replace('#', '')
    rgb_triplet = tuple(int(hex_string[i:i + 2], 16) for i in (0, 2, 4))
    return rgb_triplet


def rgb_to_lab(rgb_triplet):
    # use skimage to convert hex to lab
    lab_triplet = rgb2lab(rgb_triplet)
    return lab_triplet


def hex_to_lab(hex_string: str):
    rgb_triplet = hex_to_rgb(hex_string)
    lab_triplet = rgb_to_lab(rgb_triplet)
    return lab_triplet


def get_colour_name_rgb(hex_string: str):
    rgb_triplet = hex_to_rgb(hex_string)
    min_colours = {}
    for name, key in colour_dict.items():
        # Use euclidean distance to find the closest colour
        r_c, g_c, b_c = hex_to_rgb(key)
        rd = (r_c - rgb_triplet[0]) ** 2
        gd = (g_c - rgb_triplet[1]) ** 2
        bd = (b_c - rgb_triplet[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def narrow_down(lab_triplet):
    min_colours = {}
    for name, key in colour_dict.items():
        # Use euclidean distance to find the closest colour
        r_c, g_c, b_c = hex_to_lab(key)
        rd = (r_c - lab_triplet[0]) ** 2
        gd = (g_c - lab_triplet[1]) ** 2
        bd = (b_c - lab_triplet[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def color_to_df(input):
    colors_pre_list = str(input).replace('([(', '').split(', (')[0:-1]
    df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
    df_count = [i.split('), ')[1].replace(')', '') for i in colors_pre_list]
    # conver the count to a percentage of the total
    df_percent = [int(i) / sum([int(i) for i in df_count]) for i in df_count]
    # convert RGB to HEX code
    df_color_up = [
        rgb2hex(int(i.split(',')[0].replace('(', '')), int(i.split(',')[1]), int(i.split(',')[2].replace(')', ''))) for
        i in df_rgb]
    df = pd.DataFrame(zip(df_color_up, df_percent), columns=['c_code', 'occurence'])
    return df


def get_car_colour(image):
    car_image = center_of_image(image)
    df = get_colour_pallette(car_image, tolerance=25, limit=8)
    # get the most common colour
    most_common_colour = df['c_code'].iloc[0]
    print(most_common_colour)
    lab = hex_to_lab(most_common_colour)
    return narrow_down(lab)
