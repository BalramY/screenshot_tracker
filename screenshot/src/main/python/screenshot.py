from PyQt5.QtWidgets import (QVBoxLayout, QLabel,
                             QWidget, QHBoxLayout)
import sys
import os
import subprocess
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QCursor
import pyautogui
import random
import requests
from datetime import datetime
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import importlib


class Window(QtWidgets.QMainWindow):

    def __init__(self, username, time_val, appctxt, token, ip, id):
        super().__init__()
        # setting geometry of main window
        self.Width = 1000
        self.height = int(0.618 * self.Width)
        self.resize(self.Width, self.height)
        # self.resize(400, 200)
        # self.setFixedSize(400, 200)
        self.setStyleSheet("background: white")
        self.state = False
        # set ip address
        self.ip = ip
        # set token value for calling api
        self.token = token
        # set timer value
        self.time_val = time_val
        # set id value
        self.id = id
        self.key_count = 0
        self.end = False
        # set username value
        self.username = username

        self.set_time = 10

        self.time_interval = int(self.set_time / 2)
        self.sequence = [i*2 for i in range(1, self.time_interval)]
        # hour array for calling image upload api at diffrence of 5 minute
        self.hours = [hour*5 for hour in range(1, 13)]
        # subtract 1 from last value of hour array
        self.hours[11] = self.hours[11] - 1
        print(self.hours)
        hr = int(self.time_val.split(':')[0])
        self.min = minute = int(self.time_val.split(':')[1])
        sec = int(self.time_val.split(':')[2])
        # set hour, minute and second value in timer object
        self.time = QtCore.QTime(hr, minute, sec)
        self.max = int(self.min) + self.set_time - 1
        if self.max > 59:
            self.max = self.max - 60
        print('min', self.min, 'max', self.max)
        # set value of appctxt for get value of resources
        self.appctxt = appctxt
        # set count index for calling image upload api
        if minute != 0:
            try:
                self.count = self.hours.index(list(filter
                                                   (lambda k: k > minute,
                                                    self.hours))[0])
            except IndexError:
                self.count = 0
        else:
            self.count = 0
        # click screenshot interval
        self.click_ss = minute
        self.toggle = True
        self.image_path = []
        self.myScreenshot = ''
        # get random for taking screenshots
        self.counter = random.choice(self.sequence)
        check_min = int(self.time.toString('hh:mm:ss').split(':')[1])
        # initial value for taking screenshots
        self.click_ss = check_min + self.counter
        # check screenshot value > 59
        if self.click_ss > 59:
            self.click_ss = self.counter
        print(self.click_ss)
        self.close_app = False
        self.empty_call = False
        # show application view
        self.startMethod()
        self.UiComponents()

        # showing all the widgets
        self.show()

    # method called by timer
    def showTime(self):
        """getting current time and take screenshot at
           random time interval """
        global time, state
        if self.state:
            self.time = self.time.addSecs(1)
            check_min = int(self.time.toString('hh:mm:ss').split(':')[1])
            # check current minute value and screenshot min value for taking
            # screenshots
            if check_min == self.click_ss:
                package_name = 'pyautogui'
                spec = importlib.util.find_spec(package_name)
                # check pyautogui package is install or not
                if spec is None:
                    # command to install pyautogui
                    subprocess.check_call([sys.executable,
                                           "-m", "pip", "install",
                                           package_name])
                self.myScreenshot = pyautogui.screenshot()
                # if image folder is not exist then create
                if not os.path.exists('image'):
                    os.makedirs('image')
                # save screenshot
                self.myScreenshot.save('image/' + self.username + '-' +
                                       datetime.now().strftime("%H_%M_%p") +
                                       ('-time') + '.png')
                # append image path
                self.image_path.append('image/' + self.username + '-' +
                                       datetime.now().strftime("%H_%M_%p") +
                                       ('-time') + '.png')
                # pick random value for taking screenshots
                self.counter = random.choice(self.sequence)
                self.click_ss = check_min + self.counter
                # check if screenshot min is less than to max value then add
                # some interval
                if self.click_ss < self.max:
                    self.click_ss += self.set_time
                    self.counter += self.set_time
                # re calculate max value
                self.max = int(self.max) + self.set_time
                if self.max > 59:
                    self.max = 0
                print('max', self.max)
                # if click screnshot min is greater than 59 then reinitialize
                # it to 0
                if self.click_ss > 59:
                    self.click_ss = 0
                print(self.click_ss)
                self.key_count = 0
            # check hour minute equal to current minute for calling image
            # upload api
            try:
                if check_min == self.hours[self.count]:
                    # call image upload api
                    self.api_call()
                    print(check_min, self.hours[self.count])
            except IndexError:
                self.count = 0
                print(self.count)

        # converting QTime object to string
        label_time = self.time.toString('hh:mm:ss')

        # showing it to the label
        self.label.setText(label_time)

    def get_csrf(self):
        """method to call api for csrf token"""
        try:
            res = requests.get(self.ip+"/get_csrf_token/")
            resJson = res.json()
            csrftoken = resJson['csrfToken']
            return csrftoken
        except requests.exceptions.RequestException as e:
            print('get_csrf error', e)
            msg = QtWidgets.QErrorMessage()
            msg.showMessage('Connection error')
            msg.exec_()
            self.close()

    def startMethod(self):
        """Method to start or unpause timer"""
        global state
        self.state = True

    def api_call(self):
        """Api call for send all screenshot that will
           capture in last one hour"""
        if not os.path.exists('image'):
            os.makedirs('image')
        self.image_path = list(set(self.image_path))
        print(self.image_path, 'image')
        try:
            csrftoken = self.get_csrf()
            headers = {"X-CSRFToken": csrftoken,
                       'token': self.token,
                       'username': self.username}
            try:
                print('execute')
                file_list = [('image', (path.split('/')[1],
                                        open(path, 'rb'), 'image/png'))
                             for path in self.image_path]
                print(file_list, 'file_list')
                data = {"username": self.username, "image": file_list}
                res = requests.post(self.ip+"/upload_screenshot/",
                                    data=data, files=file_list,
                                    headers=headers, timeout=180)
                print(res.json())
                self.image_path = []
            except (OSError, ValueError) as e:
                print('upload image error', e)
                print('error')
                msg = QtWidgets.QErrorMessage()
                msg.showMessage(str(e))
                msg.exec_()
                self.close_app = True
                self.close()
                self.image_path = []

        except requests.exceptions.RequestException as e:
            msg = QtWidgets.QErrorMessage()
            msg.showMessage('Connection error')
            msg.exec_()
            self.close()

        self.count = self.count + 1
        print('count' + str(self.count))

    def UiComponents(self):
        """layout of window"""
        # creating a vertical layout

        self.setWindowTitle('Monitoring')
        # self.setWindowIcon(QtGui.QIcon(self.appctxt.get_resource('logo.ico')))
        self.layout = QVBoxLayout()
        # creating font object
        font = QFont('Arial', 19, QFont.Bold)
        # label to show employee name
        self.emp_name = QLabel('<font size="4">'+self.username+'</font>')
        self.emp_name.setAlignment(Qt.AlignLeft)
        self.emp_name.setGeometry(QtCore.QRect(20, 70, 101, 5))

        self.label_name = QLabel('<font size="3" color="grey">TODAY</font>')
        self.label_name.setAlignment(Qt.AlignLeft)
        self.label_name.setGeometry(QtCore.QRect(20, 80, 101, 5))

        # creating a label object to show timer value
        self.label = QLabel(self.time_val)

        # setting font to the label
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        # creating start button
        self.startButton = QtWidgets.QPushButton('', self)
        self.startButton.setGeometry(QtCore.QRect(170, 390, 91, 31))
        self.startButton.setIcon(QIcon(self.appctxt.get_resource('start.png')))
        self.startButton.setIconSize(QtCore.QSize(50, 50))
        self.startButton.setStyleSheet("QPushButton{ margin-top: 15px; \
                                        width:50; height: 50px; \
                                        border: 0px;}")
        self.startButton.setFont(font)
        self.startButton.clicked.connect(self.startMethod)
        self.startButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.layout.setContentsMargins(15, 10, 10, 28)

        self.initUI()

    def initUI(self):
        # add elements in layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.emp_name)

        left_layout.addStretch(5)
        left_layout.setSpacing(10)
        left_widget = QWidget()
        left_widget.setFont(QFont('Arial', 13))
        left_widget.setLayout(left_layout)

        # creating a timer object
        timer = QTimer(self)

        # adding action to timer
        timer.timeout.connect(self.showTime)

        # update the timer every second
        timer.start(1000)

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.setStretch(0, 40)
        main_layout.setStretch(1, 200)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setWindowState(Qt.WindowMaximized)
        self.setCentralWidget(main_widget)

    def closeEvent(self, event):
        # Show pop up for exit from application
        exit_msg = "Are you sure you want to exit ?"
        result = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                exit_msg,
                                                QtWidgets.QMessageBox.Yes |
                                                QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            # call image upload api for rest images upload on server
            self.api_call()

            # if their is an error in upload image api then close application
            if self.close_app:
                event.accept()
            # logout api calling
            try:
                csrftoken = self.get_csrf()
                headers = {"X-CSRFToken": csrftoken,
                           'token': self.token,
                           'username': self.username}
                data = {"username": self.username}
                res = requests.post(self.ip+"/logout/",
                                    data=data, headers=headers)
                self.state = False
                folder_path = ('image')
                test = os.listdir(folder_path)
                # delete all images when employee exit from application
                for images in test:
                    if images.endswith(".png"):
                        os.remove(os.path.join(folder_path, images))
                try:
                    print(res.json())
                except ValueError:
                    print("Error")
            except requests.exceptions.RequestException as e:
                print('logout error', e)
            event.accept()


if __name__ == '__main__':

    # create pyqt5 app
    # App = QApplication(sys.argv)
    appctxt = ApplicationContext()
    appctxt.app.setApplicationName("Monitor")
    # create the instance of our Window
    window = Window('balram.wangoes@gmail.com', '00:00:00',
                    appctxt, token, ip, id)

    # showing all the widgets
    window.show()

    # start the app
    App.exit(appctxt.app.exec_())
