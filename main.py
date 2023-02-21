import serial
import time
import sys
import random
from PySide6.QtCore import QStandardPaths, Qt, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence, QScreen
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
                               QMainWindow, QSlider, QStyle, QToolBar)
from PySide6.QtMultimedia import (QAudio, QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui_window import Ui_Form
import ffmpeg
from PySide6.QtMultimedia import (QCamera, QImageCapture,
                                  QCameraDevice, QMediaCaptureSession,
                                  QMediaDevices)

# serialPort="/dev/tty.usbserial-14310"
# baudRate = 115200
# ser=serial.Serial(serialPort,baudRate)
# ser.flushInput()

# while True:
#     count = ser.inWaiting()
#     if count!=0:
#         recv=ser.read(ser.in_waiting).decode("gbk")
#         print(recv)

# class MyWidget(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()

#        self.player1=QMediaPlayer()

#     @QtCore.Slot()
#     def magic(self):
#         self.text.setText(random.choice(self.hello))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 视频播放
        self.player = QMediaPlayer()
        self.player.errorOccurred.connect(self._player_error)
        self.player.setVideoOutput(self.ui.widget)
        self.ui.pushButton.clicked.connect(self.start)

        # 摄像头捕捉
        available_cameras = QMediaDevices.videoInputs()

    @Slot()
    def start(self):
        self.player.setSource("test.mp4")
        self.player.play()
        print('start play')

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, error, file=sys.stderr)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
