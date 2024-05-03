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

        if accessLevel == None: # If the access level is None, show the login page
            self.frames[LoginPage].usernameField.delete(0, 'end') # Clear the username field
            self.frames[LoginPage].passwordField.delete(0, 'end') # Clear the password field
            self.showFrame(LoginPage, resizeTo='1000x1000+250+0') # Show the login page
            self.bind('<Return>', self.frames[LoginPage].login) # Bind the login function to the return key press event

            widgets = self.frames[Dashboard].buttonFrame.winfo_children() # Get all the widgets in the button frame on the Dashboard
            #widgets.extend(self.frames[Dashboard].eventFrame.winfo_children())
            for widget in widgets: # Loop through all the widgets (buttons) and enable them
                if isinstance(widget, ttk.Button):
                    widget.configure(state='enabled')
            return
        
        ui.ACCOUNT_ID = str(accountDetails[0]) # Get the ID of the user logged in with the given account details
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
        ''' Safely close lose the application. Close the database connection, clear the .temp/ folder and then destroy the window. '''
        try:
            self.quit() # Destroy the window
            connection.close() # Close the database connection

            # Clear the .temp/ folder
            generalFunctions.clearFolder('Contents/.temp')
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
        self.usernameField = ttk.Entry(self.canvasItemsFrame, font=ui.TEXT_ENTRY_FONT, validate='focusout', validatecommand=lambda: validation.validationCallback(self.usernameField, validation.validateUsername))
        self.usernameField.pack(pady=5, padx=20)
        self.usernameField.focus_set()
        
        # Set up the password label, field, and show password toggle
        self.passwordLabel = ttk.Label(self.canvasItemsFrame, text="Password")
        self.passwordLabel.pack(pady=10)
        self.passwordField = ttk.Entry(self.canvasItemsFrame, font=ui.TEXT_ENTRY_FONT, show="*", validate='focusout', validatecommand=lambda: validation.validationCallback(self.passwordField, validation.validatePassword))
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
        controller.style.configure('Login.secondary.TButton', borderwidth=2, focusthickness=2, width=20, foreground='black')
        self.loginButton = ttk.Button(self.canvasItemsFrame, text="Login", style='Login.secondary.TButton', command=self.login)
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
        ''' Function to handle the forgotten password process. Open a new toplevel window to allow the user to enter their details and send a code. '''
        # https://stackoverflow.com/a/1103063 - Overview of process
        self.forgottenPasswordWindow = tk.Toplevel(self)
        self.forgottenPasswordWindow.title('Forgotten Password')
        self.forgottenPasswordWindow.geometry('600x700+500+200')

        # Title + Instructions
        self.titleFrame = ttk.Frame(self.forgottenPasswordWindow)
        self.titleFrame.pack(side='top', expand=True)

        self.agsIcon = ImageTk.PhotoImage(Image.open(generalFunctions.resourcePath("Contents/images/ags.png")).resize((50, 50), Image.LANCZOS))
        self.titleLabel = ttk.Label(self.titleFrame, text='Forgotten Password', image=self.agsIcon, compound='left', style='file.TLabel')
        self.titleLabel.pack(side='top', expand=True)

        self.instructionLabel = ttk.Label(self.forgottenPasswordWindow, text='To reset your password, please enter your account username, the email associated with it along with your date of birth.\n\nAn email containing a code will be sent if a matching account is found - once the code is entered, you will be able to reset your password.', wraplength=500, justify='center', style='ItalicCaption.TLabel')
        self.instructionLabel.pack(side='top', expand=True)

        # Entry Frame
        self.entryFrame = ttk.Frame(self.forgottenPasswordWindow)
        self.entryFrame.pack(side='top', expand=True)

        self.usernameLabel = ttk.Label(self.entryFrame, text='Username')
        self.usernameLabel.pack(padx=10, pady=5)
        self.usernameEntry = ttk.Entry(self.entryFrame, font=ui.TEXT_ENTRY_FONT)
        self.usernameEntry.pack(padx=10, pady=10)

        self.emailLabel = ttk.Label(self.entryFrame, text='Email')
        self.emailLabel.pack(padx=10, pady=5)
        self.emailEntry = ttk.Entry(self.entryFrame, font=ui.TEXT_ENTRY_FONT)
        self.emailEntry.pack(padx=10, pady=10)

        self.dobLabel = ttk.Label(self.entryFrame, text='Date of Birth')
        self.dobLabel.pack(padx=10, pady=5)
        self.dobEntry = ttk.DateEntry(self.entryFrame, dateformat=r'%Y-%m-%d')
        self.dobEntry.pack(padx=10, pady=10)

        self.sendCodeButton = ttk.Button(self.forgottenPasswordWindow, text='Send Verification Code', style='Login.secondary.TButton', command=self.sendVerificationCode)
        self.sendCodeButton.pack(pady=10)

        # Verification Frame
        self.enterCodeFrame = ttk.Frame(self.forgottenPasswordWindow)
        self.enterCodeFrame.pack(side='top', fill='x', expand=True)

        self.codeLabel = ttk.Label(self.enterCodeFrame, text='Enter Verification Code')
        self.codeLabel.pack(padx=10, pady=5)

        self.codeEntry = ttk.Entry(self.enterCodeFrame, font=ui.TEXT_ENTRY_FONT)
        self.codeEntry.pack(padx=10, pady=10)

        self.verifyCodeButton = ttk.Button(self.forgottenPasswordWindow, text='Verify Code', style='Login.secondary.TButton', command=self.verifyCode)
        self.verifyCodeButton.pack(pady=10)

    def sendVerificationCode(self):
        ''' Function to handle sending the verification code to the user. '''
        self.username, self.email, self.dob = self.usernameEntry.get(), self.emailEntry.get(), self.dobEntry.entry.get()

        if self.username == '' or self.email == '' or self.dob == '': # If any of the fields are empty
            messagebox.showerror('Error', 'Please ensure all fields are filled in.')
            return
        
        sql = '''SELECT p.pupilID FROM tbl_Pupils as p
        INNER JOIN tbl_Accounts as a ON p.accountID = a.accountID
        WHERE a.username = ? AND p.studentEmail = ? AND p.dateOfBirth = ?'''

        cursor.execute(sql, (self.username, self.email, self.dob)) 
        result = cursor.fetchone()

        if not result: # If no account is found with the details provided
            messagebox.showerror('Error', 'No account found with the details provided.')
            return

        # Generate a random code and send it to the user
        self.verificationCode = generalFunctions.generateCode() # Generate a random 4 digit code, this code is stored in the class (self. -> @LoginPage) so it can be accessed later
        self.emailMessage = f'''Subject: Sound and Lighting - Password Reset Code\n\nYour password reset code is: {self.verificationCode}\n\nIf you did not request this code, please ignore this email.'''
        
        try:
            generalFunctions.sendEmail(self.email, self.emailMessage)
        except:
            messagebox.showerror('Error', 'Failed to send the email. Please check your email address and try again.')
            return
        messagebox.showinfo('Success', 'Verification Code Sent. Please check your email.')

    def verifyCode(self):
        ''' Function to handle verifying the code entered by the user. '''
        if self.codeEntry.get() == '': # If the code entry field is empty
            messagebox.showerror('Error', 'Please enter the verification code.')
            return
        
        if not hasattr(self, 'verificationCode'): # If the verification code has not been generated
            messagebox.showerror('Error', 'No verification code has been sent.')
            return
        
        if self.codeEntry.get() == str(self.verificationCode):
            messagebox.showinfo('Success', 'Code Verified. You can now reset your password.')

            self.forgottenPasswordWindow.destroy()

            self.resetPasswordWindow = tk.Toplevel(self)
            self.resetPasswordWindow.title('Reset Password')
            self.resetPasswordWindow.geometry('600x350+500+200')

            # Title + Instructions
            self.titleFrame = ttk.Frame(self.resetPasswordWindow)
            self.titleFrame.pack(side='top', expand=True)

            self.agsIcon = ImageTk.PhotoImage(Image.open(generalFunctions.resourcePath("Contents/images/ags.png")).resize((50, 50), Image.LANCZOS))
            self.titleLabel = ttk.Label(self.titleFrame, text='Reset Password', image=self.agsIcon, compound='left', style='file.TLabel')
            self.titleLabel.pack(side='top', expand=True)

            self.instructionLabel = ttk.Label(self.resetPasswordWindow, text='To reset your password, please enter your new password below.', wraplength=500, justify='center', style='ItalicCaption.TLabel')
            self.instructionLabel.pack(side='top', expand=True)

            # Entry Frame
            self.entryFrame = ttk.Frame(self.resetPasswordWindow)
            self.entryFrame.pack(side='top', expand=True)

            self.passwordLabel = ttk.Label(self.entryFrame, text='New Password')
            self.passwordLabel.pack(padx=10, pady=5)
            self.passwordEntry = ttk.Entry(self.entryFrame, font=ui.TEXT_ENTRY_FONT, validate='focusout', validatecommand=lambda: validation.validationCallback(self.passwordEntry, validation.validatePassword))
            self.passwordEntry.pack(padx=10, pady=10)

            self.confirmPasswordLabel = ttk.Label(self.entryFrame, text='Confirm Password')
            self.confirmPasswordLabel.pack(padx=10, pady=5)
            self.confirmPasswordEntry = ttk.Entry(self.entryFrame, font=ui.TEXT_ENTRY_FONT, validate='focusout', validatecommand=lambda: validation.validationCallback(self.confirmPasswordEntry, validation.validatePassword))
            self.confirmPasswordEntry.pack(padx=10, pady=10)

            self.resetPasswordButton = ttk.Button(self.resetPasswordWindow, text='Reset Password', style='Login.secondary.TButton', command=self.resetPassword)
            self.resetPasswordButton.pack(pady=10)
        else:
            messagebox.showerror('Error', 'Code Verification Failed. Please try again.')

    def resetPassword(self):
        ''' Function to handle resetting the password. '''
        if validation.validatePassword(self.passwordEntry, self.passwordEntry.get()) and validation.validatePassword(self.confirmPasswordEntry, self.confirmPasswordEntry.get()):
            if self.passwordEntry.get() != self.confirmPasswordEntry.get(): # If the passwords do not match
                messagebox.showerror('Error', 'Passwords do not match.')
                return
            
            if self.passwordEntry.get() == 'Password1': # If the password is the default password
                messagebox.showerror('Error', 'Password cannot be the default password.')
                return

            sql = '''UPDATE tbl_Accounts SET password = ? WHERE username = ?'''
            cursor.execute(sql, (self.passwordEntry.get(), self.username))
            connection.commit()

            messagebox.showinfo('Success', 'Password Reset Successfully.')
            self.resetPasswordWindow.destroy()

    def updateDefaultPasswordPrompt(self, accountID):
        ''' Function to handle updating the password, create a toplevel window that accepts a new password. '''
        self.updatePasswordWindow = tk.Toplevel(self)
        self.updatePasswordWindow.title('Update Password')
        self.updatePasswordWindow.geometry('600x400+500+200')

        # Title + Instructions
        self.titleFrame = ttk.Frame(self.updatePasswordWindow)
        self.titleFrame.pack(side='top', expand=True)

        self.agsIcon = ImageTk.PhotoImage(Image.open(generalFunctions.resourcePath("Contents/images/ags.png")).resize((50, 50), Image.LANCZOS))
        self.titleLabel = ttk.Label(self.titleFrame, text='Update Password', image=self.agsIcon, compound='left', style='file.TLabel')
        self.titleLabel.pack(side='top', expand=True)

        self.instructionLabel = ttk.Label(self.updatePasswordWindow, text='Please update your default password!\nTo update your password, please enter your new password below.', wraplength=500, justify='center', style='ItalicCaption.TLabel')
        self.instructionLabel.pack(side='top', expand=True)

        # Entry Frame
        self.entryFrame = ttk.Frame(self.updatePasswordWindow)
        self.entryFrame.pack(side='top', expand=True)

        self.passwordLabel = ttk.Label(self.entryFrame, text='New Password')
        self.passwordLabel.pack(padx=10, pady=5)
        self.passwordEntry = ttk.Entry(self.entryFrame, font=ui.TEXT_ENTRY_FONT, validate='focusout', validatecommand=lambda: validation.validationCallback(self.passwordEntry, validation.validatePassword))
        self.passwordEntry.pack(padx=10, pady=10)

        self.confirmPasswordLabel = ttk.Label(self.entryFrame, text='Confirm Password')
        self.confirmPasswordLabel.pack(padx=10, pady=5)
        self.confirmPasswordEntry = ttk.Entry(self.entryFrame, font=ui.TEXT_ENTRY_FONT, validate='focusout', validatecommand=lambda: validation.validationCallback(self.confirmPasswordEntry, validation.validatePassword))
        self.confirmPasswordEntry.pack(padx=10, pady=10)

        self.updatePasswordButton = ttk.Button(self.updatePasswordWindow, text='Update Password', style='Login.secondary.TButton', command=lambda: self.updatePassword(accountID))
        self.updatePasswordButton.pack(pady=10)

    def updatePassword(self, accountID):
        ''' Function to handle updating the password. '''
        if validation.validatePassword(self.passwordEntry, self.passwordEntry.get()) and validation.validatePassword(self.confirmPasswordEntry, self.confirmPasswordEntry.get()):
            if self.passwordEntry.get() == 'Password1':
                messagebox.showerror('Error', 'Password cannot be the default password.')
                return
            if self.passwordEntry.get() != self.confirmPasswordEntry.get():
                messagebox.showerror('Error', 'Passwords do not match.')
                return

            sql = '''UPDATE tbl_Accounts SET password = ? WHERE accountID = ?'''
            cursor.execute(sql, (self.passwordEntry.get(), accountID))
            connection.commit()

            messagebox.showinfo('Success', 'Password Updated Successfully.')
            self.updatePasswordWindow.destroy()

            self.passwordField.delete(0, 'end') # Clear the password field
            self.passwordField.focus_set() # Focus on the password field

    def login(self, event=None):
        ''' Function to handle the login process. Validate the username and password, then attempt to login, and set the access level depending on the details linked to the account. '''
        if validation.validateUsername(self.usernameField, self.usernameField.get()) and validation.validatePassword(self.passwordField, self.passwordField.get()):
            self.accountDetails = database.login(cursor, self.usernameField.get(), self.passwordField.get())

            if self.accountDetails: # If the account exists and the password is correct
                if self.passwordField.get() == 'Password1': # If the account has the default password
                    self.updateDefaultPasswordPrompt(self.accountDetails[0]) # Update the password
                    return
                try:
                    if self.accountDetails[3]: # If the account is for a student (there is a year group present)
                        if self.accountDetails[3] in ['13', '14']: # If the account is in Year 13/14 (Sixth Form)
                            self.controller.updateAccessLevel('Senior', self.accountDetails)
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
        self.upcomingEventsTextVar = ttk.StringVar(value=f'View Upcoming Events and Assemblies\n\n\n\n{database.getLatestEventsDetails(cursor)}')
        self.upcomingEventsButton = ttk.Button(self.eventFrame, textvariable=self.upcomingEventsTextVar, style='UE.dbButton.Outline.TButton', command=lambda: controller.showFrame(UpcomingEventsPage))
        self.upcomingEventsButton.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        
        # Create a frame for buttons
        self.buttonFrame = ttk.Frame(self, style='TFrame')
        # self.buttonFrame.pack(side='right', fill='both', expand=True, padx=10, pady=10, ipadx=10, ipady=10, anchor='ne')
        self.buttonFrame.place(relx=0.3, rely=0.1, relwidth=0.7, relheight=0.85, anchor='nw')
        self.buttonFrame.grid_columnconfigure([0,1], weight=1, uniform='column')
        self.buttonFrame.grid_rowconfigure([0,1,2], weight=1)

        # Create buttons for viewing documentation, information about members, archive, connect to soundboard, training materials, and settings
        self.documentationButton = ttk.Button(self.buttonFrame, text='View Current Documentation', style='dbButton.Outline.TButton', command=lambda: controller.showFrame(DocumentationPage))
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
        self.bottomFrame.place(relx=0, rely=0.95, relwidth=1, relheight=0.05, anchor='nw')
        self.bottomFrame.grid_columnconfigure([0,1,2], weight=1, uniform='column')
        self.bottomFrame.grid_rowconfigure([0], weight=1)
        
        self.userLabel = ttk.Label(self.bottomFrame, text='Logged in as: PLACEHOLDER', style='BoldCaption.TLabel', anchor='center')
        self.userLabel.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.timeLabel = ttk.Label(self.bottomFrame, text='', style='BoldCaption.TLabel', anchor='center')
        self.timeLabel.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.versionLabel = ttk.Label(self.bottomFrame, text='Version: 1.0', style='BoldCaption.TLabel', anchor='center')
        self.versionLabel.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')

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
        self.upcomingEventsTextVar.set(f'View Upcoming Events and Assemblies\n\n\n\n{database.getLatestEventsDetails(cursor)}')
        # Call the updater function again after 10000ms (10 seconds)
        self.after(10000, self.updatePage)

class UpcomingEventsPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard)

        self.table = ui.EventsTableView(self, controller, connection, cursor, rowData=database.getUpcomingEventsDetails(cursor), columnData=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements'])

class DocumentationPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard).place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')

        self.createRotaButton = ttk.Button(self, text='Create New Rota', image=controller.style.images['addRota'], compound='left', style='action.secondary.Outline.TButton', command=self.createRotaCallback)
        ui.createTooltip(self.createRotaButton, 'Create a new random rota of all pupils.')

        self.baseFilePath = generalFunctions.resourcePath('Contents/Documents/Current Working Documents')
        self.accordion = ui.Accoridon(self, controller=controller, data=generalFunctions.getDirectoryStructure(self.baseFilePath))
        self.accordion.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.9, anchor='nw')

        self.controlsFrame = ui.FileControlBar(self, controller)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf() # Create a pdf object
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location='') # and set the default content to be a pdf, this will be changed when a file is selected
        self.contentViewer.pack(side='top', fill='both', expand=True)

        self.addCreateRotaButton() # Call the function to add the create rota button if the user is an admin/Head of the Team
    
    def addCreateRotaButton(self):
        ''' If the user is an admin/Head of the Team, add a button to create a new rota above the accordion and update the positions accordingly. '''
        if ui.ACCESS_LEVEL == 'Admin' or ui.ACCESS_LEVEL == 'Head Of the Team':
            self.createRotaButton.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.1, anchor='nw')
            self.accordion.place(relx=0, rely=0.2, relwidth=0.3, relheight=0.8, anchor='nw')
        else:
            self.createRotaButton.place_forget()
            self.accordion.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.9, anchor='nw')

        self.accordion.after(5000, self.addCreateRotaButton) # Call the function again after 5 seconds to check if the user's access level has changed

    def createRotaCallback(self):
        ''' Callback function to create a new rota. '''
        members = [f'{member[1]} {member[2]}' for member in database.getAllMemberDetails(cursor)] # Get all the members and format them as 'First Name Surname'
        
        generalFunctions.createRota(members) # Call the createRota function to create a new rota

        messagebox.showinfo('Success', 'Rota Created Successfully. Please check the Rotas folder for the new rota.')

        self.accordion.refreshFields(generalFunctions.getDirectoryStructure(self.baseFilePath)) # Refresh the accordion to show the new rota

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

        # Create the graphs for the statistics, TODO - Add more statistics
        self.createGraphs()

        # Create the staff information table
        self.staffTable = ui.StaffTableView(self.tabbedFrame, controller, connection, cursor, rowData=database.getAllStaffDetails(cursor), columnData=['Staff ID', 'First Name', 'Surname', 'Username', 'Role', 'Staff Email'])
        self.tabbedFrame.add(self.staffTable, text='Staff Information')

    def createGraphs(self):
        ''' Used to create the all graphs for the statistics tab. Also removes and updates the graphs every 20 seconds.'''
        for widget in self.statisticsFrame.winfo_children(): # Remove all widgets from the frame
            widget.destroy()

        self.showMostActiveMembers()
        self.showMostActiveHouses()
        self.showMostFrequentRequesters()
        self.showPopularLocations()

        self.after(20000, self.createGraphs) # Call the function again after 20 seconds to update the graphs

    def showMostActiveMembers(self):
        ''' Query the database for the members who have set up the most events and create a bar graph showing the results. '''
        self.heading = ttk.Label(self.statisticsFrame, text='Most Active Members (Top 10)', style='ItalicCaption.TLabel')
        self.heading.pack(padx=10, pady=10)

        # Query the database to get the number of times each member has taken an event
        cursor.execute('''SELECT p.firstName || ' ' || p.surname || ' ' || c.yearGroup || c.registrationClass, COUNT(*) 
                       FROM tbl_SetupGroups as sg 
                       INNER JOIN tbl_Pupils as p ON sg.pupilID = p.pupilID 
                       INNER JOIN tbl_Classes as c ON p.classID = c.classID
                       GROUP BY sg.pupilID ORDER BY COUNT(*) DESC LIMIT 10''')
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

    def showMostActiveHouses(self):
        ''' Query the database for the Houses who have set up the most events and create a pie graph showing the results. '''
        self.heading = ttk.Label(self.statisticsFrame, text='Most Active Houses', style='ItalicCaption.TLabel')
        self.heading.pack(padx=10, pady=10)

        # Query the database to get the number of times each member has taken an event
        cursor.execute('''SELECT p.house, COUNT(*) 
                       FROM tbl_SetupGroups as sg 
                       INNER JOIN tbl_Pupils as p ON sg.pupilID = p.pupilID
                       GROUP BY p.house ORDER BY COUNT(*) DESC''')
        result = cursor.fetchall()

        # Separate the Members and the count of events into their own lists
        house = [row[0] for row in result]
        houseCount = [row[1] for row in result]
        colours = { # Colours for each house
            'Tower': '#A41820',
            'Massereene': '#0293D4',
            'Clotworthy': '#FDC922',
            'Tardree': '#03753F'
        }

        # Create the figure and bar itself
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.plot.pie(houseCount, labels=house, autopct='%1.1f%%', colors=[colours[key] for key in house])

        # Create the canvas to display the graph
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.statisticsFrame)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.canvas.draw()

    def showPopularLocations(self):
        ''' Query the database for information on the most popular locations and create a pie chart showing the results. '''
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
        # self.plot.bar(locations, locationCount, tick_label=locations)
        self.plot.pie(locationCount, labels=locations, autopct='%1.1f%%')

        # Create the canvas to display the graph
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.statisticsFrame)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.canvas.draw()

    def showMostFrequentRequesters(self):
        ''' Query the database for the top requesters of SL, display the information in a graph '''
        self.heading = ttk.Label(self.statisticsFrame, text='Most Frequent Event/Assembly Requesters (Top 10)', style='ItalicCaption.TLabel')
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

        self.controlsFrame = ui.FileControlBar(self, controller)

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

        self.isRecording = False
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
        if not self.isRecording:
            self.isRecording = True
            soundBoardController.sendOutput(soundBoardController.controlMuteChannel('MTX1-2', False)) # UNMUTE MTX1-2
            soundBoardController.sendOutput(soundBoardController.setVolume('MTX1-2', 100)) # SET MTX1-2 FADER TO aprox 1dBu, routing audio to the USB B port

            self.recordingThread = threading.Thread(target=soundBoardController.audioRecording.recordAudio) # Create a new thread to record audio, to prevent the GUI from freezing
            self.recordingThread.start() # Start the recording thread

            self.updateRecordingTimer() # Call the function to update the recording timer initially
        
    def updateRecordingTimer(self):
        ''' Function to update the recording timer every second. '''
        if self.isRecording:
            self.seconds += 1
            if self.seconds == 60:
                self.mins += 1
                self.seconds = 0
            
            self.recordingTimer.configure(text=f'Recording: {self.mins}:{self.seconds:02d}') # Update the recording timer text to show the current time
            self.eventID = self.recordingTimer.after(1000, self.updateRecordingTimer) # Call the function again after 1000ms (1 second) and store the event ID to cancel the event later

    def endRecordingCallback(self):
        ''' Callback function to stop recording audio from the soundboard. Set the stop flag to True and wait for the recording thread to finish. '''
        if self.isRecording:
            self.isRecording = False
            soundBoardController.audioRecording.STOP_FLAG = True # Set the stop flag to True, breaking the loop in the recording thread
            self.recordingThread.join() # Wait for the recording thread to finish

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

        self.controlsFrame = ui.FileControlBar(self, controller)

        self.contentFrame = ttk.Frame(self, style='TFrame')
        self.contentFrame.place(relx=0.3, rely=0.2, relwidth=0.7, relheight=0.8, anchor='nw')

        self.pdfObject = tkPDF.ShowPdf()
        self.contentViewer = self.pdfObject.pdf_view(self.contentFrame, bar=False, pdf_location='')
        self.contentViewer.pack(side='top', fill='both', expand=True)

