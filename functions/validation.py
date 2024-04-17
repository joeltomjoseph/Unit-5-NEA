import re
import ui
import datetime

def validationCallback(widget, *validationRoutines):
    ''' Callback function to validate the input in the given widget using the given validation routine(s). '''
    for routine in validationRoutines: # Loop through all the validation routines
        if not routine(widget, widget.get()): # If the routine returns False, return False
            return False
    return True # If all routines pass, return True
    # return validationRoutine(widget, widget.get())

def presenceCheck(widget, data: list) -> bool:
    ''' Check if all fields in a list of data are present, 
    this can also be used to check if a single value is present by passing in a single value '''
    if data == '' or data == None:
        ui.createTooltip(widget, 'This field must be filled in.', onWidget=True, error=True)
        return False
    
    for field in data:
        if field == '' or field == None:
            ui.createTooltip(widget, 'This field must be filled in.', onWidget=True, error=True)
            return False
    return True

def emailFormatCheck(widget, email: str) -> bool:
    ''' Check if the email is in the correct format X@Y.Z '''
    splitEmail = email.split("@")
    
    if len(splitEmail) != 2:
        ui.createTooltip(widget, 'Email must contain one "@" symbol.', onWidget=True, error=True)
        return False  # If there isn't one "@" symbol
    
    firstPart = splitEmail[0]
    secondPart = splitEmail[1]
    
    if len(firstPart) == 0 or len(secondPart) == 0:
        ui.createTooltip(widget, 'Email must be of standard format, eg. jjoseph123@c2ken.net', onWidget=True, error=True)
        return False  # Parts should not be empty
    
    if firstPart.count('.') > 0 or secondPart.count('.') < 1:
        ui.createTooltip(widget, 'Must contain one . in the second part of the email and none in the first.', onWidget=True, error=True)
        return False  # At least one dot in second part and none in local part
    
    domainParts = secondPart.split(".")
    if len(domainParts[-1]) < 2:
        ui.createTooltip(widget, 'Top-level domain (.com/.net) must be at least 2 characters.', onWidget=True, error=True)
        return False  # Top-level domain (.com/.net) should be at least 2 chars
    
    return True

def timeFormatCheck(widget, time: str) -> bool:
    ''' Check if the time is in the correct format `HH:MM` '''
    timeParts = time.split(":")
    
    if len(timeParts) != 2:
        ui.createTooltip(widget, 'Time must be in the format HH:MM.', onWidget=True, error=True)
        return False
    
    hours = timeParts[0]
    minutes = timeParts[1]
    
    if not (hours.isnumeric() and minutes.isnumeric()):
        ui.createTooltip(widget, 'Hours and minutes must be numbers.', onWidget=True, error=True)
        return False
    
    if not (len(hours) == 2 and len(minutes) == 2):
        ui.createTooltip(widget, 'Hours and minutes must each be 2 digits long. (HH:MM)', onWidget=True, error=True)
        return False
    
    hours = int(hours)
    minutes = int(minutes)
    
    if not (hours >= 0 and hours <= 23 and minutes >= 0 and minutes <= 59):
        ui.createTooltip(widget, 'Hours must be between 0 and 23, minutes must be between 0 and 59.', onWidget=True, error=True)
        return False
    
    return True

def dateInFutureCheck(widget, inputDate: str) -> bool:
    ''' Check if the input date is in the future. '''
    currentDate = datetime.datetime.today().date() # Get the current date
    inputDate = datetime.datetime.strptime(inputDate, "%Y-%m-%d").date()  # Convert the input date to a datetime object

    if inputDate >= currentDate:
        return True  # Date is in the future
    else:
        ui.createTooltip(widget, 'Date must be in the future.', onWidget=True, error=True)
        return False

def dateInPastCheck(widget, inputDate: str) -> bool:
    ''' Check if the input date is in the past. '''
    currentDate = datetime.datetime.today().date()  # Get the current date
    inputDate = datetime.datetime.strptime(inputDate, "%Y-%m-%d").date()  # Convert the input date to a datetime object

    if inputDate < currentDate:
        return True  # Date is in the past
    else:
        ui.createTooltip(widget, 'Date must be in the past.', onWidget=True, error=True)
        return False

def validateUsername(widget, username: str) -> bool:
    ''' Validate the username. Checking if it is between `minUsernameLength` and `maxUsernameLength`. Create a tooltip on the widget if the username is invalid. '''
    minUsernameLength = 6
    maxUsernameLength = 20

    if len(username) < minUsernameLength or len(username) > maxUsernameLength:
        #print(f"Invalid username. Username has to be between {minUsernameLength} and {maxUsernameLength} characters long.")
        ui.createTooltip(widget, f'Username has to be between {minUsernameLength} and {maxUsernameLength} characters long.', onWidget=True, error=True)
        return False
    return True

def validatePassword(widget, password: str) -> bool:
    '''Validate password: At least 9 characters, one uppercase, one lowercase, one number. Create a tooltip on the widget if the password is invalid. '''
    if len(password) < 9:
        #print("Invalid password. Password must be at least 9 characters.")
        ui.createTooltip(widget, 'Password must be at least 9 characters.', onWidget=True, error=True)
        return False

    if not re.search(r'[A-Z]', password):
        #print("Invalid password. Password must contain at least one uppercase letter.")
        ui.createTooltip(widget, 'Password must contain at least one uppercase letter.', onWidget=True, error=True)
        return False

    if not re.search(r'[a-z]', password):
        #print("Invalid password. Password must contain at least one lowercase letter.")
        ui.createTooltip(widget, 'Password must contain at least one lowercase letter.', onWidget=True, error=True)
        return False

    if not re.search(r'\d', password):
        #print("Invalid password. Password must contain at least one digit.")
        ui.createTooltip(widget, 'Password must contain at least one digit.', onWidget=True, error=True)
        return False

    return True