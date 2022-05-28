import json

import pyqtgraph as pg
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow

from PyQt5 import uic


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.change_operation = None
        uic.loadUi('architecture.ui', self).show()

        self.socket = QTcpSocket(self)
        self.socket.readyRead.connect(self.on_socket_ready)
        self.socket.connected.connect(self.on_socket_connected)
        self.socket.error.connect(self.on_socket_error)

        self.start_sin_button.clicked.connect(self.on_click_start_sin_button)
        self.start_cos_button.clicked.connect(self.on_click_start_cos_button)
        self.start_random_button.clicked.connect(self.on_click_start_random_button)
        self.connect_server_button.clicked.connect(self.on_click_connect_server_button)
        self.start_graph_button.clicked.connect(self.on_click_start_graph_button)
        self.stop_graph_button.clicked.connect(self.on_click_stop_graph_button)

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_x = []
        self.data_y = []
        self.graph_line = self.graphWidget.plot(self.data_x, self.data_y, pen=pen)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.on_timer_tick)

    def on_timer_tick(self):
        socket_state = self.socket.state()
        if socket_state != QAbstractSocket.ConnectedState:
            self.statusbar.showMessage('Conexion no realizada')
            self.timer.stop()
            return

        if self.change_operation is not None:
            self.socket.writeData(json.dumps({'command': 'change_operation', 'operation': self.change_operation}).encode())
            self.change_operation = None
            return

        self.socket.writeData(json.dumps({'command': 'get_value'}).encode())

    def update_graph(self, new_y):
        self.data_x.append(len(self.data_x))
        self.data_y.append(new_y)
        self.graph_line.setData(self.data_x, self.data_y)
        print(self.data_x)
        print(self.data_y)
        self.graphWidget.autoRange()

    def on_socket_ready(self):
        print("on_socket_ready")
        msg_str = self.socket.readAll().data().decode()
        print("Client Message:", msg_str, len(msg_str))

        message = json.loads(msg_str)
        print(message['log'])
        if message['response'] == 'get_value':
            self.update_graph(message['value'])

    def on_socket_error(self, error):
        print("on_socket_error")
        print(error)
        print(self.socket.errorString())
        self.statusbar.showMessage('Hubo un error con la conexion')

    def on_socket_connected(self):
        print('on_socket_connected')
        # self.socket.writeData(json.dumps({'command': 'get_value'}).encode())
        self.statusbar.showMessage('Conexion al servidor exitosa')

    def on_click_connect_server_button(self):
        self.statusbar.showMessage('Conectando al servidor ...')
        self.socket.connectToHost('127.0.0.1', 65439)

    def on_click_start_graph_button(self):
        self.timer.start()

    def on_click_stop_graph_button(self):
        self.timer.stop()

    def on_click_start_sin_button(self):
        self.change_operation = 'sin'

    def on_click_start_cos_button(self):
        self.change_operation = 'cos'

    def on_click_start_random_button(self):
        self.change_operation = 'random'


app = QApplication(sys.argv)

w = MainWindow()
w.show()

sys.exit(app.exec_())
