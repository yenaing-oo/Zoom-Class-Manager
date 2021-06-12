from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import pyqtSlot, QPoint, Qt
from PyQt5.QtGui import QFontDatabase, QIcon
import sys
import resources_rc

from ui_main import Ui_MainWindow
from ui_functions import *
from form import NewForm

myappid = 'yenoo.ZoomClassManager.V1'
try:
    # targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QFontDatabase.addApplicationFont(":/fonts/lato")
        QFontDatabase.addApplicationFont(":/fonts/latoBold")
        QFontDatabase.addApplicationFont(":/fonts/moon")
        QFontDatabase.addApplicationFont(":/fonts/moonBold")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set title bar to movable window
        self.ui.title_bar.mouseMoveEvent = self.moveWindow

        # cause double click on taskbar to maximize/restore
        self.ui.title_bar.mouseDoubleClickEvent = self.doubleClickTaskBar

        # Connect to database and retireve connection and cursor objs
        self.con, self.cur = UIFunctions.connect()
        # get current list of courses loaded from database, for easy referencing when inserting into layout
        self.courseList = UIFunctions.sqlLoadData(self)
        # setup the main screen, fill with widgets
        UIFunctions.setupMainScreen(self)


    def moveWindow(self, event):
        # if maximized, when window is dragged, move cursor and window back to restored position
        if UIFunctions.getWindowState() == 1:
            xPosRatio = event.globalX()/self.width()
            yOffset = event.globalY() - self.pos().y() + 8
            UIFunctions.maximizeRestore(self)
            xOffset = int(xPosRatio * self.width())

            self.move(event.globalPos() - QPoint(xOffset, yOffset))

        # if left-click and dragged, and drag point not on any of window buttons, move window
        if event.buttons() == Qt.LeftButton and not (self.ui.btn_maximize.underMouse() or self.ui.btn_minimize.underMouse() or self.ui.btn_close.underMouse()):
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
    
    def doubleClickTaskBar(self, event):
        UIFunctions.maximizeRestore(self)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # get drag position when mouse is clicked
        self.dragPos = event.globalPos()
        # if mouse is clicked when pop-up menu is open, close the pop-up menu
        if event.buttons() == Qt.LeftButton and self.popupMenu.selectedCourse:
            self.popupMenu.hide()

    def displayNewForm(self):
        # Create an instance of a form ready
        self.newForm = NewForm()
        # connect validated signal to function that will receive the data
        self.newForm.validated.connect(self.receiveFormData)
        self.newForm.display()

    @pyqtSlot(dict)
    def receiveFormData(self, dataDict):
        # convert 24 hour times to 12 hour times
        UIFunctions.convertTimeto12(dataDict)
        # insert new course info into database, and get index for widget
        newCourse, index = UIFunctions.insertNewCourse(self, dataDict)
        # if index is greater than the number of items in layout, then it should be added to the bottom
        if index > self.ui.courseFrameLayout.count():
            self.ui.courseFrameLayout.addWidget(newCourse)
        # else, insert at correct position
        else:
            self.ui.courseFrameLayout.insertWidget(index, newCourse)
        self.con.commit()

        # display message
        self.msgBox.display(new=dataDict["courseName"])
        self.msgBox.move(int((self.width() - self.msgBox.width())/2), int(self.height() * 0.85))


    @pyqtSlot(dict)
    def updateCourse(self, dataDict):
        # get course object that requested updated
        courseToUpdate = self.sender()
        # update course info in database, and get new index based on new start time
        newIndex = UIFunctions.sqlUpdateData(self.cur, dataDict)
        # update widget's position in layout
        self.ui.courseFrameLayout.insertWidget(newIndex, courseToUpdate)
        self.con.commit()

        # display message to show course info has been updated
        self.msgBox.display(update=dataDict["courseName"])
        # position message to bottom center of window
        self.msgBox.move(int((self.width() - self.msgBox.width())/2), int(self.height() * 0.85))

    @pyqtSlot(bool)
    def deleteCourse(self):
        # get course which sent signal
        courseToDelete = self.sender()
        # close widget
        courseToDelete.close()
        # remove from course widget list
        self.courseList.remove(courseToDelete)
        # remove course info from database
        UIFunctions.sqlDeleteCourse(self.cur, courseToDelete.courseID)
        self.con.commit()


    def showCopiedMsg(self):
        # display "email copied" popup message, since no parameters provided
        self.msgBox.display()
        # position message to bottom center of window
        self.msgBox.move(int((self.width() - self.msgBox.width())/2), int(self.height() * 0.85))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/icons/appIcon'))
    window = MainWindow()
    window.show()
    app.exec_()
    UIFunctions.close(window.con)