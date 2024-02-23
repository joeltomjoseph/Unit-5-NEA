import tkinter as tk
from typing import Any
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from PIL import Image, ImageTk
from tkVideoPlayer import TkinterVideo
import platform
from pathlib import Path
import datetime

from functions import generalFunctions, database

''' Constants '''
COLOURS = {
    "primary": "#3d4b74",
    "secondary": "#fbc536",
    "success": "#02b875",
    "info": "#17a2b8",
    "warning": "#f0ad4e",
    "danger": "#d9534f",
    "light": "#F8F9FA",
    "dark": "#343A40",
    "bg": "#ffffff",
    "fg": "#343a40",
    "selectbg": "#adb5bd",
    "selectfg": "#ffffff",
    "border": "#bfbfbf",
    "inputfg": "#343a40",
    "inputbg": "#ffffff",
    "active": "#f5f5f5"
}

ACCESS_LEVEL = '' # Determines what functionality is available to the user. Set after the user logs in.

# Fonts
BODY_FONT = 'TkTextFont 15'
HEADING_FONT = 'TkHeadingFont 38 bold'
ITALIC_CAPTION_FONT = 'TEMP - set in main.py when MainApp is initialised'
BOLD_CAPTION_FONT = 'TEMP - set in main.py when MainApp is initialised'
TOOLTIP_FONT = 'TkTooltipFont 13'
TEXT_ENTRY_FONT = 'TkTextFont 15'

def createWidgetStyles(style: ttk.Style):
    ''' Creates the custom styles for the widgets which overwrite the base styles from the theme '''
    # Test styles for debugging
    style.configure('test.TFrame', background='red')

    # Default - Override all widgets
    style.configure('.', font=(BODY_FONT)) # Used to fix the size of buttons created by default as they were too small

    # Text
    style.configure('TLabel', font=BODY_FONT)
    style.configure('Heading.TLabel', font=HEADING_FONT, background=COLOURS["primary"], foreground='#ffffff')
    style.configure('ItalicCaption.TLabel', font=ITALIC_CAPTION_FONT)
    style.configure('BoldCaption.TLabel', font=BOLD_CAPTION_FONT)
    style.configure('Entry.TLabel', font=TEXT_ENTRY_FONT)

    # Menu bar
    style.configure('mb.TFrame', background='#3D4B74')
    style.configure("mt.TLabel", font=("Arial", 16, "bold"), foreground="#ffffff", background="#3D4B74")
    style.configure("Close.secondary.TButton", foreground='black', font=('TkTextFont 15 bold'), width=10)

    # Video player
    style.configure('videoplayer.TFrame', background='#f5f5f5')
    style.configure('play.secondary.TButton', foreground='black', font=('TkTextFont 15 bold'), width=10)
    style.configure('skip.secondary.TButton', foreground='black', font=('TkTextFont 15 bold'), width=5)

    # Tableview
    style.configure('t.primary.Treeview', font=BODY_FONT, rowheight=30)
    
    # Dashboard
    style.configure('db.TFrame', background='#F5F5F5')
    style.configure('dbButton.Outline.TButton', background='#F5F5F5', foreground='black', font=BODY_FONT, justify='center', wraplength=350)
    style.configure('UE.dbButton.Outline.TButton', font='TkTextFont 18')
    style.configure('dbLabel.TLabel', background='#F5F5F5', foreground='black', font=BODY_FONT, justify='center', wraplength=250)

    # Documentation
    style.configure('accordion.primary.Treeview', font=BODY_FONT, rowheight=30)
    style.configure('accordion.primary.Treeview.Item', indicatorsize=2)
    style.configure('file.TLabel', foreground='black', font=('TkTextFont 18 bold'))
    style.configure('action.secondary.TButton', foreground='black', font=('TkTextFont 15 bold'), width=15)

    # Connecting to Soundboard
    style.configure('start.success.TButton', font=BODY_FONT, justify='center', wraplength=350)
    style.configure('end.danger.TButton', font=BODY_FONT, justify='center', wraplength=350)

def createImages() -> dict:
    ''' Creates a dictionary of all (excluding a few) images created as PhotoImages in the images folder. These Photoimages can be reused when needed. '''
    images = {}
    for file in Path(generalFunctions.resourcePath('./Contents/images')).iterdir():
        if file.stem != '.DS_Store' and file.stem not in ['ags', 'backdrop', 'backdropHQ']: # Ignore the .DS_Store file and the images in the list
            images[file.stem] = tk.PhotoImage(name=file.stem, file=generalFunctions.resourcePath(file))
    return images

