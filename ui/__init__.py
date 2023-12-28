import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import platform

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
    
    # Dashboard
    style.configure('db.TFrame', background='#F5F5F5')
    style.configure('dbButton.Outline.TButton', background='#F5F5F5', foreground='black', font=BODY_FONT, justify='center', wraplength=350)
    style.configure('dbLabel.TLabel', background='#F5F5F5', foreground='black', font=BODY_FONT, justify='center', wraplength=250)

    # Documentation
    style.configure('accordion.primary.Treeview', font=BODY_FONT, rowheight=30)
    style.configure('accordion.primary.Treeview.Item', indicatorsize=2)

def createStyle():
    ''' Initialises the style and loads the theme for the entire application '''
    style = ttk.Style()
    ttk.Style.load_user_themes(style, 'agsStyle.json')
    style.theme_use('ags')
    createWidgetStyles(style)
    return style

#Tooltip class and functions adapted from
#https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
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

# Adapted from https://stackoverflow.com/questions/46762061/how-to-create-multiple-label-in-button-widget-of-tkinter
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
        self.logo = ImageTk.PhotoImage(Image.open("images/ags.png").resize((50, 50), Image.LANCZOS))
        self.titleLabel = ttk.Label(self, text="Sound and Lighting", image=self.logo, compound='left', style='mt.TLabel')
        self.titleLabel.pack(side="left", padx=10, pady=5)

        # Create close button
        closeButton = ttk.Button(self, text="Close", command=self.quit, style='Close.secondary.TButton')
        closeButton.pack(side="right", padx=10, pady=5)

        # Create FAQ/Help button
        helpButton = ttk.Button(self, text="FAQ", command=lambda: controller.showFrame(FAQPage), style='Close.secondary.TButton')
        helpButton.pack(side="right", padx=10, pady=5)

        if lastPage:
            # Create back button
            backButton = ttk.Button(self, text="Back", command=lambda: controller.showFrame(lastPage), style='Close.secondary.TButton')
            backButton.pack(side="left", padx=10, pady=5)

class Accoridon(ttk.Treeview):
    ''' Class to create the accordion menu, allowing the user to view the Options available '''
    def __init__(self, parent, controller, data, **kwargs):
        super().__init__(parent, **kwargs)

        self.column('#0', stretch=True, minwidth=100)
        self.configure(style='accordion.primary.Treeview', show='tree')
        self.tag_configure('directory', font=BOLD_CAPTION_FONT)
        self.tag_bind('file', '<Double-Button-1>', self.onFileClick)
        
        for key, value in data.items():
            if key == 'files':
                self.insertField(value, '') # Skip inserting the field for 'files' and instead insert its children
            else:
                id = self.insert('', 'end', text=key, tags='directory')
                self.insertField(value, id)
    
    def insertField(self, data, parentID):
        ''' Recursively create new fields inside the treeview with parent id of parentID. '''
        if isinstance(data, list):
            for file in data:
                self.insert(parentID, 'end', text=file, tags='file')

        else:
            for key, value in data.items():
                if key == 'files':
                    self.insertField(value, parentID) # Skip inserting the field for 'files' and instead insert its children
                else:
                    id = self.insert(parentID, 'end', text=key, tags='directory')
                    self.insertField(value, id)
    
    def refreshFields(self, data, *event):
        ''' Refresh the fields in the treeview '''
        self.delete(*self.get_children())
        
        self.insertField(data, '')

        #self.after(10000, self.refreshFields, data) # Refresh the fields after 10 seconds
    
    def onFileClick(self, event):
        ''' Handles when a file is clicked - get the file path of the clicked file and display it in the pdf viewer '''
        def getParents(event, baseIID) -> list:
            ''' Get all parents of the clicked item in the hierarchy '''
            parents = []
            currentIID = baseIID

            while currentIID:
                parentIID = event.widget.parent(currentIID)
                if parentIID:
                    parents.append(event.widget.item(parentIID, 'text'))
                currentIID = parentIID

            return parents

        itemIID = event.widget.selection()[0]
        item = event.widget.item(itemIID, 'text')
        
        parents = getParents(event, itemIID)

        filePath = f'{self.master.baseFilePath}/{"/".join(parent for parent in parents)}/{item}'
        #print(filePath)

        if item.endswith('.pdf') or item.endswith('.png'):
            try:
                self.master.pdfViewer.destroy()
                self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None
                self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                self.master.pdfViewer = self.master.pdfObject.pdf_view(self.master.contentFrame, bar=False, pdf_location=filePath)
                self.master.pdfViewer.pack(side='top', fill='both', expand=True)
            except Exception as e:
                print(e)