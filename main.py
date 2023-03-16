import tkinter
# import filedialog module
from tkinter import filedialog

import cv2
from PIL import Image, ImageTk
from customtkinter import CTkButton, CTkLabel, CTkEntry, CTkCheckBox, CTkCanvas

import image_utils
from anpr import ANPR
from colour import get_car_colour
from image_utils import crop_bbox, draw_bbox
from make import MakeModel


class MainWindow:
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    BACKGROUND_COLOR = "#46607E"
    FONT_NAME = "Courier New"
    ANPR_MODEL = ANPR("weights/small-300E-600I.pt")
    MAKE_MODEL = MakeModel("weights/150px.h5")

    video_capture = None
    play = True
    show_webcam = False
    show_bboxes = True
    show_stats = False
    show_confidence = False

    def __init__(self, master):
        self.master = master
        self.master.geometry("900x600")
        self.master.resizable(False, False)
        self.master.configure(bg=self.BACKGROUND_COLOR)

        # Title label
        self.title = CTkLabel(master=master, text="Stolen Vehicle Search", font=(self.FONT_NAME, 35, "bold"),
                              bg_color=self.BACKGROUND_COLOR, text_color="white")
        self.title.place(relx=0.59, rely=0.08, anchor=tkinter.CENTER)

        # Label frame to hold all the search fields
        self.search_frame = tkinter.LabelFrame(master=master,
                                               text="Search",
                                               height=220,
                                               width=200,
                                               bg=self.BACKGROUND_COLOR,
                                               border=1)
        self.search_frame.pack()
        self.search_frame.place(relx=0.01, rely=0.136)

        # Textboxes and Labels for make,colour and numberplate search
        self.make_label = CTkLabel(master=self.search_frame, text="Make")
        self.make_label.place(relx=0.1, rely=0.1, anchor=tkinter.W)
        self.make_entry = CTkEntry(master=self.search_frame, width=150)
        self.make_entry.place(relx=0.45, rely=0.25, anchor=tkinter.CENTER)

        self.colour_label = CTkLabel(master=self.search_frame, text="Colour")
        self.colour_label.place(relx=0.1, rely=0.4, anchor=tkinter.W)
        self.colour_entry = CTkEntry(master=self.search_frame, width=150)
        self.colour_entry.place(relx=0.45, rely=0.55, anchor=tkinter.CENTER)

        self.numberplate_label = CTkLabel(master=self.search_frame, text="Numberplate")
        self.numberplate_label.place(relx=0.1, rely=0.7, anchor=tkinter.W)
        self.numberplate_entry = CTkEntry(master=self.search_frame, width=150)
        self.numberplate_entry.place(relx=0.45, rely=0.85, anchor=tkinter.CENTER)

        # Label frame to hold options checkboxes
        self.options_frame = tkinter.LabelFrame(master=master,
                                                text="Options",
                                                height=170,
                                                width=200,
                                                bg=self.BACKGROUND_COLOR,
                                                border=1)
        self.options_frame.pack()
        self.options_frame.place(relx=0.01, rely=0.54)

        # Checkboxes for options
        self.draw_bbox = CTkCheckBox(master=self.options_frame, text="Draw Bounding Box",
                                     command=self.bbox_checkbox_changed)
        self.draw_bbox.place(relx=0.4, rely=0.1, anchor=tkinter.CENTER)

        self.show_confidence = CTkCheckBox(master=self.options_frame, text="Show Confidence",
                                           command=self.confidence_checkbox_changed)
        self.show_confidence.place(relx=0.375, rely=0.35, anchor=tkinter.CENTER)

        self.show_stats = CTkCheckBox(master=self.options_frame, text="Show Stats",
                                      command=self.stats_checkbox_changed)
        self.show_stats.place(relx=0.3, rely=0.6, anchor=tkinter.CENTER)

        self.use_webcam = CTkCheckBox(master=self.options_frame, text="Use Webcam",
                                      command=self.webcam_checkbox_changed)
        self.use_webcam.place(relx=0.312, rely=0.85, anchor=tkinter.CENTER)

        # Create a canvas
        self.frame = CTkCanvas(master=master,
                               width=650,
                               height=400,
                               bg="#D9D9D9",
                               highlightcolor="#747c94",
                               highlightbackground="#747c94",
                               highlightthickness=5)

        self.frame.pack(padx=30, pady=30)
        self.frame.place(relx=0.25, rely=0.15)

        # Select file button
        button = CTkButton(master=master, corner_radius=10, command=self.open_explorer, text="Select Source", height=30,
                           width=150)
        button.place(relx=0.119, rely=0.87, anchor=tkinter.CENTER)

        # Video play/pause button
        self.play_button = CTkButton(master=master, corner_radius=10, command=self.play_pause, text="Play", height=30,
                                     width=150)
        self.play_button.place(relx=0.55, rely=0.9, anchor=tkinter.CENTER)

        # Select button for stolen vehicle image
        self.stolen_button = CTkButton(master=master, corner_radius=10, command=self.open_stolen,
                                       text="Select Stolen Vehicle", height=30,
                                       width=150)
        self.stolen_button.place(relx=0.119, rely=0.93, anchor=tkinter.CENTER)

        master.title("Stolen Vehicle Search")

    def play_pause(self):
        self.play = not self.play
        if self.play:
            self.play_button.configure(text="Pause")
            if self.video_capture is not None:
                self.stream_video()
        else:
            self.play_button.configure(text="Play")

    def open_explorer(self):
        filepath = filedialog.askopenfilename(initialdir="/Users/charlie/Documents/Repos/inferenceGUI",
                                              title="Select a File")
        if filepath == '':
            print("No file selected")
            return

        file_type = filepath.split('.')[-1]
        if file_type == 'jpg' or file_type == 'png':
            img = cv2.imread(filepath)
            self.display_image(img, draw_bbox=self.show_bboxes, show_confidence=self.show_confidence,
                               show_stats=self.show_stats)
        elif file_type == 'mp4':
            self.video_capture = cv2.VideoCapture(filepath)
            self.stream_video()

    def stream_video(self):
        # Loop through each frame and display it
        ret, frame = self.video_capture.read()
        if not ret:
            self.video_capture.release()
            return
        self.display_image(frame)
        if self.play:
            self.frame.after(10, self.stream_video)

    def display_image(self, img):
        make_empty = self.make_entry.get() == ''
        colour_empty = self.colour_entry.get() == ''
        numberplate_empty = self.numberplate_entry.get() == ''

        # Perform Object Detection
        plates, cars = self.ANPR_MODEL.get_image_detections(img)
        for car in cars:
            data = {}
            car_label = "Car"
            car_img = crop_bbox(img, car)

            if not colour_empty:
                car_pil = image_utils.cv_2_pil(car_img)
                data["colour"] = self.fetch_colour(car_pil)
                car_label += " " + data["colour"]
            if not make_empty:
                data["make"] = self.fetch_make(car_img)
                car_label += " " + data["make"]
            img = draw_bbox(img, car, car_label, (0, 255, 0))

        for plate in plates:
            plate_label = "Plate"
            plate_img = crop_bbox(img, plate)
            if not numberplate_empty:
                plate_text = "NOT IMPLEMENTED"
                plate_label += " " + plate_text
            img = draw_bbox(img, plate, plate_label, (0, 0, 255))

        # Convert the image to PIL format which is what tkinter wants
        detected_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        detected_img = Image.fromarray(detected_img)
        # Resize the Image using resize method
        resized_image = detected_img.resize((650, 400), Image.LANCZOS)
        new_image = ImageTk.PhotoImage(resized_image)
        self.frame.create_image(5, 5, image=new_image, anchor=tkinter.NW)
        self.frame.image = new_image
        self.frame.place(relx=0.25, rely=0.15)

    def fetch_colour(self, img):
        colour = get_car_colour(image_utils.center_of_image(img))
        if colour == self.colour_entry.get().lower():
            self.colour_entry.configure(border_color="green")
        else:
            self.colour_entry.configure(border_color="red")
        return colour

    def fetch_make(self, img):
        pred = self.MAKE_MODEL.infer_image(img)
        if pred == self.make_entry.get().lower():
            self.make_entry.configure(border_color="green")
        else:
            self.make_entry.configure(border_color="red")
        return pred

    def bbox_checkbox_changed(self):
        self.show_bboxes = not self.show_bboxes

    def confidence_checkbox_changed(self):
        self.show_confidence = not self.show_confidence

    def stats_checkbox_changed(self):
        self.show_stats = not self.show_stats

    def webcam_checkbox_changed(self):
        self.show_webcam = not self.show_webcam
        if self.show_webcam:
            self.video_capture = cv2.VideoCapture(0)
            self.stream_video()

    def open_stolen(self):
        filepath = filedialog.askopenfilename(initialdir="/Users/charlie/Documents/Repos/inferenceGUI",
                                              title="Select a File")
        if filepath == '':
            print("No file selected")
            return

        file_type = filepath.split('.')[-1]
        if file_type == 'jpg' or file_type == 'png':
            img = cv2.imread(filepath)
            make = self.MAKE_MODEL.infer_image(img)
            car_pil = image_utils.cv_2_pil(img)
            colour = get_car_colour(car_pil)
            self.make_entry.insert(0, make)
            self.make_entry.configure(state="disabled", border_color="yellow")
            self.colour_entry.insert(0, colour)
            self.colour_entry.configure(state="disabled", border_color="yellow")


root = tkinter.Tk()
my_gui = MainWindow(root)
root.mainloop()
