import tkinter
# import filedialog module
from tkinter import filedialog

import cv2
from customtkinter import CTkLabel, CTkButton, CTkImage

from utils.image import cv_2_pil


class MainWindow:
    def __init__(self, master):
        self.filepath = None
        self.master = master

        master.title("Car Inference")
        self.label = CTkLabel(master=master, text="Something")
        self.label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        button = CTkButton(master=master, corner_radius=10, command=self.open_explorer)
        button.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

    def open_explorer(self):
        self.filepath = filedialog.askopenfilename(initialdir="/Users/charlie/Documents/Repos/inferenceGUI",
                                                   title="Select a File")
        if self.filepath == '':
            print("No file selected")
            return

        file_type = self.filepath.split('.')[-1]
        image = cv2.imread(self.filepath)
        im_pil = cv_2_pil(image)

        image = CTkImage(light_image=im_pil,
                         dark_image=im_pil,
                         size=(400, 600))

        label_image = CTkLabel(master=self.master,
                               image=image,
                               text='')
        label_image.image = image
        label_image.place(relx=0.3, rely=0.3, anchor="w")


root = tkinter.Tk()
my_gui = MainWindow(root)
root.mainloop()
