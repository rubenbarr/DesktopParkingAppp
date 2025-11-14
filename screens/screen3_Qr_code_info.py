from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from settings import apiUrl, kioscoInfo, kioscoData, errorLogs
from datetime import datetime

import requests
import json

import socket
import threading

class CoinServer(threading.Thread):
    def __init__(self,host, port, callback):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.callback = callback
        self.running = True
        self.socket = None
        print(f'[Coinserver] running state: {self.running}')
        
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print(f"[CoinSever] listeting socket on {self.host}:{self.port}")
        
        try:
            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    print(f"[CoinSever] connection from: {addr}")
                    
                except OSError:
                    break
                
                while self.running:
                    data = conn.recv(1024)
                    if not data:
                        break
                    msg = data.decode().strip()
                    print(f"[CoinServer] data from socket: {msg}")
                    self.callback(msg)
                conn.close()
        finally:
            self.socket.close()
            print(f"[CoinServer] socked fully closed")
            
        
                
    def stop(self):
        print("[CoinSever] attempting to close socket....")
        self.running = False
        try:
            self.socket.send('close_connection')
        except:
            pass
        try:
            self.socket.close()
            print("[CoinSever] closed socket")
        except:
            pass

class Screen3_Qr_code_info(QWidget):
    def __init__(self, app):
        self.locationId = None
        self.kioscoId = None
        self.kioscoToken = None
        
        self.initialData = {}
        self.editIncome = {}
        self.editChange = {}
        with open (kioscoData, "r") as d:
            data = json.load(d)
            self.initialData = data
            self.editIncome = data['income']
            self.editChange = data['change']

        with open(kioscoInfo, "r") as f:
            data = json.load(f)
            self.kioscoId = data.get('kioscoId')
            self.locationId = data.get('locationId')
            self.kioscoToken = data.get('kioscoToken')
            
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #ffffff;")
        self._amount = 0
        self.ticketId = ""
        self.errorMessage = "hubo un error Intente nuevamente"
        
        self.currency_symbol = "$"
        self._initial_amount = 0
        self._amount = f"{self.currency_symbol}{self._initial_amount:,.2f}"
        
        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)
        font = QFont("Arial", 25)
        font.setBold(True)

        #contenedor "total a pagar + monto $"
        self.title = QLabel("Total a pagar")
        self.title.setFont(QFont("Arial", 28))
        self.title.setAlignment(Qt.AlignCenter)
        
        self.subTitle  = QLabel(f"Monto:  {self._amount}")
        self.subTitle.setFont(font)
        self.subTitle.setAlignment(Qt.AlignCenter)
        self.total_pagado = 0
        # termina contenedor
        
        self.total_pagado_currency = f"{self.currency_symbol}{self.total_pagado:,.2f}"
        self.total_remanente = 0
        self.total_remanente_currency = f"{self.currency_symbol}{self.total_remanente:,.2f}"
        
        # inicia contenedor total pagado + cantidad pagada $
        total_pagado_col = QVBoxLayout()
        totalPagadoLabel = QLabel('Total Pagado')
        totalPagadoLabel.setFont(QFont("Arial", 28))
        totalPagadoLabel.setAlignment(Qt.AlignCenter)
        
 
        
        self.totalPagadoAmountCurrency = QLabel(self.total_pagado_currency)
        self.totalPagadoAmountCurrency.setFont(font)
        self.totalPagadoAmountCurrency.setAlignment(Qt.AlignCenter)
        total_pagado_col.addWidget(totalPagadoLabel)
        total_pagado_col.addWidget(self.totalPagadoAmountCurrency)
        #termina contenedor total pagado + cantida pagada $
        
        #inicia contenedor total remanente +  cantidad
        total_remanente_col = QVBoxLayout()
        totalRemanenteLabel = QLabel('Total Restante')
        totalRemanenteLabel.setFont(QFont("Arial", 28))
        totalRemanenteLabel.setAlignment(Qt.AlignCenter)
        self.totalRemanenteLabelCurrency = QLabel(self.total_remanente_currency)
        self.totalRemanenteLabelCurrency.setFont(font)
        self.totalRemanenteLabelCurrency.setAlignment(Qt.AlignCenter)
        total_remanente_col.addWidget(totalRemanenteLabel)
        total_remanente_col.addWidget(self.totalRemanenteLabelCurrency)

        #termina contenedor total remanente +  cantidad
        
   
        self.totals_contenedor = QHBoxLayout()
        self.totals_contenedor.addLayout(total_pagado_col)
        self.totals_contenedor.addSpacing(40)
        self.totals_contenedor.addLayout(total_remanente_col)
        self.totales = QWidget()
        self.totales.setLayout(self.totals_contenedor)
        
        self.cancelarButton = QPushButton('Cancelar')
        self.cancelarButton.setFixedHeight(40)
        self.cancelarButton.setStyleSheet("""
            font-size: 18px;
            background-color: #086972;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 50px;
            """)
        self.cancelarButton.clicked.connect(self.goToStart)
        
        aplicandoLabel = QLabel('Aplicando Pago...')
        aplicandoLabel.setFont(QFont("Arial", 20))
        aplicandoLabel.setAlignment(Qt.AlignCenter)
        spinnerIcon = QLabel()
        iconMovie = QMovie("assets/loadingIcon.gif")
        iconMovie.setScaledSize(QSize(200,200))
        spinnerIcon.setMovie(iconMovie)
        iconMovie.start()
        spinnerIcon.setAlignment(Qt.AlignCenter)
        
        secompletoPagoLabel = QLabel("Pago Registrado correctamente")
        secompletoPagoLabel.setFont(QFont("Arial", 20))
        secompletoPagoLabel.setAlignment(Qt.AlignCenter)
        apartirDeAhoraLabel = QLabel("A partir de ahora cuenta con 15 min para salir")
        apartirDeAhoraLabel.setFont(QFont("Arial", 15))
        apartirDeAhoraLabel.setAlignment(Qt.AlignCenter)
        goToStartHomeButton = QPushButton("Pagar nuevo Ticket")
        goToStartHomeButton.setFixedHeight(40)
        goToStartHomeButton.setStyleSheet("""
            font-size: 18px;
            background-color: #086972;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 50px;
        """)
        goToStartHomeButton.clicked.connect(self.goToStart)
        
        labelChangeTitle = QLabel("Por favor tome Su cambio")
        labelChangeTitle.setFont(QFont("Arial", 20))
        labelChangeTitle.setAlignment(Qt.AlignCenter)
        self.labelChangeSubTitle = QLabel(f"Cambio: {self.total_remanente_currency}")
        self.labelChangeSubTitle.setFont(QFont("Arial", 20))
        self.labelChangeSubTitle.setAlignment(Qt.AlignCenter)
        
        okgif = QLabel()
        okMovie = QMovie("assets/ok.gif")
        okMovie.setScaledSize(QSize(200,200))
        okgif.setMovie(okMovie)
        okMovie.start()
        okgif.setAlignment(Qt.AlignCenter)
        
        huboErrorTitle = QLabel("Hubo un error, registrando pago")
        huboErrorTitle.setFont(QFont("Arial", 20))
        huboErrorTitle.setAlignment(Qt.AlignCenter)
        self.errorSubtitleLabel = QLabel(self.errorMessage)
        self.errorSubtitleLabel.setFont(QFont("Arial", 15))
        self.errorSubtitleLabel.setAlignment(Qt.AlignCenter)
        
        
        errorGifMovie = QMovie("assets/error.gif")
        errorGifMovie.setScaledSize(QSize(200,200))
        errorGifMovie.start()
        errorGifLabel = QLabel()
        errorGifLabel.setMovie(errorGifMovie)
        errorGifLabel.setAlignment(Qt.AlignCenter)
        self.restarButton = QPushButton('Reintentar')
        self.restarButton.setFixedHeight(40)
        self.restarButton.setStyleSheet("""
            font-size: 18px;
            background-color: #086972;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 50px;
            """)
        self.restarButton.clicked.connect(self.goToStart)
        
        
        self.errorContentLayout = QVBoxLayout()
        self.errorContentLayout.addWidget(huboErrorTitle)
        self.errorContentLayout.addWidget(self.errorSubtitleLabel)
        self.errorContentLayout.addWidget(errorGifLabel)
        self.errorContentLayout.addWidget(self.restarButton, alignment=Qt.AlignCenter)
        self.errorContent = QWidget()
        self.errorContent.setLayout(self.errorContentLayout)
        self.errorContent.hide()
        
        
        self.okGifLayout = QVBoxLayout()
        self.okGifLayout.addWidget(secompletoPagoLabel)
        self.okGifLayout.addWidget(apartirDeAhoraLabel)
        self.okGifLayout.addWidget(okgif)
        self.okGifLayout.addWidget(labelChangeTitle)
        self.okGifLayout.addWidget(self.labelChangeSubTitle)
        self.okGifLayout.addSpacing(20)
        self.okGifLayout.addWidget(goToStartHomeButton, alignment=Qt.AlignCenter)
        self.okGifContent = QWidget()
        self.okGifContent.setLayout(self.okGifLayout)
        self.okGifContent.hide()
        
        
        self.loadingContent = QVBoxLayout()
        self.loadingContent.addWidget(aplicandoLabel)
        self.loadingContent.addWidget(spinnerIcon)
        self.loadingContent.setAlignment(Qt.AlignCenter)
        self.loadingContentWidget = QWidget()
        self.loadingContentWidget.setLayout(self.loadingContent)
        self.loadingContentWidget.hide()

        # self.addCoinButton = QPushButton('Agregar dinero')
        # self.addCoinButton.setFixedHeight(40)
        # self.addCoinButton.setStyleSheet("""
        #     font-size: 18px;
        #     background-color: #086972;
        #     color: white;
        #     border: none;
        #     border-radius: 8px;
        #     padding: 10px 50px;
        #     """)
        
        # self.addCoinButton.clicked.connect(self.addCoin)
        # self.addCoinButton.hide()

        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)
        
        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(self.title)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(self.subTitle)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(self.totales)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(self.cancelarButton, alignment=Qt.AlignCenter)
        outer_layout.addSpacing(10)
        # outer_layout.addWidget(self.addCoinButton, alignment=Qt.AlignCenter)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(self.loadingContentWidget)
        outer_layout.addWidget(self.okGifContent)
        outer_layout.addWidget(self.errorContent)
        outer_layout.setAlignment(Qt.AlignTop)

        self.setLayout(outer_layout)
        
    def addCoinFromSocket(self, data):
        dataSplit = data.split(":")
        moneyType = dataSplit[0]
        amount = int(dataSplit[1])
        self.addCoin(moneyType, amount)
        
    def goToStart(self):
        if hasattr(self, "coinserver") and self.coinserver.running:
            self.coinserver.stop()
            
        self.total_pagado = 0;
        self.total_pagado_currency = f"{self.currency_symbol}{self.total_pagado:,.2f}"
        self.totalPagadoAmountCurrency.setText(self.total_pagado_currency)
        self.totales.show()
        self.loadingContentWidget.hide()
        self.title.show()
        self.subTitle.show()
        self.cancelarButton.show()
        # self.addCoinButton.show()
        self.errorContent.hide()
        self.okGifContent.hide()
        self.app.go_to(0)
        
    def setTotalAmount(self,data:str):
        self.ticketId = data['ticketId']
        amount = data.get('total_payment', False);
        self._amount = amount
        self.app.go_to(3)
        
        if hasattr(self, 'coinserver') and self.coinserver.running:
            self.coinserver.stop()

        self.coinserver = CoinServer("0.0.0.0", 5050, self.addCoinFromSocket)        
        self.coinserver.start()
        
        total = f"{self.currency_symbol}{amount:,.2f}"
        self.subTitle.setText(f"Monto:  {total}")
        self.total_remanente_currency = f"{self.currency_symbol}{amount:,.2f}"
        self.totalRemanenteLabelCurrency.setText(self.total_remanente_currency)
        
    def addCoin(self, moneyType, amount):
        self.editIncomeData(moneyType, amount)
        self.total_pagado = self.total_pagado + amount
        
        self.total_pagado_currency = f"{self.currency_symbol}{self.total_pagado:,.2f}"
        self.total_remanente = self._amount - self.total_pagado
        self.total_remanente_currency = f"{self.currency_symbol}{self.total_remanente:,.2f}"
        self.totalRemanenteLabelCurrency.setText(self.total_remanente_currency)
        self.totalPagadoAmountCurrency.setText(self.total_pagado_currency)
        
        cambio = abs(self.total_remanente)
        cambioCurrency = f"{self.currency_symbol}{cambio:,.2f}"
        self.labelChangeSubTitle.setText(f"Cambio: {cambioCurrency}")
        if self.total_pagado >= self._amount:
            self.addPayment()

    def editIncomeData(self, moneyType, amount):
        amount_str = str(amount)
        if moneyType == 'billete':
            self.editIncome['bills'][amount_str] += 1
        elif moneyType == 'moneda':
            self.editIncome['coins'][amount_str] += 1
        
    def updateKioscoData(self):
        self.initialData['income'] = self.editIncome
        with open(kioscoData, "w") as w:
            json.dump(self.initialData, w)
            
    def updateCloudDataFromKiosco(self):
        try:
            headers = { 'locationId': self.locationId, 'kioscoToken': self.kioscoToken, 'kioscoId': self.kioscoId}
            url = f"{apiUrl}/api/kiosco_routes/addKioscoData/{self.kioscoId}"
            payload = self.initialData
            
            requests.patch(url, json=payload, headers=headers)
            # print(f'[updating kiosto Response]: {req.json()}')
            
        except Exception as e:
            error = {
                'action': "Actualizando info de kiosco",
                'fecha': str(datetime.now()),
                'error': str(e)
            }
            with open (errorLogs, 'r') as initial:
                data = json.load(initial)
                data['logs'].append(error)            
            with open (errorLogs, 'w') as w:
                json.dump(data, w)
        
        
        
        
    def addPayment(self):
        self.title.hide()
        self.subTitle.hide()
        self.totales.hide()
        self.cancelarButton.hide()
        # self.addCoinButton.hide()
        self.loadingContentWidget.show()
        
        self.worker = PaymentClass(self.ticketId, self.kioscoToken, self.locationId, self.kioscoId, self._amount)
        self.worker.done.connect(self.onSuccess)
        self.worker.failed.connect(self.onError)
        self.worker.start()
        
    def onSuccess(self, data):
        self.loadingContentWidget.hide()
        status = data.get('status', False)

        if hasattr(self, "coinserver") and self.coinserver.running:
            self.coinserver.stop()
        
        if status:
            self.okGifContent.show()
            self.goToStartAferPaymentAplied()
            self.updateKioscoData()
            self.updateCloudDataFromKiosco()
        else:
            self.errorContent.show()
                    
    def onError(self):
        self.loadingContentWidget.hide()
        self.errorContent.show()
            
            
    def goToStartAferPaymentAplied(self):
        timer = QTimer.singleShot(10000, self.goToStart)
        
        
class PaymentClass(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)
    
    def __init__(self, ticketId, token, locationId, kioscoId, amount):
        super().__init__()
        self.ticketId = ticketId 
        self.token = token
        self.locationId = locationId
        self.kioscoId = kioscoId
        self.amount = amount
        
    def run(self):
        try:
            headers = { 'locationId': self.locationId, 'kioscoToken': self.token, 'kioscoId': self.kioscoId}
            url = f"{apiUrl}/api/ticketRoute/payTicket/{self.ticketId}"
            pago = { "pago": self.amount}
            req = requests.patch(url, json=pago, headers=headers)
            print('[Payment request response]: applying payment response:', req.json())
            data = req.json()
            self.done.emit(data)
                        
        except Exception as e:
            print(f" [Payment request response]: Error intentando aplicar pago, error: {str(e)}")
            self.failed.emit(str(e))
        