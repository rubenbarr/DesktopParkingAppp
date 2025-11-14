from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize
import requests
from settings import apiUrl


class Screen2ValidatingTicket(QWidget):
    def __init__(self, app):
        super().__init__()
        
        self.app = app

        self.setStyleSheet("background-color: #ffffff;")
        
        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)

        title = QLabel("Validando Información")
        title.setFont(QFont("Arial", 28))
        title.setAlignment(Qt.AlignCenter)

        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)

        spinnerIcon = QLabel()
        iconMovie = QMovie("assets/loadingIcon.gif")
        iconMovie.setScaledSize(QSize(200,200))
        spinnerIcon.setMovie(iconMovie)
        iconMovie.start()
        spinnerIcon.setAlignment(Qt.AlignCenter)

        # button = QPushButton('Intentar Nuevamente')
        # button.setFixedHeight(40)
        # button.setStyleSheet("font-size: 20px; background-color: #086972; color: white;border: none; border-radius: 5px; ")
        # button.clicked.connect(self.goToStart)

        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(title)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(spinnerIcon)

        outer_layout.setAlignment(Qt.AlignTop)

        self.setLayout(outer_layout)
        
    def get_ticket_data(self, data:str):
        qrCode = data.replace("'","-")
        self.validateTicket(qrCode)
            
    def validateTicket(self, ticket: str):
        try:
            req = requests.post(f"{apiUrl}/api/ticketRoute/checkTicket/{ticket}")
            data = req.json()
            estado = data.get("estado", False)
            tolerancia = data.get('tolerancia', False)
            tiempo_restante = data.get('tiempo_restante', 0)
            if req.status_code == 200:
                if estado == "pagado":
                    return self.app.goToErrorPage('Este Boleto ya está pagado', 'error',  data)
                if tolerancia:
                    return self.app.goToErrorPage(f'Cuenta con {tiempo_restante} minutos para salir', 'alert', data)
                if estado == "pendiente":
                    return self.app.pass_data_to_screen_3(data, ticket) 
                if not estado:
                    return self.app.goToErrorPage(data.get('message', 'Hubo un error intente más tarde o solicite ayuda'), 'error',  data)
            else:
                self.app.go_to(2) 
        except Exception as e:
            print("Hubo un error: " + str(e))
            self.app.go_to(2)


    def goToStart(self):
        try:            
            self.app.go_to(2)
        except Exception as e:
            print(f"Hubo un error al pasar de pantalla error: {str(e)}")
                    
    def goToPayment(self):
        self.app.go_to(3)   