class SettingsPage(ui.PageStructure):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent, controller)

        self.menuBar = ui.MenuBar(self, controller, FAQPage, Dashboard).place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')

        self.mainFrame = ttk.Frame(self, style='TFrame')
        self.mainFrame.place(relx=0.3, rely=0.1, relwidth=0.7, relheight=0.9, anchor='nw')

        data = {
            #'General': self.generalSettingsFrame, TODO - Add the general settings frame
            'Personal Details': self.personalDetailsFrame,
            'Private Study Periods': self.privateStudyPeriodsFrame
        }
        self.accordion = ui.SettingsAccordion(self, controller=controller, data=data)
        self.accordion.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.9, anchor='nw')

        self.titleFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.titleFrame.place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')
        self.titleLabel = ttk.Label(self.mainFrame, text='Click a Heading to view Details', style='Heading2.TLabel', justify='center')
        self.titleLabel.pack()

        self.contentFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.contentFrame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9, anchor='nw')

    def generalSettingsFrame(self):
        ''' Function to create the general settings frame. '''
        self.titleLabel.configure(text='General Settings')
        self.settingsFrame = ScrolledFrame(self.contentFrame, style='TFrame')
        self.settingsFrame.pack(fill='both', expand=True)

    def personalDetailsFrame(self):
        ''' Function to create the personal details frame. '''
        self.titleLabel.configure(text='Personal Details')
        self.personalFrame = ScrolledFrame(self.contentFrame, style='TFrame')
        self.personalFrame.pack(side='top', fill='both', expand=True)

        if ui.ACCESS_LEVEL in ['Admin', 'Head of the Team', 'Staff']:
            self.createStaffFormWidgets()
        else:
            self.createPupilFormWidgets()

    def createStaffFormWidgets(self):
        ''' Function to allow the admin/staff to edit their personal details. '''
        data = list(database.getStaffDetails(cursor, ui.ACCOUNT_ID))

        accountValues = [account.split(': ') for account in database.getAccountsAndIDs(cursor)] # ie. [['1', 'jjoseph553'], ['2', 'bjohnston123']]
        data[3] = [account for account in accountValues if account[1] == data[3]][0] # replace the name with the id and username of the account

        ttk.Label(self.personalFrame, text="", style='ItalicCaption.TLabel').pack()

        ttk.Label(self.personalFrame, text="First Name*").pack()
        firstNameEntry = ttk.Entry(self.personalFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(firstNameEntry, validation.presenceCheck))
        firstNameEntry.insert(0, data[1])
        firstNameEntry.pack()

        ttk.Label(self.personalFrame, text="Surname*").pack()
        surnameEntry = ttk.Entry(self.personalFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(surnameEntry, validation.presenceCheck))
        surnameEntry.insert(0, data[2])
        surnameEntry.pack()

        ttk.Label(self.personalFrame, text="Username*").pack()
        usernameEntry = ttk.Entry(self.personalFrame)
        usernameEntry.insert(0, data[3][0])
        usernameEntry.configure(state='disabled')
        usernameEntry.pack()
        ttk.Label(self.personalFrame, text=data[3][1]).pack()
        ui.createTooltip(usernameEntry, 'Your Username cannot be changed.')

        ttk.Label(self.personalFrame, text="Role*").pack()
        roleEntry = ttk.Combobox(self.personalFrame, state='readonly', values=['Admin', 'Staff'])
        roleEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(roleEntry, validation.presenceCheck))
        roleEntry.set(data[4])
        roleEntry.configure(state='disabled')
        roleEntry.pack()
        ui.createTooltip(roleEntry, 'Your Role cannot be changed.')

        ttk.Label(self.personalFrame, text="Email*").pack()
        emailEntry = ttk.Entry(self.personalFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(emailEntry, validation.presenceCheck, validation.emailFormatCheck))
        emailEntry.insert(0, data[5])
        emailEntry.pack()

        for widget in self.personalFrame.winfo_children(): # Loop through all the widgets in the personalFrame
            widget.pack_configure(pady=5) # Add padding to each widget

        self.submitButton = ttk.Button(self.personalFrame, text="Update", style='FormButton.secondary.TButton', command=lambda: self.updateStaff(id=data[0]))
        self.submitButton.pack(padx=10, pady=10)

    def updateStaff(self, id):
        ''' Function to update the staff member's details in the database. '''
        data = ui.GenericForm.getData(None, self.personalFrame)

        if data == None: return # If the data is None due to validation, return
        
        database.updateStaff(connection, cursor, data, id)

        messagebox.showinfo('Success', 'Your Details have been Updated Successfully.')

        for widget in self.personalFrame.winfo_children(): # Loop through all the widgets in the personalFrame
            widget.destroy() # Destroy each widget

        self.createStaffFormWidgets() # Call the function to create the form widgets again, clearing the page and refreshing the data

    def createPupilFormWidgets(self):
        ''' Function to allow pupils to edit their personal details. '''
        data = list(database.getMemberDetails(cursor, ui.ACCOUNT_ID))
        
        classValues = [clss.split(': ') for clss in database.getClassesandIDs(cursor)] # ie. [['1', '14S'], ['2', '14T'], ['3', '14E'], ['4', '14P']]
        accountValues = [account.split(': ') for account in database.getAccountsAndIDs(cursor)] # ie. [['1', 'jjoseph553'], ['2', 'bjohnston123']]

        data[3] = [account for account in accountValues if account[1] == data[3]][0] # replace the name with the id and username of the account
        data[4] = [cls for cls in classValues if cls[0] == str(data[4])][0] # replace the id with the id and name of the class
        # print(data)

        ttk.Label(self.personalFrame, text="First Name*").pack()
        firstNameEntry = ttk.Entry(self.personalFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(firstNameEntry, validation.presenceCheck))
        firstNameEntry.insert(0, data[1])
        firstNameEntry.pack()

        ttk.Label(self.personalFrame, text="Surname*").pack()
        surnameEntry = ttk.Entry(self.personalFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(surnameEntry, validation.presenceCheck))
        surnameEntry.insert(0, data[2])
        surnameEntry.pack()

        ttk.Label(self.personalFrame, text="Username*").pack()
        usernameEntry = ttk.Entry(self.personalFrame)
        usernameEntry.insert(0, data[3][0])
        usernameEntry.configure(state='disabled')
        usernameEntry.pack()
        ttk.Label(self.personalFrame, text=data[3][1]).pack()
        ui.createTooltip(usernameEntry, 'Your Username cannot be changed.')

        ttk.Label(self.personalFrame, text="Class*").pack()
        classEntry = ttk.Combobox(self.personalFrame, state='readonly', values=classValues)
        classEntry.set(data[4])
        classEntry.configure(state='disabled')
        classEntry.pack()
        ui.createTooltip(classEntry, 'Your Class cannot be changed.')

        ttk.Label(self.personalFrame, text="Email*").pack()
        emailEntry = ttk.Entry(self.personalFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(emailEntry, validation.presenceCheck, validation.emailFormatCheck))
        emailEntry.insert(0, data[5])
        emailEntry.pack()

        ttk.Label(self.personalFrame, text="Date of Birth*").pack()
        birthDateEntry = ttk.DateEntry(self.personalFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
        birthDateEntry.entry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(birthDateEntry.entry, validation.presenceCheck, validation.dateInPastCheck))
        birthDateEntry.entry.delete(0, 'end')
        birthDateEntry.entry.insert(0, data[6])
        birthDateEntry.pack()

        ttk.Label(self.personalFrame, text="House*").pack()
        houseEntry = ttk.Combobox(self.personalFrame, state='readonly', values=['Tower', 'Massereene', 'Tardree', 'Clotworthy'])
        houseEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(houseEntry, validation.presenceCheck))
        houseEntry.set(data[7])
        houseEntry.pack()

        for widget in self.personalFrame.winfo_children(): # Loop through all the widgets in the personalFrame
            widget.pack_configure(pady=5) # Add padding to each widget

        self.submitButton = ttk.Button(self.personalFrame, text="Update", style='FormButton.secondary.TButton', command=lambda: self.updatePupil(id=data[0]))
        self.submitButton.pack(padx=10, pady=10)

    def updatePupil(self, id):
        ''' Function to update the pupil's details in the database. '''
        data = ui.GenericForm.getData(None, self.personalFrame)

        if data == None: return # If the data is None due to validation, return
        
        database.updateMember(connection, cursor, data, id)

        messagebox.showinfo('Success', 'Your Details have been Updated Successfully.')

        for widget in self.personalFrame.winfo_children(): # Loop through all the widgets in the personalFrame
            widget.destroy() # Destroy each widget

        self.createPupilFormWidgets() # Call the function to create the form widgets again, clearing the page and refreshing the data

    def privateStudyPeriodsFrame(self):
        ''' Function to create the private study periods frame. '''
        self.titleLabel.configure(text='Private Study Periods')
        self.privateStudyFrame = ScrolledFrame(self.contentFrame, style='TFrame')
        self.privateStudyFrame.pack(side='top', fill='both', expand=True)

        self.comingSoon = ttk.Label(self.privateStudyFrame, text='Coming Soon!', style='Heading2.TLabel', justify='center')
        self.comingSoon.pack()

