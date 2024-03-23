import tkinter as tk
from tkinter import messagebox, font
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from PIL import Image, ImageTk
from tkPDFViewer2 import tkPDFViewer as tkPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import sqlite3 as sql
import threading

import ui
from functions import generalFunctions, validation, database, soundBoardController

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
        for F in (LoginPage, UpcomingEventsPage, DocumentationPage, MemberandStaffInformationPage, ArchivePage, ConnectToSoundboardPage, TrainingMaterialsPage, SettingsPage, Dashboard):
            frame = F(contentFrame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        
        # Show the login page
        frame = LoginPage(contentFrame, self)
        self.frames[LoginPage] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        self.showFrame(LoginPage)
        
        # frame = Dashboard(contentFrame, self)
        # self.frames[Dashboard] = frame
        # frame.grid(row=0, column=0, sticky='nsew')
        # self.showFrame(Dashboard, resizeTo='1920x1080+0+0')
    
    def showFrame(self, cont, resizeTo: str = None, showFAQ: bool = False):
        ''' Show the frame for the given page name. If `resizeTo` is given, resize the window to the given dimensions. If `showFAQ` is true, show the FAQ Toplevel window. '''
        if resizeTo:
            #self.state('zoomed')
            self.geometry(resizeTo)
        if showFAQ:
            FAQPage(cont, self)
            return
        frame = self.frames[cont]
        frame.tkraise()

    def updateAccessLevel(self, accessLevel: str | None, accountDetails: list | None):
        ''' Update the access level of the user and change the functions available for them. Show the Dashboard, update the Logged in user label, and unbind the return key press event. 
        If the access level is `None`, show the login page. '''
        ui.ACCESS_LEVEL = accessLevel

        if accessLevel == None:
            self.frames[LoginPage].usernameField.delete(0, 'end')
            self.frames[LoginPage].passwordField.delete(0, 'end')
            self.showFrame(LoginPage, resizeTo='1000x1000+250+0')
            self.bind('<Return>', self.frames[LoginPage].login)

            widgets = self.frames[Dashboard].buttonFrame.winfo_children()
            #widgets.extend(self.frames[Dashboard].eventFrame.winfo_children())
            for widget in widgets:
                if isinstance(widget, ttk.Button):
                    widget.configure(state='enabled')
            return
        
        self.showFrame(Dashboard, resizeTo='1920x1080+0+0')
        self.frames[Dashboard].userLabel.configure(text=f'Logged in as: {accountDetails[1]} | Year {accountDetails[3]}') if accountDetails[3] else self.frames[Dashboard].userLabel.configure(text=f'Logged in as: {accountDetails[1]} | {accountDetails[2]}')
        self.unbind('<Return>')

        if ui.ACCESS_LEVEL == 'Senior':
            self.frames[Dashboard].membersButton.configure(state='disabled')
        elif ui.ACCESS_LEVEL == 'Junior':
            self.frames[Dashboard].membersButton.configure(state='disabled')
            self.frames[Dashboard].archiveButton.configure(state='disabled')
        elif ui.ACCESS_LEVEL == 'Staff':
            self.frames[Dashboard].membersButton.configure(state='disabled')
            self.frames[Dashboard].archiveButton.configure(state='disabled')
            self.frames[Dashboard].trainingButton.configure(state='disabled')

    def closeApplication(self):
        ''' Safely close lose the application. Close the database connection and then destroy the window. '''
        try:
            self.destroy() # Destroy the window
            connection.close() # Close the database connection
        except:
            messagebox.showinfo('Error', 'Failed to close the application, this is likely due to something still running. Please try again. ')

class LoginPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent, controller)
        self.controller = controller
        self.controller.bind('<Return>', self.login) # Bind the login function to the return key press event
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
        self.usernameField.focus_set()
        
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
        self.loginButton = ttk.Button(self.canvasItemsFrame, text="Login", style='Login.secondary.TButton', command=self.login) #controller.showFrame(Dashboard, resizeTo='1920x1080+0+0'))
        self.loginButton.pack(pady=10)

        # Set up the canvas items; title and login form
        self.title = self.canvas.create_window(self.winfo_screenwidth()/2, (self.winfo_screenheight()/2)+100, anchor='center', window=self.titleLabel)
        self.frame = self.canvas.create_window(self.winfo_screenwidth()/2, self.winfo_screenheight()/2, anchor='center', window=self.canvasItemsFrame)
        self.canvas.bind('<Configure>', self.resizeCanvas) # Bind the resizeCanvas function to the canvas resizing event
    
    def validationCallback(self, widget, validationRoutine):
        ''' Callback function to validate the input in the given widget using the given validation routine. '''
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
        ''' Function to handle the forgotten password process. Open a new toplevel window. '''
        # https://stackoverflow.com/a/1103063 - Overview of process
        # TODO: Implement forgotten password functionality
        pass
    
    def login(self, event=None):
        ''' Function to handle the login process. Validate the username and password, then attempt to login, and set the access level depending on the details linked to the account. '''
        if validation.validateUsername(self.usernameField, self.usernameField.get()) and validation.validatePassword(self.passwordField, self.passwordField.get()):
            self.accountDetails = database.login(cursor, self.usernameField.get(), self.passwordField.get())

            if self.accountDetails: # If the account exists and the password is correct
                try:
                    if self.accountDetails[3]: # If the account is for a student (there is a year group present)
                        if self.accountDetails[3] in ['13', '14']: # If the account is in Year 13/14 (Sixth Form)
                            self.controller.updateAccessLevel('Senior', self.accountDetails)
                            # ui.ACCESS_LEVEL = 'Senior'
                            # self.controller.showFrame(Dashboard, resizeTo='1920x1080+0+0')
                            # self.controller.frames[Dashboard].userLabel.configure(text=f'Logged in as: {self.accountDetails[1]} | Year {self.accountDetails[3]}')
                            # self.controller.unbind('<Return>')
                        else: # else the account is part of the junior school
                            self.controller.updateAccessLevel('Junior', self.accountDetails)
                    else: # else the account is for a staff member
                        if self.accountDetails[2] == 'Staff':
                            self.controller.updateAccessLevel('Staff', self.accountDetails)
                        elif self.accountDetails[2] == 'Admin' or self.accountDetails[2] == 'Head Of the Team':
                            self.controller.updateAccessLevel('Admin', self.accountDetails)
                except:
                    messagebox.showerror('Error', 'The Account Exists, however there are no User Details. Please contact the system administrator.')
            else:
                messagebox.showerror('Login Failed', 'Invalid username or password')
                return