def createStyle() -> ttk.Style:
    ''' Initialises the style and loads the theme for the entire application '''
    style = ttk.Style()
    ttk.Style.load_user_themes(style, generalFunctions.resourcePath('Contents/agsStyle.json'))
    style.theme_use('ags')
    createWidgetStyles(style)
    style.images = createImages()
    return style

#Tooltip class and functions adapted from https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
class ToolTip:
    ''' Class to create a tooltip for a given widget. With customisable text. '''
    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.tipWindow = None
        self.id = None
        self.text = ''
        self.x = self.y = 0

    def showTooltip(self, text: str):
        ''' Display text in a tooltip window based on the mouse position '''
        self.text = text
        if self.tipWindow or not self.text:
            return
        x = self.widget.winfo_pointerx() + 8
        y = self.widget.winfo_pointery() + 8
        self.tipWindow = tk.Toplevel(self.widget)
        self.tipWindow.wm_overrideredirect(1)
        self.tipWindow.wm_geometry(f'+{x}+{y}')
        label = ttk.Label(self.tipWindow, text=self.text, justify='left',
                          background='#ffffff', relief='flat', borderwidth=1,
                          font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def showTooltipOnWidget(self, text: str):
        ''' Display text in a tooltip window based on the widget position '''
        self.text = text
        if self.tipWindow or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() - 10
        y = self.widget.winfo_rooty() - 10
        self.tipWindow = tk.Toplevel(self.widget)
        self.tipWindow.wm_overrideredirect(1)
        if platform.system() == 'Darwin': # If on MacOS
            self.tipWindow.transient(self.widget.master) # Shows the tooltip at all times so it won't be hidden behind the main window
        self.tipWindow.wm_geometry(f'+{x}+{y}')
        label = ttk.Label(self.tipWindow, text=self.text, justify='left',
                          background='#ffffff', relief='flat', borderwidth=1,
                          font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def hideTooltip(self):
        if self.tipWindow:
            self.tipWindow.destroy()
        self.tipWindow = None

def createTooltip(widget: tk.Widget, text: str, onWidget: bool = False):
    ''' Initialise a tooltip with text that is shown when the user hovers over chosen widget.
    If onWidget is True, the tooltip will be shown on the widget itself without the need to hover over it. '''
    tool_tip = ToolTip(widget)

    if onWidget:
        tool_tip.showTooltipOnWidget(text)

        def leave(tk_event: tk.Event = None):
            tool_tip.hideTooltip()

        widget.bind('<FocusIn>', leave)
        widget.after(8000, leave) # After 8 seconds, hide the tooltip
        #master.bind('<ShowFrame>', leave) #Add an event for when the page is changed to hide the tooltip
    else:
        def enter(tk_event: tk.Event):
            tool_tip.showTooltip(text)

        def leave(tk_event: tk.Event):
            tool_tip.hideTooltip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

# Adapted from https://stackoverflow.com/questions/46762061/how-to-create-multiple-label-in-button-widget-of-tkinter #TODO - try get this working for the UE button
class ContentButton(ttk.Button):
    ''' Class to create a button with a label on the top and another label in the center to show content like a table '''
    def __init__(self, parent, controller, textvariable, command, **kwargs):
        super().__init__(parent, **kwargs)
        self.textvariable = textvariable
        self.command = command

        self.configure(style='dbButton.TButton', command=self.command)
        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)

        self.buttonFrame = ttk.Frame(self, style='db.TFrame')
        self.buttonFrame.pack(side='top', fill='both', expand=True, pady=10, padx=10)
        self.buttonFrame.bind('<Enter>', self.enter)
        self.buttonFrame.bind('<ButtonRelease-1>', self.command)

        self.titleLabel = ttk.Label(self.buttonFrame, text='Upcoming Events', style='dbLabel.TLabel')
        self.titleLabel.pack(side='top', fill='x', pady=10, padx=10)
        self.titleLabel.bind('<ButtonRelease-1>', self.command)

        self.contentLabel = ttk.Label(self.buttonFrame, textvariable=self.textvariable, style='dbLabel.TLabel')
        self.contentLabel.pack(side='top', fill='both', pady=10, padx=10)
        self.contentLabel.bind('<ButtonRelease-1>', self.command)

        self.pack(side='top', fill='both', expand=True, padx=10, pady=10)

    def enter(self, event):
        for widget in (self, self.buttonFrame, self.titleLabel, self.contentLabel):
            widget.configure(state='active') #ERROR - This doesn't work
    
    def leave(self, event):
        for widget in (self, self.buttonFrame, self.titleLabel, self.contentLabel):
            widget.configure(state='disabled') #ERROR - This doesn't work

class PageStructure(ttk.Frame):
    ''' Base class for all pages '''
    def __init__(self, parent, controller):
        super().__init__(parent)

class MenuBar(ttk.Frame):
    ''' Class to create the menu bar shown on many pages '''
    def __init__(self, parent, controller, FAQPage, lastPage = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.pack(side='top', fill='x')

        self.configure(style='mb.TFrame')
        
        # Create title label
        self.logo = ImageTk.PhotoImage(Image.open(generalFunctions.resourcePath("Contents/images/ags.png")).resize((50, 50), Image.LANCZOS))
        self.titleLabel = ttk.Label(self, text="Sound and Lighting", image=self.logo, compound='left', style='mt.TLabel')
        self.titleLabel.pack(side="left", padx=10, pady=5)

        # Create close button
        closeButton = ttk.Button(self, text="Close", image=controller.style.images['logout'], compound='left', command=self.quit, style='Close.secondary.TButton')
        closeButton.pack(side="right", padx=10, pady=5)

        # Create FAQ/Help button
        helpButton = ttk.Button(self, text="FAQ", image=controller.style.images['help'], compound='left', command=lambda: controller.showFrame(FAQPage), style='Close.secondary.TButton')
        helpButton.pack(side="right", padx=10, pady=5)

        if lastPage:
            # Create back button
            backButton = ttk.Button(self, text="Back", image=controller.style.images['back'], compound='left', command=lambda: controller.showFrame(lastPage), style='Close.secondary.TButton')
            backButton.pack(side="left", padx=10, pady=5)

class updatedTableview(Tableview):
    ''' Overrides the base Tableview class to allow for customisation of the tableview.
    This changes the _build_search_frame function to include more controls such as an Add, Edit and Delete button. '''
    def __init__(self, master=None, controller=None, *args, **kwargs):
            self.controller = controller
            super().__init__(master, *args, **kwargs)

            self.view.configure(selectmode='browse', takefocus=False) # Set the selectmode to browse so only one row can be selected at a time
            self.view.bind('<<TreeviewSelect>>', self.updateButtons) # Bind the TreeviewSelect event to the updateButtons function to update the state of the buttons when a row is selected
    
    def _build_search_frame(self):
        """Build the search frame containing the search widgets. This
        frame is only created if `searchable=True` when creating the
        widget. Modified to include extra buttons for controls.
        """
        frame = ttk.Frame(self, padding=5)
        frame.pack(fill='x', side='top')
        ttk.Label(frame, text="Search").pack(side='left', padx=5)
        searchterm = ttk.Entry(frame, textvariable=self._searchcriteria)
        searchterm.pack(fill='x', side='left', expand=True)
        searchterm.bind("<Return>", self._search_table_data)
        searchterm.bind("<KP_Enter>", self._search_table_data)
        # Added extra buttons for controls
        self.deleteButton = ttk.Button(frame, text='Delete', image=self.controller.style.images['delete'], compound='left', style='action.secondary.TButton', command=self.master.deleteField)
        self.deleteButton.pack(side='right', fill='both', padx=10, pady=10)
        self.deleteButton.configure(state='disabled') # Set the delete button to be disabled by default
        self.addButton = ttk.Button(frame, text='Add', image=self.controller.style.images['add'], compound='left', style='action.secondary.TButton', command=self.master.addField)
        self.addButton.pack(side='right', fill='both', padx=10, pady=10)
        self.editButton = ttk.Button(frame, text='Edit', image=self.controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=self.master.editField)
        self.editButton.pack(side='right', fill='both', padx=10, pady=10)
        self.editButton.configure(state='disabled') # Set the edit button to be disabled by default

        ttk.Button(frame, text="⎌", command=self.reset_table, style="symbol.Link.TButton").pack(side='right', padx=5, pady=5)

    def updateButtons(self, event):
        ''' Update the state of the buttons based on the row that is selected. '''
        row = self.view.focus()

        if row:
            self.deleteButton.configure(state='normal')
            self.editButton.configure(state='normal')

class EventsTableView(ttk.Frame):
    ''' Class to create the tableview, allowing the user to view the data in a table format. '''
    def __init__(self, parent, controller, connection, cursor, rowData, columnData, **kwargs):
        super().__init__(parent, **kwargs)
        self.connection = connection
        self.cursor = cursor
        self.controller = controller

        self.pack(side='top', fill='both', expand=True)

        self.table = updatedTableview(self, self.controller, coldata=columnData, rowdata=rowData, paginated=True, searchable=True)
        self.table.configure(style='t.primary.Treeview')
        self.table.bind
        self.table.pack(side='top', fill='both', expand=True)
    
    def deleteField(self):
        ''' Handles when the delete button is clicked - get the id of the row that is selected and delete it from the database. '''
        row = self.table.view.focus() # get the row that is selected
    
        if row: # if a row is selected
            if Messagebox.show_question('Are you sure you want to delete this event?', 'Delete Event') == 'Yes':
                data = self.table.view.item(row, 'values') # get the data from the row
                # print(data)
                database.deleteRowWithID(self.connection, self.cursor, 'tbl_Events', 'eventID', data[0])

                self.table.build_table_data(rowdata=database.getAllEventsDetails(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Location', 'Requirements']) # rebuild the table with the updated data
        
    def addField(self):
        ''' Handles when the add button is clicked - open a new window to enter details and commit new event to the database. '''
        staffValues = [staff.split(': ') for staff in database.getStaffNamesandIDs(self.cursor)] # ie. [['1', 'Henderson'], ['2', 'Campbell-Nesbitt'], ['3', 'Byrne'], ['4', 'Dark']]
        locationValues = [location.split(': ') for location in database.getLocationsandIDs(self.cursor)] # ie. [['1', 'Stinson Hall'], ['2', 'Sports Hall'], ['3', 'Conference Room']]

        self.eventForm = GenericForm(self, self.controller, 'Add an Event/Assembly', '600x700') # Create a new popup window for the form

        self.title = ttk.Label(self.eventForm.titleFrame, text='Add an Event/Assembly', style='BoldCaption.TLabel')
        self.title.pack()
        # create the fields for the form
        self.name = ttk.Label(self.eventForm.formFrame, text="Name")
        self.name.pack()
        eventNameEntry = ttk.Entry(self.eventForm.formFrame)
        eventNameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Date").pack()
        eventDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
        eventDateEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Time (hh:mm)").pack()
        eventTimeEntry = ttk.Entry(self.eventForm.formFrame)
        eventTimeEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Duration (hh:mm)").pack()
        eventDurationEntry = ttk.Entry(self.eventForm.formFrame)
        eventDurationEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Requested By").pack()
        eventRequestedByEntry = ttk.Combobox(self.eventForm.formFrame, values=staffValues)
        eventRequestedByEntry.state(['readonly'])
        eventRequestedByEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Location").pack()
        eventLocationEntry = ttk.Combobox(self.eventForm.formFrame, values=[f'{location[0]} {location[1]}' for location in locationValues]) # unpack the values so they are formatted correctly
        eventLocationEntry.state(['readonly'])
        eventLocationEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Requirements").pack()
        eventRequirementsEntry = ttk.Entry(self.eventForm.formFrame)
        eventRequirementsEntry.pack()

        self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Submit", style='action.secondary.TButton', command=self.submit)
        self.submitButton.pack(side='left', padx=10, pady=10)

    def submit(self):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame) # get the data from the form
        # print(data)
        database.insertDataIntoEventsTable(self.connection, self.cursor, data)

        Messagebox.show_info('Event Added Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllEventsDetails(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Location', 'Requirements']) # rebuild the table with the updated data

        self.eventForm.destroy() # destroy the popup window

    def editField(self):
        ''' Handles when the edit button is clicked - open a new window to edit the details of the selected row and commit the changes to the database. '''
        row = self.table.view.focus() # get the row that is selected
        if row: # if a row is selected
            data = list(self.table.view.item(row, 'values')) # get the data from the row

            staffValues = [staff.split(': ') for staff in database.getStaffNamesandIDs(self.cursor)] # [['1', 'Henderson'], ['2', 'Campbell-Nesbitt'], ['3', 'Byrne'], ['4', 'Dark']]
            locationValues = [location.split(': ') for location in database.getLocationsandIDs(self.cursor)] # [['1', 'Stinson Hall'], ['2', 'Sports Hall'], ['3', 'Conference Room']]

            data[5] = [staff for staff in staffValues if staff[1] == data[5]][0] # replace the staff name with the id and name of the staff member ie. 'Henderson' -> ['1', 'Henderson'] 
            data[6] = [location for location in locationValues if location[1] == data[6]][0] # replace the name of location with the id and name of the location ie. 'Stinson Hall' -> ['1', 'Stinson Hall']
            # print(data)

            self.eventForm = GenericForm(self, self.controller, 'Update an Event/Assembly', '600x700') # Create a new popup window for the form

            self.title = ttk.Label(self.eventForm.titleFrame, text='Update an Event/Assembly', style='BoldCaption.TLabel')
            self.title.pack()
            # create the fields for the form
            self.name = ttk.Label(self.eventForm.formFrame, text="Name")
            self.name.pack()
            eventNameEntry = ttk.Entry(self.eventForm.formFrame)
            eventNameEntry.insert(0, data[1]) # insert the data from the row into the form so the user can see what they are editing
            eventNameEntry.pack()
            
            ttk.Label(self.eventForm.formFrame, text="Date").pack()
            eventDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
            eventDateEntry.entry.delete(0, 'end') # delete the default date that is shown
            eventDateEntry.entry.insert(0, data[2])
            eventDateEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Time (hh:mm)").pack()
            eventTimeEntry = ttk.Entry(self.eventForm.formFrame)
            eventTimeEntry.insert(0, data[3])
            eventTimeEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Duration (hh:mm)").pack()
            eventDurationEntry = ttk.Entry(self.eventForm.formFrame)
            eventDurationEntry.insert(0, data[4])
            eventDurationEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Requested By").pack()
            eventRequestedByEntry = ttk.Combobox(self.eventForm.formFrame, values=staffValues) #[staff[1] for staff in staffValues]
            eventRequestedByEntry.state(['readonly']) # make the combobox readonly so the user can't type in it, only select from the list
            # eventRequestedByEntry.insert(0, data[5])
            eventRequestedByEntry.set(data[5]) # set the value of the combobox to the staff member that is in the selected row
            eventRequestedByEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Location").pack()
            eventLocationEntry = ttk.Combobox(self.eventForm.formFrame, values=[f'{location[0]} {location[1]}' for location in locationValues]) #[location[1] for location in locationValues]
            eventLocationEntry.state(['readonly'])
            # eventLocationEntry.insert(0, data[6])
            eventLocationEntry.set(f'{data[6][0]} {data[6][1]}')
            eventLocationEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Requirements").pack()
            eventRequirementsEntry = ttk.Entry(self.eventForm.formFrame)
            eventRequirementsEntry.insert(0, data[7])
            eventRequirementsEntry.pack()

            self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Update", style='action.secondary.TButton', command=lambda: self.edit(id=data[0]))
            self.submitButton.pack(side='left', padx=10, pady=10)

    def edit(self, id):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame) # get the data from the form

        database.updateEvent(self.connection, self.cursor, data, id)

        Messagebox.show_info('Event Updated Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllEventsDetails(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Location', 'Requirements']) # rebuild the table with the updated data

        self.eventForm.destroy() # destroy the popup window

