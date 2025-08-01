from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize
import requests
from settings import apiUrl


class Screen2FErrorWhileCheckingTicket(QWidget):
    def __init__(self, app):
        
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #ffffff;")
        
        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)

        title = QLabel("Ups! Hubo un error, intente nuevamente, si el error persiste, intente más tarde.")
        title.setFont(QFont("Arial", 28))
        title.setAlignment(Qt.AlignCenter)

        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)
        
        qr_img = QLabel()
        qr_img.setPixmap(QPixmap("assets/warning_icon.png").scaled(400, 600, Qt.KeepAspectRatio))
        qr_img.setAlignment(Qt.AlignCenter)
        
        button = QPushButton('Intentar Nuevamente')
        button.setFixedHeight(40)
        button.setStyleSheet("font-size: 20px; background-color: #086972; color: white;border: none; border-radius: 5px; ")
        button.clicked.connect(self.goToStart)

             
        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(title)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(qr_img)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(button)

        outer_layout.setAlignment(Qt.AlignTop)

        self.setLayout(outer_layout)
        
    def goToStart(self):
        self.app.go_to(0)   
        
