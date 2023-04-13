import os

import cv2

import image_utils
from anpr import ANPR

if __name__ == "__main__":
    anpr = ANPR('../weights/small-300E-600I.pt')
    # Get image with OpenCV
    actual_contents = {
        '0.png': 'MIDLYPH',
        '1.jpg': 'SG012O7',
        '2.jpg': 'KV20YSY',
        '3.jpg': 'HCO2LOW',
        '4.jpg': 'DA59YCL',
        '5.png': 'KP65UXL',
        '6.jpg': 'MS01926',
        '7.jpg': 'LR33TEE',
        '8.png': 'EU7OCVA',
        '9.jpg': 'OE18RYY',
        '10.jpg': 'LLZ3919',
        '11.jpg': 'AV08BGU',
        '12.jpg': 'KP58JPY',
        '13.jpg': 'YX68LGL',
    }

    results = {

    }

    # loop through each file in the directory
    for filename in os.listdir('numplate_tests'):
        # ignore non-jpeg files
        if not filename.endswith(('.jpg', '.jpeg', '.png')):
            continue
        # get the full path to the file
        filepath = os.path.join('numplate_tests', filename)
        # open the file
        image = cv2.imread(filepath)

        # run the image through the model
        data = anpr.get_main_detections(image)
        plate = data['plate']
        expected_contents = actual_contents[filename]
        expected_contents.replace(' ', '')
        plate_img = image_utils.crop_bbox(image, plate)
        plate_text = anpr.read_plate(plate_img)
        # get the % of the contents that is correct
        correct = 0
        if plate_text is None:
            plate_text = 'PLATE NOT DETECTED'
        for i in range(len(plate_text)):
            if i >= len(expected_contents):
                break
            if expected_contents[i] == plate_text[i]:
                correct += 1
        results[filename] = correct / len(expected_contents) * 100
        print(f'{filename} - got:{plate_text} - expected:{expected_contents}')
    total = 0
    for filename, accuracy in results.items():
        total += accuracy
        print(f'{filename} - {accuracy}%')
    print(f'Average accuracy: {total / len(results)}%')