class MemberTableView(ttk.Frame):
    ''' Class to create the tableview, allowing the user to view the data in a table format. '''
    def __init__(self, parent, controller, connection, cursor, rowData, columnData, **kwargs):
        super().__init__(parent, **kwargs)
        self.connection = connection
        self.cursor = cursor
        self.controller = controller

        self.pack(side='top', fill='both', expand=True)

        self.table = updatedTableview(self, self.controller, coldata=columnData, rowdata=rowData, paginated=True, searchable=True)
        self.table.configure(style='t.primary.Treeview')
        self.table.pack(side='top', fill='both', expand=True)
    
    def deleteField(self):
        ''' Handles when the delete button is clicked - get the id of the row that is selected and delete it from the database. '''
        row = self.table.view.focus() # get the row that is selected
    
        if row: # if a row is selected
            if Messagebox.show_question('Are you sure you want to delete this Member?', 'Delete Member') == 'Yes':
                data = self.table.view.item(row, 'values') # get the data from the row
                # print(data)
                database.deleteRowWithID(self.connection, self.cursor, 'tbl_Pupils', 'memberID', data[0])

                self.table.build_table_data(rowdata=database.getAllMemberDetails(self.cursor), coldata=['Member ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])
        
    def addField(self):
        ''' Handles when the add button is clicked - open a new window to enter details and commit new event to the database. '''
        # yearGroupValues = [staff.split(': ') for staff in database.getStaffNamesandIDs(self.cursor)] # [['1', 'Henderson'], ['2', 'Campbell-Nesbitt'], ['3', 'Byrne'], ['4', 'Dark']]
        # regClassValues = [location.split(': ') for location in database.getLocationsandIDs(self.cursor)]
        classValues = [clss.split(': ') for clss in database.getClassesandIDs(self.cursor)] # ie. [['1', '14S'], ['2', '14T'], ['3', '14E'], ['4', '14P']]

        self.eventForm = GenericForm(self, self.controller, 'Add a Member', '600x700') # Create a new popup window for the form

        self.title = ttk.Label(self.eventForm.titleFrame, text='Add an Member', style='BoldCaption.TLabel')
        self.title.pack()

        ttk.Label(self.eventForm.formFrame, text="First Name").pack()
        firstNameEntry = ttk.Entry(self.eventForm.formFrame)
        firstNameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Surname").pack()
        surnameEntry = ttk.Entry(self.eventForm.formFrame)
        surnameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Username, *this will create a new Account with default password 'password'").pack()
        usernameEntry = ttk.Entry(self.eventForm.formFrame)
        usernameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Class").pack()
        classEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=classValues)
        classEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Email").pack()
        emailEntry = ttk.Entry(self.eventForm.formFrame)
        emailEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Date of Birth").pack()
        birthDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
        birthDateEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="House").pack()
        houseEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=['Tower', 'Massereene', 'Tardree', 'Clotworthy'])
        houseEntry.pack()

        self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Submit", style='action.secondary.TButton', command=self.submit)
        self.submitButton.pack(side='left', padx=10, pady=10)

    def submit(self):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame) #TODO - add validation, check if account with username already exists
        #print(data)
        data[2] = database.createAccount(self.connection, self.cursor, [data[2]]) # create account with default password 'password' and update the value of data[2] to the accountID
        database.insertDataIntoMemberTable(self.connection, self.cursor, data)

        Messagebox.show_info('Member Added Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllMemberDetails(self.cursor), coldata=['Member ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])

        self.eventForm.destroy()

    def editField(self):
        ''' Handles when the edit button is clicked - open a new window to edit the details of the selected row and commit the changes to the database. '''
        row = self.table.view.focus()
        if row:
            data = list(self.table.view.item(row, 'values'))

            classValues = [clss.split(': ') for clss in database.getClassesandIDs(self.cursor)] # ie. [['1', '14S'], ['2', '14T'], ['3', '14E'], ['4', '14P']]
            accountValues = [account.split(': ') for account in database.getAccountsAndIDs(self.cursor)] # ie. [['1', 'jjoseph553'], ['2', 'bjohnston123']]

            data[3] = [account for account in accountValues if account[1] == data[3]][0] # replace the name with the id and username of the account
            data[4] = [cls for cls in classValues if cls[1] == data[4]][0] # replace the name with the id and name of the staff member
            # print(data)

            self.eventForm = GenericForm(self, self.controller, 'Update Member Info', '600x700') # Create a new popup window for the form

            self.title = ttk.Label(self.eventForm.titleFrame, text='Update Member Info', style='BoldCaption.TLabel')
            self.title.pack()

            ttk.Label(self.eventForm.formFrame, text="First Name").pack()
            firstNameEntry = ttk.Entry(self.eventForm.formFrame)
            firstNameEntry.insert(0, data[1])
            firstNameEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Surname").pack()
            surnameEntry = ttk.Entry(self.eventForm.formFrame)
            surnameEntry.insert(0, data[2])
            surnameEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Username").pack()
            usernameEntry = ttk.Entry(self.eventForm.formFrame)
            usernameEntry.insert(0, data[3][0])
            usernameEntry.configure(state='readonly')
            usernameEntry.pack()
            ttk.Label(self.eventForm.formFrame, text=data[3][1]).pack()

            ttk.Label(self.eventForm.formFrame, text="Class").pack()
            classEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=classValues)
            classEntry.set(data[4])
            classEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Email").pack()
            emailEntry = ttk.Entry(self.eventForm.formFrame)
            emailEntry.insert(0, data[5])
            emailEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Date of Birth").pack()
            birthDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
            birthDateEntry.entry.delete(0, 'end')
            birthDateEntry.entry.insert(0, data[6])
            birthDateEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="House").pack()
            houseEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=['Tower', 'Massereene', 'Tardree', 'Clotworthy'])
            houseEntry.set(data[7])
            houseEntry.pack()

            self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Update", style='action.secondary.TButton', command=lambda: self.edit(id=data[0]))
            self.submitButton.pack(side='left', padx=10, pady=10)

    def edit(self, id):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame)
        #print(data)
        database.updateMember(self.connection, self.cursor, data, id)

        Messagebox.show_info('Member Updated Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllMemberDetails(self.cursor), coldata=['Member ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])

        self.eventForm.destroy()

