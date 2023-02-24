import csv
import os
import threading
import serial
import time
import sys
import socket
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
        _udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        address = ("127.0.0.1", 1347)
        while self._running:
            count = self.ser.inWaiting()
            if count != 0:
                recv = self.ser.read(self.ser.in_waiting)
                with open(os.path.join(os.getcwd(), "output", str(int(self.startTime))+".csv"), 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([recv, time.time()-self.startTime])
                    _udp.sendto(recv, address)
        _udp.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.basePath = os.getcwd()

        # 初始化界面
        self.ui.pushButton.clicked.connect(self.start)
        files = [f for f in os.listdir(
            os.path.join(self.basePath, "video")) if not f.startswith('.')]
        self.ui.comboBox.addItems(files)

        # 视频播放
        self.player = QMediaPlayer()
        self.player.errorOccurred.connect(self._player_error)
        self.player.setVideoOutput(self.ui.widget)

        # 摄像头捕捉
        available_cameras = QMediaDevices.videoInputs()
        self._capture_session = None
        self.recorder = QMediaRecorder()
        self.recorder.errorOccurred.connect(self._recorder_error)
        self.recorder.recorderStateChanged.connect(self.recorderStateChanged)
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
            startTime = time.time()

            device = self.ui.lineEdit.text() if self.ui.lineEdit.text(
            ) != "" else "/dev/tty.usbserial-14310"
            rate = self.ui.lineEdit_2.text() if self.ui.lineEdit_2.text() != "" else 115200
            self.task = CanStopTask(device, rate, startTime)
            # threading.Thread(target=self.task.run).start()

            path = os.path.join(self.basePath, "output",
                                str(int(startTime))+".mp4")
            self.recorder.setOutputLocation(QUrl.fromLocalFile(path))
            self.recorder.record()
            # threading.Thread(target=self.recorder.record).start()

            videoPath = os.path.join(
                self.basePath, "video", self.ui.comboBox.currentText())
            self.player.setSource(QUrl.fromLocalFile(videoPath))
            self.player.play()

            self.ui.pushButton.setText("stop")
        else:
            self.player.stop()
            self.recorder.stop()
            self.task.terminate()
            self.ui.pushButton.setText("start")

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, error, file=sys.stderr)
        sys.exit()

    @Slot(QCamera.Error, str)
    def _camera_error(self, error, error_string):
        print(error_string, file=sys.stderr)

    @Slot(QMediaRecorder.Error, str)
    def _recorder_error(self, error, error_string):
        print(error_string, error, file=sys.stderr)
        sys.exit()

    def recorderStateChanged(self, state):
        if state == QMediaRecorder.RecordingState:
            self.task.startTime = time.time()
            threading.Thread(target=self.task.run).start()
            print(time.time())
        elif state == QMediaRecorder.StoppedState:
            self.task.terminate()
            print(time.time())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