class FAQPage(ttk.Toplevel):
    def __init__(self, parent, controller: MainApp):
        super().__init__(parent)
        self.title('FAQ - Help')
        self.geometry('960x600')
        self.minsize(960, 600)
        self.iconphoto(True, tk.PhotoImage(file=generalFunctions.resourcePath('Contents/images/ags.png')))

        self.mainFrame = ttk.Frame(self, style='TFrame')
        self.mainFrame.place(relx=0.3, rely=0, relwidth=0.7, relheight=1, anchor='nw')

        data = { # Data for the accordion and main content
            'General': 
            '''This software is used to manage the school\'s assemblies/events along with documentation and statistics. The Admin/Head of the Team can access all features including;\n\t- Creating Random Rotas\n\t- Managing (Adding/Editing and Removing) Members and Staff\n\t- Viewing Statistics\n\t- Managing (Adding/Editing and Removing) Events\n\t- Managing all Documentation\n\t- Connecting to and controlling the Soundboard\n\n
            Staff can access the following features;\n\t- Managing (Adding/Editing and Removing) Events\n\t- Viewing Current Documentation\n\t- Connecting to and controlling the Soundboard\n\n
            Senior Pupils can access the following features;\n\t- Viewing All Events and assigning themselves to an event\n\t- Managing all Documentation\n\t- Connecting to and controlling the Soundboard\n\n
            Junior Pupils can access the following features;\n\t- Viewing All Events and assigning themselves to an event\n\t- Viewing Current Documentation\n\t- Connecting to and controlling the Soundboard\n\n''',
            'Login Page': '''This page allows you to reset your password using the Forgot Password button, this will prompt you to enter your username along with it's associated email and date of birth to verify that the account is yours. \n\nAn email will then be sent with a random code - enter the code correctly and you will be able to set a new password.''',
            'Dashboard': '''The Dashboard has buttons to the rest of the program - depending on the user's access level, certain buttons will be disabled. ''',
            'Upcoming Events': '''This Page shows a table that can either display all events stored in the system or the upcoming events (from today onwards) using a toggle at the top "Show All Events".\n\nIf the user is a staff member (Admin/Staff/Head of the Team), the buttons on the top will be Add/Edit and Delete Events. \n\nIf the user is a pupil (Junior or Senior), those buttons will be replaced with a single button to join/leave the setup group for the selected event.\n\nUsers are also able to search through all records using the search bar and sort the results by clicking on the column heading.''',
            'View Working Documentation': '''Shows documentation stored in the Current Working Documentation folder. Videos do not play audio. If the user is an Admin/Head of the Team, an extra button will be shown allowing them to Generate a New Random Rota - this will randomly choose members in the database and create a Word Document for a 2 week rota in both the Stinson Hall and Sports Hall. This is created from a template stored in the Templates Folder.''',
            'Member and Staff Information': '''Allows the user to view all pupils, staff and statistics in the system. Only available to Admins/Head of the Team. 3 buttons to Add/Edit or Delete pupils/Staff.''',
            'Archive': '''Shows documentation stored in the Archive Folder.''',
            'Connect to Soundboard': '''This functionality only works when this device is connected to the QU-24 Soundboard directly using a USB-B connection. Allows users to Mute/Unmute specific channels on the board and also has a button to change multiple channels and set their volume to "Setup for Assembly". This unmutes and sets the volume of the channels most likely to be used during an average assembly.\n\nAdditionally, it allows users to record audio directly from the board (the output that is routed to the speakers will be recorded). This will be saved to the Recordings Folder.''',
            'Training Materials': '''This shows the documentation related to Training stored in the Training Materials folder. This includes Videos and Manuals.''',
            'Settings': '''This settings page allows users to change their own personal details (where applicable; cannot change what class they are in etc.).\n\n Future functionality includes General Settings like colour scheme or font size. Also the ability to add Private Study Periods for students to allow a Free Period Table to be created for Staff.''',
        }
        self.accordion = ui.FAQAccordion(self, controller=controller, data=data)
        self.accordion.place(relx=0, rely=0, relwidth=0.3, relheight=1, anchor='nw')

        self.titleFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.titleFrame.place(relx=0, rely=0, relwidth=1, relheight=0.1, anchor='nw')
        self.titleLabel = ttk.Label(self.mainFrame, text='Click a Heading to view Details', style='Heading2.TLabel')
        self.titleLabel.pack()
        
        self.contentFrame = ScrolledFrame(self.mainFrame, style='TFrame', autohide=True)
        self.contentFrame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9, anchor='nw')
        self.contentLabel = ttk.Label(self.mainFrame, text='', style='paragraph.TLabel', wraplength=650, justify='left', anchor='nw')
        self.contentLabel.pack(side='left', fill='both', expand=True)

''' Main Program '''
#CONSTANTS
generalFunctions.createTempFolder() # Create the temp folder if it doesnt exist

connection = sql.connect(generalFunctions.resourcePath("Contents/database.db"))  # Establish a connection to the database
cursor = connection.cursor() # Create a cursor object to execute SQL queries

database.createAllTables(cursor) # Create all the tables in the database if they don't already exist
if len(database.getAllRows(cursor, 'tbl_Accounts')) == 0: # If the table is empty, create an admin account
    database.createAccount(connection, cursor, ('admin000',))
    database.insertDataIntoStaffTable(connection, cursor, ('Admin', 'Admin', 1, 'Admin', 'agssoundandlighting@gmail.com'))

app = MainApp()
app.mainloop()