class GenericForm(tk.Toplevel):
    ''' Class to create a generic form that can be used for adding and editing data. '''
    def __init__(self, parent, controller, title, size, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.title(title)
        self.geometry(size)
        self.iconphoto(True, tk.PhotoImage(file=generalFunctions.resourcePath('Contents/images/ags.png')))
        
        self.titleFrame = ttk.Frame(self)
        self.titleFrame.pack(side='top', fill='x')

        self.formFrame = ttk.Frame(self)
        self.formFrame.pack(side='top', expand=True)

        self.buttonsFrame = ttk.Frame(self)
        self.buttonsFrame.pack(side='bottom', fill='x')

        self.closeButton = ttk.Button(self.buttonsFrame, text='Close', style='Close.secondary.TButton', command=self.destroy)
        self.closeButton.pack(side='right', padx=10, pady=10)
    
    def getData(self, frame: ttk.Frame) -> list:
        ''' Get the data from the entry widgets within a Frame and return it as a list. '''
        data = []
        entries = [entry for entry in frame.winfo_children() if isinstance(entry, (ttk.Entry, ttk.Combobox, ttk.DateEntry))] # get all entry widgets in the frame
        
        for entry in entries:
            if isinstance(entry, ttk.Combobox): # if the widget is a combobox
                if entry.get().split(' ')[0].isdigit(): # if the first part of the string is a digit denoting an ID
                    data.append(entry.get().split(' ')[0]) # only append the ID, ie. '1 Henderson' -> '1'
                else: # if the first part of the string is not a digit
                    data.append(entry.get()) # append the whole string, ie. 'Henderson'
            elif hasattr(entry, 'get'): # if the widget has a get method
                data.append(entry.get())
            elif isinstance(entry, ttk.DateEntry): # if the widget is a DateEntry
                data.append(entry.entry.get()) # get the entry component of the DateEntry widget
        #print(data)
        return data

class Accoridon(ttk.Treeview):
    ''' Class to create the accordion menu, allowing the user to view the Options available '''
    def __init__(self, parent, controller, data, **kwargs):
        super().__init__(parent, **kwargs)

        self.column('#0', stretch=True, minwidth=100)
        self.configure(style='accordion.primary.Treeview', show='tree', selectmode='browse')
        self.tag_configure('directory', font=BOLD_CAPTION_FONT) # Set the font for the directory tags
        self.tag_bind('file', '<Double-Button-1>', self.onFileClick) # Bind the double click event to the file tags
        
        for key, value in data.items(): # Iterate through the data
            if key == 'files':
                self.insertField(value, '') # Skip inserting the field for 'files' and instead insert its children
            else:
                id = self.insert('', 'end', text=key, tags='directory') # Insert the key as a directory tag
                self.insertField(value, id) # Insert the children of the key
    
    def insertField(self, data, parentID):
        ''' Recursively create new fields inside the treeview with parent id of parentID. '''
        if isinstance(data, list): # If the data is a list
            for file in data: # Iterate through the list
                self.insert(parentID, 'end', text=file, tags='file') # Insert the files as a file tag

        else:
            for key, value in data.items():
                if key == 'files':
                    self.insertField(value, parentID) # Skip inserting the field for 'files' and instead insert its children
                else:
                    id = self.insert(parentID, 'end', text=key, tags='directory') 
                    self.insertField(value, id) # Insert the children of the key
    
    def refreshFields(self, data, *event):
        ''' Refresh the fields in the treeview '''
        self.delete(*self.get_children()) # Delete all the children of the treeview
        
        self.insertField(data, '') # Insert the new data into the treeview

        #self.after(10000, self.refreshFields, data) # Refresh the fields after 10 seconds
    
    def onFileClick(self, event):
        ''' Handles when a file is clicked - get the file path of the clicked file and display it in the pdf viewer '''
        def getParents(event, baseIID) -> list:
            ''' Get all parents of the clicked item in the hierarchy '''
            parents = []
            currentIID = baseIID

            while currentIID: # While the currentIID is not ''
                parentIID = event.widget.parent(currentIID) # Get the parent of the currentIID
                if parentIID and event.widget.item(parentIID, 'text') not in parents: # if parentIID isnt '' and the parent isn't already in the list due to base filepath
                    parents.append(event.widget.item(parentIID, 'text')) # append the parent to the list
                    #print(parents[-1])
                currentIID = parentIID # set the currentIID to the parentIID

            return parents

        itemIID = event.widget.selection()[0] # Get the item that was clicked
        item = event.widget.item(itemIID, 'text') # Get the text of the item that was clicked
        
        parents = getParents(event, itemIID)[::-1] # Get all the parents of the clicked item in the hierarchy and reverse the list so the base filepath is first

        filePath = generalFunctions.resourcePath(f'{self.master.baseFilePath}/{"/".join(parent for parent in parents)}/{item}') # Create the filepath to the file that was clicked
        #print(filePath)

        if item.endswith('.pdf') or item.endswith('.png'): # If the file is a pdf or png
            try:
                self.master.contentViewer.destroy() # Destroy the current contentViewer
                self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None # Reset the display_msg, frame and text variables
                self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                self.master.contentViewer = self.master.pdfObject.pdf_view(self.master.contentFrame, bar=False, pdf_location=filePath) # Create a new pdf viewer
                self.master.contentViewer.pack(side='top', fill='both', expand=True)
                self.master.contentName.configure(text=item) # Set the contentName label to the name of the file

                self.master.exportButton.configure(state='normal') # Enable the export button
                self.master.exportButton.configure(command=lambda: generalFunctions.copyFile(filePath)) # Set the export button to export the clicked file
                self.master.openFileLocButton.configure(state='normal') # Enable the open file location button
                self.master.openFileLocButton.configure(command=lambda: generalFunctions.showFileExplorer(filePath)) # Set the open file location button to open the clicked file
            except Exception as e:
                print(e)

        if item.endswith('.mp4') or item.endswith('.mov'): # If the file is a video
            try:
                self.master.contentViewer.destroy() # Destroy the current contentViewer
                self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None # Reset the display_msg, frame and text variables
                self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                self.master.contentViewer = videoPlayer(self.master.contentFrame, self.master, filePath) # Create a new video player
                self.master.contentViewer.pack(side='top', fill='both', expand=True)
                self.master.contentViewer.load_video(filePath) # Load the video
                self.master.contentName.configure(text=item) # Set the contentName label to the name of the file

                self.master.exportButton.configure(state='normal') # Enable the export button
                self.master.exportButton.configure(command=lambda: generalFunctions.copyFile(filePath)) # Set the export button to export the clicked file
                self.master.openFileLocButton.configure(state='normal') # Enable the open file location button
                self.master.openFileLocButton.configure(command=lambda: generalFunctions.showFileExplorer(filePath)) # Set the open file location button to open the clicked file
            except Exception as e:
                print(e)

        if item.endswith('.docx'): # If the file is a word document
            try:
                self.master.contentViewer.destroy() # Destroy the current contentViewer
                self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None # Reset the display_msg, frame and text variables
                self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                self.master.contentName.configure(text=item) # Set the contentName label to the name of the file

                self.master.exportButton.configure(state='normal') # Enable the export button
                self.master.exportButton.configure(command=lambda: generalFunctions.copyFile(filePath)) # Set the export button to export the clicked file
                self.master.openFileLocButton.configure(state='normal') # Enable the open file location button
                self.master.openFileLocButton.configure(command=lambda: generalFunctions.showFileExplorer(filePath)) # Set the open file location button to open the clicked file
            except Exception as e:
                print(e)

# Adapted from https://github.com/PaulleDemon/tkVideoPlayer/blob/master/examples/sample_player.py
class videoPlayer(ttk.Frame):
    ''' Class to create the video player along with its UI '''
    def __init__(self, parent, controller, videoPath, **kwargs):
        super().__init__(parent, **kwargs)

        self.pack(side='top', fill='both', expand=True)

        self.configure(style='videoplayer.TFrame')

        self.videoPlayer = TkinterVideo(self, videoPath, keep_aspect=True, background='#f5f5f5')
        self.videoPlayer.pack(side='top', fill='both', expand=True)

        self.play_pause_btn = ttk.Button(self, style='play.secondary.TButton', text="Play", command=self.play_pause)
        self.play_pause_btn.pack()
        # controller.bind(self, '<space>', self.play_pause)

        self.skip_plus_5sec = ttk.Button(self, style='skip.secondary.TButton', text="-5", command=lambda: self.skip(-5))
        self.skip_plus_5sec.pack(side="left")

        self.start_time = ttk.Label(self, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_value = tk.DoubleVar(self)

        self.progress_slider = ttk.Scale(self, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        # progress_slider.bind("<ButtonRelease-1>", seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = ttk.Label(self, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.videoPlayer.bind("<<Duration>>", self.update_duration)
        self.videoPlayer.bind("<<SecondChanged>>", self.update_scale)
        self.videoPlayer.bind("<<Ended>>", self.video_ended )

        self.skip_plus_5sec = ttk.Button(self, style='skip.secondary.TButton', text="+5", command=lambda: self.skip(5))
        self.skip_plus_5sec.pack(side="left")

    def update_duration(self, event):
        """ updates the duration after finding the duration """
        duration = self.videoPlayer.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=int(duration)))
        self.progress_slider["to"] = duration

    def update_scale(self, event):
        """ updates the scale value """
        currentTime = self.videoPlayer.current_duration()
        self.progress_value.set(self.videoPlayer.current_duration())
        self.start_time["text"] = str(datetime.timedelta(seconds=int(currentTime)))

    def load_video(self, filePath):
        """ loads the video """
        if filePath:
            self.videoPlayer.load(filePath)

            self.progress_slider.config(to=0, from_=0)
            self.play_pause_btn["text"] = "Play"
            self.progress_value.set(0)

    def seek(self, value):
        """ used to seek a specific timeframe """
        self.videoPlayer.seek(int(float(value)))

    def skip(self, value: int):
        """ skip seconds """
        self.videoPlayer.seek(int(self.progress_slider.get())+value)
        self.progress_value.set(self.progress_slider.get() + value)

    def play_pause(self, event=None):
        """ pauses and plays """
        if self.videoPlayer.is_paused():
            self.videoPlayer.play()
            self.play_pause_btn["text"] = "Pause"

        else:
            self.videoPlayer.pause()
            self.play_pause_btn["text"] = "Play"

    def video_ended(self, event):
        """ handle video ended """
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)