class Dashboard(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
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

        self.membersButton = ttk.Button(self.buttonFrame, text='Member and Staff Information', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(MemberandStaffInformationPage))
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

        self.versionLabel = ttk.Label(self.bottomFrame, text='Version: 0.3', style='ItalicCaption.TLabel')
        self.versionLabel.pack(side='right', expand=True)

        self.timeLabel = ttk.Label(self.bottomFrame, text='', style='ItalicCaption.TLabel')
        self.timeLabel.pack(side='bottom', expand=True)

        self.time() # Call the time function to start updating the time at the bottom of the window
        self.updatePage() # Call the updater function to start updating the page (e.g. upcoming events)

    def time(self):
        ''' Time function used to update the time at bottom of window every second '''
        # creating a formatted string to show the date and time
        self.timeValue = datetime.datetime.now().strftime("%d/%m/%y | %I:%M:%S %p")
        self.timeLabel.configure(text = self.timeValue)
        # Calling the time function again after 1000ms (1 second)
        self.timeLabel.after(1000, self.time)

    def updatePage(self):
        ''' Refresh the upcoming events button every 10 seconds to ensure up to date information is displayed '''
        # Update the upcoming events button text to show the latest events
        self.upcomingEventsTextVar.set(f'Upcoming Events\n\n\n{database.getLatestEventsDetails(cursor)}')
        # Call the updater function again after 10000ms (10 seconds)
        self.after(10000, self.updatePage)

class UpcomingEventsPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard)

        self.table = ui.EventsTableView(self, controller, connection, cursor, rowData=database.getAllEventsDetails(cursor), columnData=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements'])

class DocumentationPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
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
        self.openFileLocButton = ttk.Button(self.controlsFrame, text='Open File Location', image=controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None)
        self.openFileLocButton.pack(side='right', fill='both', padx=10, pady=10)
        self.exportButton.configure(state='disabled')
        self.openFileLocButton.configure(state='disabled')

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf() # Create a pdf object
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location='') # and set the default content to be a pdf, this will be changed when a file is selected
        self.contentViewer.pack(side='top', fill='both', expand=True)

class MemberandStaffInformationPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard)
        # Create the tabbed frame to hold the member and staff information + Statistics
        self.tabbedFrame = ttk.Notebook(self, style='TNotebook')
        self.tabbedFrame.pack(side='top', fill='both', expand=True)

        # Create the member information table
        self.MemberTable = ui.MemberTableView(self.tabbedFrame, controller, connection, cursor, rowData=database.getAllMemberDetails(cursor), columnData=['Member ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])
        self.tabbedFrame.add(self.MemberTable, text='Member Information')

        # Create the member statistics frame
        self.statisticsFrame = ScrolledFrame(self.tabbedFrame, style='TFrame')
        self.statisticsFrame.pack(side='top', fill='both', expand=True)
        self.tabbedFrame.add(self.statisticsFrame.container, text='Member Statistics')

        self.showMostActiveMembers()
        self.showPopularLocations()
        self.showMostFrequentRequesters()

        # Create the staff information table
        self.staffTable = ui.StaffTableView(self.tabbedFrame, controller, connection, cursor, rowData=database.getAllStaffDetails(cursor), columnData=['Staff ID', 'First Name', 'Surname', 'Username', 'Role', 'Staff Email'])
        self.tabbedFrame.add(self.staffTable, text='Staff Information')

    def showMostActiveMembers(self):
        ''' Query the database for the members who have set up the most events and create a bar graph showing the results. '''
        self.heading = ttk.Label(self.statisticsFrame, text='Most Active Members (Top 10)', style='ItalicCaption.TLabel')
        self.heading.pack(padx=10, pady=10)

        # Query the database to get the number of times each member has taken an event
        cursor.execute('''SELECT p.firstName || ' ' || p.surname || ' ' || c.yearGroup || c.registrationClass, COUNT(*) 
                       FROM tbl_SetupGroups as sg 
                       INNER JOIN tbl_Pupils as p ON sg.pupilID = p.memberID 
                       INNER JOIN tbl_Classes as c ON p.classID = c.classID
                       GROUP BY pupilID ORDER BY COUNT(*) DESC LIMIT 10''')
        result = cursor.fetchall()

        # Separate the Members and the count of events into their own lists
        members = [row[0] for row in result]
        eventCount = [row[1] for row in result]

        # Create the figure and bar itself
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.plot.bar(members, eventCount, tick_label=members)

        # Create the canvas to display the graph
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.statisticsFrame)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.canvas.draw()

    def showPopularLocations(self):
        ''' Query the database for information on the most popular locations and create a bar graph showing the results. '''
        self.heading = ttk.Label(self.statisticsFrame, text='Most Popular Event Locations', style='ItalicCaption.TLabel')
        self.heading.pack(padx=10, pady=10)

        # Query the database to get the number of times each member has taken an event
        cursor.execute('''SELECT l.nameOfLocation, COUNT(*) 
                       FROM tbl_Events as e
                       INNER JOIN tbl_Locations as l ON e.locationID = l.locationID
                       GROUP BY e.locationID ORDER BY COUNT(*) DESC''')
        result = cursor.fetchall()

        # Separate the Members and the count of events into their own lists
        locations = [row[0] for row in result]
        locationCount = [row[1] for row in result]

        # Create the figure and bar itself
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.plot.bar(locations, locationCount, tick_label=locations)

        # Create the canvas to display the graph
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.statisticsFrame)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.canvas.draw()

    def showMostFrequentRequesters(self):
        ''' Query the database for the top requesters of SL, display the information in a graph '''
        self.heading = ttk.Label(self.statisticsFrame, text='Most Frequent Event/Assembly Requesters', style='ItalicCaption.TLabel')
        self.heading.pack(padx=10, pady=10)

        # Query the database to get the number of times each member has taken an event
        cursor.execute('''SELECT s.firstName || ' ' || s.surname, COUNT(*) 
                       FROM tbl_Events AS e 
                       INNER JOIN tbl_Staff AS s ON e.requestedBy = s.staffID 
                       GROUP BY staffID ORDER BY COUNT(*) DESC LIMIT 10''')
        result = cursor.fetchall()

        # Separate the Members and the count of events into their own lists
        staff = [row[0] for row in result]
        staffCount = [row[1] for row in result]

        # Create the figure and bar itself
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.plot.bar(staff, staffCount, tick_label=staff)

        # Create the canvas to display the graph
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.statisticsFrame)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.canvas.draw()

