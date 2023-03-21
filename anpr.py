import ssl
import time

import torch
from pytesseract import pytesseract

import image_utils
from image_utils import draw_bbox, process_plate, area_of_bbox


class ANPR:

    def __init__(self, model_path, debug=False):
        ssl._create_default_https_context = ssl._create_unverified_context
        self.debug = debug
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
        self.model.conf = 0.375
        pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        cuda = torch.cuda.is_available()
        if cuda:
            self.model.cuda()
        self.device = torch.device("cuda:0" if cuda else "cpu")
        self.model.to(self.device)
        print(torch.cuda.get_device_name(0))
        self.log("Model loaded")

    def log(self, message):
        if self.debug:
            print(message)

    def get_image_detections(self, image):
        data = {}
        start = time.time()
        results = self.model(image, size=416)
        results = results.pandas().xyxy[0]
        self.log(results)
        plates = []
        cars = []
        for detection in results.iterrows():
            detection = detection[1]
            if detection['name'] == 'number-plate':
                plates.append(detection)
            elif detection['name'] == 'car':
                cars.append(detection)
        data['plates'] = plates
        data['cars'] = cars
        stop = time.time()
        data['time'] = (stop - start) * 1000
        return data

    def get_main_detections(self, image):
        data = {}
        start = time.time()
        results = self.model(image, size=416)
        results = results.pandas().xyxy[0]
        self.log(results)
        # Get the largest vehicle detection and the largest plate detection
        car = None
        plate = None
        for detection in results.iterrows():
            detection = detection[1]
            # Get the largest car detection
            if detection['name'] == 'car':
                if car is None:
                    car = detection
                else:
                    if area_of_bbox(detection) > area_of_bbox(car):
                        car = detection

        for detection in results.iterrows():
            detection = detection[1]
            # Get the largest plate detection
            if detection['name'] == 'number-plate':
                if plate is None:
                    plate = detection
                else:
                    if area_of_bbox(detection) > area_of_bbox(plate):
                        plate = detection

        data['plate'] = plate
        data['car'] = car
        stop = time.time()
        data['time'] = (stop - start) * 1000
        return data

    def infer_image(self, image):
        # get the detections
        plates, cars = self.get_image_detections(image)
        for car in cars:
            draw_bbox(image, car, colour=(0, 255, 0))
        for plate in plates:
            draw_bbox(image, plate, colour=(255, 0, 0))
        return image

    def read_plate(self, plate):
        plate = process_plate(plate)
        # Read the plate - only allow caps and numbers
        plate_text = pytesseract.image_to_string(plate,
                                                 config='--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        return plate_text
