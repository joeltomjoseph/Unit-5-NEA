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
        self.geometry('1000x900+0+0')
        #self.state('zoomed')
        self.minsize(1000,900)
        self.style = ui.createStyle() # Initialise the ttkbootstrap style

        #Initialising some required fonts 
        fontCaption = font.nametofont('TkCaptionFont')
        # Setting a caption font as italic
        fontCaption['size'], fontCaption['slant'] = 10, 'italic'
        ui.ITALIC_CAPTION_FONT = font.Font(**fontCaption.actual())
        # Creating another Caption font but bold
        fontCaption['weight'], fontCaption['slant'] = 'bold', 'roman'
        ui.BOLD_CAPTION_FONT = font.Font(**fontCaption.actual())

        mainFrame = ttk.Frame(self)
        mainFrame.pack(side='top', fill='both', expand=True)

        contentFrame = ttk.Frame(mainFrame)
        contentFrame.pack(side='top', fill='both', expand=True)
        contentFrame.grid_rowconfigure(0, weight=1)
        contentFrame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Initialise all the pages
        for F in (LoginPage, PageOne, PageTwo):
            frame = F(contentFrame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        # Show the login page
        frame = LoginPage(contentFrame, self)
        self.frames[LoginPage] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        self.showFrame(LoginPage)
    
    def showFrame(self, cont, *args):
        ''' Show the frame for the given page name '''
        frame = self.frames[cont]
        frame.tkraise()

class LoginPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, relief='ridge')
        self.canvas.pack(side='top', fill="both", expand=True)
        
        # Set up the title label
        self.logo = ImageTk.PhotoImage(Image.open("images/ags.png").resize((100, 100), Image.LANCZOS))
        self.titleLabel = ttk.Label(self.canvas, text="Sound and Lighting", image=self.logo, compound='left', style='Heading.TLabel')
        
        #Create frame to hold login form
        self.canvasItemsFrame = ttk.Frame(self.canvas)

        # Set up the background image
        self.image = Image.open("images/backdrop.png")
        self.imgCopy= self.image.copy()
        self.backgroundImage = ImageTk.PhotoImage(self.image)
        self.background = self.canvas.create_image(0, 0, image=self.backgroundImage, anchor='nw')
        
        # Set up the username label and field
        self.usernameLabel = ttk.Label(self.canvasItemsFrame, text="Username")
        self.usernameLabel.pack(pady=10)
        self.usernameField = ttk.Entry(self.canvasItemsFrame)
        self.usernameField.pack(pady=5, padx=20)
        
        # Set up the password label, field, and show password toggle
        self.passwordLabel = ttk.Label(self.canvasItemsFrame, text="Password")
        self.passwordLabel.pack(pady=10)
        self.passwordField = ttk.Entry(self.canvasItemsFrame, show="*")
        self.passwordField.pack(pady=5)
        self.showPasswordVar = tk.BooleanVar()
        self.showPasswordVar.set(False)
        self.showPasswordToggle = ttk.Checkbutton(self.canvasItemsFrame, text="Show password", variable=self.showPasswordVar, command=self.togglePasswordVisibility)
        self.showPasswordToggle.pack(pady=5)
        
        # Set up the forgotten password button
        self.forgottenPasswordButton = ttk.Button(self.canvasItemsFrame, text="Forgotten password?", command=self.forgottenPassword)
        self.forgottenPasswordButton.pack(pady=10)
        
        # Set up the login button
        self.loginButton = ttk.Button(self.canvasItemsFrame, text="Login", command=lambda: controller.showFrame(PageOne))
        self.loginButton.pack(pady=10)

        # Set up the canvas items; title and login form
        self.title = self.canvas.create_window(self.winfo_screenwidth()/2, (self.winfo_screenheight()/2)+100, anchor='center', window=self.titleLabel)
        self.frame = self.canvas.create_window(self.winfo_screenwidth()/2, self.winfo_screenheight()/2, anchor='center', window=self.canvasItemsFrame)
        self.canvas.bind('<Configure>', self.resizeCanvas) # Bind the resizeCanvas function to the canvas resizing event

    def resizeImage(self, event):
        ''' Resize the background image to fit the canvas '''
        self.image = self.imgCopy.resize((event.width, event.width), Image.LANCZOS)

        self.backgroundImage = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image = self.backgroundImage, anchor='nw')

    def resizeCanvas(self, event):
        ''' Reposition the canvas items (Title and login form) to be centered in the canvas '''
        self.canvas.coords(self.title, event.width/2, (event.height/2)-350)
        self.canvas.coords(self.frame, event.width/2, event.height/2)

        self.resizeImage(event) # Resize the background image to fit the canvas at the same time
        
    def togglePasswordVisibility(self):
        ''' Toggle the visibility of the password field '''
        if self.showPasswordVar.get():
            self.passwordField.config(show="")
        else:
            self.passwordField.config(show="*")
            
    def forgottenPassword(self):
        # TODO: Implement forgotten password functionality
        pass
    
    def login(self):
        # TODO: Implement login functionality
        pass

class PageOne(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self)

        self.loginButton = ttk.Button(self, text='Page One Moment', command=lambda: controller.showFrame(PageTwo), style='TButton')
        self.loginButton.pack()
        ui.createTooltip(self.loginButton, 'Click it for suprise')

        self.label = ttk.Label(self, text='RAHHHHH', style='TLabel')
        self.label.pack()
        self.label2 = ttk.Label(self, text='SUIUIIUIUIIII', style='TLabel')
        self.label2.pack()

class PageTwo(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.newFrame = ttk.Frame(self, style='TFrame')
        self.newFrame.pack(side='top', fill='both', expand=True)

        self.loginButton = ttk.Button(self.newFrame, text='Page Two Moment', command=lambda: controller.showFrame(PageOne), style='TButton')
        self.loginButton.pack()

        self.label = ttk.Label(self.newFrame, text='Hey', style='TLabel')
        self.label.pack()
        self.label2 = ttk.Label(self.newFrame, text='Does this work??', style='TLabel')
        self.label2.pack()

''' Main Program '''
#CONSTANTS

app = MainApp()
app.mainloop()