class ArchivePage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
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
        self.openFileLocButton = ttk.Button(self.controlsFrame, text='Open File Location', image=controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None)
        self.openFileLocButton.pack(side='right', fill='both', padx=10, pady=10)
        self.exportButton.configure(state='disabled')
        self.openFileLocButton.configure(state='disabled')

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf()
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location='')
        self.contentViewer.pack(side='top', fill='both', expand=True)

class ConnectToSoundboardPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard).place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')

        self.infoFrame = ttk.Frame(self, style='TFrame')
        self.infoFrame.place(relx=0, rely=0.1, relwidth=1, relheight=0.05, anchor='nw')

        self.infoLabel = ttk.Label(self.infoFrame, text=f'''Status: {"Connected to Qu-24" if soundBoardController.checkIfConnected(b'qu-24') else "Not Connected"}''', style='ItalicCaption.TLabel')
        self.infoLabel.pack()

        self.controlsFrame = ttk.Frame(self, style='TFrame')
        self.controlsFrame.place(relx=0, rely=0.15, relwidth=0.5, relheight=0.85)
        self.controlsFrame.grid_columnconfigure([0,1], weight=1, uniform='column')
        self.controlsFrame.grid_rowconfigure([0,1,2], weight=1)

        self.setupButton = ttk.Button(self.controlsFrame, text='Setup for Assembly', style='dbButton.Outline.TButton', command=lambda: self.setupForAssemblyCallback())
        self.setupButton.grid(row=0, column=0, pady=10, padx=10, sticky='nsew')

        self.startRecordingButton = ttk.Button(self.controlsFrame, text='Start Recording', style='start.success.TButton', command=lambda: self.startRecordingCallback())
        self.startRecordingButton.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')

        self.seconds, self.mins = 0, 0 # Create variables to store the seconds and minutes of the recording
        self.recordingTimer = ttk.Label(self.controlsFrame, text='Press Start Recording to Begin', style='ItalicCaption.TLabel', justify='center') # Create a label to display the time of the recording
        self.recordingTimer.grid(row=1, column=1, pady=10, padx=10)

        self.endRecordingButton = ttk.Button(self.controlsFrame, text='End Recording', style='end.danger.TButton', command=lambda: self.endRecordingCallback())
        self.endRecordingButton.grid(row=2, column=0, pady=10, padx=10, sticky='nsew')

        self.openRecordingsButton = ttk.Button(self.controlsFrame, text='Open Recordings Folder', style='dbButton.Outline.TButton', command=lambda: generalFunctions.showFileExplorer(generalFunctions.resourcePath('Contents/Recordings')))
        self.openRecordingsButton.grid(row=2, column=1, pady=50, padx=50, sticky='nsew')

        self.unmuteFrame = ttk.Frame(self, style='TFrame')
        self.unmuteFrame.place(relx=0.5, rely=0.15, relwidth=0.5, relheight=0.85)
        self.unmuteFrame.grid_columnconfigure([0,1], weight=1, uniform='column')
        self.unmuteFrame.grid_rowconfigure([0,1,2], weight=1)

        self.unmuteCh1Button = ttk.Button(self.unmuteFrame, text='Unmute Channel 1', style='dbButton.Outline.TButton', command=lambda: self.toggleButtonFunctionality(self.unmuteCh1Button, [soundBoardController.controlMuteChannel(1, False), soundBoardController.controlMuteChannel(1, True)]))
        self.unmuteCh1Button.grid(row=0, column=0, pady=10, padx=10, sticky='nsew')

        self.unmuteCh2Button = ttk.Button(self.unmuteFrame, text='Unmute Channel 2', style='dbButton.Outline.TButton', command=lambda: self.toggleButtonFunctionality(self.unmuteCh2Button, [soundBoardController.controlMuteChannel(2, False), soundBoardController.controlMuteChannel(2, True)]))
        self.unmuteCh2Button.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')

        self.unmuteCh3Button = ttk.Button(self.unmuteFrame, text='Unmute Channel 3', style='dbButton.Outline.TButton', command=lambda: self.toggleButtonFunctionality(self.unmuteCh3Button, [soundBoardController.controlMuteChannel(3, False), soundBoardController.controlMuteChannel(3, True)]))
        self.unmuteCh3Button.grid(row=2, column=0, pady=10, padx=10, sticky='nsew')

        self.unmuteCh23Button = ttk.Button(self.unmuteFrame, text='Unmute Channel 23', style='dbButton.Outline.TButton', command=lambda: self.toggleButtonFunctionality(self.unmuteCh23Button, [soundBoardController.controlMuteChannel(23, False), soundBoardController.controlMuteChannel(23, True)]))
        self.unmuteCh23Button.grid(row=0, column=1, pady=10, padx=10, sticky='nsew')

        self.unmuteST3Button = ttk.Button(self.unmuteFrame, text='Unmute ST3', style='dbButton.Outline.TButton', command=lambda: self.toggleButtonFunctionality(self.unmuteST3Button, [soundBoardController.controlMuteChannel('ST3', False), soundBoardController.controlMuteChannel('ST3', True)]))
        self.unmuteST3Button.grid(row=1, column=1, pady=10, padx=10, sticky='nsew')

        self.unmuteLRButton = ttk.Button(self.unmuteFrame, text='Unmute Master', style='dbButton.Outline.TButton', command=lambda: self.toggleButtonFunctionality(self.unmuteLRButton, [soundBoardController.controlMuteChannel('LR', False), soundBoardController.controlMuteChannel('LR', True)]))
        self.unmuteLRButton.grid(row=2, column=1, pady=10, padx=10, sticky='nsew')

        global isRecording
        isRecording = False
        self.updatePage() # Call the updater function to start updating the page (e.g. status of connection to soundboard and buttons)

    def updatePage(self):
        ''' Function to update the page, checking the status of the connection to the soundboard and enabling/disabling buttons accordingly. '''
        # print(soundBoardController.checkIfConnected(b'qu-24'))
        if soundBoardController.checkIfConnected(b'qu-24'):
            self.infoLabel.configure(text=f'''Status: Connected to Qu-24''')
            # for all widgets in the controlsFrame and unmuteFrame, enable them
            widgets = self.controlsFrame.winfo_children()
            widgets.extend(self.unmuteFrame.winfo_children())
            for widget in widgets:
                if isinstance(widget, ttk.Button):
                    widget.configure(state='enabled')
            
        else:
            self.infoLabel.configure(text=f'''Status: Not Connected''')
            # for all widgets in the controlsFrame and unmuteFrame, disable them so they can't be clicked
            widgets = self.controlsFrame.winfo_children()
            widgets.extend(self.unmuteFrame.winfo_children())
            for widget in widgets:
                if isinstance(widget, ttk.Button):
                    widget.configure(state='disabled')
        # Call the updater function again after 1000ms (1 second)
        self.after(1000, self.updatePage)

    def setupForAssemblyCallback(self):
        ''' Callback function to setup the soundboard for assembly, sends multiple MIDI messages to the soundboard control more than one channel at a time. '''
        groupsOfMessages = [
            soundBoardController.controlMuteChannel('LR', False), # UNMUTE LR MASTER
            soundBoardController.controlMuteChannel(1, False), # UNMUTE CHANNEL 1
            soundBoardController.controlMuteChannel(23, False), # UNMUTE CHANNEL 23
            soundBoardController.setVolume('LR', 98), # SET LR MASTER FADER TO 0dB
            soundBoardController.setVolume(1, 98), # SET CHANNEL 1 FADER TO 0dB
            soundBoardController.setVolume(23, 98) # SET CHANNEL 23 FADER TO 0dB
        ]

        for message in groupsOfMessages:
            soundBoardController.sendOutput(message)
        
    def startRecordingCallback(self):
        ''' Callback function to start recording audio from the soundboard. '''
        global isRecording, recordingThread
        if not isRecording:
            isRecording = True
            soundBoardController.sendOutput(soundBoardController.controlMuteChannel('MTX1-2', False)) # UNMUTE MTX1-2
            soundBoardController.sendOutput(soundBoardController.setVolume('MTX1-2', 127)) # SET MTX1-2 FADER TO 10dBu, routing audio to the USB B port

            recordingThread = threading.Thread(target=soundBoardController.audioRecording.recordAudio) # Create a new thread to record audio, to prevent the GUI from freezing
            recordingThread.start() # Start the recording thread

            self.updateRecordingTimer() # Call the function to update the recording timer initially
        
    def updateRecordingTimer(self):
        ''' Function to update the recording timer every second. '''
        global isRecording
        if isRecording:
            self.seconds += 1
            if self.seconds == 60:
                self.mins += 1
                self.seconds = 0
            
            self.recordingTimer.configure(text=f'Recording: {self.mins}:{self.seconds:02d}') # Update the recording timer text to show the current time
            self.eventID = self.recordingTimer.after(1000, self.updateRecordingTimer) # Call the function again after 1000ms (1 second) and store the event ID to cancel the event later

    def endRecordingCallback(self):
        ''' Callback function to stop recording audio from the soundboard. Set the stop flag to True and wait for the recording thread to finish. '''
        global isRecording, recordingThread
        if isRecording:
            isRecording = False
            soundBoardController.audioRecording.stopFlag = True # Set the stop flag to True, breaking the loop in the recording thread
            recordingThread.join() # Wait for the recording thread to finish

            self.recordingTimer.after_cancel(self.eventID) # Cancel the event to update the recording timer
            self.recordingTimer.configure(text='Recording Ended') # Update the recording timer text to show that the recording has ended
            self.seconds, self.mins = 0, 0 # Reset the seconds and minutes variables

            messagebox.showinfo("Recording Completed", "The audio has been saved in the Recordings Folder!")

    def toggleButtonFunctionality(self, button: ttk.Button, commands: list):
        ''' Function to toggle the functionality of a button between two commands ie. an unmute and mute button in one. '''
        if 'Unmute' in button['text']: # If the button is an unmute button
            button.configure(text=button['text'].replace('Unmute', 'Mute')) # Change the text to be a mute button
            soundBoardController.sendOutput(commands[0]) # Send the unmute command
        else:
            button.configure(text=button['text'].replace('Mute', 'Unmute')) # Change the text to be an unmute button
            soundBoardController.sendOutput(commands[1]) # Send the mute command

class TrainingMaterialsPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
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
        self.openFileLocButton = ttk.Button(self.controlsFrame, text='Open File Location', image=controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None)
        self.openFileLocButton.pack(side='right', fill='both', padx=10, pady=10)
        self.exportButton.configure(state='disabled')
        self.openFileLocButton.configure(state='disabled')

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf()
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location='')
        self.contentViewer.pack(side='top', fill='both', expand=True)

class SettingsPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
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

class FAQPage(ttk.Toplevel):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent)
        self.title('FAQ - Help')
        self.geometry('820x600')
        self.minsize(820, 600)
        self.iconphoto(True, tk.PhotoImage(file=generalFunctions.resourcePath('Contents/images/ags.png')))

        self.mainFrame = ttk.Frame(self, style='TFrame')
        self.mainFrame.place(relx=0.3, rely=0, relwidth=0.7, relheight=1, anchor='nw')

        data = { # Data for the accordion and main content
            'General': 'This is the general section',
            'Login Page': 'What is this?',
            'Upcoming Events': 'What is this?',
            'Dashboard': 'This is the dashboard',
            'Member and Staff Information': 'This is the member and staff information',
            'Archive': 'This is the archive',
            'Connect to Soundboard': 'This is the connect to soundboard',
            'Training Materials': 'This is the training materials',
            'Settings': 'This is the settings',
            'FAQ': 'This is the FAQ'
        }
        self.accordion = ui.FAQAccordion(self, controller=controller, data=data)
        self.accordion.place(relx=0, rely=0, relwidth=0.3, relheight=1, anchor='nw')

        self.titleLabel = ttk.Label(self.mainFrame, text='Click a Heading to view Details', style='file.TLabel')
        self.titleLabel.place(relx=0.35, rely=0, relwidth=1, relheight=0.1, anchor='nw')
        self.contentLabel = ttk.Label(self.mainFrame, text='', style='paragraph.TLabel', wraplength=700, justify='left', anchor='nw')
        self.contentLabel.place(relx=0, rely=0.1, relwidth=1, relheight=0.9, anchor='nw')

''' Main Program '''
#CONSTANTS
connection = sql.connect(generalFunctions.resourcePath("Contents/TestDatabase.db"))  # Establish a connection to the database
cursor = connection.cursor() # Create a cursor object to execute SQL queries
database.createAllTables(cursor) # Create all the tables in the database if they don't already exist

app = MainApp()
app.mainloop()