import tkinter as tk
from typing import Any
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from PIL import Image, ImageTk
from tkVideoPlayer import TkinterVideo
import docx2pdf
import platform
from pathlib import Path
import datetime

from functions import generalFunctions, database, validation

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
ACCOUNT_ID = '' # The ID of the user that is logged in. Set after the user logs in.

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
    style.configure('test.TLabel', background='red')

    # Default - Override all widgets
    style.configure('.', font=(BODY_FONT)) # Used to set the size of buttons created by default as they were too small

    # Text
    style.configure('TLabel', font=BODY_FONT)
    style.configure('Heading.TLabel', font=HEADING_FONT, background=COLOURS["primary"], foreground='#ffffff')
    style.configure('Heading2.TLabel', font=HEADING_FONT)
    style.configure('ItalicCaption.TLabel', font=ITALIC_CAPTION_FONT)
    style.configure('BoldCaption.TLabel', font=BOLD_CAPTION_FONT)
    style.configure('Entry.TLabel', font=TEXT_ENTRY_FONT)
    style.configure('paragraph.TLabel', font=BODY_FONT, justify='left', wraplength=500)

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
    style.configure('file.TLabel', foreground='black', font=('TkTextFont 19 bold'))
    style.configure('action.secondary.TButton', foreground='black', font=('TkTextFont 15 bold'), width=20, justify='center')
    style.configure('action.secondary.Outline.TButton', foreground='black', font=('TkTextFont 15 bold'), width=20, justify='center')
    style.map('action.secondary.Outline.TButton', foreground=[('selected', 'black')])

    # Connecting to Soundboard
    style.configure('start.success.TButton', font=BODY_FONT, justify='center', wraplength=350)
    style.configure('end.danger.TButton', font=BODY_FONT, justify='center', wraplength=350)

    # Forms
    style.configure('FormButton.secondary.TButton', foreground='black', font=('TkTextFont 15 bold'), width=10, justify='center')

def createImages() -> dict[str, tk.PhotoImage]:
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

    def showTooltipOnWidget(self, text: str, error: bool = False):
        ''' Display text in a tooltip window based on the widget position, if `error` is True, the tooltip will be shown in red. '''
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
        if error:
            label.configure(background='red', foreground='white')
        
        label.pack(ipadx=1)

    def hideTooltip(self):
        if self.tipWindow:
            self.tipWindow.destroy()
        self.tipWindow = None

def createTooltip(widget: tk.Widget, text: str, onWidget: bool = False, error: bool = False):
    ''' Initialise a tooltip with text that is shown when the user hovers over chosen widget.
    If `onWidget` is True, the tooltip will be shown on the widget itself without the need to hover over it.
    If `error` is True, the tooltip will be shown in red. '''
    tool_tip = ToolTip(widget)

    if onWidget:
        tool_tip.showTooltipOnWidget(text, error)

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
        self.closeButton = ttk.Button(self, text="Close", image=controller.style.images['logout'], compound='left', command=controller.closeApplication, style='Close.secondary.TButton')
        self.closeButton.pack(side="right", padx=10, pady=5)

        # Create Logout button
        self.logoutButton = ttk.Button(self, text="Logout", image=controller.style.images['logout'], compound='left', command=lambda: controller.updateAccessLevel(None, None), style='Close.secondary.TButton')
        self.logoutButton.pack(side="right", padx=10, pady=5)

        # Create FAQ/Help button
        self.helpButton = ttk.Button(self, text="FAQ", image=controller.style.images['help'], compound='left', command=lambda: controller.showFrame(controller, showFAQ = True), style='Close.secondary.TButton')
        self.helpButton.pack(side="right", padx=10, pady=5)

        if lastPage:
            # Create back button
            backButton = ttk.Button(self, text="Back", image=controller.style.images['back'], compound='left', command=lambda: controller.showFrame(lastPage), style='Close.secondary.TButton')
            backButton.pack(side="left", padx=10, pady=5)

