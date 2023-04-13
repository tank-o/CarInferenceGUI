import time

import cv2

import colour
import image_utils
from anpr import ANPR
from make import MakeModel

if __name__ == "__main__":
    image = cv2.imread(r'C:\Users\Charlie\PycharmProjects\ANPRProject\testImages\fiesta.jpg')

    anpr = ANPR('../weights/small-300E-600I.pt')
    make = MakeModel('../weights/150px.h5')

    anpr.warmup()
    make.warmup()

    for i in range(5):
        obj_start = time.time()
        data = anpr.get_main_detections(image)
        obj_stop = time.time()
        obj_time = (obj_stop - obj_start) * 1000
        print(f'Object detection took {obj_time}ms')

        car_img = image_utils.crop_bbox(image, data['car'])
        plate_img = image_utils.crop_bbox(image, data['plate'])

        make_start = time.time()
        make_data = make.infer_image(car_img)
        make_stop = time.time()
        make_time = (make_stop - make_start) * 1000
        print(f'Make detection took {make_time}ms')

        colour_start = time.time()
        car_pil = image_utils.cv_2_pil(car_img)
        extracted_colour = colour.get_car_colour(car_pil)
        colour_stop = time.time()
        colour_time = (colour_stop - colour_start) * 1000
        print(f'Colour detection took {colour_time}ms')

        plate_start = time.time()
        plate_text = anpr.read_plate(plate_img)
        plate_stop = time.time()
        plate_time = (plate_stop - plate_start) * 1000
        print(f'Plate detection took {plate_time}ms')

        print('Total time:', str(obj_time + make_time + colour_time + plate_time) + 'ms')

