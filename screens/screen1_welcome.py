from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import time

class Screen1Welcome(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._already_triggered = False
        self.setStyleSheet("background-color: #ffffff;")
        
                 
        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)

        title = QLabel("Bienvenido, escanee el QR para pagar")
        title.setFont(QFont("Arial", 28))
        title.setAlignment(Qt.AlignCenter)

        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)


        qr_img = QLabel()
        qr_img.setPixmap(QPixmap("assets/qrCodeHelpImage.png").scaled(400, 600, Qt.KeepAspectRatio))
        qr_img.setAlignment(Qt.AlignCenter)


        self.qr_input = QLineEdit()
        self.qr_input.setPlaceholderText("qrCode")
        self.qr_input.textChanged.connect(self.handle_text_change)
        # self.qr_input.setFixedHeight(0)
        


        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(title)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(qr_img)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.qr_input)

        outer_layout.setAlignment(Qt.AlignTop)

        self.setLayout(outer_layout)
        
        
    def handle_text_change(self):
        text = self.qr_input.text()
        if len(text) >= 36:
            self.qr_input.clear()
            self.app.pass_data_to_screen_2(text)