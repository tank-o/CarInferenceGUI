import cv2
from PIL import Image


def cv_2_pil(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(image)
    return im_pil
