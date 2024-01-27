import tkinter as tk
from tkinter import messagebox, font
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from tkPDFViewer2 import tkPDFViewer as tkPDF
import datetime
import sqlite3 as sql

import ui
from functions import generalFunctions, validation, database #, soundBoardController

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Setting up Starting Window
        self.title('AGS Sound and Lighting')
        self.iconphoto(True, tk.PhotoImage(file=generalFunctions.resourcePath('Contents/images/ags.gif')))
        self.geometry('1000x1000+250+0')
        #self.state('zoomed')
        self.minsize(1000,900)
        self.protocol("WM_DELETE_WINDOW", self.closeApplication) # Bind the closeApplication function to the window closing event

        #Initialising some required fonts 
        fontCaption = font.nametofont('TkCaptionFont')
        # Setting a caption font as italic
        fontCaption['size'], fontCaption['slant'] = 15, 'italic'
        ui.ITALIC_CAPTION_FONT = font.Font(**fontCaption.actual())
        # Creating another Caption font but bold
        fontCaption['weight'], fontCaption['slant'] = 'bold', 'roman'
        ui.BOLD_CAPTION_FONT = font.Font(**fontCaption.actual())

        self.style = ui.createStyle() # Initialise the ttkbootstrap style

        mainFrame = ttk.Frame(self)
        mainFrame.pack(side='top', fill='both', expand=True)

        contentFrame = ttk.Frame(mainFrame)
        contentFrame.pack(side='top', fill='both', expand=True)
        contentFrame.grid_rowconfigure(0, weight=1)
        contentFrame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Initialise all the pages
        for F in (LoginPage, FAQPage, UpcomingEventsPage, DocumentationPage, MemberInformationPage, ArchivePage, ConnectToSoundboardPage, TrainingMaterialsPage, SettingsPage, Dashboard):
            frame = F(contentFrame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        
        # Show the login page
        # frame = LoginPage(contentFrame, self)
        # self.frames[LoginPage] = frame
        # frame.grid(row=0, column=0, sticky='nsew')
        # self.showFrame(LoginPage)
        
        frame = Dashboard(contentFrame, self)
        self.frames[Dashboard] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        self.showFrame(Dashboard, resizeTo='1920x1080+0+0')
    
    def showFrame(self, cont, resizeTo: str = None):
        ''' Show the frame for the given page name. If resizeTo is given, resize the window to the given dimensions. '''
        if resizeTo:
            #self.state('zoomed')
            self.geometry(resizeTo)
        frame = self.frames[cont]
        frame.tkraise()

    def closeApplication(self):
        ''' Safely close lose the application. Close the database connection and then destroy the window. '''
        try:
            self.destroy() # Destroy the window
            connection.close() # Close the database connection
        except:
            messagebox.showinfo('Error', 'Failed to close the application, this is likely due to something still. Please try again. ')

class LoginPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, relief='ridge')
        self.canvas.pack(side='top', fill="both", expand=True)
        
        # Set up the title label
        self.logo = ImageTk.PhotoImage(Image.open(generalFunctions.resourcePath("Contents/images/ags.png")).resize((100, 100), Image.LANCZOS))
        self.titleLabel = ttk.Label(self.canvas, text="Sound and Lighting", image=self.logo, compound='left', style='Heading.TLabel')
        
        #Create frame to hold login form
        self.canvasItemsFrame = ttk.Frame(self.canvas, padding=(10,10,10,10))

        # Set up the background image
        self.image = Image.open(generalFunctions.resourcePath("Contents/images/backdrop.png"))
        self.imgCopy= self.image.copy()
        self.backgroundImage = ImageTk.PhotoImage(self.image)
        self.background = self.canvas.create_image(0, 0, image=self.backgroundImage, anchor='nw')
        
        # Set up the username label and field
        self.usernameLabel = ttk.Label(self.canvasItemsFrame, text="Username")
        self.usernameLabel.pack(pady=10)
        self.usernameField = ttk.Entry(self.canvasItemsFrame, font=ui.TEXT_ENTRY_FONT, validate='focusout', validatecommand=lambda: self.validationCallback(self.usernameField, validation.validateUsername))
        self.usernameField.pack(pady=5, padx=20)
        
        # Set up the password label, field, and show password toggle
        self.passwordLabel = ttk.Label(self.canvasItemsFrame, text="Password")
        self.passwordLabel.pack(pady=10)
        self.passwordField = ttk.Entry(self.canvasItemsFrame, font=ui.TEXT_ENTRY_FONT, show="*", validate='focusout', validatecommand=lambda: self.validationCallback(self.passwordField, validation.validatePassword))
        self.passwordField.pack(pady=5)
        
        self.showPasswordVar = tk.BooleanVar()
        self.showPasswordVar.set(False)
        self.showPasswordToggle = ttk.Checkbutton(self.canvasItemsFrame, text="Show password", variable=self.showPasswordVar, command=self.togglePasswordVisibility)
        self.showPasswordToggle.pack(pady=5)
        
        # Set up the forgotten password button
        controller.style.configure('forgot.primary.Outline.TButton', borderwidth=2, focusthickness=2, width=18)
        self.forgottenPasswordButton = ttk.Button(self.canvasItemsFrame, text="Forgotten password?", style='forgot.primary.Outline.TButton', command=self.forgottenPassword)
        self.forgottenPasswordButton.pack(pady=10)
        
        # Set up the login button
        controller.style.configure('Login.secondary.TButton', borderwidth=2, focusthickness=2, width=20)
        self.loginButton = ttk.Button(self.canvasItemsFrame, text="Login", style='Login.secondary.TButton', command=lambda: controller.showFrame(Dashboard, resizeTo='1920x1080+0+0'))
        self.loginButton.pack(pady=10)

        # Set up the canvas items; title and login form
        self.title = self.canvas.create_window(self.winfo_screenwidth()/2, (self.winfo_screenheight()/2)+100, anchor='center', window=self.titleLabel)
        self.frame = self.canvas.create_window(self.winfo_screenwidth()/2, self.winfo_screenheight()/2, anchor='center', window=self.canvasItemsFrame)
        self.canvas.bind('<Configure>', self.resizeCanvas) # Bind the resizeCanvas function to the canvas resizing event
    
    def validationCallback(self, widget, validationRoutine):
        return validationRoutine(widget, widget.get())
        #return (controller.register(validationRoutine), widget, '%P')

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

