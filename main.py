import time
import tkinter
# import filedialog module
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter.messagebox import showerror

import cv2
from PIL import Image, ImageTk
from customtkinter import CTkButton, CTkLabel, CTkEntry, CTkCheckBox, CTkCanvas

import image_utils
from anpr import ANPR
from colour import get_car_colour
from db import VehicleStore
from image_utils import crop_bbox
from make import MakeModel


class MainWindow:
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    BACKGROUND_COLOR = "#46607E"
    FONT_NAME = "Courier New"
    ANPR_MODEL = ANPR("weights/small-300E-600I.pt")
    MAKE_MODEL = MakeModel("weights/150px.h5")
    DB = VehicleStore()

    video_capture = None
    play = True
    show_webcam = False
    show_stats_opt = False
    show_confidence_opt = False

    def __init__(self, master):
        self.master = master
        self.master.geometry("900x600")
        self.master.resizable(False, False)
        self.master.configure(bg=self.BACKGROUND_COLOR)

        self.logo = self.create_logo()
        self.logo_label = tkinter.Label(master=master,
                                        image=self.logo,
                                        bg=self.BACKGROUND_COLOR,
                                        width=220,
                                        height=110)
        self.logo_label.pack()
        self.logo_label.place(relx=0.12, rely=0.08, anchor=tkinter.CENTER)
        # Scrolled Text Box to Display key info
        self.log_box = scrolledtext.ScrolledText(master=master,
                                                 width=22,
                                                 height=13,
                                                 bg=self.BACKGROUND_COLOR,
                                                 state=tkinter.DISABLED)
        self.log_box.pack()
        self.log_box.place(relx=0.12, rely=0.34, anchor=tkinter.CENTER)

        # Label frame to hold all the search fields
        self.search_frame = tkinter.LabelFrame(master=master,
                                               text="Search",
                                               height=75,
                                               width=650,
                                               bg=self.BACKGROUND_COLOR,
                                               border=1)
        self.search_frame.pack()
        self.search_frame.place(relx=0.25, rely=0.011)

        self.add_to_db_button = CTkButton(master=self.search_frame, corner_radius=10, command=self.db_button_callback,
                                          text="+", height=55,
                                          width=35)
        self.add_to_db_button.place(relx=0.95, rely=0.42, anchor=tkinter.CENTER)

        # Textboxes and Labels for make,colour and numberplate search
        self.make_label = CTkLabel(master=self.search_frame, text="Make")
        self.make_label.place(relx=0.05, rely=0.22, anchor=tkinter.W)
        self.make_entry = CTkEntry(master=self.search_frame, width=150)
        self.make_entry.place(relx=0.05, rely=0.65, anchor=tkinter.W)

        self.colour_label = CTkLabel(master=self.search_frame, text="Colour")
        self.colour_label.place(relx=0.35, rely=0.22, anchor=tkinter.W)
        self.colour_entry = CTkEntry(master=self.search_frame, width=150)
        self.colour_entry.place(relx=0.35, rely=0.65, anchor=tkinter.W)

        self.numberplate_label = CTkLabel(master=self.search_frame, text="Numberplate")
        self.numberplate_label.place(relx=0.65, rely=0.22, anchor=tkinter.W)
        self.numberplate_entry = CTkEntry(master=self.search_frame, width=150)
        self.numberplate_entry.place(relx=0.65, rely=0.65, anchor=tkinter.W)

        # Label frame to hold options checkboxes
        self.options_frame = tkinter.LabelFrame(master=master,
                                                text="Options",
                                                height=170,
                                                width=200,
                                                bg=self.BACKGROUND_COLOR,
                                                border=1)
        self.options_frame.pack()
        self.options_frame.place(relx=0.01, rely=0.54)

        self.show_confidence = CTkCheckBox(master=self.options_frame, text="Show Confidence",
                                           command=self.confidence_checkbox_changed)
        self.show_confidence.place(relx=0.375, rely=0.18, anchor=tkinter.CENTER)

        self.show_stats = CTkCheckBox(master=self.options_frame, text="Show Stats",
                                      command=self.stats_checkbox_changed)
        self.show_stats.place(relx=0.3, rely=0.47, anchor=tkinter.CENTER)

        self.use_webcam = CTkCheckBox(master=self.options_frame, text="Use Webcam",
                                      command=self.webcam_checkbox_changed)
        self.use_webcam.place(relx=0.312, rely=0.76, anchor=tkinter.CENTER)

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
                                     width=150, )

        # Select button for stolen vehicle image
        self.stolen_button = CTkButton(master=master, corner_radius=10, command=self.open_stolen,
                                       text="Add Vehicle", height=30,
                                       width=150)
        self.stolen_button.place(relx=0.119, rely=0.93, anchor=tkinter.CENTER)

        master.title("Stolen Vehicle Search")
        self.log("Vehicle Search Loaded")

    def log(self, text):
        self.log_box.configure(state=tkinter.NORMAL)
        self.log_box.insert(tkinter.END, text + "\n")
        self.log_box.configure(state=tkinter.DISABLED)

    def play_pause(self):
        self.play = not self.play
        if self.play:
            self.play_button.configure(text="Pause")
            self.log("Video Playing")
            if self.video_capture is not None:
                self.stream_video()
        else:
            self.log("Video Paused")
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
            self.display_image(img, show_confidence=self.show_confidence_opt,
                               show_stats=self.show_stats_opt)
        elif file_type == 'mp4':
            self.video_capture = cv2.VideoCapture(filepath)
            self.play_button.place(relx=0.6, rely=0.9, anchor=tkinter.CENTER)
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

    def display_image(self, img, show_confidence=False, show_stats=False):
        make_empty = self.make_entry.get() == ''
        colour_empty = self.colour_entry.get() == ''
        numberplate_empty = self.numberplate_entry.get() == ''
        start = time.time()

        # Perform Object Detection
        data = self.ANPR_MODEL.get_main_detections(img)
        car = data["car"]
        plate = data["plate"]

        data = {}

        if car is not None:
            car_label = "Car"
            car_img = crop_bbox(img, car)
            car_pil = image_utils.cv_2_pil(car_img)

            data["colour"] = get_car_colour(image_utils.center_of_image(car_pil))
            car_label += " " + data["colour"]

            data["make"] = self.MAKE_MODEL.infer_image(car_img)
            car_label += " " + data["make"]


        if plate is not None:
            plate_label = "Plate"
            plate_img = crop_bbox(img, plate)
            extracted = self.ANPR_MODEL.read_plate(plate_img)
            if extracted not in [None,'']:
                data["numberplate"] = extracted
                plate_label += " " + data["numberplate"]

        # if any of the boxes are filled in, check it against the database
        if self.DB.check_car_matches(data) not in [None, []]:
            car_label = "MATCH"

        if car is not None:
            img = image_utils.draw_bbox(img, car, car_label, (0, 255, 0))
        if plate is not None:
            img = image_utils.draw_bbox(img, plate, plate_label, (0, 0, 255))
        stop = time.time()
        total_time = stop - start
        # Round to 2 decimal places
        total_time = round(total_time, 2)
        self.log("Inference Time: " + str(total_time) + "s")

        # Convert the image to PIL format which is what tkinter wants
        detected_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        detected_img = Image.fromarray(detected_img)
        # Resize the Image using resize method
        resized_image = detected_img.resize((650, 400), Image.LANCZOS)
        new_image = ImageTk.PhotoImage(resized_image)
        self.frame.create_image(5, 5, image=new_image, anchor=tkinter.NW)
        self.frame.image = new_image
        self.frame.place(relx=0.25, rely=0.15)

    def confidence_checkbox_changed(self):
        self.show_confidence_opt = not self.show_confidence_opt

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
            data = self.ANPR_MODEL.get_main_detections(img)
            car_img = crop_bbox(img, data["car"])
            plate_img = crop_bbox(img, data["plate"])
            make = self.MAKE_MODEL.infer_image(car_img)
            plate = self.ANPR_MODEL.read_plate(plate_img)
            car_pil = image_utils.cv_2_pil(car_img)
            colour = get_car_colour(car_pil)
            self.make_entry.insert(0, make)
            self.make_entry.configure(state="disabled", border_color="yellow")
            self.colour_entry.insert(0, colour)
            self.colour_entry.configure(state="disabled", border_color="yellow")
            self.numberplate_entry.insert(0, plate)
            self.numberplate_entry.configure(state="disabled", border_color="yellow")

    def create_logo(self):
        logo = Image.open("logo.png")
        logo = logo.resize((210, 60), Image.LANCZOS)
        logo = ImageTk.PhotoImage(logo)
        return logo

    def db_button_callback(self):
        make = self.make_entry.get()
        colour = self.colour_entry.get()
        numberplate = self.numberplate_entry.get()
        data = {}
        if make != '':
            data["make"] = make
        if colour != '':
            data["colour"] = colour
        if numberplate != '':
            data["numberplate"] = numberplate
        if len(data) == 0:
            showerror("Error", "No data specified")
            return
        self.DB.add_vehicle(data)
        self.numberplate_entry.configure(textvariable='', state="normal")
        self.colour_entry.configure(textvariable='', state="normal")
        self.make_entry.configure(textvariable='', state="normal")

root = tkinter.Tk()
my_gui = MainWindow(root)
root.mainloop()
