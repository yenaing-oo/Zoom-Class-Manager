from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import QSize, Qt, QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve
from PyQt5.QtGui import QFont

class MessageBox(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(300, 40))

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("""QFrame{
                                background-color: #2D2D2D;
                                color: #ffffff;
                                border-radius: 10px;}""")
        font = QFont("Lato", 11)
        font.setBold(True)
        self.label = QLabel()
        self.label.setFont(font)
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)

    def display(self, **kwargs):
        """
        Set message to display, based on passed in arguments
        """
        if 'new' in kwargs:
            self.label.setText(f"New course: \"{kwargs['new']}\" added")
        elif 'update' in kwargs:
            self.label.setText(f"Course: \"{kwargs['update']}\" updated")
        else:
            self.label.setText("Email copied to clipboard")
        
        self.label.adjustSize()

        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self.fadeInAnim = QPropertyAnimation(effect, b'opacity')
        self.fadeInAnim.setStartValue(0)
        self.fadeInAnim.setEndValue(1)
        self.fadeInAnim.setDuration(1500)

        self.fadeOutAnim = QPropertyAnimation(effect, b"opacity")
        self.fadeOutAnim.setStartValue(1)
        self.fadeOutAnim.setEndValue(0)
        self.fadeOutAnim.setDuration(1500)

        self.fadeInAnim.setEasingCurve(QEasingCurve.InQuad)
        self.fadeOutAnim.setEasingCurve(QEasingCurve.OutQuad)

        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(self.fadeInAnim)
        self.anim_group.addPause(2000)
        self.anim_group.addAnimation(self.fadeOutAnim)

        self.show()
        self.anim_group.start()



        
        




        