class updatedTableview(Tableview):
    ''' Overrides the base Tableview class to allow for customisation of the tableview.
    This changes the '_build_search_frame' function to include more controls such as an Add, Edit and Delete button. '''
    def __init__(self, master=None, controller=None, eventPage: bool = False, *args, **kwargs):
            self.controller = controller
            super().__init__(master, autoalign=True, *args, **kwargs)

            self.view.configure(selectmode='browse', takefocus=False) # Set the selectmode to browse so only one row can be selected at a time
            self.view.bind('<<TreeviewSelect>>', self.updateButtons) # Bind the TreeviewSelect event to the updateButtons function to update the state of the buttons when a row is selected

            if eventPage:
                self.view.bind('<<TreeviewSelect>>', self.updateEventPageButtons) # Bind the TreeviewSelect event to the pupilOnlyJoinSetupGroup function to update the state of the buttons when a row is selected

    def autoalign_columns(self):
        """Align the columns and headers based on the data type of the
        values. All text/numbers is center-aligned. This
        method will have no effect if there is no data in the tables.
        Modified to center align all text and numbers."""
        if len(self._tablerows) == 0:
            return

        values = self._tablerows[0]._values
        for i, value in enumerate(values):
            if str(value).isnumeric():
                self.view.column(i, anchor='center')
                self.view.heading(i, anchor='center')
            else:
                self.view.column(i, anchor='center')
                self.view.heading(i, anchor='center')

    def _build_search_frame(self):
        """Build the search frame containing the search widgets. This
        frame is only created if `searchable=True` when creating the
        widget. Modified to include extra buttons for controls.
        """
        self.frame = ttk.Frame(self, padding=5)
        self.frame.pack(fill='x', side='top')
        ttk.Label(self.frame, text="Search").pack(side='left', padx=5)
        searchterm = ttk.Entry(self.frame, textvariable=self._searchcriteria)
        searchterm.pack(fill='x', side='left', expand=True)
        searchterm.bind("<Return>", self._search_table_data)
        searchterm.bind("<KP_Enter>", self._search_table_data)
        # Added extra buttons for controls
        self.deleteButton = ttk.Button(self.frame, text='Delete', image=self.controller.style.images['delete'], compound='left', style='action.secondary.TButton', command=self.master.deleteField)
        self.deleteButton.pack(side='right', fill='both', padx=10, pady=10)
        self.deleteButton.configure(state='disabled') # Set the delete button to be disabled by default
        self.addButton = ttk.Button(self.frame, text='Add', image=self.controller.style.images['add'], compound='left', style='action.secondary.TButton', command=self.master.addField)
        self.addButton.pack(side='right', fill='both', padx=10, pady=10)
        self.addButton.configure(state='disabled') # Set the add button to be disabled by default
        self.editButton = ttk.Button(self.frame, text='Edit', image=self.controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=self.master.editField)
        self.editButton.pack(side='right', fill='both', padx=10, pady=10)
        self.editButton.configure(state='disabled') # Set the edit button to be disabled by default
        # Added button for students only on event page
        self.setupButton = ttk.Button(self.frame, text='Join/Leave Setup Group\nFor this Event', image=self.controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None)

        self.removeFiltersButton = ttk.Button(self.frame, text="⎌", command=self.reset_table, style="symbol.Link.TButton")
        self.removeFiltersButton.pack(side='right', padx=5, pady=5)
        createTooltip(self.removeFiltersButton, 'Remove all Filters and Sorts applied')

    def updateButtons(self, event):
        ''' Update the state of the buttons based on the row that is selected. '''
        row = self.view.focus()

        if row and ACCESS_LEVEL in ['Admin', 'Staff']: # If a row is selected and the user is an admin or Staff, enable the buttons
            self.removeFiltersButton.pack_configure(side='right', fill='both', padx=5, pady=5)
            self.deleteButton.pack(side='right', fill='both', padx=10, pady=10)
            self.addButton.pack(side='right', fill='both', padx=10, pady=10)
            self.editButton.pack(side='right', fill='both', padx=10, pady=10)

            self.deleteButton.configure(state='normal')
            self.editButton.configure(state='normal')
            self.addButton.configure(state='normal')
    
    def updateEventPageButtons(self, event):
        ''' Update the state of the buttons based on the row that is selected if the user is a pupil. '''
        row = self.view.focus()

        if row and ACCESS_LEVEL in ['Admin', 'Staff']: # If a row is selected and the user is an admin or Staff, enable the buttons
            self.setupButton.pack_forget()
            self.master.toggleButton.pack_configure(side='left', fill='both', padx=10, pady=10)
            self.removeFiltersButton.pack_configure(side='left', before=self.master.toggleButton, fill='both', padx=5, pady=5)
            self.deleteButton.pack(side='right', fill='both', padx=10, pady=10)
            self.addButton.pack(side='right', fill='both', padx=10, pady=10)
            self.editButton.pack(side='right', fill='both', padx=10, pady=10)

            self.deleteButton.configure(state='normal')
            self.editButton.configure(state='normal')
            self.addButton.configure(state='normal')
        elif row and ACCESS_LEVEL in ['Senior', 'Junior']: # If the user is a Senior or Junior, remove the buttons for add, edit and delete and replace with a button to join the setup group
            self.deleteButton.pack_forget()
            self.editButton.pack_forget()
            self.addButton.pack_forget()
            self.setupButton.pack_forget()
            
            self.setupButton.configure(command=self.master.joinSetupGroup)
            self.setupButton.pack(side='right', fill='both', padx=10, pady=10)
            self.master.toggleButton.pack_configure(side='left', fill='both', padx=10, pady=10)
            self.removeFiltersButton.pack_configure(side='left', before=self.master.toggleButton, fill='both', padx=5, pady=5)

