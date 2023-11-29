import sqlite3 as sql
import re

# Establish a connection to the database
connection = sql.connect("TestDatabase.db")

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

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
        yearGroup VARCHAR(2),
        registrationClass VARCHAR(1),
        PRIMARY KEY (yearGroup, registrationClass)
    );'''
    cursor.execute(sql)

# Function to create the 'tbl_Houses' table
def createHouseTable(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tbl_Houses (
        houseID INT PRIMARY KEY,
        houseName VARCHAR(20)
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
def insertData(cursor, tableName, data: list):
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

# Function to check if data passed in is present
def presenceCheck(data: list):
    ''' Check if all fields in a list of data are present, 
    this can also be used to check if a single value is present by passing in a single value as a list '''
    for field in data:
        if field == '' or field == None:
            return False
    return True

def validateUsername(username):
    # Validate username: At least minUsernameLength and greater than maxUsernameLength
    minUsernameLength = 6
    maxUsernameLength = 20

    if len(username) < minUsernameLength or len(username) > maxUsernameLength:
        print(f"Invalid username. Username has to be between {minUsernameLength} and {maxUsernameLength} characters long.")
        return False
    return True

def validatePassword(password):
    # Validate password: At least 9 characters, one uppercase, one lowercase, one number
    if len(password) < 9:
        print("Invalid password. Password must be at least 9 characters.")
        return False

    if not re.search(r'[A-Z]', password):
        print("Invalid password. Password must contain at least one uppercase letter.")
        return False

    if not re.search(r'[a-z]', password):
        print("Invalid password. Password must contain at least one lowercase letter.")
        return False

    if not re.search(r'\d', password):
        print("Invalid password. Password must contain at least one digit.")
        return False

    return True

