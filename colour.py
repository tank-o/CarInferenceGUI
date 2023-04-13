import colorsys

import extcolors
import pandas as pd
from colormap import rgb2hex
from matplotlib import pyplot as plt
from skimage.color import rgb2lab

from image_utils import center_of_image

colour_dict = {
    '#FF0000': 'red',
    '#711300': 'red',
    '#008000': 'green',
    '#1654AB': 'blue',
    '#002D93': 'navy',
    '#EFB300': 'yellow',
    '#977600': 'yellow',
    '#A35900': 'orange',
    '#CB8800': 'orange',
    '#800080': 'purple',
    '#FFC0CB': 'pink',
    '#000000': 'black',
    '#D9D7D7': 'white',
    '#A1A1A1': 'silver'
}


def get_colour_pallette(image, tolerance=25, limit=8):
    colors_x = extcolors.extract_from_image(image, tolerance=tolerance, limit=limit)
    color_df = color_to_df(colors_x)
    return color_df


def hex_to_rgb(hex_string: str):
    hex_string = hex_string.replace('#', '')
    rgb_triplet = tuple(int(hex_string[i:i + 2], 16) for i in (0, 2, 4))
    return rgb_triplet


def rgb_2_hsv(r, g, b):
    hsv_triplet = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return hsv_triplet

def max_saturation(hex_string: str):
    # Convert the hex string to RGB
    r, g, b = tuple(int(hex_string[i:i + 2], 16) for i in (1, 3, 5))
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # Set saturation to max
    if s > 0.3:
        s = 1.0
    # Convert HSV to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    # Convert RGB to hex string
    output_hex = '#{:02X}{:02X}{:02X}'.format(int(r * 255), int(g * 255), int(b * 255))
    # Print the output hex string
    return output_hex


def rgb_to_lab(rgb_triplet):
    # use skimage to convert hex to lab
    lab_triplet = rgb2lab(rgb_triplet)
    return lab_triplet


def hex_to_lab(hex_string: str):
    rgb_triplet = hex_to_rgb(hex_string)
    lab_triplet = rgb_to_lab(rgb_triplet)
    return lab_triplet


def narrow_down_rgb(hex_string: str):
    rgb_triplet = hex_to_rgb(hex_string)
    min_colours = {}
    for key, name in colour_dict.items():
        # Use euclidean distance to find the closest colour
        r_c, g_c, b_c = hex_to_rgb(key)
        rd = (r_c - rgb_triplet[0]) ** 2
        gd = (g_c - rgb_triplet[1]) ** 2
        bd = (b_c - rgb_triplet[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def narrow_down(lab_triplet):
    min_colours = {}
    for key,name in colour_dict.items():
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
    # resize the image to 100x100 with PIL
    car_image = car_image.resize((80,80))
    df = get_colour_pallette(car_image, tolerance=25, limit=8)
    if len(df) == 0:
        return 'Unknown'
    # get the most common colour
    most_common_colour = df['c_code'].iloc[0]
    # if the saturation is above 50, use the max saturation
    most_common_colour = max_saturation(most_common_colour)
    lab = hex_to_lab(most_common_colour)
    return narrow_down(lab)


def show_colour(hex_string: str):
    plt.switch_backend('TkAgg')
    # Create a figure and axis object
    fig, ax = plt.subplots()
    # Plot a rectangle with the given color
    rect = plt.Rectangle((0, 0), 1, 1, color=hex_string)
    ax.add_patch(rect)
    # Set the axis limits and remove the ticks
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_xticks([])
    ax.set_yticks([])
    # Show the plot
    plt.show()
