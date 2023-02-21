import os
import threading
import serial
import time
import sys
import random
from PySide6.QtCore import QStandardPaths, Qt, Slot, QUrl
from PySide6.QtGui import QAction, QIcon, QKeySequence, QScreen
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
                               QMainWindow, QSlider, QStyle, QToolBar)
from PySide6.QtMultimedia import (QAudio, QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui_window import Ui_Form
from PySide6.QtMultimedia import (QCamera, QImageCapture,
                                  QCameraDevice, QMediaCaptureSession,
                                  QMediaDevices, QMediaRecorder)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.start)
        self.ui.pushButton_2.clicked.connect(self.end)

        # 数据采集
        self.t = None

        # 视频播放
        self.player = QMediaPlayer()
        self.player.errorOccurred.connect(self._player_error)
        self.player.setVideoOutput(self.ui.widget)

        # 摄像头捕捉
        available_cameras = QMediaDevices.videoInputs()
        self._capture_session = None
        self.recorder = QMediaRecorder()
        if available_cameras:
            self._camera_info = available_cameras[0]
            self._camera = QCamera(self._camera_info)
            self._camera.errorOccurred.connect(self._camera_error)
            self._image_capture = QImageCapture(self._camera)
            self._capture_session = QMediaCaptureSession()
            self._capture_session.setCamera(self._camera)
            self._capture_session.setImageCapture(self._image_capture)
            self._capture_session.setRecorder(self.recorder)

        if self._camera and self._camera.error() == QCamera.NoError:
            self._capture_session.setVideoOutput(self.ui.widget_2)
            self._camera.start()
            print(os.getcwd())
            self.recorder.setOutputLocation(
                "%s/%f.mp4" % (os.getcwd(), time.time()))

    @Slot()
    def start(self):
        self.player.setSource("test.mp4")
        self.player.play()
        self.recorder.record()
        self.t = threading.Thread(target=self.gather, args=(
            "/dev/tty.usbserial-14310", 115200))
        self.t.start()

    @Slot()
    def end(self):
        self.player.stop()
        self.recorder.stop()
        threading.Thread._Thread__stop(self.t)

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, error, file=sys.stderr)

    @Slot(QCamera.Error, str)
    def _camera_error(self, error, error_string):
        print(error_string, file=sys.stderr)

    def gather(self, device, rate):
        # serialPort = "/dev/tty.usbserial-14310"
        # baudRate = 115200
        serialPort = device
        baudRate = rate
        ser = serial.Serial(serialPort, baudRate)
        ser.flushInput()

        while True:
            count = ser.inWaiting()
            if count != 0:
                recv = ser.read(ser.in_waiting).decode("gbk")
                print(recv)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
