import re
import ui

# Function to check if data passed in is present
def presenceCheck(data: list):
    ''' Check if all fields in a list of data are present, 
    this can also be used to check if a single value is present by passing in a single value as a list '''
    for field in data:
        if field == '' or field == None:
            return False
    return True

def validateUsername(widget, username):
    # Validate username: At least minUsernameLength and greater than maxUsernameLength
    minUsernameLength = 6
    maxUsernameLength = 20

    if len(username) < minUsernameLength or len(username) > maxUsernameLength:
        #print(f"Invalid username. Username has to be between {minUsernameLength} and {maxUsernameLength} characters long.")
        ui.createTooltip(widget, f'Username has to be between {minUsernameLength} and {maxUsernameLength} characters long.', onWidget=True)
        return False
    return True

def validatePassword(widget, password):
    # Validate password: At least 9 characters, one uppercase, one lowercase, one number
    if len(password) < 9:
        #print("Invalid password. Password must be at least 9 characters.")
        ui.createTooltip(widget, 'Password must be at least 9 characters.', onWidget=True)
        return False

    if not re.search(r'[A-Z]', password):
        #print("Invalid password. Password must contain at least one uppercase letter.")
        ui.createTooltip(widget, 'Password must contain at least one uppercase letter.', onWidget=True)
        return False

    if not re.search(r'[a-z]', password):
        #print("Invalid password. Password must contain at least one lowercase letter.")
        ui.createTooltip(widget, 'Password must contain at least one lowercase letter.', onWidget=True)
        return False

    if not re.search(r'\d', password):
        #print("Invalid password. Password must contain at least one digit.")
        ui.createTooltip(widget, 'Password must contain at least one digit.', onWidget=True)
        return False

    return True