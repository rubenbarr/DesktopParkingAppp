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
        
        self.data = {}
        self.ticketId  = ""
        
        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)

        self.errorMessage = "Ups! Hubo un error, intente nuevamente, si el error persiste comuniquese con la administración"
        self.titleLabel = QLabel(self.errorMessage)
        self.titleLabel.setFont(QFont("Arial", 28))
        self.titleLabel.setAlignment(Qt.AlignCenter)

        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)
        
        errorGifMovie = QMovie("assets/error.gif")
        errorGifMovie.setScaledSize(QSize(200,200))
        errorGifMovie.start()
        self.errorGifLabel = QLabel()
        self.errorGifLabel.setMovie(errorGifMovie)
        self.errorGifLabel.setAlignment(Qt.AlignCenter)
        self.errorGifLabel.hide()
        
        okGifMovie = QMovie("assets/ok.gif")
        okGifMovie.setScaledSize(QSize(200,200))
        okGifMovie.start()
        self.okGifLabel = QLabel()
        self.okGifLabel.setMovie(errorGifMovie)
        self.okGifLabel.setAlignment(Qt.AlignCenter)
        self.okGifLabel.hide()
        alertMovieGif = QMovie("assets/alert.gif")
        alertMovieGif.setScaledSize(QSize(200,200))
        alertMovieGif.start()
        self.alertGifLabel = QLabel()
        self.alertGifLabel.setMovie(alertMovieGif)
        self.alertGifLabel.setAlignment(Qt.AlignCenter)
        self.alertGifLabel.hide()
        
        button = QPushButton('Intentar nuevo ticket')
        button.setFixedHeight(40)
        button.setStyleSheet("""
                    QPushButton {
                        font-size: 20px;
                        background-color: #086972;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 50px;
                    }
                    QPushButton:pressed {
                        background-color: #055056; 
                    }
                """)
        button.clicked.connect(self.goToStart)
        
        self.payButton = QPushButton('Pagar Ticket')
        self.payButton.setFixedHeight(45)
        self.payButton.setStyleSheet("""
                    QPushButton {
                        font-size: 20px;
                        background-color: #086972;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 50px;
                    }
                    QPushButton:pressed {
                        background-color: #055056; 
                    }
                """)
        self.payButton.clicked.connect(self.goToPay)
        self.payButton.hide()
        
        self.payTicketLabel = "¿Desea pagar el ticket?"
        self.payTicketLabel = QLabel(self.payTicketLabel)
        self.payTicketLabel.setFont(QFont("Arial", 25))
        self.payTicketLabel.setAlignment(Qt.AlignCenter)
        self.payTicketLabel.hide()

             
        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.titleLabel)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.errorGifLabel)
        outer_layout.addWidget(self.okGifLabel)
        outer_layout.addWidget(self.alertGifLabel)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.payTicketLabel)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.payButton, alignment=Qt.AlignCenter)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(button, alignment=Qt.AlignCenter)

        outer_layout.setAlignment(Qt.AlignTop)

        self.setLayout(outer_layout)
        
    def goToStart(self):
        self.app.go_to(0)
    def goToPay(self):
        self.app.pass_data_to_screen_3(self.data)
            
    def handleErrorMessage(self, errorMessage:str = "Ups, intente más tarde", errorType:str='ok' , data:any =[]):
        self.errorMessage = errorMessage
        self.data = data
        self.ticketId = data.get('ticketId', "") if 'ticketId' in data else ""
        if errorType == 'ok':
            self.okGifLabel.show()
        elif errorType == 'error':
            self.errorGifLabel.show()
        elif errorType == "alert":
            self.alertGifLabel.show()
            self.payTicketLabel.show()
            self.payButton.show()
        self.titleLabel.setText(self.errorMessage)
        self.app.go_to(2)
