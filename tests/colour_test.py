import os

import cv2
import pandas as pd

import image_utils
from anpr import ANPR
from colour import get_car_colour

if __name__ == "__main__":
    anpr = ANPR('../weights/small-300E-600I.pt')
    # Get image with OpenCV
    actual_colours = {
        '0.jpg': 'white',
        '1.jpg': 'blue',
        '2.jpg': 'white',
        '3.jpg': 'red',
        '4.jpg': 'silver',
        '5.jpg': 'red',
        '6.jpg': 'yellow',
        '7.png': 'yellow',
        '8.png': 'red',
        '9.jpg': 'green',
        '10.jpg': 'white',
        '11.jpg': 'silver',
        '12.jpg': 'white',
        '13.png': 'yellow',
        '14.jpg': 'blue',
        '15.jpg': 'blue',
        '16.jpg': 'blue',
        '17.jpg': 'blue',
        '18.jpg': 'black',
        '19.jpg': 'black',
        '20.jpg': 'black',
        '21.jpg': 'white',
        '22.png': 'white',
        '23.jpg': 'white',
        '24.jpg': 'white',
        '25.jpg': 'silver',
        '26.jpg': 'silver',
        '27.jpg': 'silver',
        '28.jpg': 'orange',
        '29.jpg': 'orange',
        '30.jpg': 'yellow',
        '31.jpg': 'yellow',
        '32.jpg': 'yellow',
    }

    results = {

    }

    predicted = []
    actual = []

    # loop through each file in the directory
    for filename in os.listdir('colour_tests'):
        # ignore non-jpeg files
        if not filename.endswith(('.jpg', '.jpeg', '.png')):
            continue

        # get the full path to the file
        filepath = os.path.join('colour_tests', filename)

        # open the file
        image = cv2.imread(filepath)

        # run the image through the model
        data = anpr.get_main_detections(image)
        car = data['car']
        car_img = image_utils.crop_bbox(image, car)
        car_pil = image_utils.cv_2_pil(car_img)
        expected_colour = actual_colours[filename]
        # check if the colour is correct
        colour = get_car_colour(car_pil)
        results[filename] = (colour.lower() == expected_colour.lower())
        print(f'{filename} - got:{colour} - expected:{expected_colour}')
        predicted.append(colour)
        actual.append(expected_colour)

    # get the count of correct and incorrect results
    correct = sum(results.values())
    incorrect = len(results) - correct
    print(f'Correct: {correct} - Incorrect: {incorrect}')
    print(f'Accuracy: {correct / len(results) * 100}%')

    # get the confusion matrix
    df_confusion = pd.crosstab(actual, predicted)
    print(df_confusion)
