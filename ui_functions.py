from PopMenu import PopMenu
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QFrame, QSizeGrip
from PyQt5.QtGui import QCursor, QColor
import sqlite3
from Course import Course
from PopMenu import PopMenu
from MessageBox import MessageBox
from main import *

# global variable for state of window (1 for maximized, 0 for not)
WINDOW_STATE = 0

class UIFunctions(MainWindow):

    DATABASE = 'userData.db'
    TABLE_NAME = 'courses'
    COLUMN_NAME_STRING = 'courseName, instructorEmail, startTime, endTime, daysOfWeek, link, linkParam, meetingID, passcode'

    @staticmethod
    # connect to database, create databse file if not exists
    def connect():
        """
        return connection and cursor object
        """
        con = sqlite3.connect(UIFunctions.DATABASE)
        cur = con.cursor()
        return con, cur

    # close sqlite connection to database
    @staticmethod
    def close(con):
        con.close()

    def sqlLoadData(self):
        courseList = list()
        self.cur.executescript(f"""
            CREATE TABLE IF NOT EXISTS {UIFunctions.TABLE_NAME}(
                courseID INTEGER PRIMARY KEY AUTOINCREMENT,
                courseName TEXT NOT NULL,
                instructorEmail TEXT,
                startTime time NOT NULL,
                endTime time NOT NULL,
                daysOfWeek TEXT NOT NULL,
                link TEXT,
                linkParam TEXT,
                meetingID TEXT,
                passcode TEXT
                )""")

        # order by start time of course in ascending order (time format - HH:MM AM/PM)
        self.cur.execute(f"SELECT * FROM {UIFunctions.TABLE_NAME} ORDER BY substr(startTime,7) || substr(startTime, 1, 5) ASC")
        data = self.cur.fetchall()

        for item in data:
            argDict = {'courseID': item[0], 'courseName': item[1], 'startTime': item[3],\
                     'endTime': item[4], 'daysOfWeek': item[5]}
            
            if item[2]:
                argDict['instructorEmail'] = item[2]
            
            if item[6]:
                argDict['link'] = item[6]
                argDict['linkParam'] = item[7]
                course = Course(argDict)
            else:
                argDict['meetingID'] = item[8]
                if item[9]:
                    argDict['passcode'] = item[9]
                course = Course(argDict)
            course.createWidget()

            # connect widget signals to respective slots
            course.requestDelete.connect(self.deleteCourse)
            course.sendUpdatedInfo.connect(self.updateCourse)
            course.copyEmailBtn.clicked.connect(self.showCopiedMsg)
            # store references to widget for convenient insertion into layout, already in order
            courseList.append(course)
        
        return courseList
    
    # create course widget from data from dictionary
    def insertNewCourse(self, dic):
        values = (dic.get('courseName'), dic.get('instructorEmail'), dic.get('startTime'), dic.get('endTime'),\
                dic.get('daysOfWeek'), dic.get('link'), dic.get('linkParam'), dic.get('meetingID'), dic.get('passcode'))
        
        # insert new course info into database
        self.cur.execute(f"INSERT INTO {UIFunctions.TABLE_NAME} ({UIFunctions.COLUMN_NAME_STRING}) VALUES (?,?,?,?,?,?,?,?,?)", values)
        self.cur.execute("SELECT last_insert_rowid()")
        courseID = self.cur.fetchone()[0]
        
        # insert generated courseID into dataDict
        dic['courseID'] = courseID

        # order by start time of course in ascending order (time format - HH:MM AM/PM)
        self.cur.execute("SELECT courseID FROM courses ORDER BY substr(startTime,7) || substr(startTime, 1, 5) ASC")
        
        # get index of new inserted course
        index = 0
        for tuple in self.cur.fetchall():
            if tuple[0] == courseID:
                break
            index += 1
    
        newCourse = Course(dic)
        newCourse.createWidget()
        # connect widget signals to respective slots
        newCourse.requestDelete.connect(self.deleteCourse)
        newCourse.sendUpdatedInfo.connect(UIFunctions.sqlUpdateData)
        newCourse.copyEmailBtn.clicked.connect(self.showCopiedMsg)
        newCourse.showPopMenu.connect(self.popupMenu.displayMenu)

        return newCourse, index

    @staticmethod
    def sqlUpdateData(cur, dataDict):
        courseID = dataDict.pop("courseID")
        
        # generate part of sql command to update a record
        sql = ""
        for col in dataDict:
            sql += col + "=" + f"'{dataDict[col]}'" + ","

        # first, clear fields which are variable to prevent overlap between link type and id type
        # then update the entire row with new course info, keeping courseID the same
        cur.executescript(f"""UPDATE {UIFunctions.TABLE_NAME}
                                    SET (link, linkParam, meetingID, passcode) = (NULL, NULL, NULL, NULL)
                                    WHERE courseID = {courseID};
                                UPDATE {UIFunctions.TABLE_NAME}
                                    SET {sql[:-1]} WHERE courseID = {courseID};
                                    """)
        # order again by startTime
        cur.execute("SELECT courseID FROM courses ORDER BY substr(startTime,7) || substr(startTime, 1, 5) ASC")
        
        # get index of record
        index = 0
        for tuple in cur.fetchall():
            if tuple[0] == courseID:
                break
            index += 1

        return index
    
    # delete record from database, using courseID
    @staticmethod
    def sqlDeleteCourse(cursor, id):
        cursor.execute(f"DELETE FROM {UIFunctions.TABLE_NAME} WHERE courseID = {id};")

    # convert 24 hour time to 12 hour times
    @staticmethod
    def convertTimeto12(dataDict):
        dataDict["startTime"] = dataDict["startTime"].strftime("%I:%M %p")
        dataDict["endTime"] = dataDict["endTime"].strftime("%I:%M %p")
    
    # setup the main window, populate with widgets and connect necessary signals to slots
    def setupMainScreen(self):

        # Remove window frame
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Set functions for taskbar buttons
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_maximize.clicked.connect(lambda:UIFunctions.maximizeRestore(self))
        self.ui.btn_minimize.clicked.connect(self.showMinimized)

        # create and set shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(1,2)
        self.ui.shadowFrame.setGraphicsEffect(shadow)

        # create popup to be called whenever a course item is right-clicked
        self.popupMenu = PopMenu(parent=self)
        self.popupMenu.hide()

        # create a messagebox for displaying info
        self.msgBox = MessageBox(parent=self)
        self.msgBox.hide()

        # Create frame for to contain course frames
        self.ui.courseFrame = QFrame()
        self.ui.courseFrameLayout = QVBoxLayout()
        self.ui.courseFrameLayout.setContentsMargins(0,0,0,0)
        self.ui.courseFrameLayout.setSpacing(20)

        # Title
        self.ui.meetingsHeading = QLabel("COURSES")
        self.ui.meetingsHeading.setMinimumHeight(30)
        self.ui.meetingsHeading.setStyleSheet("font: bold 20px Moon; margin-bottom: 15px; margin-left: 5px;")
        self.ui.contentLayout.insertWidget(0, self.ui.meetingsHeading)

        
        # Add group boxes to groupframe layout
        for course in self.courseList:
            self.ui.courseFrameLayout.addWidget(course)
            # Connect course widget's right click signal to popupmenu
            course.showPopMenu.connect(self.popupMenu.displayMenu)

        # Set layout for groupframe
        self.ui.courseFrame.setLayout(self.ui.courseFrameLayout)
        self.ui.scrollAreaLayout.addWidget(self.ui.courseFrame)
        self.ui.scrollAreaLayout.setSpacing(0)
        self.ui.scrollAreaLayout.setAlignment(Qt.AlignTop)
        self.ui.scrollArea.setStyleSheet("background-color: transparent;")
    
        # Size Grip
        self.ui.sizegrip = QSizeGrip(self.ui.sizeGrip)

        self.ui.newMeetingBtn.setCursor(QCursor(Qt.PointingHandCursor))
        # Display form when add button is clicked
        self.ui.newMeetingBtn.clicked.connect(self.displayNewForm)

    #### WINDOW FUNCTIONS ####

    def maximizeRestore(self):
        global WINDOW_STATE

        # If not maximized
        if WINDOW_STATE == 0:
            self.showMaximized()

            # Switch states
            WINDOW_STATE = 1

            # If maximized, remove border radius and content margins of central widget
            self.ui.centralWidgetLayout.setContentsMargins(0,0,0,0)
            self.ui.title_bar.setStyleSheet(".QFrame {background-color: rgb(40, 57, 113);}")
            self.ui.backgroundFrame.setStyleSheet(".QFrame {background-color: rgb(130,171,192);}")
            self.ui.btn_maximize.setToolTip("Restore")
        
        else:
            WINDOW_STATE = 0
            # revert to window state before maximized
            self.showNormal()
            # set margins and round corners
            self.ui.centralWidgetLayout.setContentsMargins(10,10,10,10)
            self.ui.title_bar.setStyleSheet(""".QFrame {
                                                    background-color: rgb(40, 57, 113);
                                                    border-top-left-radius: 10px;
                                                    border-top-right-radius: 10px;
                                                    border-bottom-left-radius: 0;
                                                    border-bottom-right-radius: 0;}""")
            self.ui.backgroundFrame.setStyleSheet(""".QFrame {background-color: rgb(130,171,192);
                                                        border-bottom-left-radius: 10px;
                                                        border-bottom-right-radius: 10px;
                                                        border-top-left-radius: 0;
                                                        border-top-right-radius: 0;}""")
            self.ui.btn_maximize.setToolTip("Maximize")

    def getWindowState():
        return WINDOW_STATE


            