class EventsTableView(ttk.Frame):
    ''' Class to create the tableview, allowing the user to view the data in a table format. '''
    def __init__(self, parent, controller, connection, cursor, rowData, columnData, **kwargs):
        super().__init__(parent, **kwargs)
        self.connection = connection
        self.cursor = cursor
        self.controller = controller

        self.pack(side='top', fill='both', expand=True)

        self.table = updatedTableview(self, self.controller, eventPage=True, coldata=columnData, rowdata=rowData, paginated=True, searchable=True)
        self.table.configure(style='t.primary.Treeview')
        self.table.pack(side='top', fill='both', expand=True)

        # Add the toggle button to show all events
        self.toggleButton = ttk.Checkbutton(self.table.frame, text='Show All Events', command=self.toggleEventVisibility, style='Roundtoggle.TCheckbutton')
        self.toggleButton.pack(side='right', before=self.table.removeFiltersButton, fill='both', padx=10, pady=10)

        self.currentTableState = database.getUpcomingEventsDetails # Set the current table state to show upcoming events

    def toggleEventVisibility(self):
        ''' Toggle the visibility of all events in the table. '''
        if self.toggleButton.instate(['selected']):
            self.currentTableState = database.getAllEventsDetails
            self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements'])
        else:
            self.currentTableState = database.getUpcomingEventsDetails
            self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements'])
    
    def joinSetupGroup(self):
        ''' Join (or leave) the setup group for the selected event and send an email to the user logged in as confirmation for joining. '''
        row = self.table.view.focus()

        if row:
            data = list(self.table.view.item(row, 'values')) # get the data from the row

            question = Messagebox.show_question('Are you sure you want to join/leave the setup group for this event?', 'Join/Leave Setup Group', buttons=['Cancel:secondary','Leave:danger','Join:success'])
            if question == 'Join':
                try:
                    database.joinSetupGroup(self.connection, self.cursor, data[0], database.getUserID(self.cursor, ACCOUNT_ID))
                    self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements']) # rebuild the table with the updated data

                    Messagebox.show_info('You have joined the setup group for this event.', 'Success')

                    generalFunctions.sendEmail(database.getUserEmail(self.cursor, ACCOUNT_ID), f'Subject: Sound and Lighting: Setup Event\n\nYou have joined the setup group for the event "{data[1]}" on {data[2]} at {data[3]}.')
                except database.sql.IntegrityError:
                    if Messagebox.show_question('You are already a part of the setup group for this event. Would you like to leave the setup group?', 'Error') == 'Yes':
                        database.leaveSetupGroup(self.connection, self.cursor, data[0], database.getUserID(self.cursor, ACCOUNT_ID))

                        Messagebox.show_info('You have left the setup group for this event.', 'Success')

                        self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements'])
                except Exception as e:
                    Messagebox.show_error(f'An error occurred: {e}', 'Error')
            elif question == 'Leave':
                try:
                    database.leaveSetupGroup(self.connection, self.cursor, data[0], database.getUserID(self.cursor, ACCOUNT_ID))

                    Messagebox.show_info('You have left the setup group for this event.', 'Success')

                    self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements']) # rebuild the table with the updated data
                except Exception as e:
                    Messagebox.show_error(f'An error occurred: {e}', 'Error')

    def deleteField(self):
        ''' Handles when the delete button is clicked - get the id of the row that is selected and delete it from the database. '''
        row = self.table.view.focus() # get the row that is selected
    
        if row: # if a row is selected
            if Messagebox.show_question('Are you sure you want to delete this event?', 'Delete Event') == 'Yes':
                data = self.table.view.item(row, 'values') # get the data from the row
                # print(data)
                database.removeEvent(self.connection, self.cursor, data[0]) # remove the event from the database

                self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements']) # rebuild the table with the updated data
        
    def addField(self):
        ''' Handles when the add button is clicked - open a new window to enter details and commit new event to the database. '''
        staffValues = [staff.split(': ') for staff in database.getStaffNamesandIDs(self.cursor)] # ie. [['1', 'Henderson'], ['2', 'Campbell-Nesbitt'], ['3', 'Byrne'], ['4', 'Dark']]
        locationValues = [location.split(': ') for location in database.getLocationsandIDs(self.cursor)] # ie. [['1', 'Stinson Hall'], ['2', 'Sports Hall'], ['3', 'Conference Room']]

        self.eventForm = GenericForm(self, self.controller, 'Add an Event/Assembly', '600x700') # Create a new popup window for the form

        self.title = ttk.Label(self.eventForm.titleFrame, text='Add an Event/Assembly', style='BoldCaption.TLabel')
        self.title.pack()
        # create the fields for the form
        self.name = ttk.Label(self.eventForm.formFrame, text="Name Of Event*")
        self.name.pack()
        eventNameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(eventNameEntry, validation.presenceCheck))
        eventNameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Date*").pack()
        eventDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
        eventDateEntry.entry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(eventDateEntry.entry, validation.presenceCheck, validation.dateInFutureCheck))
        eventDateEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Time (hh:mm)*").pack()
        eventTimeEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(eventTimeEntry, validation.presenceCheck, validation.timeFormatCheck))
        eventTimeEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Duration (hh:mm)*").pack()
        eventDurationEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(eventDurationEntry, validation.presenceCheck, validation.timeFormatCheck))
        eventDurationEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Requested By*").pack()
        eventRequestedByEntry = ttk.Combobox(self.eventForm.formFrame, values=staffValues)
        eventRequestedByEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(eventRequestedByEntry, validation.presenceCheck))
        eventRequestedByEntry.state(['readonly'])
        eventRequestedByEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Setup By").pack()
        eventSetupByEntry = ttk.Menubutton(self.eventForm.formFrame, text='Assign Members', style='outline.TButton')
        eventSetupByEntry.pack(pady=5, padx=20)
        eventSetupByEntry.menu = tk.Menu(eventSetupByEntry, tearoff=0)
        eventSetupByEntry['menu'] = eventSetupByEntry.menu
        # for loop to create a checkbutton for each member in db and also a var for each checkbutton to store the value
        eventSetupByEntry.menu.vars = []
        for user in database.getAllMemberDetails(self.cursor):
            eventSetupByEntry.menu.vars.append(tk.StringVar(master=eventSetupByEntry.menu))
            eventSetupByEntry.menu.add_checkbutton(label=f'{user[1]} {user[2]} {user[4]}', onvalue=user[0], offvalue='', variable=eventSetupByEntry.menu.vars[-1])

        # self.testB = ttk.Button(self.eventForm.formFrame, text='Test', style='outline.TButton', command=lambda: print([var.get() for var in eventSetupByEntry.menu.vars]))
        # self.testB.pack(pady=5, padx=20)

        ttk.Label(self.eventForm.formFrame, text="Location*").pack()
        eventLocationEntry = ttk.Combobox(self.eventForm.formFrame, values=[f'{location[0]} {location[1]}' for location in locationValues]) # unpack the values so they are formatted correctly
        eventLocationEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(eventLocationEntry, validation.presenceCheck))
        eventLocationEntry.state(['readonly'])
        eventLocationEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Requirements").pack()
        eventRequirementsEntry = ttk.Entry(self.eventForm.formFrame)
        eventRequirementsEntry.pack()

        self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Submit", style='FormButton.secondary.TButton', command=self.submit)
        self.submitButton.pack(side='right', padx=10, pady=10)

    def submit(self):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame) # get the data from the form
        # print(data)
        if data == None: return # If the data is None due to validation, return
        
        # send emails to pupils doing the setup.
        setupMembersIDs = data[5] # get the members Account IDs that are in the setup group
        setupMembersEmails = [database.getUserEmailWithUserID(self.cursor, memberID) for memberID in setupMembersIDs] # get the emails of the members in the setup group
        try:
            for email in setupMembersEmails:
                generalFunctions.sendEmail(email, f'Subject: Sound and Lighting: Setup Event\n\nYou have been assigned to the setup group for the event "{data[0]}" on {data[1]} at {data[2]}.')
        except Exception as e:
            Messagebox.show_error(f'An error occurred: {e}', 'Error')

        database.insertDataIntoEventsTable(self.connection, self.cursor, data)

        Messagebox.show_info('Event Added Successfully', 'Success')

        self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements']) # rebuild the table with the updated data

        self.eventForm.destroy() # destroy the popup window

    def editField(self):
        ''' Handles when the edit button is clicked - open a new window to edit the details of the selected row and commit the changes to the database. '''
        row = self.table.view.focus() # get the row that is selected
        if row: # if a row is selected
            data = list(self.table.view.item(row, 'values')) # get the data from the row

            staffValues = [staff.split(': ') for staff in database.getStaffNamesandIDs(self.cursor)] # [['1', 'Henderson'], ['2', 'Campbell-Nesbitt'], ['3', 'Byrne'], ['4', 'Dark']]
            locationValues = [location.split(': ') for location in database.getLocationsandIDs(self.cursor)] # [['1', 'Stinson Hall'], ['2', 'Sports Hall'], ['3', 'Conference Room']]

            data[5] = [staff for staff in staffValues if staff[1] == data[5]][0] # replace the staff name with the id and name of the staff member ie. 'Henderson' -> ['1', 'Henderson']
            data[6] = [member for member in data[6].split(', ')] # split the string of members into a list of individual members
            data[7] = [location for location in locationValues if location[1] == data[7]][0] # replace the name of location with the id and name of the location ie. 'Stinson Hall' -> ['1', 'Stinson Hall']
            # print(data)

            self.eventForm = GenericForm(self, self.controller, 'Update an Event/Assembly', '600x700') # Create a new popup window for the form

            self.title = ttk.Label(self.eventForm.titleFrame, text='Update an Event/Assembly', style='BoldCaption.TLabel')
            self.title.pack()
            # create the fields for the form
            self.name = ttk.Label(self.eventForm.formFrame, text="Name of Event*")
            self.name.pack()
            eventNameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(eventNameEntry, validation.presenceCheck))
            eventNameEntry.insert(0, data[1]) # insert the data from the row into the form so the user can see what they are editing
            eventNameEntry.pack()
            
            ttk.Label(self.eventForm.formFrame, text="Date*").pack()
            eventDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
            eventDateEntry.entry.delete(0, 'end') # delete the default date that is shown
            eventDateEntry.entry.insert(0, data[2])
            eventDateEntry.entry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(eventDateEntry.entry, validation.presenceCheck, validation.dateInFutureCheck))
            eventDateEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Time (hh:mm)*").pack()
            eventTimeEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(eventTimeEntry, validation.presenceCheck, validation.timeFormatCheck))
            eventTimeEntry.insert(0, data[3])
            eventTimeEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Duration (hh:mm)*").pack()
            eventDurationEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(eventDurationEntry, validation.presenceCheck, validation.timeFormatCheck))
            eventDurationEntry.insert(0, data[4])
            eventDurationEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Requested By*").pack()
            eventRequestedByEntry = ttk.Combobox(self.eventForm.formFrame, values=staffValues) #[staff[1] for staff in staffValues]
            eventRequestedByEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(eventRequestedByEntry, validation.presenceCheck))
            eventRequestedByEntry.state(['readonly']) # make the combobox readonly so the user can't type in it, only select from the list
            eventRequestedByEntry.set(data[5]) # set the value of the combobox to the staff member that is in the selected row
            eventRequestedByEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Setup By").pack()
            eventSetupByEntry = ttk.Menubutton(self.eventForm.formFrame, text='Assign Members', style='outline.TButton')
            eventSetupByEntry.state(['readonly'])
            eventSetupByEntry.pack(pady=5, padx=20)
            eventSetupByEntry.menu = tk.Menu(eventSetupByEntry, tearoff=0)
            eventSetupByEntry['menu'] = eventSetupByEntry.menu
            # for loop to create a checkbutton for each member in db and also a var for each checkbutton
            eventSetupByEntry.menu.vars = []
            for user in database.getAllMemberDetails(self.cursor):
                eventSetupByEntry.menu.vars.append(tk.StringVar(master=eventSetupByEntry.menu))
                eventSetupByEntry.menu.add_checkbutton(label=f'{user[1]} {user[2]} {user[4]}', onvalue=user[0], offvalue='', variable=eventSetupByEntry.menu.vars[-1])
                if f'{user[1]} {user[2]} {user[4]}' in data[6]:
                    eventSetupByEntry.menu.vars[-1].set(user[0]) # if the member is in the list of members for the event, set the checkbutton to be checked

            ttk.Label(self.eventForm.formFrame, text="Location*").pack()
            eventLocationEntry = ttk.Combobox(self.eventForm.formFrame, values=[f'{location[0]} {location[1]}' for location in locationValues]) #[location[1] for location in locationValues]
            eventLocationEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(eventLocationEntry, validation.presenceCheck))
            eventLocationEntry.state(['readonly'])
            # eventLocationEntry.insert(0, data[7])
            eventLocationEntry.set(f'{data[7][0]} {data[7][1]}')
            eventLocationEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Requirements").pack()
            eventRequirementsEntry = ttk.Entry(self.eventForm.formFrame)
            eventRequirementsEntry.insert(0, data[8])
            eventRequirementsEntry.pack()

            self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Update", style='FormButton.secondary.TButton', command=lambda: self.edit(id=data[0]))
            self.submitButton.pack(side='right', padx=10, pady=10)

    def edit(self, id):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame) # get the data from the form

        if data == None: return # If the data is None due to validation, return
        
        database.updateEvent(self.connection, self.cursor, data, id)

        Messagebox.show_info('Event Updated Successfully', 'Success')
        
        self.table.build_table_data(rowdata=self.currentTableState(self.cursor), coldata=['Event ID', 'Name', 'Date', 'Time', 'Duration', 'Requested By', 'Setup By', 'Location', 'Requirements']) # rebuild the table with the updated data

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
                # database.deleteRowWithID(self.connection, self.cursor, 'tbl_Pupils', 'pupilID', data[0])
                database.removeMember(self.connection, self.cursor, data[0]) # remove the member from the database

                self.table.build_table_data(rowdata=database.getAllMemberDetails(self.cursor), coldata=['Pupil ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])
        
    def addField(self):
        ''' Handles when the add button is clicked - open a new window to enter details and commit new event to the database. '''
        # yearGroupValues = [staff.split(': ') for staff in database.getStaffNamesandIDs(self.cursor)] # [['1', 'Henderson'], ['2', 'Campbell-Nesbitt'], ['3', 'Byrne'], ['4', 'Dark']]
        # regClassValues = [location.split(': ') for location in database.getLocationsandIDs(self.cursor)]
        classValues = [clss.split(': ') for clss in database.getClassesandIDs(self.cursor)] # ie. [['1', '14S'], ['2', '14T'], ['3', '14E'], ['4', '14P']]

        self.eventForm = GenericForm(self, self.controller, 'Add a Member', '600x700') # Create a new popup window for the form

        self.title = ttk.Label(self.eventForm.titleFrame, text='Add an Member', style='BoldCaption.TLabel')
        self.title.pack()

        ttk.Label(self.eventForm.formFrame, text="First Name*").pack()
        firstNameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(firstNameEntry, validation.presenceCheck))
        firstNameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Surname*").pack()
        surnameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(surnameEntry, validation.presenceCheck))
        surnameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Username*, (this will create a new Account\nwith default password 'Password1')", justify='center').pack()
        usernameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(usernameEntry, validation.presenceCheck))
        usernameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Class*").pack()
        classEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=classValues)
        classEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(classEntry, validation.presenceCheck))
        classEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Email*").pack()
        emailEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(emailEntry, validation.presenceCheck, validation.emailFormatCheck))
        emailEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Date of Birth*").pack()
        birthDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
        birthDateEntry.entry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(birthDateEntry.entry, validation.presenceCheck, validation.dateInPastCheck))
        birthDateEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="House*").pack()
        houseEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=['Tower', 'Massereene', 'Tardree', 'Clotworthy'])
        houseEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(houseEntry, validation.presenceCheck))
        houseEntry.pack()

        self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Submit", style='FormButton.secondary.TButton', command=self.submit)
        self.submitButton.pack(side='right', padx=10, pady=10)

    def submit(self):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame)
        #print(data)
        
        existingAccounts = [account.split(': ')[1] for account in database.getAccountsAndIDs(self.cursor)] # ie. ['jjoseph553', 'bjohnston123']
        if data[2] in existingAccounts: # if the username already exists in the database
            Messagebox.show_error('An account with that username already exists. Please choose a different username.', 'Error')
            return

        if data == None: return # If the data is None due to validation, return
        
        data[2] = database.createAccount(self.connection, self.cursor, [data[2]]) # create account with default password 'Password1' and update the value of data[2] to the accountID
        database.insertDataIntoMemberTable(self.connection, self.cursor, data)

        Messagebox.show_info('Member Added Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllMemberDetails(self.cursor), coldata=['Pupil ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])

        self.eventForm.destroy()

    def editField(self):
        ''' Handles when the edit button is clicked - open a new window to edit the details of the selected row and commit the changes to the database. '''
        row = self.table.view.focus()
        if row:
            data = list(self.table.view.item(row, 'values'))

            classValues = [clss.split(': ') for clss in database.getClassesandIDs(self.cursor)] # ie. [['1', '14S'], ['2', '14T'], ['3', '14E'], ['4', '14P']]
            accountValues = [account.split(': ') for account in database.getAccountsAndIDs(self.cursor)] # ie. [['1', 'jjoseph553'], ['2', 'bjohnston123']]

            data[3] = [account for account in accountValues if account[1] == data[3]][0] # replace the name with the id and username of the account
            data[4] = [cls for cls in classValues if cls[1] == data[4]][0] # replace the name with the id and name of the class
            # print(data)

            self.eventForm = GenericForm(self, self.controller, 'Update Member Info', '600x700') # Create a new popup window for the form

            self.title = ttk.Label(self.eventForm.titleFrame, text='Update Member Info', style='BoldCaption.TLabel')
            self.title.pack()

            ttk.Label(self.eventForm.formFrame, text="First Name*").pack()
            firstNameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(firstNameEntry, validation.presenceCheck))
            firstNameEntry.insert(0, data[1])
            firstNameEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Surname*").pack()
            surnameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(surnameEntry, validation.presenceCheck))
            surnameEntry.insert(0, data[2])
            surnameEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Username*").pack()
            usernameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(usernameEntry, validation.presenceCheck))
            usernameEntry.insert(0, data[3][0])
            usernameEntry.configure(state='readonly')
            usernameEntry.pack()
            ttk.Label(self.eventForm.formFrame, text=data[3][1]).pack()
            createTooltip(usernameEntry, 'Username cannot be changed')

            ttk.Label(self.eventForm.formFrame, text="Class*").pack()
            classEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=classValues)
            classEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(classEntry, validation.presenceCheck))
            classEntry.set(data[4])
            classEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Email*").pack()
            emailEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(emailEntry, validation.presenceCheck, validation.emailFormatCheck))
            emailEntry.insert(0, data[5])
            emailEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Date of Birth*").pack()
            birthDateEntry = ttk.DateEntry(self.eventForm.formFrame, dateformat=r'%Y-%m-%d') # ie. 2024-01-10, DATE datatype format recognised by SQLite
            birthDateEntry.entry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(birthDateEntry.entry, validation.presenceCheck, validation.dateInPastCheck))
            birthDateEntry.entry.delete(0, 'end')
            birthDateEntry.entry.insert(0, data[6])
            birthDateEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="House*").pack()
            houseEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=['Tower', 'Massereene', 'Tardree', 'Clotworthy'])
            houseEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(houseEntry, validation.presenceCheck))
            houseEntry.set(data[7])
            houseEntry.pack()

            self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Update", style='FormButton.secondary.TButton', command=lambda: self.edit(id=data[0]))
            self.submitButton.pack(side='right', padx=10, pady=10)

    def edit(self, id):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame)
        #print(data)
        if data == None: return # If the data is None due to validation, return

        database.updateMember(self.connection, self.cursor, data, id)

        Messagebox.show_info('Member Updated Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllMemberDetails(self.cursor), coldata=['Pupil ID', 'First Name', 'Surname', 'Username', 'Class', 'Email', 'Date Of Birth', 'House'])

        self.eventForm.destroy()

class StaffTableView(ttk.Frame):
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
            if Messagebox.show_question('Are you sure you want to delete this Staff Member?', 'Delete Staff') == 'Yes':
                data = self.table.view.item(row, 'values') # get the data from the row
                # print(data)
                # database.deleteRowWithID(self.connection, self.cursor, 'tbl_Staff', 'staffID', data[0])
                database.removeStaff(self.connection, self.cursor, data[0]) # remove the staff member from the database

                self.table.build_table_data(rowdata=database.getAllStaffDetails(self.cursor), coldata=['Staff ID', 'First Name', 'Surname', 'Username', 'Role', 'Staff Email'])
        
    def addField(self):
        ''' Handles when the add button is clicked - open a new window to enter details and commit new event to the database. '''
        self.eventForm = GenericForm(self, self.controller, 'Add a Staff Member', '500x500') # Create a new popup window for the form

        self.title = ttk.Label(self.eventForm.titleFrame, text='Add an Staff Member', style='BoldCaption.TLabel')
        self.title.pack()

        ttk.Label(self.eventForm.formFrame, text="First Name*").pack()
        firstNameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(firstNameEntry, validation.presenceCheck))
        firstNameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Surname*").pack()
        surnameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(surnameEntry, validation.presenceCheck))
        surnameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Username*, (this will create a new Account\nwith default password 'Password1')", justify='center').pack()
        usernameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(usernameEntry, validation.presenceCheck))
        usernameEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Role*").pack()
        classEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=['Admin', 'Staff'])
        classEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(classEntry, validation.presenceCheck))
        classEntry.pack()

        ttk.Label(self.eventForm.formFrame, text="Email*").pack()
        emailEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(emailEntry, validation.presenceCheck, validation.emailFormatCheck))
        emailEntry.pack()

        self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Submit", style='FormButton.secondary.TButton', command=self.submit)
        self.submitButton.pack(side='right', padx=10, pady=10)

    def submit(self):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame)
        #print(data)

        existingAccounts = [account.split(': ')[1] for account in database.getAccountsAndIDs(self.cursor)]
        if data[2] in existingAccounts: # if the username already exists in the database
            Messagebox.show_error('An account with that username already exists. Please choose a different username.', 'Error')
            return
        
        if data == None: return # If the data is None due to validation, return

        data[2] = database.createAccount(self.connection, self.cursor, [data[2]]) # create account with default password 'Password1' and update the value of data[2] to the accountID
        database.insertDataIntoStaffTable(self.connection, self.cursor, data)

        Messagebox.show_info('Staff Member Added Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllStaffDetails(self.cursor), coldata=['Staff ID', 'First Name', 'Surname', 'Username', 'Role', 'Staff Email'])

        self.eventForm.destroy()

    def editField(self):
        ''' Handles when the edit button is clicked - open a new window to edit the details of the selected row and commit the changes to the database. '''
        row = self.table.view.focus()
        if row:
            data = list(self.table.view.item(row, 'values'))

            accountValues = [account.split(': ') for account in database.getAccountsAndIDs(self.cursor)] # ie. [['1', 'jjoseph553'], ['2', 'bjohnston123']]

            data[3] = [account for account in accountValues if account[1] == data[3]][0] # replace the name with the id and username of the account
            # print(data)

            self.eventForm = GenericForm(self, self.controller, 'Update Staff Info', '500x500') # Create a new popup window for the form

            self.title = ttk.Label(self.eventForm.titleFrame, text='Update Staff Info', style='BoldCaption.TLabel')
            self.title.pack()

            ttk.Label(self.eventForm.formFrame, text="First Name*").pack()
            firstNameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(firstNameEntry, validation.presenceCheck))
            firstNameEntry.insert(0, data[1])
            firstNameEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Surname*").pack()
            surnameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(surnameEntry, validation.presenceCheck))
            surnameEntry.insert(0, data[2])
            surnameEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Username*").pack()
            usernameEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(usernameEntry, validation.presenceCheck))
            usernameEntry.insert(0, data[3][0])
            usernameEntry.configure(state='readonly')
            usernameEntry.pack()
            ttk.Label(self.eventForm.formFrame, text=data[3][1]).pack()
            createTooltip(usernameEntry, 'Username cannot be changed')

            ttk.Label(self.eventForm.formFrame, text="Role*").pack()
            classEntry = ttk.Combobox(self.eventForm.formFrame, state='readonly', values=['Admin', 'Staff'])
            classEntry.configure(validate='focusout', validatecommand=lambda: validation.validationCallback(classEntry, validation.presenceCheck))
            classEntry.set(data[4])
            classEntry.pack()

            ttk.Label(self.eventForm.formFrame, text="Email*").pack()
            emailEntry = ttk.Entry(self.eventForm.formFrame, validate='focusout', validatecommand=lambda: validation.validationCallback(emailEntry, validation.presenceCheck, validation.emailFormatCheck))
            emailEntry.insert(0, data[5])
            emailEntry.pack()

            self.submitButton = ttk.Button(self.eventForm.buttonsFrame, text="Update", style='FormButton.secondary.TButton', command=lambda: self.edit(id=data[0]))
            self.submitButton.pack(side='right', padx=10, pady=10)

    def edit(self, id):
        ''' Handles when the submit button is clicked - get the data from the form and commit it to the database. '''
        data = self.eventForm.getData(self.eventForm.formFrame)
        #print(data)
        if data == None: return # If the data is None due to validation, return
        
        database.updateStaff(self.connection, self.cursor, data, id)

        Messagebox.show_info('Staff Member Updated Successfully', 'Success')
        
        self.table.build_table_data(rowdata=database.getAllStaffDetails(self.cursor), coldata=['Staff ID', 'First Name', 'Surname', 'Username', 'Role', 'Staff Email'])

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

        self.icon = ImageTk.PhotoImage(Image.open(generalFunctions.resourcePath("Contents/images/ags.png")).resize((70, 70), Image.LANCZOS))
        self.iconLabel = ttk.Label(self.titleFrame, image=self.icon) # Create a label with the image
        self.iconLabel.pack(side='top')

        self.formFrame = ttk.Frame(self)
        self.formFrame.pack(side='top', expand=True)

        self.buttonsFrame = ttk.Frame(self)
        self.buttonsFrame.pack(side='bottom', fill='x')

        self.closeButton = ttk.Button(self.buttonsFrame, text='Close', style='Close.secondary.TButton', command=self.destroy)
        self.closeButton.pack(side='left', padx=10, pady=10)
    
    def getData(self, frame: ttk.Frame) -> list | None:
        ''' Get the data from the entry widgets within a Frame and return it as a list. Rechecks the validation of the entry widgets - if they are not valid, return None. '''
        data = []
        entries = [entry for entry in frame.winfo_children() if isinstance(entry, (ttk.Entry, ttk.Combobox, ttk.DateEntry, ttk.Menubutton))] # get all entry widgets in the frame
        
        for entry in entries:
            if isinstance(entry, ttk.Combobox): # if the widget is a combobox
                if not entry.validate(): # if the combobox is not valid
                    return None # return None to indicate the data is not valid
                if entry.get().split(' ')[0].isdigit(): # if the first part of the string is a digit denoting an ID
                    data.append(entry.get().split(' ')[0]) # only append the ID, ie. '1 Henderson' -> '1'
                else: # if the first part of the string is not a digit
                    data.append(entry.get()) # append the whole string, ie. 'Henderson'

            elif isinstance(entry, ttk.Menubutton): # if the widget is an Menubutton
                data.append([var.get() for var in entry.menu.vars if var.get()]) # append the value of each checkbutton in the menu

            elif hasattr(entry, 'get'): # if the widget has a get method
                if not entry.validate(): # if the entry is not valid
                    return None # return None to indicate that the data is not valid
                data.append(entry.get())

            elif isinstance(entry, ttk.DateEntry): # if the widget is a DateEntry
                if not entry.entry.validate(): # if the entry is not valid
                    return None
                data.append(entry.entry.get()) # get the entry component of the DateEntry widget
        # print(data)
        return data