class Dashboard(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage).place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')

        # Create a frame for upcoming event details
        self.eventFrame = ttk.Frame(self, style='TFrame')
        # self.eventFrame.pack(side='left', fill='both', expand=True, padx=10, pady=10, ipadx=10, ipady=10, anchor='w')
        self.eventFrame.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.85, anchor='nw')
        
        # Create buttons for viewing upcoming events and adding new events
        self.upcomingEventsTextVar = ttk.StringVar(value=f'Upcoming Events\n\n\n{database.getLatestEventsDetails(cursor)}')
        # self.upcomingEventsButton = ui.ContentButton(self.eventFrame, controller, self.upcomingEventsTexself.accordionar, lambda: controller.showFrame(UpcomingEventsPage))
        self.upcomingEventsButton = ttk.Button(self.eventFrame, textvariable=self.upcomingEventsTextVar, style='UE.dbButton.Outline.TButton', command=lambda: controller.showFrame(UpcomingEventsPage))
        self.upcomingEventsButton.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        # self.upcomingEventsLabel = ttk.Label(self.upcomingEventsButton, text='SOURCED FROM DATABASE', style='dbLabel.TLabel')
        # self.upcomingEventsLabel.pack(side='bottom', padx=10, pady=10)
        
        # Create a frame for buttons
        self.buttonFrame = ttk.Frame(self, style='TFrame')
        # self.buttonFrame.pack(side='right', fill='both', expand=True, padx=10, pady=10, ipadx=10, ipady=10, anchor='ne')
        self.buttonFrame.place(relx=0.3, rely=0.1, relwidth=0.7, relheight=0.85, anchor='nw')
        self.buttonFrame.grid_columnconfigure([0,1], weight=1, uniform='column')
        self.buttonFrame.grid_rowconfigure([0,1,2], weight=1)

        # Create buttons for viewing documentation, information about members, archive, connect to soundboard, training materials, and settings
        self.documentationButton = ttk.Button(self.buttonFrame, text='View Documentation', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(DocumentationPage))
        self.documentationButton.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.membersButton = ttk.Button(self.buttonFrame, text='Information about Members', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(MemberInformationPage))
        self.membersButton.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.archiveButton = ttk.Button(self.buttonFrame, text='Archive', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(ArchivePage))
        self.archiveButton.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.soundboardButton = ttk.Button(self.buttonFrame, text='Connect to Soundboard', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(ConnectToSoundboardPage))
        self.soundboardButton.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

        self.trainingButton = ttk.Button(self.buttonFrame, text='Training Materials', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(TrainingMaterialsPage))
        self.trainingButton.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.settingsButton = ttk.Button(self.buttonFrame, text='Settings', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(SettingsPage))
        self.settingsButton.grid(row=2, column=1, padx=10, pady=10, sticky='nsew')

        # Create a frame for the time/date and other information at bottom
        self.bottomFrame = ttk.Frame(self, style='TFrame')
        # self.bottomFrame.pack(side='bottom', fill='x', after=self.menuBar, anchor='s')
        self.bottomFrame.place(relx=0, rely=0.95, relwidth=1, relheight=0.05, anchor='nw')
        
        self.userLabel = ttk.Label(self.bottomFrame, text='Logged in as: PLACEHOLDER', style='ItalicCaption.TLabel')
        self.userLabel.pack(side='left', expand=True)

        self.versionLabel = ttk.Label(self.bottomFrame, text='Version: PROTOTYPE', style='ItalicCaption.TLabel')
        self.versionLabel.pack(side='right', expand=True)

        self.timeLabel = ttk.Label(self.bottomFrame, text='RAHH', style='ItalicCaption.TLabel')
        self.timeLabel.pack(side='bottom', expand=True)

        self.time() # Call the time function to start updating the time at the bottom of the window

    # time function used to update the time at bottom of window every second
    def time(self):
        # creating a formatted string to show the date and time
        self.timeValue = datetime.datetime.now().strftime("%d/%m/%y | %I:%M:%S %p")
        self.timeLabel.configure(text = self.timeValue)
        # Calling the time function again after 1000ms (1 second)
        self.timeLabel.after(1000, self.time)

class UpcomingEventsPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard)

        self.table = ui.EventsTableView(self, controller, connection, cursor, rowData=database.getAllEventsDetails(cursor), columnData=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Location', 'Requirements'])

class DocumentationPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard).place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')

        self.baseFilePath = generalFunctions.resourcePath('Contents/Documents/Current Working Documents')
        self.accordion = ui.Accoridon(self, controller=controller, data=generalFunctions.getDirectoryStructure(self.baseFilePath))
        self.accordion.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.9, anchor='nw')

        self.controlsFrame = ttk.Frame(self, style='TFrame')
        self.controlsFrame.place(relx=0.3, rely=0.1, relwidth=0.7, relheight=0.1, anchor='nw')

        self.contentName = ttk.Label(self.controlsFrame, text='Click a File to View', style='file.TLabel')
        self.contentName.pack(side='left', padx=10, pady=20)

        self.exportButton = ttk.Button(self.controlsFrame, text='Export', image=controller.style.images['download'], compound='left', style='action.secondary.TButton', command=None)
        self.exportButton.pack(side='right', fill='both', padx=10, pady=10)
        self.deleteButton = ttk.Button(self.controlsFrame, text='Delete', image=controller.style.images['delete'], compound='left', style='action.secondary.TButton', command=None)
        self.deleteButton.pack(side='right', fill='both', padx=10, pady=10)
        self.saveButton = ttk.Button(self.controlsFrame, text='Save', image=controller.style.images['save'], compound='left', style='action.secondary.TButton', command=None)
        self.saveButton.pack(side='right', fill='both', padx=10, pady=10)
        self.editButton = ttk.Button(self.controlsFrame, text='Edit', image=controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None)
        self.editButton.pack(side='right', fill='both', padx=10, pady=10)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf() # Create a pdf object
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location='') # and set the default content to be a pdf, this will be changed when a file is selected
        self.contentViewer.pack(side='top', fill='both', expand=True)

class MemberInformationPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard)

        self.statisticsFrame = ttk.Frame(self, style='TFrame')
        self.statisticsFrame.pack(side='top', fill='both', expand=True)

        self.statisticsLabel = ttk.Label(self.statisticsFrame, text='Statistics', style='ItalicCaption.TLabel')
        self.statisticsLabel.pack(padx=10, pady=10)

        self.table = ui.MemberTableView(self, controller, connection, cursor, rowData=database.getAllMemberDetails(cursor), columnData=['Member ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])

class ArchivePage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard).place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')

        self.baseFilePath = generalFunctions.resourcePath('Contents/Documents/Archive')
        self.accordion = ui.Accoridon(self, controller=controller, data=generalFunctions.getDirectoryStructure(self.baseFilePath))
        self.accordion.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.9, anchor='nw')

        self.controlsFrame = ttk.Frame(self, style='TFrame')
        self.controlsFrame.place(relx=0.3, rely=0.1, relwidth=0.7, relheight=0.1, anchor='nw')

        self.contentName = ttk.Label(self.controlsFrame, text='Click a File to View', style='file.TLabel')
        self.contentName.pack(side='left', padx=10, pady=20)

        self.exportButton = ttk.Button(self.controlsFrame, text='Export', image=controller.style.images['download'], compound='left', style='action.secondary.TButton', command=None)
        self.exportButton.pack(side='right', fill='both', padx=10, pady=10)
        self.deleteButton = ttk.Button(self.controlsFrame, text='Delete', image=controller.style.images['delete'], compound='left', style='action.secondary.TButton', command=None)
        self.deleteButton.pack(side='right', fill='both', padx=10, pady=10)
        self.saveButton = ttk.Button(self.controlsFrame, text='Save', image=controller.style.images['save'], compound='left', style='action.secondary.TButton', command=None)
        self.saveButton.pack(side='right', fill='both', padx=10, pady=10)
        self.editButton = ttk.Button(self.controlsFrame, text='Edit', image=controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None)
        self.editButton.pack(side='right', fill='both', padx=10, pady=10)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf()
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location=generalFunctions.resourcePath('Contents/Documents/Archive/Manuals/soundboardManual.pdf'))
        self.contentViewer.pack(side='top', fill='both', expand=True)

class ConnectToSoundboardPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.pack(side='top', fill='both', expand=True)

        self.loginButton = ttk.Button(self.contentFrame, text='Connecting to Soundboard Time ;3', command=lambda: controller.showFrame(Dashboard), style='TButton')
        self.loginButton.pack()

        self.label = ttk.Label(self.contentFrame, text='Hey', style='TLabel')
        self.label.pack()
        self.label2 = ttk.Label(self.contentFrame, text='Does this work??', style='TLabel')
        self.label2.pack()

class TrainingMaterialsPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard).place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')

        self.baseFilePath = generalFunctions.resourcePath('Contents/Documents/Training Materials')
        self.accordion = ui.Accoridon(self, controller=controller, data=generalFunctions.getDirectoryStructure(self.baseFilePath))
        self.accordion.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.9, anchor='nw')

        self.controlsFrame = ttk.Frame(self, style='TFrame')
        self.controlsFrame.place(relx=0.3, rely=0.1, relwidth=0.7, relheight=0.1, anchor='nw')

        self.contentName = ttk.Label(self.controlsFrame, text='Click a File to View', style='file.TLabel')
        self.contentName.pack(side='left', padx=10, pady=20)

        self.exportButton = ttk.Button(self.controlsFrame, text='Export', image=controller.style.images['download'], compound='left', style='action.secondary.TButton', command=None)
        self.exportButton.pack(side='right', fill='both', padx=10, pady=10)
        self.deleteButton = ttk.Button(self.controlsFrame, text='Delete', image=controller.style.images['delete'], compound='left', style='action.secondary.TButton', command=None)
        self.deleteButton.pack(side='right', fill='both', padx=10, pady=10)
        self.saveButton = ttk.Button(self.controlsFrame, text='Save', image=controller.style.images['save'], compound='left', style='action.secondary.TButton', command=None)
        self.saveButton.pack(side='right', fill='both', padx=10, pady=10)
        self.editButton = ttk.Button(self.controlsFrame, text='Edit', image=controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None)
        self.editButton.pack(side='right', fill='both', padx=10, pady=10)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf()
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location='')
        self.contentViewer.pack(side='top', fill='both', expand=True)

class SettingsPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.pack(side='top', fill='both', expand=True)

        self.loginButton = ttk.Button(self.contentFrame, text='Settings rahhh', command=lambda: controller.showFrame(Dashboard), style='TButton')
        self.loginButton.pack()

        self.label = ttk.Label(self.contentFrame, text='Hey', style='TLabel')
        self.label.pack()
        self.label2 = ttk.Label(self.contentFrame, text='Does this work??', style='TLabel')
        self.label2.pack()

class FAQPage(ui.PageStructure):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.pack(side='top', fill='both', expand=True)

        self.loginButton = ttk.Button(self.contentFrame, text='HMMM?? time', command=lambda: controller.showFrame(Dashboard), style='TButton')
        self.loginButton.pack()

        self.label = ttk.Label(self.contentFrame, text='Hey', style='TLabel')
        self.label.pack()
        self.label2 = ttk.Label(self.contentFrame, text='Does this work??', style='TLabel')
        self.label2.pack()

''' Main Program '''
#CONSTANTS
connection = sql.connect(generalFunctions.resourcePath("Contents/TestDatabase.db"))  # Establish a connection to the database
cursor = connection.cursor() # Create a cursor object to execute SQL queries
database.createAllTables(cursor) # Create all the tables in the database if they don't already exist

app = MainApp()
app.mainloop()