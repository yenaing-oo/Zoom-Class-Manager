from datetime import datetime
from PyQt5.QtCore import pyqtSignal, QRegExp, Qt, QPoint
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QRegExpValidator, QColor
import datetime
import resources_rc
from ui_form import Ui_Dialog

class NewForm(QDialog):
    # global class variables
    redBorder = "border: 1px solid rgb(247, 17, 48);"
    validated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        # store day buttons and line edits in tuples for convenient access
        self.dayBtnList = (self.form.sun_btn, self.form.mon_btn, self.form.tue_btn, self.form.wed_btn, self.form.thu_btn, self.form.fri_btn, self.form.sat_btn)
        lineEditList = (self.form.courseLineEdit, self.form.instructorEmailLineEdit, self.form.linkLineEdit, self.form.meetingIDLineEdit, self.form.passcodeLineEdit)
        
        # Remove window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # create and set shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(QPoint(0,0))
        self.setGraphicsEffect(shadow)

        # Allow window to be moved
        self.form.titleBar.mouseMoveEvent = self.moveWindow

        # Populate time comboboxes
        self.setupComboBoxes()

        # Make day buttons checkable
        for button in self.dayBtnList:
            button.setCheckable(True)
            button.clicked.connect(self.resetButtonColor)

        # Initially check invitation link option radio button
        self.form.linkRadioBtn.setChecked(True)

        # Hide parts of form relevant to meetingID and password, since radio button is initially link option 
        self.hideItems(self.form.idLabel, self.form.meetingIDLineEdit, self.form.meetingIDLineEdit, self.form.checkBox, self.form.passLabel, self.form.passcodeLineEdit)

        # Save button hover color change
        self.form.addBtn.setStyleSheet(
        "QPushButton:hover {" +
        "color : white;" +
        "background-color: rgb(12,114,237);}" 
        )
        
        # Cancel button hover style
        self.form.cancelBtn.setStyleSheet(
            "QPushButton:hover {" +
            "background-color: rgb(218, 218, 218);}"
        )

        # Change editability of password lineEdit initially
        self.form.passcodeLineEdit.setEnabled(False)
        self.form.passcodeLineEdit.setStyleSheet("QLineEdit {background-color: rgb(238,238,238);}")
        self.form.checkBox.stateChanged.connect(self.checkBoxToggle)

        # Reset border colors when text edited in line edits
        for lineEdit in lineEditList:
            lineEdit.textEdited.connect(self.resetBorderColor)

        # Set validators and maximum lengths for line edits
        validator = QRegExpValidator(QRegExp("[^\n\t]{1,25}"))
        self.form.courseLineEdit.setValidator(validator)
        validator = QRegExpValidator(QRegExp("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"))
        self.form.instructorEmailLineEdit.setValidator(validator)
        validator = QRegExpValidator(QRegExp("^https://(?:www\.)?(?:us02web\.)?zoom.us/[jw]/(\d)+(\?[a-z]+=[^=\n\r/]+)*"))
        self.form.linkLineEdit.setValidator(validator)
        validator = QRegExpValidator(QRegExp("[0-9]{10,11}"))
        self.form.meetingIDLineEdit.setValidator(validator)
        validator = QRegExpValidator(QRegExp("[^\s\t]{1,16}"))
        self.form.passcodeLineEdit.setValidator(validator)

        # Set default button (when Enter is pressed,button is also pressed)
        self.form.addBtn.setDefault(True)

        # Call validate function when 'Save' button is clicked
        self.form.addBtn.clicked.connect(self.validate)

        # Close form box if cancel is clicked
        self.form.cancelBtn.clicked.connect(self.close)

        # Call toggle function when one of the radio buttons are toggled, only one needed as there are only 2 buttons
        self.form.linkRadioBtn.toggled.connect(self.toggleRadio)

    def setupComboBoxes(self):
        # Create a list of time objects and a list of strings to represent the time objects
        timeList = list()
        startDateTime = datetime.datetime(100, 1, 1, hour = 0, minute = 0)
        timeDelta = datetime.timedelta(minutes = 15)
        for i in range(96):
            timeItem = startDateTime + i * timeDelta
            timeList.append(timeItem.time())
        timeStringList = [time.strftime("%I:%M %p") for time in timeList]

        # Populate time comboboxes
        for time, timeString in zip(timeList, timeStringList):
            self.form.startComboBox.addItem(timeString, time)
            self.form.endComboBox.addItem(timeString, time)
        
        # set maximum items shown in combobox, and set default values
        self.form.startComboBox.setMaxVisibleItems(6)
        self.form.startComboBox.setCurrentIndex(36)
        self.form.startComboBox.setMaxVisibleItems(6)
        self.form.endComboBox.setCurrentIndex(42)

    def validate(self):
        # list to store days of week chosen (eg. [0,1,0,1,0,1,0] represents Mon,Tue and Wed)
        dayList = list()
        # boolean to store whether all data entries are valid
        self.validationPass = True

        self.checkInput(self.form.courseLineEdit)

        # since this field is optional, check only if there is text
        if self.form.instructorEmailLineEdit.text():
            self.checkInput(self.form.instructorEmailLineEdit)

        # at least one day chosen for course
        oneChecked = False
        for btn in self.dayBtnList:
            dayList.append("1" if btn.isChecked() else "0")
            if btn.isChecked():
                oneChecked = True        
        
        # if at least one day is not chosen
        if not oneChecked:
            self.form.dayGroupBox.setStyleSheet(self.form.dayGroupBox.styleSheet().replace("255,255,255", "255,212,212", 1))
            self.validationPass = False
        
        # if link option chosen
        if self.form.linkRadioBtn.isChecked():
            self.checkInput(self.form.linkLineEdit)
        # if meeting id option chosen
        else:
            self.checkInput(self.form.meetingIDLineEdit)
            # if passcode checkbox is ticked
            if self.form.checkBox.isChecked():
                self.checkInput(self.form.passcodeLineEdit)
        
        # If all entries have acceptable input, emit signal
        if self.validationPass:
            dataDict = {"courseName": self.form.courseLineEdit.text(),
                        "startTime": self.form.startComboBox.currentData(),
                        "endTime": self.form.endComboBox.currentData(),
                        "daysOfWeek": "".join(dayList)
                        }
            
            if self.form.instructorEmailLineEdit.text():
                dataDict["instructorEmail"] = self.form.instructorEmailLineEdit.text()

            if self.form.linkRadioBtn.isChecked():
                dataDict["link"] = self.form.linkLineEdit.text()
                # get paramenters from invitation link
                rx = QRegExp("(?:\d+)(?:\?[a-z]+=[^=\n\r/]+)*")
                rx.indexIn(self.form.linkLineEdit.text())
                li = rx.capturedTexts()
                dataDict["linkParam"] = "confno=" + li[0].replace("?", "^&")
            else:
                dataDict["meetingID"] = self.form.meetingIDLineEdit.text()
                if self.form.checkBox.isChecked():
                    dataDict["passcode"] = self.form.passcodeLineEdit.text()
            
            self.validated.emit(dataDict)
            self.close()

    # apply red border to line edit if invalid input provided
    def checkInput(self, *widgets):
        for widget in widgets:
            if not widget.hasAcceptableInput():
                widget.setStyleSheet(self.redBorder)
                self.validationPass = False

    # if line edit is modified, reset border color
    def resetBorderColor(self):
        lineEditSender = self.sender()
        lineEditSender.setStyleSheet("border: 1px solid rgb(171, 171, 171);")

    # if any day button is clicked, reset background color of all buttons
    def resetButtonColor(self):
        self.form.dayGroupBox.setStyleSheet(self.form.dayGroupBox.styleSheet().replace("255,212,212", "255,255,255", 1))

    # hide/show data fields based on selected "join type"
    def toggleRadio(self, state):
        if state:
            self.hideItems(self.form.idLabel, self.form.meetingIDLineEdit, self.form.meetingIDLineEdit, self.form.checkBox, self.form.passLabel, self.form.passcodeLineEdit)
            self.showItems(self.form.meetingLinkLabel, self.form.linkLineEdit)
        else:
            self.hideItems(self.form.meetingLinkLabel, self.form.linkLineEdit)
            self.showItems(self.form.idLabel, self.form.meetingIDLineEdit, self.form.meetingIDLineEdit, self.form.checkBox, self.form.passLabel, self.form.passcodeLineEdit)

    # enable/disable passcode line edit based on checkbox toggle
    def checkBoxToggle(self, state):
        if state == 2:
            self.form.passcodeLineEdit.setEnabled(True)
            self.form.passcodeLineEdit.setStyleSheet("QLineEdit {background-color: rgb(255,255,255);}")
        elif state == 0:
            self.form.passcodeLineEdit.clear()
            self.form.passcodeLineEdit.setEnabled(False)
            self.form.passcodeLineEdit.setStyleSheet("QLineEdit {background-color: rgb(238,238,238);}")

    #### utility functions to hide/show items ####
    def hideItems(self, *args):
        for widget in args:
            widget.hide()
    
    def showItems(self, *args):
        for widget in args:
            widget.show()
    ##############################

    #### WINDOW MOVE FUNCTIONS ####
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
    
    def moveWindow(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
    #############################
    # prevent user from using main window while form window is open, then display form
    def display(self):
        self.setModal(True)
        self.show()
        self.exec_()
        

    