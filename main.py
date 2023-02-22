import csv
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


class CanStopTask:
    def __init__(self, device, rate, startTime):
        self._running = True
        serialPort = device
        baudRate = rate
        self.startTime = startTime
        self.ser = serial.Serial(serialPort, baudRate)
        self.ser.flushInput()

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            count = self.ser.inWaiting()
            if count != 0:
                recv = self.ser.read(self.ser.in_waiting).decode("gbk")
                with open("%s/output/%f.csv" % (os.getcwd(), self.startTime), 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([recv, time.time()-self.startTime])


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.basePath = os.getcwd()

        # 初始化界面
        self.ui.pushButton.clicked.connect(self.start)
        files = [f for f in os.listdir(
            self.basePath+"/video") if not f.startswith('.')]
        self.ui.comboBox.addItems(files)

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

    @Slot()
    def start(self):
        if self.ui.pushButton.text() == "start":
            self.player.setSource(
                self.basePath+"/video/"+self.ui.comboBox.currentText())
            self.player.play()
            startTime = time.time()
            self.recorder.setOutputLocation(
                "%s/output/%f.mp4" % (self.basePath, startTime))
            self.recorder.record()
            device = self.ui.lineEdit.text() if self.ui.lineEdit.text(
            ) != "" else "/dev/tty.usbserial-14310"
            rate = self.ui.lineEdit_2.text() if self.ui.lineEdit_2.text() != "" else 115200
            self.task = CanStopTask(device, rate, startTime)
            threading.Thread(target=self.task.run).start()
            self.ui.pushButton.setText("stop")
        else:
            self.player.stop()
            self.recorder.stop()
            self.task.terminate()
            self.ui.pushButton.setText("start")

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, error, file=sys.stderr)

    @Slot(QCamera.Error, str)
    def _camera_error(self, error, error_string):
        print(error_string, file=sys.stderr)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
