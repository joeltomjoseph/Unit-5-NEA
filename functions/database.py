import sqlite3 as sql

# Function to create the 'tbl_Accounts' table
def createAccountTable(cursor: sql.Cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Accounts (
        accountID INTEGER PRIMARY KEY,
        username VARCHAR(20),
        password VARCHAR(20)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Staff' table
def createStaffTable(cursor: sql.Cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Staff (
        staffID INTEGER PRIMARY KEY,
        firstName VARCHAR(10),
        surname VARCHAR(20),
        accountID INTEGER,
        role VARCHAR(10),
        staffEmail VARCHAR(50),
        FOREIGN KEY (accountID) REFERENCES tbl_Accounts(accountID) ON DELETE CASCADE
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Pupils' table
def createPupilTable(cursor: sql.Cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Pupils (
        pupilID INTEGER PRIMARY KEY,
        firstName VARCHAR(10),
        surname VARCHAR(20),
        accountID INTEGER,
        dateOfBirth DATE,
        studentEmail VARCHAR(50),
        classID INTEGER,
        house VARCHAR(15),
        FOREIGN KEY (accountID) REFERENCES tbl_Accounts(accountID) ON DELETE CASCADE,
        FOREIGN KEY (classID) REFERENCES tbl_Classes(classID)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Classes' table
def createClassesTable(cursor: sql.Cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Classes (
        classID INTEGER PRIMARY KEY,
        yearGroup VARCHAR(2),
        registrationClass VARCHAR(1)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Events' table
def createEventTable(cursor: sql.Cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Events (
        eventID INTEGER PRIMARY KEY,
        eventName VARCHAR(50),
        dateOfEvent DATE,
        timeOfEvent TIME,
        durationOfEvent TIME,
        requestedBy INTEGER,
        locationID INTEGER,
        requirements VARCHAR(50),
        FOREIGN KEY (requestedBy) REFERENCES tbl_Staff(staffID) ON DELETE SET NULL,
        FOREIGN KEY (locationID) REFERENCES tbl_Locations(locationID)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Locations' table
def createLocationsTable(cursor: sql.Cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Locations (
        locationID INTEGER PRIMARY KEY,
        nameOfLocation VARCHAR(50)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_SetupGroups' table
def createSetupGroupsTable(cursor: sql.Cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_SetupGroups (
        eventID INTEGER,
        pupilID INTEGER,
        PRIMARY KEY (eventID, pupilID),
        FOREIGN KEY (eventID) REFERENCES tbl_Events(eventID) ON DELETE CASCADE,
        FOREIGN KEY (pupilID) REFERENCES tbl_Pupils(pupilID) ON DELETE CASCADE
    );'''
    cursor.execute(sql)

def populateLocationsTable(cursor: sql.Cursor):
    ''' Function to populate the `tbl_Locations` table with default locations. '''
    sql = "INSERT INTO tbl_Locations(nameOfLocation) VALUES ('Stinson Hall'), ('Sports Hall'), ('Conference Room');"
    cursor.execute(sql)

def populateClassesTable(cursor: sql.Cursor):
    ''' Function to populate the `tbl_Classes` table with default classes. '''
    for year in range(11, 15): # 11, 12, 13, 14
        for regClass in ['S', 'T', 'E', 'P']:
            sql = "INSERT INTO tbl_Classes(yearGroup, registrationClass) VALUES (?, ?);"
            cursor.execute(sql, (year, regClass))

def createAllTables(cursor: sql.Cursor):
    ''' Call all the functions to create the tables and populate them if they are empty.'''
    createAccountTable(cursor)
    createStaffTable(cursor)
    createPupilTable(cursor)
    createClassesTable(cursor)
    createEventTable(cursor)
    createLocationsTable(cursor)
    createSetupGroupsTable(cursor)
    
    if len(getAllRows(cursor, 'tbl_Locations')) == 0: populateLocationsTable(cursor) # If the table is empty, populate it with default locations
    if len(getAllRows(cursor, 'tbl_Classes')) == 0: populateClassesTable(cursor) # If the table is empty, populate it with default classes

def insertData(connection: sql.Connection, cursor: sql.Cursor, tableName, data: list):
    ''' Function to insert data into a table. '''
    sql = f"INSERT INTO {tableName} VALUES ({', '.join(['?' for field in range(len(data))])})"
    cursor.execute(sql, data)
    connection.commit()

def getAllRows(cursor, tableName):
    ''' Function to fetch all rows from a table. '''
    sql = f"SELECT * FROM {tableName}"
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

def fetchRowByCondition(cursor: sql.Cursor, tableName, condition):
    ''' Function to fetch a specific row from a table based on a condition. '''
    sql = f"SELECT * FROM {tableName} WHERE ?"
    cursor.execute(sql, (condition,))
    row = cursor.fetchone()
    return row

def deleteRowWithID(connection: sql.Connection, cursor: sql.Cursor, tableName, idName, id):
    ''' Function to delete a row from a table with a given ID. '''
    sql = f"DELETE FROM {tableName} WHERE ?=?"
    cursor.execute(sql, (idName, id))
    connection.commit()

def login(cursor: sql.Cursor, username: str, password: str) -> list | None:
    ''' Function to check if the username and password are correct.
    Returns None if no match or A list containing the account ID, username, role (if applicable else None), and year group (if applicable, else None) of the user.
    ie. whenderson000, woody123 -> (1, 'whenderson000', 'Staff', None)
    ie. jjoseph553, joel123 -> (2, 'jjoseph553', None, '14')
    '''
    sql = f"""SELECT tbl_Accounts.accountID, tbl_Accounts.username, tbl_Staff.role, tbl_Classes.yearGroup FROM tbl_Accounts
    LEFT JOIN tbl_Staff ON tbl_Accounts.accountID = tbl_Staff.accountID
    LEFT JOIN tbl_Pupils ON tbl_Accounts.accountID = tbl_Pupils.accountID
    LEFT JOIN tbl_Classes ON tbl_Pupils.classID = tbl_Classes.classID
    WHERE tbl_Accounts.username=? AND tbl_Accounts.password=?"""

    cursor.execute(sql, (username, password))
    row = cursor.fetchone()
    return row
# print(login(sql.connect("/Users/joeljoseph/Documents/Projects/Coding Projects/Unit-5-NEA/Contents/TestDatabase.db").cursor(), "dbyrne702", "Agsags123"))

def insertDataIntoEventsTable(connection: sql.Connection, cursor: sql.Cursor, data: list):
    ''' Function to insert data into the 'tbl_Events' table. '''
    memberSetupIDs = data.pop(5)
    sql = f"INSERT INTO tbl_Events(eventName, dateOfEvent, timeOfEvent, durationOfEvent, requestedBy, locationID, requirements) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(sql, data)
    connection.commit()

    setupGroupsData = [(cursor.lastrowid, memberID) for memberID in memberSetupIDs]
    sql = f"INSERT INTO tbl_SetupGroups(eventID, pupilID) VALUES (?, ?)"
    cursor.executemany(sql, setupGroupsData)
    connection.commit()

def updateEvent(connection: sql.Connection, cursor: sql.Cursor, data: list, id):
    ''' Function to update an event in the 'tbl_Events' table along with the SetupGroups table. '''
    memberSetupIDs = data.pop(5)
    sql = f"UPDATE tbl_Events SET eventName=?, dateOfEvent=?, timeOfEvent=?, durationOfEvent=?, requestedBy=?, locationID=?, requirements=? WHERE eventID={id}"
    cursor.execute(sql, data)
    connection.commit()

    sql = f"DELETE FROM tbl_SetupGroups WHERE eventID=?"
    cursor.execute(sql, (id,))
    connection.commit()

    setupGroupsData = [(id, memberID) for memberID in memberSetupIDs]
    sql = f"INSERT INTO tbl_SetupGroups(eventID, pupilID) VALUES (?, ?)"
    cursor.executemany(sql, setupGroupsData)
    connection.commit()

def removeEvent(connection: sql.Connection, cursor: sql.Cursor, id):
    ''' Function to remove an event from the 'tbl_Events' table along with the SetupGroups table. '''
    sql = f"DELETE FROM tbl_Events WHERE eventID={id}"
    cursor.execute(sql)
    connection.commit()

    sql = f"DELETE FROM tbl_SetupGroups WHERE eventID={id}"
    cursor.execute(sql)
    connection.commit()

def joinSetupGroup(connection: sql.Connection, cursor: sql.Cursor, eventID, pupilID):
    ''' Function to join a Senior/Junior pupil to a setup group. '''
    sql = f"INSERT INTO tbl_SetupGroups(eventID, pupilID) VALUES (?, ?)"
    cursor.execute(sql, (eventID, pupilID))
    connection.commit()

def leaveSetupGroup(connection: sql.Connection, cursor: sql.Cursor, eventID, pupilID):
    ''' Function to leave a Senior/Junior pupil from a setup group. '''
    sql = f"DELETE FROM tbl_SetupGroups WHERE eventID=? AND pupilID=?"
    cursor.execute(sql, (eventID, pupilID))
    connection.commit()

def getLatestEventsDetails(cursor: sql.Cursor) -> str:
    ''' Function to get the details of the latest 3 events. Gets relevant details to be displayed on the dashboard. '''
    sql = f'''SELECT tbl_Events.eventName, tbl_Events.dateOfEvent, tbl_Events.timeOfEvent, tbl_Events.durationOfEvent, tbl_Staff.surname, group_concat(tbl_Pupils.firstName || ' ' || tbl_Pupils.surname || ' ' || tbl_Classes.yearGroup || tbl_Classes.registrationClass, ', '), tbl_Locations.nameOfLocation, tbl_Events.requirements
        FROM tbl_Events
        LEFT OUTER JOIN tbl_Staff ON tbl_Events.requestedBy = tbl_Staff.staffID
        LEFT OUTER JOIN tbl_Locations ON tbl_Events.locationID = tbl_Locations.locationID
        LEFT OUTER JOIN tbl_SetupGroups ON tbl_SetupGroups.eventID = tbl_Events.eventID
        LEFT OUTER JOIN tbl_Pupils ON tbl_SetupGroups.pupilID = tbl_Pupils.pupilID
		LEFT OUTER JOIN tbl_Classes ON tbl_Pupils.classID = tbl_Classes.classID 
        WHERE tbl_Events.dateOfEvent >= DATE()
        GROUP by tbl_Events.eventID
        ORDER BY tbl_Events.dateOfEvent ASC
        LIMIT 3; '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    formatted = '' if len(rows) != 0 else "No events found."
    for row in rows:
        formatted += f'{row[0]} in the {row[6]}\n{row[1]} at {row[2]}\n{row[5]}\n\n'
    return formatted

def getAllEventsDetails(cursor: sql.Cursor) -> list:
    ''' Function to get the details of all events. Gets relevant details to be displayed on the Upcoming Events Page. '''
    sql = f'''SELECT tbl_Events.eventID, tbl_Events.eventName, tbl_Events.dateOfEvent, tbl_Events.timeOfEvent, tbl_Events.durationOfEvent, tbl_Staff.surname, group_concat(tbl_Pupils.firstName || ' ' || tbl_Pupils.surname || ' ' || tbl_Classes.yearGroup || tbl_Classes.registrationClass, ', '), tbl_Locations.nameOfLocation, tbl_Events.requirements
        FROM tbl_Events 
        LEFT OUTER JOIN tbl_Staff ON tbl_Events.requestedBy = tbl_Staff.staffID
        LEFT OUTER JOIN tbl_Locations ON tbl_Events.locationID = tbl_Locations.locationID
        LEFT OUTER JOIN tbl_SetupGroups ON tbl_SetupGroups.eventID = tbl_Events.eventID
        LEFT OUTER JOIN tbl_Pupils ON tbl_SetupGroups.pupilID = tbl_Pupils.pupilID
		LEFT OUTER JOIN tbl_Classes ON tbl_Pupils.classID = tbl_Classes.classID 
		GROUP by tbl_Events.eventID;'''
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

def getUpcomingEventsDetails(cursor: sql.Cursor) -> list:
    ''' Function to get the details of all upcoming events (After the current date). Gets relevant details to be displayed on the Upcoming Events Page. '''
    sql = f'''SELECT tbl_Events.eventID, tbl_Events.eventName, tbl_Events.dateOfEvent, tbl_Events.timeOfEvent, tbl_Events.durationOfEvent, tbl_Staff.surname, group_concat(tbl_Pupils.firstName || ' ' || tbl_Pupils.surname || ' ' || tbl_Classes.yearGroup || tbl_Classes.registrationClass, ', '), tbl_Locations.nameOfLocation, tbl_Events.requirements
        FROM tbl_Events 
        LEFT OUTER JOIN tbl_Staff ON tbl_Events.requestedBy = tbl_Staff.staffID
        LEFT OUTER JOIN tbl_Locations ON tbl_Events.locationID = tbl_Locations.locationID
        LEFT OUTER JOIN tbl_SetupGroups ON tbl_SetupGroups.eventID = tbl_Events.eventID
        LEFT OUTER JOIN tbl_Pupils ON tbl_SetupGroups.pupilID = tbl_Pupils.pupilID
		LEFT OUTER JOIN tbl_Classes ON tbl_Pupils.classID = tbl_Classes.classID 
		WHERE tbl_Events.dateOfEvent >= DATE()
        GROUP by tbl_Events.eventID
        ORDER BY tbl_Events.dateOfEvent ASC;'''
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

def getStaffNamesandIDs(cursor: sql.Cursor) -> list:
    ''' Function to get the ids and names of all staff members. '''
    sql = f"SELECT staffID, surname FROM tbl_Staff"
    cursor.execute(sql)
    rows = cursor.fetchall()

    formattedRows = [f'{record[0]}: {record[1]}' for record in rows] # ie. ['1: Smith', '2: Doe', . . . ] this allows id and name to be split easily for displaying in the combobox easily and commiting to the database easily
    return formattedRows

def getLocationsandIDs(cursor: sql.Cursor) -> list:
    ''' Function to get the ids and names of all locations. '''
    sql = f"SELECT locationID, nameOfLocation FROM tbl_Locations"
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    formattedRows = [f'{record[0]}: {record[1]}' for record in rows] # ie. ['1: Sports Hall', '2: Conference Room', . . . ] this allows id and name to be split easily for displaying in the combobox easily and commiting to the database easily
    return formattedRows

def getAllMemberDetails(cursor: sql.Cursor) -> list:
    ''' Function to get the details of all members. Gets relevant details to be displayed on the Members Page. '''
    sql = f'''SELECT tbl_Pupils.pupilID, tbl_Pupils.firstName, tbl_Pupils.surname, tbl_Accounts.username, tbl_Classes.yearGroup || tbl_Classes.registrationClass, tbl_Pupils.studentEmail, tbl_Pupils.dateOfBirth, tbl_Pupils.house
        FROM tbl_Pupils INNER JOIN tbl_Classes ON tbl_Pupils.classID = tbl_Classes.classID
        INNER JOIN tbl_Accounts ON tbl_Pupils.accountID = tbl_Accounts.accountID; '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

def getMemberDetails(cursor: sql.Cursor, id: int) -> list:
    ''' Function to get the details of a member based on their accountID. '''
    sql = f'''SELECT tbl_Pupils.pupilID, tbl_Pupils.firstName, tbl_Pupils.surname, tbl_Accounts.username, tbl_Pupils.classID, tbl_Pupils.studentEmail, tbl_Pupils.dateOfBirth, tbl_Pupils.house
        FROM tbl_Pupils INNER JOIN tbl_Accounts ON tbl_Pupils.accountID = tbl_Accounts.accountID WHERE tbl_Pupils.accountID=?; '''
    cursor.execute(sql, (id,))
    row = cursor.fetchone()
    return row

def getClassesandIDs(cursor: sql.Cursor) -> list:
    ''' Function to get the ids and names of all Classes. '''
    sql = f"SELECT classID, yearGroup, registrationClass FROM tbl_Classes"
    cursor.execute(sql)
    rows = cursor.fetchall()

    formattedRows = [f'{record[0]}: {record[1]}{record[2]}' for record in rows] # ie. ['1: 14S', '2: 14T', . . . ] this allows id and name to be split easily for displaying in the combobox easily and commiting to the database easily
    return formattedRows

def insertDataIntoMemberTable(connection: sql.Connection, cursor: sql.Cursor, data: list):
    ''' Function to insert data into the 'tbl_Pupils' table. '''
    sql = f"INSERT INTO tbl_Pupils(firstName, surname, accountID, classID, studentEmail, dateOfBirth, house) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(sql, data)
    connection.commit()

def updateMember(connection: sql.Connection, cursor: sql.Cursor, data: list, id):
    ''' Function to update a member in the 'tbl_Pupils' table. '''
    sql = f"UPDATE tbl_Pupils SET firstName=?, surname=?, accountID=?, classID=?, studentEmail=?, dateOfBirth=?, house=? WHERE pupilID={id}"
    cursor.execute(sql, data)
    connection.commit()

def removeMember(connection: sql.Connection, cursor: sql.Cursor, id):
    ''' Function to remove a member from the 'tbl_Pupils' and the 'tbl_Accounts' table. '''
    sql = f"DELETE FROM tbl_Accounts WHERE accountID=(SELECT accountID FROM tbl_Pupils WHERE pupilID={id})"
    cursor.execute(sql)
    connection.commit()

    sql = f"DELETE FROM tbl_Pupils WHERE pupilID={id}"
    cursor.execute(sql)
    connection.commit()

def getAllStaffDetails(cursor: sql.Cursor) -> list:
    ''' Function to get the details of all staff members. Gets relevant details to be displayed on the Staff Page. '''
    sql = f'''SELECT tbl_Staff.staffID, tbl_Staff.firstName, tbl_Staff.surname, tbl_Accounts.username, tbl_Staff.role, tbl_Staff.staffEmail
        FROM tbl_Staff INNER JOIN tbl_Accounts ON tbl_Staff.accountID = tbl_Accounts.accountID; '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

def getStaffDetails(cursor: sql.Cursor, id: int) -> list:
    ''' Function to get the details of a staff member based on their AccountID. '''
    sql = f'''SELECT tbl_Staff.staffID, tbl_Staff.firstName, tbl_Staff.surname, tbl_Accounts.username, tbl_Staff.role, tbl_Staff.staffEmail
        FROM tbl_Staff INNER JOIN tbl_Accounts ON tbl_Staff.accountID = tbl_Accounts.accountID WHERE tbl_Staff.accountID=?; '''
    cursor.execute(sql, (id,))
    row = cursor.fetchone()
    return row

def insertDataIntoStaffTable(connection: sql.Connection, cursor: sql.Cursor, data: list):
    ''' Function to insert data into the 'tbl_Staff' table. '''
    sql = f"INSERT INTO tbl_Staff(firstName, surname, accountID, role, staffEmail) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(sql, data)
    connection.commit()

def updateStaff(connection: sql.Connection, cursor: sql.Cursor, data: list, id):
    ''' Function to update a staff member in the 'tbl_Staff' table. '''
    sql = f"UPDATE tbl_Staff SET firstName=?, surname=?, accountID=?, role=?, staffEmail=? WHERE staffID={id}"
    cursor.execute(sql, data)
    connection.commit()

def removeStaff(connection: sql.Connection, cursor: sql.Cursor, id):
    ''' Function to remove a staff member from the 'tbl_Staff' and 'tbl_Accounts' table. '''
    sql = f"DELETE FROM tbl_Accounts WHERE accountID=(SELECT accountID FROM tbl_Staff WHERE staffID={id})"
    cursor.execute(sql)
    connection.commit()

    sql = f"DELETE FROM tbl_Staff WHERE staffID={id}"
    cursor.execute(sql)
    connection.commit()

def createAccount(connection: sql.Connection, cursor: sql.Cursor, username: list[str]) -> int:
    ''' Function to create an account with given username and default password 'Password1'.
        Returns the accountID of the created account. '''
    sql = f"INSERT INTO tbl_Accounts(username, password) VALUES (?, 'Password1')"
    cursor.execute(sql, username)
    connection.commit()

    return cursor.lastrowid

def getAccountsAndIDs(cursor: sql.Cursor) -> list:
    ''' Function to get the ids and usernames of all accounts. '''
    sql = f"SELECT accountID, username FROM tbl_Accounts"
    cursor.execute(sql)
    rows = cursor.fetchall()

    formattedRows = [f'{record[0]}: {record[1]}' for record in rows] # ie. ['1: Smith', '2: Doe', . . . ] this allows id and name to be split easily for displaying in the combobox easily and commiting to the database easily
    return formattedRows

def getUserID(cursor: sql.Cursor, accountID: int) -> int:
    ''' Function to get the ID of a user with a given accountID. '''
    sql = f"SELECT pupilID FROM tbl_Pupils WHERE accountID=?"
    cursor.execute(sql, (accountID,))
    row = cursor.fetchone()

    if row == None:
        sql = f"SELECT staffID FROM tbl_Staff WHERE accountID=?"
        cursor.execute(sql, (accountID,))
        row = cursor.fetchone()

    return row[0]

def getUserEmail(cursor: sql.Cursor, accountID: int) -> str:
    ''' Function to get the email of a user with a given accountID. '''
    sql = f"SELECT studentEmail FROM tbl_Pupils WHERE accountID=?"
    cursor.execute(sql, (accountID,))
    row = cursor.fetchone()

    if row == None:
        sql = f"SELECT staffEmail FROM tbl_Staff WHERE accountID=?"
        cursor.execute(sql, (accountID,))
        row = cursor.fetchone()

    return row[0]

def getUserEmailWithUserID(cursor: sql.Cursor, userID: int) -> str:
    ''' Function to get the email of a user with a given userID. '''
    sql = f"SELECT studentEmail FROM tbl_Pupils WHERE pupilID=?"
    cursor.execute(sql, (userID,))
    row = cursor.fetchone()

    if row == None:
        sql = f"SELECT staffEmail FROM tbl_Staff WHERE staffID=?"
        cursor.execute(sql, (userID,))
        row = cursor.fetchone()

    return row[0]
