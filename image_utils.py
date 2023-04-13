import cv2
import numpy as np
from PIL import Image


def cv_2_pil(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(image)
    return im_pil


def pil_2_cv(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return image


# https://stackoverflow.com/questions/56108183/python-opencv-cv2-drawing-rectangle-with-text
def draw_bbox(image, detection, label=None, colour=(0, 255, 0)):
    """Draws a bounding box on an image with a given color."""
    if label is None:
        label = detection['name']

    xmin, ymin, xmax, ymax = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(
        detection['ymax'])

    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)
    # draw bounding box
    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), colour, 2)
    # draw text
    cv2.rectangle(image, (xmin, ymin - h - 5), (xmin + w, ymin), colour, -1)
    cv2.putText(image, label, (xmin, ymin - 5), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 1)
    # draw fancy text box
    return image


def center_of_image(image):
    """Crops the center 25% of a bounding box from an image."""
    x_length = image.width
    y_length = image.height
    yoffset = y_length * 0.25
    xoffset = x_length * 0.25
    center_x = x_length // 2
    center_y = y_length // 2
    return image.crop((center_x - xoffset, center_y - yoffset, center_x + xoffset, center_y + yoffset))


def crop_bbox(image, detection):
    """Crops a bounding box from an image."""
    xmin, ymin, xmax, ymax = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(
        detection['ymax'])
    return image[ymin:ymax, xmin:xmax]


def area_of_bbox(detection):
    """Returns the area of a bounding box."""
    xmin, ymin, xmax, ymax = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(
        detection['ymax'])
    return (xmax - xmin) * (ymax - ymin)


def is_inside(bbox1, bbox2):
    """Checks if bbox1 is inside bbox2."""
    xmin1, ymin1, xmax1, ymax1 = int(bbox1['xmin']), int(bbox1['ymin']), int(bbox1['xmax']), int(bbox1['ymax'])
    xmin2, ymin2, xmax2, ymax2 = int(bbox2['xmin']), int(bbox2['ymin']), int(bbox2['xmax']), int(bbox2['ymax'])
    return xmin1 > xmin2 and xmax1 < xmax2 and ymin1 > ymin2 and ymax1 < ymax2


def process_plate(plate):
    # use tesseract to read the plate
    plate = cv2.resize(plate, (0, 0), fx=3, fy=3)
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # get the contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # sort the contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    # get the largest contour
    largest_contour = contours[0]
    # get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    # crop the image to the bounding box
    cropped = thresh[y:y + h, x:x + w]
    return cropped
