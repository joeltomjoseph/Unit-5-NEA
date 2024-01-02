import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from PIL import Image, ImageTk
from tkVideoPlayer import TkinterVideo
import platform
from pathlib import Path
import datetime

from functions import generalFunctions

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
    style.configure('action.secondary.TButton', foreground='black', font=('TkTextFont 15 bold'), width=10)

def createImages():
    ''' Creates a dictionary of all (excluding a few) images created as PhotoImages in the images folder. These Photoimages can be reused when needed. '''
    images = {}
    for file in Path(generalFunctions.resourcePath('./Contents/images')).iterdir():
        if file.stem != '.DS_Store' and file.stem not in ['ags', 'backdrop', 'backdropHQ']: # Ignore the .DS_Store file and the images in the list
            images[file.stem] = tk.PhotoImage(name=file.stem, file=generalFunctions.resourcePath(file))
    return images

def createStyle():
    ''' Initialises the style and loads the theme for the entire application '''
    style = ttk.Style()
    ttk.Style.load_user_themes(style, generalFunctions.resourcePath('Contents/agsStyle.json'))
    style.theme_use('ags')
    createWidgetStyles(style)
    style.images = createImages()
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

class TableView(ttk.Frame):
    def __init__(self, parent, controller, rowData, columnData, **kwargs):
        super().__init__(parent, **kwargs)

        self.pack(side='top', fill='both', expand=True)

        self.table = Tableview(self, coldata=columnData, rowdata=rowData, paginated=True, searchable=True)
        self.table.configure(style='t.primary.Treeview')
        self.table.pack(side='top', fill='both', expand=True)
        

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
                if parentIID and event.widget.item(parentIID, 'text') not in parents: # if parentIID isnt '' and the parent isn't already in the list due to base filepath
                    parents.append(event.widget.item(parentIID, 'text'))
                    #print(parents[-1])
                currentIID = parentIID

            return parents

        itemIID = event.widget.selection()[0]
        item = event.widget.item(itemIID, 'text')
        
        parents = getParents(event, itemIID)[::-1]

        filePath = generalFunctions.resourcePath(f'{self.master.baseFilePath}/{"/".join(parent for parent in parents)}/{item}')
        #print(filePath)

        if item.endswith('.pdf') or item.endswith('.png'):
            try:
                self.master.contentViewer.destroy()
                self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None
                self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                self.master.contentViewer = self.master.pdfObject.pdf_view(self.master.contentFrame, bar=False, pdf_location=filePath)
                self.master.contentViewer.pack(side='top', fill='both', expand=True)
                self.master.contentName.configure(text=item)
            except Exception as e:
                print(e)

        if item.endswith('.mp4') or item.endswith('.mov'):
            try:
                self.master.contentViewer.destroy()
                self.master.pdfObject.display_msg, self.master.pdfObject.frame, self.master.pdfObject.text = None, None, None
                self.master.pdfObject.img_object_li.clear() # Clear the list of images already stored from previous pdf

                self.master.contentViewer = videoPlayer(self.master.contentFrame, self.master, filePath)
                self.master.contentViewer.pack(side='top', fill='both', expand=True)
                self.master.contentViewer.load_video(filePath)
                self.master.contentName.configure(text=item)
            except Exception as e:
                print(e)

        if item.endswith('.docx'):
            try:
                pass
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

    def play_pause(self):
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