class FileControlBar(ttk.Frame):
    ''' Class to create the control bar for the file explorer pages (Documentation, Archive and Training Materials). '''
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller

        self.place(relx=0.3, rely=0.1, relwidth=0.7, relheight=0.1, anchor='nw') # Place the frame in the top right corner of the parent frame
        # parent is used to assign these widgets as children of the parent frame, so they can be accessed by other classes (like the accordion menu) more easily
        parent.contentName = ttk.Label(self, text='Click a File to View', style='file.TLabel') # Create a label to display the name of the file that is being viewed
        parent.contentName.pack(side='left', padx=10, pady=20)

        parent.exportButton = ttk.Button(self, text='Export', image=controller.style.images['download'], compound='left', style='action.secondary.TButton', command=None) # Create a button to export the file
        parent.exportButton.pack(side='right', fill='both', padx=10, pady=10)
        createTooltip(parent.exportButton, 'Save the file to your desktop') # Create a tooltip for the export button

        parent.openFileLocButton = ttk.Button(self, text='Open File Location', image=controller.style.images['edit'], compound='left', style='action.secondary.TButton', command=None) # Create a button to open the file location
        parent.openFileLocButton.pack(side='right', fill='both', padx=10, pady=10)
        createTooltip(parent.openFileLocButton, 'Open the file location in File Explorer') # Create a tooltip for the open file location button

        parent.exportButton.configure(state='disabled') # Disable the export button
        parent.openFileLocButton.configure(state='disabled') # Disable the open file location button

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

                if ACCESS_LEVEL in ['Admin', 'Senior']: # If the user is an admin or Senior member, enable the open file location button
                    self.master.openFileLocButton.configure(state='normal') # Enable the open file location button
                    self.master.openFileLocButton.configure(command=lambda: generalFunctions.showFileExplorer(filePath)) # Set the open file location button to open the clicked file

                self.master.exportButton.configure(state='normal') # Enable the export button
                self.master.exportButton.configure(command=lambda: self.showMessageboxCallback(generalFunctions.copyFile(filePath))) # Set the export button to export the clicked file
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

                if ACCESS_LEVEL in ['Admin', 'Senior']: # If the user is an admin or Senior member, enable the open file location button
                    self.master.openFileLocButton.configure(state='normal') # Enable the open file location button
                    self.master.openFileLocButton.configure(command=lambda: generalFunctions.showFileExplorer(filePath)) # Set the open file location button to open the clicked file

                self.master.exportButton.configure(state='normal') # Enable the export button
                self.master.exportButton.configure(command=lambda: self.showMessageboxCallback(generalFunctions.copyFile(filePath))) # Set the export button to export the clicked file
            except Exception as e:
                print(e)

        if item.endswith('.docx'): # If the file is a word document, convert it to a pdf and display it in the pdf viewer
            if generalFunctions.checkIfFileExists(f'Contents/.temp/{item[:-5]}.pdf'): # If the pdf file already exists
                self.master.contentViewer.destroy() # Destroy the current contentViewer
                self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None # Reset the display_msg, frame and text variables
                self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                pdfPath = generalFunctions.resourcePath(f'Contents/.temp/{item[:-5]}.pdf') # Create the filepath to the pdf file that was converted already

                self.master.contentViewer = self.master.pdfObject.pdf_view(self.master.contentFrame, bar=False, pdf_location=pdfPath) # Create a new pdf viewer
                self.master.contentViewer.pack(side='top', fill='both', expand=True)

                self.master.contentName.configure(text=item) # Set the contentName label to the name of the file

                if ACCESS_LEVEL in ['Admin', 'Senior']: # If the user is an admin or Senior member, enable the open file location button
                    self.master.openFileLocButton.configure(state='normal') # Enable the open file location button
                    self.master.openFileLocButton.configure(command=lambda: generalFunctions.showFileExplorer(filePath)) # Set the open file location button to open the clicked file

                self.master.exportButton.configure(state='normal') # Enable the export button
                self.master.exportButton.configure(command=lambda: self.showMessageboxCallback(generalFunctions.copyFile(filePath))) # Set the export button to export the clicked file
            else: # If the pdf file does not exist
                if Messagebox.show_question('Would you like to convert this Word Document to a PDF? This will require Microsoft Word installed.', 'Convert Word Document') == 'Yes':
                    try:
                        self.master.contentViewer.destroy() # Destroy the current contentViewer
                        self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None # Reset the display_msg, frame and text variables
                        self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                        try:
                            docx2pdf.convert(filePath, generalFunctions.resourcePath('Contents/.temp'), hide_progress=True) # Convert the docx file to a pdf file inside the .temp folder
                            pdfPath = generalFunctions.resourcePath(f'Contents/.temp/{item[:-5]}.pdf') # Create the filepath to the pdf file that was converted

                            self.master.contentViewer = self.master.pdfObject.pdf_view(self.master.contentFrame, bar=False, pdf_location=pdfPath) # Create a new pdf viewer
                            self.master.contentViewer.pack(side='top', fill='both', expand=True)
                        except Exception as e:
                            Messagebox.show_error('Error converting Word Document to PDF!\n\nYou will require Microsoft Word installed on this device to convert.', 'Error')

                        self.master.contentName.configure(text=item) # Set the contentName label to the name of the file

                        if ACCESS_LEVEL in ['Admin', 'Senior']: # If the user is an admin or Senior member, enable the open file location button
                            self.master.openFileLocButton.configure(state='normal') # Enable the open file location button
                            self.master.openFileLocButton.configure(command=lambda: generalFunctions.showFileExplorer(filePath)) # Set the open file location button to open the clicked file

                        self.master.exportButton.configure(state='normal') # Enable the export button
                        self.master.exportButton.configure(command=lambda: self.showMessageboxCallback(generalFunctions.copyFile(filePath))) # Set the export button to export the clicked file
                    except Exception as e:
                        print(e)
            
    def showMessageboxCallback(self, functionToExecute):
        ''' Execute a function and show the message box with the result of the function. '''
        lambda: functionToExecute() # Execute the function
        Messagebox.show_info('File has been saved to your Desktop!', 'File Exported Successfully')

