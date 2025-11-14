
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
import requests
from settings import apiUrl, kioscoInfo
import json



# qrActivationStructure = activationKey&locationId}&kioskId

class DefaultScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #ffffff;")
        
        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)
        
        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)
        

        self.MainTitle = QLabel("Este Kiosco no ha sido activado, escanee el codigo de activación para habilitar Kiosco")
        self.MainTitle.setFont(QFont("Arial", 28))
        self.MainTitle.setAlignment(Qt.AlignCenter)



        self.qr_img = QLabel()
        self.qr_img.setPixmap(QPixmap("assets/qrCodeHelpImage.png").scaled(400, 600, Qt.KeepAspectRatio))
        self.qr_img.setAlignment(Qt.AlignCenter)


        self.activation_code_input = QLineEdit()
        self.activation_code_input.setPlaceholderText("Ingresar codigo  de activación")
        self.activation_code_input.textChanged.connect(self.handle_text_change)
        self.activation_code_input.setFixedHeight(0)
        
        self.loadingTitle = QLabel("Activando Kiosco")
        self.loadingTitle.setFont(QFont("Arial", 28))
        self.loadingTitle.setAlignment(Qt.AlignCenter)
        
        self.spinnerIcon = QLabel()
        loadingIcon = QMovie("assets/loadingIcon.gif")
        loadingIcon.setScaledSize(QSize(200,200))
        self.spinnerIcon.setMovie(loadingIcon)
        loadingIcon.start()
        self.spinnerIcon.setAlignment(Qt.AlignCenter)
        
        self.errorMessage = "Ups! Hubo un error, intente nuevamente, si el error persiste, conctacte a soporte técnico."
        self.titleLabel = QLabel(self.errorMessage)
        self.titleLabel.setFont(QFont("Arial", 28))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        
        errorGifMovie = QMovie("assets/error.gif")
        errorGifMovie.setScaledSize(QSize(200,200))
        errorGifMovie.start()
        self.errorGifLabel = QLabel()
        self.errorGifLabel.setMovie(errorGifMovie)
        self.errorGifLabel.setAlignment(Qt.AlignCenter)
        self.errorGifLabel.show()
        
        self.RetryButton = QPushButton('Intentar Nuevamente')
        self.RetryButton.setFixedHeight(40)
        self.RetryButton.setStyleSheet("""
                    QPushButton {
                        font-size: 20px;
                        background-color: #086972;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 50px;
                    }
                    QPushButton:pressed {
                        background-color: #055056;   /* darker tone */
                    }
                """)
        
        self.RetryButton.clicked.connect(self.retryActivation)
        
        self.goToHome = QPushButton('Intentar Nuevamente')
        self.goToHome.setFixedHeight(40)
        self.goToHome.setStyleSheet("""
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
        self.goToHome.clicked.connect(self.retryActivation)
        
        self.activatedTitle = QLabel("Kiosco Activado Correctamente")
        self.activatedTitle.setFont(QFont("Arial", 28))
        self.activatedTitle.setAlignment(Qt.AlignCenter)
        
        self.GoMainPage = QPushButton('Ir a menu principal')
        self.GoMainPage.setFixedHeight(40)
        self.GoMainPage.setStyleSheet( """
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
        self.GoMainPage.clicked.connect(self.goToMainPage)

        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.MainTitle)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.qr_img)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.activation_code_input)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.loadingTitle)
        outer_layout.addWidget(self.spinnerIcon)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.titleLabel)
        outer_layout.addWidget(self.errorGifLabel)
        outer_layout.addWidget(self.RetryButton)
        outer_layout.addWidget(self.activatedTitle)
        outer_layout.addWidget(self.GoMainPage)
        
        self.qr_img.show()
        self.spinnerIcon.hide()
        self.loadingTitle.hide()
        
        self.titleLabel.hide()
        self.errorGifLabel.hide()
        self.RetryButton.hide()
        self.activatedTitle.hide()
        self.GoMainPage.hide()
        
        outer_layout.setAlignment(Qt.AlignTop)
        self.setLayout(outer_layout)
    
    def handle_text_change(self):
        text = self.activation_code_input.text()
        if len(text) >= 81:
            self.activation_code_input.clear()
            self.validateActivationKey(text)
            
            
    
    def validateActivationKey(self, activationKey:str):
        self.spinnerIcon.show()
        self.loadingTitle.show()
        self.qr_img.hide()
        self.MainTitle.hide()
        
        self.worker = TicketValidator(activationKey)
        self.worker.done.connect(self.onSuccess)
        self.worker.failed.connect(self.onError)
        self.worker.start()

    def onSuccess(self, response):
        self.loadingTitle.hide()
        self.spinnerIcon.hide()
        data = response.get('res', None)

        if data:
            
            state = data.get('state', None)
            message = data.get('message', None)
            kioskoToken = data.get('data', None)
            locationId = response.get('locationId', None)
            kioscoId = response.get('kioscoId', None)
        
            if not state:
                self.qr_img.hide()
                self.MainTitle.hide()
                self.onError(message, False)
            if state:
                self.ActivateKiosco(kioskoToken, locationId, kioscoId)
                self.activatedTitle.show()
                self.GoMainPage.show()
        else: 
            self.onError('Hubo un error,intente nuevamente')

    def goToMainPage(self):
        return self.app.go_to(0)

    def onError(self, msg, default=True):
        
        if not default:
            self.titleLabel.setText(msg)
        else:
            self.titleLabel.setText(self.errorMessage)
        self.spinnerIcon.hide()
        self.loadingTitle.hide()
        self.titleLabel.show()
        self.errorGifLabel.show()
        self.RetryButton.show()
        self.MainTitle.hide()
        
        print("Error:", msg)
        
    def retryActivation(self):
        self.titleLabel.setText(self.errorMessage)
        self.qr_img.show()
        self.MainTitle.show()
        self.titleLabel.hide()
        self.errorGifLabel.hide()
        self.RetryButton.hide()
        return
    
    def ActivateKiosco(self, kioscoToken, locationId, kioscoId):
            with open(kioscoInfo, "r") as r:
                data = json.load(r);
                data['activated'] = True
                data['kioscoToken'] = kioscoToken
                data['locationId'] = locationId
                data['kioscoId'] = kioscoId
            with open(kioscoInfo, "w") as f:
                json.dump(data,f)

class TicketValidator(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, qrCode):
        super().__init__()
        self.qrCode = qrCode

    def run(self):
        try:
            qrCode = self.qrCode;
            activationCode = ""
            locationId = ""
            kioscoId = ""
            serialNumber = None
            if "&" in qrCode:
                splitQr = qrCode.split("&")
                activationCode = splitQr[0]
                locationId = splitQr[1].replace("'", "-")
                kioscoId = splitQr[2].replace("'", "-")
                
            else:
                splitQr = qrCode.split("/")
                activationCode = splitQr[0]
                locationId = splitQr[1].replace("'", "-")
                kioscoId = splitQr[2].replace("'", "-")
            
            
            with open(kioscoInfo, "r") as f:
                data = json.load(f)
                serialNumber = data.get('serialNumber')
            headers = { "SerialNumber": serialNumber, 'activationKey': activationCode, "Content-Type": "application/json"}
            payload = {}
            r = requests.patch(f"{apiUrl}/api/kiosco_routes/activateKiosco/{kioscoId}", headers=headers, json=payload)
            res = r.json()
            response = {'res': res, 'locationId':locationId, 'kioscoId':kioscoId}
            self.done.emit(response)
        except Exception as e:
            print(str(e))
            self.failed.emit(str(e))