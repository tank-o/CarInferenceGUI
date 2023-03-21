import cv2
import numpy as np
import tensorflow as tf


class MakeModel:
    classes = ["Audi", "BMW", "Ford", "Mercedes", "Nissan", "Toyota", "Vauxhall", "Volkswagen"]

    def __init__(self, model_path, debug=False):
        self.model = tf.keras.models.load_model(model_path, compile=False)
        print(tf.config.list_physical_devices())
        self.debug = debug

    def infer_image(self, img):
        img = cv2.resize(img, (150,150), interpolation=cv2.INTER_AREA)
        # Rescale image to 0-1
        img = img / 255.0
        # Add a dimension to the image
        img = (np.expand_dims(img, 0))
        predictions = self.model.predict(img)
        # get class with highest probability
        class_index = tf.argmax(predictions[0])
        class_string = self.classes[class_index]
        return self.classes[class_index]