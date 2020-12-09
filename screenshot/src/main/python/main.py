from PyQt5.QtWidgets import (QApplication)
from screenshot import *
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys
import requests


if __name__ == '__main__':
    appctxt = ApplicationContext()
    app = QApplication(sys.argv)
    app.setApplicationName("Monitor")
    # ip address for calling api
    ip = "https://176c7822f87e.ngrok.io"
    # server ip address
    # ip = "https://emptracker.wangoes.com"
    msg = QtWidgets.QErrorMessage()
    try:
        res = requests.get(ip+"/get_csrf_token/")
        resJson = res.json()
        csrftoken = resJson['csrfToken']
    except requests.exceptions.RequestException as e:
        print('get_csrf error', e)
    data = {"username": 'balram.wangoes@gmail.com',
            "password": '1234567@'}
    headers = {"X-CSRFToken": csrftoken}
    try:
        login_res = requests.post(ip + "/user_login/",
                                  data=data, headers=headers, timeout=10)
        print(login_res.json())
        login_res = login_res.json()
        token = login_res['token']
        id = login_res['id']
        ui = Window('balram.wangoes@gmail.com', '00:00:00', appctxt, token,
                    ip, id)
        ui.show()
    except Exception as e:
        print(e)

    sys.exit(appctxt.app.exec_())
