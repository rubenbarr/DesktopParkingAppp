from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from settings import apiUrl, kioscoInfo

import requests
import json



class Screen1Welcome(QWidget):
    def __init__(self, app):
        super().__init__()
        
        self.locationId = None
        self.kioscoId = None
        self.kioscoToken = None
        self.hasChange = None
        self.hasError = False
        self.errorText = ""
        self.app = app
        self._already_triggered = False
        self.setStyleSheet("background-color: #ffffff;")
        
        with open(kioscoInfo, "r") as f:
            data = json.load(f)
            self.kioscoId = data.get('kioscoId')
            self.locationId = data.get('locationId')
            self.kioscoToken = data.get('kioscoToken')
            self.hasChange = data.get('hasChange', False)
            
    
        
        if not self.hasChange:
            self.hasError = True
            self.errorText = "El kiosco no cuenta con cambio"
        else:
            self.hasError = False
            self.errorText = ""
                 
        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)

        self.MainTitle = QLabel("Bienvenido, para pagar tu boleto escanea el QR")
        self.MainTitle.setFont(QFont("Arial", 28))
        self.MainTitle.setAlignment(Qt.AlignCenter)
        
        self.errorLabel = QLabel(self.errorText)
        self.errorLabel.setFont(QFont("Arial", 20))
        self.errorLabel.setStyleSheet('color: red;')
        self.errorLabel.setAlignment(Qt.AlignCenter)
        
        if not self.hasError:
            self.errorLabel.hide()
        else: self.errorLabel.show()
            

        self.loadingTitle = QLabel("Obteniendo Información")
        self.loadingTitle.setFont(QFont("Arial", 28))
        self.loadingTitle.setAlignment(Qt.AlignCenter)
        

        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)


        self.qr_img = QLabel()
        self.qr_img.setPixmap(QPixmap("assets/qrCodeHelpImage.png").scaled(400, 600, Qt.KeepAspectRatio))
        self.qr_img.setAlignment(Qt.AlignCenter)


        self.qr_input = QLineEdit()
        self.qr_input.setPlaceholderText("qrCode")
        self.qr_input.textChanged.connect(self.handle_text_change)
        self.qr_input.setFixedHeight(30)
        
        self.spinnerIcon = QLabel()
        loadingIcon = QMovie("assets/loadingIcon.gif")
        loadingIcon.setScaledSize(QSize(200,200))
        self.spinnerIcon.setMovie(loadingIcon)
        loadingIcon.start()
        self.spinnerIcon.setAlignment(Qt.AlignCenter)


        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.MainTitle)
        outer_layout.addWidget(self.errorLabel)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.qr_img)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.qr_input)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.loadingTitle)
        outer_layout.addWidget(self.spinnerIcon)
        self.qr_img.show()
        self.spinnerIcon.hide()
        self.loadingTitle.hide()
        outer_layout.setAlignment(Qt.AlignTop)
        self.setLayout(outer_layout)
        
        
    def handle_text_change(self):
        text = self.qr_input.text()
        ticketId = text.replace("'","-")
        if len(text) >=38:
            if 'm&' in text:
                mticket = text.split("m&")
                self.validateTicket(mticket[1], True)
            elif 'm/' in text:
                mticket = text.split("m/")
                qr = mticket[1].replace("'", '-')
                print(qr)
                self.validateTicket(qr, True)
                
            else:
                self.validateTicket(ticketId, False)
         
    def validateTicket(self, ticket:str, isMaintenance):
            self.qr_img.hide()
            self.MainTitle.hide()
            self.errorLabel.hide()
            self.spinnerIcon.show()
            self.loadingTitle.show()
            if isMaintenance:               
                self.worker = MTicketVal(ticket, self.locationId, self.kioscoToken, self.kioscoId)
                self.worker.done.connect(self.onSuccessMaintenanceTicket)
                self.worker.failed.connect(self.onError)
                self.worker.start()
            else:
                self.worker = TicketValidator(ticket, self.locationId, self.kioscoToken, self.kioscoId)
                self.worker.done.connect(self.onSuccess)
                self.worker.failed.connect(self.onError)
                self.worker.start()
            self.qr_input.clear()
    
    def onSuccessMaintenanceTicket(self, data):
        self.qr_img.show()
        self.MainTitle.show()
        self.errorLabel.show()
        self.spinnerIcon.hide()
        self.loadingTitle.hide()
        self.handleMticketData(data)
    
    def onSuccess(self, data):
        self.qr_img.show()
        self.MainTitle.show()
        self.errorLabel.hide()
        self.spinnerIcon.hide()
        self.loadingTitle.hide()
        self.handleTicketData(data)
        
    def onError(self, data):
        print('Error obteniendo datos del ticket, data:', data)
        self.qr_img.show()
        self.MainTitle.show()
        self.spinnerIcon.hide()
        self.loadingTitle.hide()
        self.app.go_to(2)
    
    def handleTicketData(self, data):
            estado = data.get("estado", False)
            tolerancia = data.get('tolerancia', False)
            tiempo_restante = data.get('tiempo_restante', 0)
            if estado == "pagado":
                return self.app.goToErrorPage('Este Boleto ya está pagado', 'error',  data)
            if tolerancia:
                return self.app.goToErrorPage(f'Cuenta con {tiempo_restante} minutos para salir', 'alert', data)
            if estado == "pendiente":
                return self.app.pass_data_to_screen_3(data) 
            if not estado:
                return self.app.goToErrorPage(data.get('message', 'Hubo un error intente más tarde o solicite ayuda'), 'error',  data)
            else:
                self.app.go_to(2) 
                
    def handleMticketData(self, data):
        state = data.get('state', False)
        if state:
            self.app.gotToMaintenancePage(data)
        else:
            self.app.go_to(2) 
            

class TicketValidator(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)
    
    def __init__(self, ticketId, location, token, kioscoId):
        super().__init__()
        self.TicketId = ticketId
        self.locationId = location
        self.token = token
        self.kioscoId = kioscoId        
    def run(self):
        try: 
            headers = { 'locationId': self.locationId, 'kioscoToken': self.token, 'kioscoId': self.kioscoId}
            req = requests.post(f"{apiUrl}/api/ticketRoute/checkTicket/{self.TicketId}", headers=headers)
            
            self.done.emit(req.json())
        except Exception as e:
            self.failed.emit(str(e))
    
class MTicketVal(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)
    
    def __init__(self, ticketId, location, token, kioscoId):
        super().__init__()
        self.TicketId = ticketId
        self.locationId = location
        self.token = token
        self.kioscoId = kioscoId        
    def run(self):
        try: 
            headers = { 'locationId': self.locationId, 'kioscoToken': self.token, 'kioscoId': self.kioscoId}
            payload = {}
            req = requests.get(f"{apiUrl}/api/qr_request/activate/{self.TicketId}", headers=headers, json= payload)
            print(req)
            self.done.emit(req.json())
        except Exception as e:
            self.failed.emit(str(e))
    
                
                