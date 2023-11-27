import tkinter as tk
from tkinter import messagebox, font
import ttkbootstrap as ttk
from PIL import Image, ImageTk

import ui

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Setting up Starting Window
        self.title('AGS Sound and Lighting')
        self.iconphoto(True, tk.PhotoImage(file='images/ags.gif'))
        self.geometry('800x800+0+0')
        #self.state('zoomed')
        self.minsize(600,600)
        

        #Initialising some required fonts now 
        fontCaption = font.nametofont('TkCaptionFont')
        # Setting a caption font as italic
        fontCaption['size'], fontCaption['slant'] = 10, 'italic'
        ui.ITALIC_CAPTION_FONT = font.Font(**fontCaption.actual())
        # Creating another Caption font but bold
        fontCaption['weight'], fontCaption['slant'] = 'bold', 'roman'
        ui.BOLD_CAPTION_FONT = font.Font(**fontCaption.actual())

        mainFrame = ttk.Frame(self)
        mainFrame.pack(side='top', fill='both', expand=True)

        #self.menuBar = ui.MenuBar(mainFrame)

        contentFrame = ttk.Frame(mainFrame)
        contentFrame.pack(side='top', fill='both', expand=True)
        contentFrame.grid_rowconfigure(0, weight=1)
        contentFrame.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginPage, PageOne, PageTwo):
            frame = F(contentFrame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
            

        frame = LoginPage(contentFrame, self)
        self.frames[LoginPage] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(LoginPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def login(self):
        self.destroy()

class LoginPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.configure(padding=None)
        
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0, relief='ridge')
        self.canvas.pack(side='top', fill="both", expand=True)
        self.canvasItemsFrame = ttk.Frame(style='Items.TFrame')
        self.canvasItemsFrame.pack()

        # Set up the background image
        # self.background_image = tk.PhotoImage(file="backdrop.png")
        # self.background_label = ttk.Label(self.canvas, image=self.background_image)
        # self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.image = Image.open("images/backdrop.png")
        self.img_copy= self.image.copy()

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = ttk.Label(self.canvas, image=self.background_image)
        self.background.bind('<Configure>', self._resize_image)
        self.background.pack(fill='both', expand=True)
        
        # Set up the title label
        self.title_label = ttk.Label(self.canvasItemsFrame, text="Login", style="Heading.TLabel")
        self.title_label.pack(pady=20)
        
        # Set up the username label and field
        self.username_label = ttk.Label(self.canvasItemsFrame, text="Username")
        self.username_label.pack(pady=10)
        self.username_field = ttk.Entry(self.canvasItemsFrame)
        self.username_field.pack(pady=5)
        
        # Set up the password label, field, and show password toggle
        self.password_label = ttk.Label(self.canvasItemsFrame, text="Password")
        self.password_label.pack(pady=10)
        self.password_field = ttk.Entry(self.canvasItemsFrame, show="*")
        self.password_field.pack(pady=5)
        self.show_password_var = tk.BooleanVar()
        self.show_password_var.set(False)
        self.show_password_toggle = ttk.Checkbutton(self.canvasItemsFrame, text="Show password", variable=self.show_password_var, command=self.toggle_password_visibility)
        self.show_password_toggle.pack(pady=5)
        
        # Set up the forgotten password button
        self.forgotten_password_button = ttk.Button(self.canvasItemsFrame, text="Forgotten password?", command=self.forgotten_password)
        self.forgotten_password_button.pack(pady=10)
        
        # Set up the login button
        self.login_button = ttk.Button(self.canvasItemsFrame, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.frame = self.canvas.create_window(self.winfo_screenwidth()/2, self.winfo_screenheight()/2, anchor='center', window=self.canvasItemsFrame)
        self.canvas.bind('<Configure>', self._resizeCanvas)

    def _resize_image(self, event):
        self.image = self.img_copy.resize((event.width, event.width), Image.BICUBIC)

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image =  self.background_image)

    def _resizeCanvas(self, event):
        self.canvas.coords(self.frame, event.width/2, event.height/2)
        
    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_field.config(show="")
        else:
            self.password_field.config(show="*")
            
    def forgotten_password(self):
        # TODO: Implement forgotten password functionality
        pass
    
    def login(self):
        # TODO: Implement login functionality
        pass

class PageOne(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.loginButton = ttk.Button(self, text='Page One Moment', command=lambda: controller.show_frame(PageTwo), style='TButton')
        self.loginButton.pack()
        ui.create_tooltip(self.loginButton, 'Click it for suprise xoxo')

        self.label = ttk.Label(self, text='RAHHHHH', style='TLabel')
        self.label.pack()
        self.label2 = ttk.Label(self, text='SUIUIIUIUIIII', style='TLabel')
        self.label2.pack()

class PageTwo(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.newFrame = ttk.Frame(self, style='TFrame')
        self.newFrame.pack(side='top', fill='both', expand=True)

        self.loginButton = ttk.Button(self.newFrame, text='Page Two Moment', command=None, style='TButton')
        self.loginButton.pack()

        self.label = ttk.Label(self.newFrame, text='Hey x', style='TLabel')
        self.label.pack()
        self.label2 = ttk.Label(self.newFrame, text='Does this work??', style='TLabel')
        self.label2.pack()



''' Main Program '''
#CONSTANTS

app = MainApp()
app.mainloop()