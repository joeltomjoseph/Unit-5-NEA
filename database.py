import sqlite3 as sql

# Function to create the 'tbl_Accounts' table
def createAccountTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Accounts (
        accountID INT PRIMARY KEY,
        username VARCHAR(20),
        password VARCHAR(20)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Staff' table
def createStaffTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Staff (
        staffID INT PRIMARY KEY,
        firstName VARCHAR(10),
        surname VARCHAR(20),
        accountID INT,
        role VARCHAR(10),
        staffEmail VARCHAR(50),
        FOREIGN KEY (accountID) REFERENCES tbl_Accounts(accountID)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Pupils' table
def createPupilTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Pupils (
        memberID INT PRIMARY KEY,
        firstName VARCHAR(10),
        surname VARCHAR(20),
        accountID INT,
        dateOfBirth DATE,
        studentEmail VARCHAR(50),
        classID INT,
        house VARCHAR(15),
        FOREIGN KEY (accountID) REFERENCES tbl_Accounts(accountID),
        FOREIGN KEY (classID) REFERENCES tbl_Classes(classID)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Classes' table
def createClassesTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Classes (
        classID INT PRIMARY KEY,
        yearGroup VARCHAR(2),
        registrationClass VARCHAR(1)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Events' table
def createEventTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Events (
        eventID INT PRIMARY KEY,
        eventName VARCHAR(50),
        dateOfEvent DATE,
        timeOfEvent TIME,
        durationOfEvent TIME,
        requestedBy INT,
        locationID INT,
        requirements VARCHAR(50),
        FOREIGN KEY (requestedBy) REFERENCES tbl_Staff(staffID),
        FOREIGN KEY (locationID) REFERENCES tbl_Locations(locationID)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Locations' table
def createLocationsTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Locations (
        locationID INT PRIMARY KEY,
        nameOfLocation VARCHAR(50)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_SetupGroups' table
def createSetupGroupsTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_SetupGroups (
        eventID INT,
        pupilID INT,
        PRIMARY KEY (eventID, pupilID),
        FOREIGN KEY (eventID) REFERENCES tbl_Events(eventID),
        FOREIGN KEY (pupilID) REFERENCES tbl_Pupils(memberID)
    );'''
    cursor.execute(sql)

# # Call all the functions to create the tables
# createAccountTable(cursor)
# createStaffTable(cursor)
# createPupilTable(cursor)
# createClassesTable(cursor)
# createHouseTable(cursor)
# createEventTable(cursor)
# createLocationsTable(cursor)
# createSetupGroupsTable(cursor)

# Function to insert data into a table
def insertData(connection, cursor, tableName, data: list):
    sql = f"INSERT INTO {tableName} VALUES ({', '.join(['?' for field in range(len(data))])})"
    cursor.execute(sql, data)
    connection.commit()

# Function to fetch all rows from a table
def getAllRows(cursor, tableName):
    sql = f"SELECT * FROM {tableName}"
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

# Function to fetch a specific row from a table based on a condition
def fetchRowByCondition(cursor, tableName, condition):
    sql = f"SELECT * FROM {tableName} WHERE {condition}"
    cursor.execute(sql)
    row = cursor.fetchone()
    return row

def getLatestEventsDetails(cursor):
    ''' Function to get the details of the latest 3 events. Gets relevant details to be displayed on the dashboard. '''
    sql = f'''SELECT tbl_Events.eventName, tbl_Events.dateOfEvent, tbl_Events.timeOfEvent, tbl_Events.durationOfEvent, tbl_Staff.surname, tbl_Locations.nameOfLocation, tbl_Events.requirements
        FROM tbl_Events INNER JOIN tbl_Staff ON tbl_Events.requestedBy = tbl_Staff.staffID
        INNER JOIN tbl_Locations ON tbl_Events.locationID = tbl_Locations.locationID
        WHERE tbl_Events.dateOfEvent >= DATE() LIMIT 3; '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    #formatted = f'''{*rows[0],}\n{*rows[1],}\n{*rows[2],}'''
    formatted = f'{" - ".join(str(i) for i in rows[0])}\n\n{" - ".join(str(i) for i in rows[1])}\n\n{" - ".join(str(i) for i in rows[2])}'
    return formatted

def getAllEventsDetails(cursor):
    ''' Function to get the details of all events. Gets relevant details to be displayed on the Upcoming Events Page. '''
    sql = f'''SELECT tbl_Events.eventID, tbl_Events.eventName, tbl_Events.dateOfEvent, tbl_Events.timeOfEvent, tbl_Events.durationOfEvent, tbl_Staff.surname, tbl_Locations.nameOfLocation, tbl_Events.requirements
        FROM tbl_Events INNER JOIN tbl_Staff ON tbl_Events.requestedBy = tbl_Staff.staffID
        INNER JOIN tbl_Locations ON tbl_Events.locationID = tbl_Locations.locationID
        ; '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

#connection = sql.connect("TestDatabase.db")
#cursor = connection.cursor()

# insertData(connection, cursor, "tbl_Accounts", [3, 'lcampbellnesbitt', 'ags']); insertData(connection, cursor, "tbl_Staff", [2, 'L', 'Campbell-Nesbitt', 3, 'Admin', 'lcampbellnesbitt280@c2ken.net'])
# insertData(connection, cursor, "tbl_Accounts", [4, 'dbyrne', 'ags']); insertData(connection, cursor, "tbl_Staff", [3, 'Damien', 'Byrne', 4, 'Head Of the Team', 'dbyrne702@c2ken.net'])
# insertData(connection, cursor, "tbl_Accounts", [5, 'adark', 'ags']); insertData(connection, cursor, "tbl_Staff", [4, 'A', 'Dark', 5, 'Teacher', 'adark303@c2ken.net'])

# insertData(connection, cursor, "tbl_Locations", [2, 'Sports Hall']); insertData(connection, cursor, 'tbl_Locations', [3, 'Conference Room'])

# insertData(connection, cursor, "tbl_Events", [2, 'Senior Assembly', '30/12/23', '8:30', '45 Mins', 2, 1, 'Microphone'])
# insertData(connection, cursor, "tbl_Events", [3, 'Junior Assembly', '1/1/24', '8:45', '30 Mins', 3, 1, 'Screen'])
# insertData(connection, cursor, "tbl_Events", [4, 'Staff Meeting', '5/1/24', '9:15', '1 Hour', 3, 3, 'Connecting to screen'])
# insertData(connection, cursor, "tbl_Events", [5, 'Tower House Assembly', '8/1/24', '9:15', '30 Mins', 4, 2, 'Connecting to screen'])

#print(getLatestEventsDetails(cursor))