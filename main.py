import tkinter
# import filedialog module
from tkinter import filedialog

from PIL import Image, ImageTk
from customtkinter import CTkButton, CTkLabel, CTkEntry, CTkCheckBox, CTkCanvas


class MainWindow:
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    BACKGROUND_COLOR = "#46607E"
    FONT_NAME = "Courier New"

    def __init__(self, master):
        self.master = master

        self.master.geometry("900x600")
        self.master.resizable(False, False)
        self.master.configure(bg=self.BACKGROUND_COLOR)

        # Title label
        self.title = CTkLabel(master=master, text="Car Inference", font=(self.FONT_NAME, 35, "bold"),
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
        self.make_label.place(relx=0.17, rely=0.1, anchor=tkinter.CENTER)
        self.make_entry = CTkEntry(master=self.search_frame, width=150)
        self.make_entry.place(relx=0.45, rely=0.25, anchor=tkinter.CENTER)

        self.colour_label = CTkLabel(master=self.search_frame, text="Colour")
        self.colour_label.place(relx=0.17, rely=0.4, anchor=tkinter.CENTER)
        self.colour_entry = CTkEntry(master=self.search_frame, width=150)
        self.colour_entry.place(relx=0.45, rely=0.55, anchor=tkinter.CENTER)

        self.numberplate_label = CTkLabel(master=self.search_frame, text="Numberplate")
        self.numberplate_label.place(relx=0.27, rely=0.7, anchor=tkinter.CENTER)
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
        self.draw_bbox = CTkCheckBox(master=self.options_frame, text="Draw Bounding Box")
        self.draw_bbox.place(relx=0.4, rely=0.1, anchor=tkinter.CENTER)

        self.show_confidence = CTkCheckBox(master=self.options_frame, text="Show Confidence")
        self.show_confidence.place(relx=0.375, rely=0.35, anchor=tkinter.CENTER)

        self.show_stats = CTkCheckBox(master=self.options_frame, text="Show Stats")
        self.show_stats.place(relx=0.3, rely=0.6, anchor=tkinter.CENTER)

        self.use_webcam = CTkCheckBox(master=self.options_frame, text="Use Webcam")
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
        button = CTkButton(master=master, corner_radius=10, command=self.open_explorer, text="Select File", height=50,
                           width=150)
        button.place(relx=0.119, rely=0.9, anchor=tkinter.CENTER)

        master.title("Car Inference")

    def open_explorer(self):
        self.filepath = filedialog.askopenfilename(initialdir="/Users/charlie/Documents/Repos/inferenceGUI",
                                                   title="Select a File")
        if self.filepath == '':
            print("No file selected")
            return

        file_type = self.filepath.split('.')[-1]

        if file_type == 'jpg' or file_type == 'png':
            # Load an image in the script
            img = Image.open(self.filepath)
            # Resize the Image using resize method
            resized_image = img.resize((650, 400), Image.LANCZOS)
            new_image = ImageTk.PhotoImage(resized_image)
            self.image_label.configure(image=new_image)
            self.image_label.image = new_image


root = tkinter.Tk()
my_gui = MainWindow(root)
root.mainloop()
