from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QApplication, QMainWindow
from PyQt5.QtCore import QPoint, QSize, Qt, pyqtSlot

class PopMenu(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selectedCourse = None

        self.setMaximumSize(QSize(110,90))
        self.setMinimumSize(QSize(110,90))
        self.setStyleSheet("""QFrame{
                                background-color: #2D2D2D;
                                color: #ffffff;
                                font-size: 16px;
                                border-radius: 3px;}
                                
                                QPushButton {
                                    background: none;
                                    border: none;
                                    font: bold 16px Lato;
                                    color: #ffffff;}
                                    
                                QPushButton:hover {
                                    background-color: #3E3E3E;
                                    font: bold 16px Lato;
                                    color: #ffffff;
                                    border-radius: 3px;}""")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignHCenter)
        layout.setContentsMargins(5,5,5,7)
        layout.setSpacing(0)

        minSize = QSize(100,40)
        editBtn = QPushButton("Edit")
        editBtn.setCursor(Qt.PointingHandCursor)
        editBtn.setMinimumSize(minSize)
        deleteBtn = QPushButton("Delete")
        deleteBtn.setCursor(Qt.PointingHandCursor)
        deleteBtn.setMinimumSize(minSize)
        
        layout.addWidget(editBtn)
        layout.addWidget(deleteBtn)

        # connect buttons to functions
        deleteBtn.clicked.connect(self.deleteSelectedCourse)
        editBtn.clicked.connect(self.editSelectedCourse)

    @pyqtSlot(QPoint)
    def displayMenu(self, pos):
        self.selectedCourse = self.sender()
        self.move(pos)
        self.show()

    def deleteSelectedCourse(self):
        self.hide()
        self.selectedCourse.deleteCourse()
        
    def editSelectedCourse(self):
        self.hide()
        self.selectedCourse.editCourse()


if __name__ == "__main__":
    app = QApplication([])
    window = QMainWindow()
    window.resize(500,500)
    menu = PopMenu()
    window.setCentralWidget(menu)

    window.show()
    app.exec_()


        

