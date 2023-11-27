import sqlite3 as sql

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