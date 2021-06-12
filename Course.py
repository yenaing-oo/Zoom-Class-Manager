from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import QSize, QPoint, pyqtSignal, pyqtSlot, Qt
from form import NewForm
import subprocess
import pyperclip

class Course(QFrame):
    daysTuple = ('S', 'M', 'T', 'W', 'T', 'F', 'S')
        
    # Create signal for deletion
    requestDelete = pyqtSignal(bool)

    # Create signal for pop-menu to show
    showPopMenu = pyqtSignal(QPoint)

    # Create signal for sending updated course info to database
    sendUpdatedInfo = pyqtSignal(dict)



    def __init__(self, dataDict):
        # Intialize Course as a QObject
        QFrame.__init__(self)
        self.data = dataDict
        self.courseID = dataDict['courseID']
    
    def createWidget(self):
        self.setMaximumSize(QSize(16777215, 90))
        self.setStyleSheet(u"QFrame {\n"
                                        "background-color: #1e1e1e;\n"
                                        "color: rgb(129, 10, 209);\n"
                                        "border-radius: 16px;\n"
                                        "border-top-right-radius: 35px; \n"
                                        "border-bottom-left-radius: 35px;\n"
                                        "padding-bottom: 5px;} \n"
                                        "QLabel {\n"
                                        "background-color: none;\n"
                                        "font: bold 18px Moon; \n"
                                        "color: #ffffff;}\n"
                                        )

        courseWidgetLayout = QHBoxLayout(self)
        courseWidgetLayout.setContentsMargins(15, 0, 20, 0)

        # course header frame
        courseHeaderFrame = QFrame(self)
        courseHeaderLayout = QVBoxLayout(courseHeaderFrame)
        courseHeaderLayout.setContentsMargins(0, 20, -1, 10)
        
        # course name label
        self.courseNameLabel = QLabel(courseHeaderFrame)
        self.courseNameLabel.setStyleSheet(u"color: rgb(129, 10, 209);")
        courseHeaderLayout.addWidget(self.courseNameLabel)
        
        # time label
        self.timeLabel = QLabel(courseHeaderFrame)
        self.timeLabel.setStyleSheet(u"QLabel {\n"
"	font: bold 22px Moon;\n"
"}")
        courseHeaderLayout.addWidget(self.timeLabel)

        # adding course header frame to course frame
        courseWidgetLayout.addWidget(courseHeaderFrame)

        # adding days to courseDayFrame
        courseDayFrame = QFrame(self)
        courseDayFrame.setMaximumSize(QSize(220, 16777215))
        courseDayFrameLayout = QHBoxLayout(courseDayFrame)
        courseDayFrameLayout.setSpacing(8)
        courseDayFrameLayout.setContentsMargins(0, 15, 0, 0)
        sundayLabel = QPushButton("S", courseDayFrame)
        courseDayFrameLayout.addWidget(sundayLabel)
        mondayLabel = QPushButton("M", courseDayFrame)
        courseDayFrameLayout.addWidget(mondayLabel)
        tuesdayLabel = QPushButton("T", courseDayFrame)
        courseDayFrameLayout.addWidget(tuesdayLabel)
        wednesdayLabel = QPushButton("W", courseDayFrame)
        courseDayFrameLayout.addWidget(wednesdayLabel)
        thursdayLabel = QPushButton("T", courseDayFrame)
        courseDayFrameLayout.addWidget(thursdayLabel)
        fridayLabel = QPushButton("F", courseDayFrame)
        courseDayFrameLayout.addWidget(fridayLabel)
        saturdayLabel = QPushButton("S", courseDayFrame)
        courseDayFrameLayout.addWidget(saturdayLabel)

        self.dayButtonTuple = (sundayLabel, mondayLabel, tuesdayLabel, wednesdayLabel, thursdayLabel, fridayLabel,saturdayLabel)

        # add day frame to course layout
        courseWidgetLayout.addWidget(courseDayFrame, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        # create button frame
        courseButtonFrame = QFrame(self)
        courseBtnLayout = QHBoxLayout(courseButtonFrame)
        courseBtnLayout.setSpacing(60)
        courseBtnLayout.setContentsMargins(0, 8, 0, 0)
        self.copyEmailBtn = QPushButton(courseButtonFrame)
        self.copyEmailBtn.setStyleSheet(u"QPushButton {\n"
"	background: none;\n"
"	border: none;\n"
"	image: url(:/icons/email);\n"
"	height: 25px;\n"
"	min-width: 25px;\n"
"	max-width: 25px;\n"
"	top: 2px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	image: url(:/icons/emailHover);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	image: url(:/icons/email);\n"
"}")

        courseBtnLayout.addWidget(self.copyEmailBtn)
        self.copyEmailBtn.setVisible(False)
        self.copyEmailBtn.setCursor(Qt.PointingHandCursor)

        joinMeetingBtn = QPushButton(courseButtonFrame)
        joinMeetingBtn.clicked.connect(self.launchMeeting)
        joinMeetingBtn.setCursor(Qt.PointingHandCursor)
        joinMeetingBtn.setText("Join meeting")
        joinMeetingBtn.setMinimumSize(QSize(180, 36))
        joinMeetingBtn.setStyleSheet(u"QPushButton {\n"
"	font: bold 16px Moon;\n"
"	color: #ffffff;\n"
"	min-height: 34px;\n"
"	padding-top: 2px;\n"
"	padding-bottom: 2px;\n"
"	border-radius: 14px;\n"
"	background-color: #0e6de4;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #0c5cc2;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: #0a51ab;\n"
"}")

        courseBtnLayout.addWidget(joinMeetingBtn)
        courseWidgetLayout.addWidget(courseButtonFrame, 0, Qt.AlignRight)

        # insert text for labels
        self.fillWidgetText()

    def fillWidgetText(self):
        self.courseNameLabel.setText(self.data['courseName'])
        self.timeLabel.setText(self.data['startTime'] + "-" + self.data["endTime"])

        for i in range(len(self.dayButtonTuple)):
            button = self.dayButtonTuple[i]
            button.setStyleSheet("background: none; border: none; font: bold 20px Moon; color: #ffffff;")
            if self.data['daysOfWeek'][i] == "1":
                button.setStyleSheet("background: none; border: none; font: bold 20px Moon; color: #0d62cb;")
        
        if 'instructorEmail' in self.data:
            self.copyEmailBtn.setVisible(True)
            self.copyEmailBtn.clicked.connect(self.copyEmail)

    def launchMeeting(self):
        if "link" in self.data:
            subprocess.Popen(["cmd", "/C", f"start zoommtg://zoom.us/start?{self.data['linkParam']}"], shell=True)
        else:
            paramStr = "confno=" + str(self.data["meetingID"])
            if "passcode" in self.data:
                paramStr += "^&pwd=" + self.data["passcode"]

            subprocess.Popen(["cmd", "/C", f"start zoommtg://zoom.us/join?{paramStr}"], shell=True)
    
    def deleteCourse(self):
        # send id of this course instance to be deleted
        self.requestDelete.emit(True)

    def editCourse(self):
        newForm = NewForm()
        newForm.validated.connect(self.updateWidget)

        newForm.form.titleLabel.setText("Edit meeting")
        newForm.form.courseLineEdit.setText(self.data["courseName"])
        newForm.form.startComboBox.setCurrentText(self.data["startTime"])
        newForm.form.endComboBox.setCurrentText(self.data["endTime"])
        
        for i in range(len(self.data["daysOfWeek"])):
            if int(self.data["daysOfWeek"][i]):
                newForm.dayBtnList[i].setChecked(True)

        if "instructorEmail" in self.data:
            newForm.form.instructorEmailLineEdit.setText(self.data["instructorEmail"])

        if "link" in self.data:
            newForm.form.linkLineEdit.setText(self.data["link"])
        else:
            newForm.form.idRadioBtn.setChecked(True)
            newForm.form.meetingIDLineEdit.setText(self.data["meetingID"])
            if "passcode" in self.data:
                newForm.form.checkBox.setChecked(True)
                newForm.form.passcodeLineEdit.setText(self.data["passcode"])
        
        newForm.form.addBtn.setText("Save")
        
        newForm.display()
    
    @pyqtSlot(dict)
    def updateWidget(self, dataDict):
        dataDict["courseID"] = self.courseID
        dataDict["startTime"] = dataDict["startTime"].strftime("%I:%M %p")
        dataDict["endTime"] = dataDict["endTime"].strftime("%I:%M %p")

        self.data = dataDict
        self.fillWidgetText()
        self.sendUpdatedInfo.emit(dataDict)
    
    def copyEmail(self):
        pyperclip.copy(self.data["instructorEmail"])

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.buttons() == Qt.RightButton:
            self.showPopMenu.emit(event.windowPos().toPoint())
    
    def enterEvent(self, event):
        super().enterEvent(event)
        self.setStyleSheet(self.styleSheet().replace("1e1e1e", "212121", 1))
    
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setStyleSheet(self.styleSheet().replace("212121", "1e1e1e", 1))