class FAQAccordion(ttk.Treeview):
    ''' Class to create the FAQ accordion menu, allowing the user to see all the areas to view FAQ pages for. '''
    def __init__(self, parent, controller, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = data

        self.column('#0', stretch=True, minwidth=100)
        self.configure(style='accordion.primary.Treeview', show='tree', selectmode='browse')
        self.tag_configure('heading', font=BOLD_CAPTION_FONT) # Set the font for the directory tags
        self.tag_bind('heading', '<Double-Button-1>', self.onClick) # Bind the double click event to the heading tags
        
        for key, value in self.data.items(): # Iterate through the data
            self.insert('', 'end', text=key, tags='heading') # Insert the key as a heading tag
        
    def onClick(self, event):
        ''' Handles when a heading is clicked - get the corresponding text of the heading and display it in the FAQ viewer '''
        itemIID = event.widget.selection()[0] # Get the item that was clicked
        item = event.widget.item(itemIID, 'text') # Get the text of the item that was clicked

        text = self.data[item] # Get the text that corresponds to the clicked heading

        self.master.titleLabel.configure(text=item) # Set the titleLabel to the text of the clicked heading
        self.master.contentLabel.configure(text=text) # Set the contentLabel to the text that corresponds to the clicked heading

class SettingsAccordion(ttk.Treeview):
    ''' Class to create the Settings accordion menu, allowing the user to see all the areas to view Settings pages for. On heading click, opens a frame with the settings for that area. '''
    def __init__(self, parent, controller, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = data

        self.column('#0', stretch=True, minwidth=100)
        self.configure(style='accordion.primary.Treeview', show='tree', selectmode='browse')
        self.tag_configure('heading', font=BOLD_CAPTION_FONT) # Set the font for the directory tags
        self.tag_bind('heading', '<Double-Button-1>', self.onClick) # Bind the double click event to the heading tags
        
        for key, value in self.data.items(): # Iterate through the data
            self.insert('', 'end', text=key, tags='heading') # Insert the key as a heading tag
        
    def onClick(self, event):
        ''' Handles when a heading is clicked - get the corresponding frame of the heading and display it in the viewer '''
        itemIID = event.widget.selection()[0] # Get the item that was clicked
        item = event.widget.item(itemIID, 'text') # Get the text of the item that was clicked

        frameCreationFunction = self.data[item] # Get the frame function that corresponds to the clicked heading

        # clear the current frame
        for widget in self.master.contentFrame.winfo_children():
            widget.destroy()
        
        frameCreationFunction() # Create the frame that corresponds to the clicked heading

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