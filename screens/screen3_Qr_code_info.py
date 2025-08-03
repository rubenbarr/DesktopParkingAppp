from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, QTimer
import requests
from settings import apiUrl
import threading

class Screen3_Qr_code_info(QWidget):
    def __init__(self, app):
        
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
        
        
        
        self.addCoinButton = QPushButton('Agregar dinero')
        self.addCoinButton.setFixedHeight(40)
        self.addCoinButton.setStyleSheet("""
            font-size: 18px;
            background-color: #086972;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 50px;
            """)
        
        self.addCoinButton.clicked.connect(self.addCoin)

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
        outer_layout.addWidget(self.addCoinButton, alignment=Qt.AlignCenter)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(self.loadingContentWidget)
        outer_layout.addWidget(self.okGifContent)
        outer_layout.addWidget(self.errorContent)
        outer_layout.setAlignment(Qt.AlignTop)

        self.setLayout(outer_layout)
        
    def goToStart(self):
        self.total_pagado = 0;
        self.total_pagado_currency = f"{self.currency_symbol}{self.total_pagado:,.2f}"
        self.totalPagadoAmountCurrency.setText(self.total_pagado_currency)
        self.totales.show()
        self.loadingContentWidget.hide()
        self.title.show()
        self.subTitle.show()
        self.cancelarButton.show()
        self.addCoinButton.show()
        self.errorContent.hide()
        self.app.go_to(0)
        
    def setTotalAmount(self,data:str, ticketId:str):
        self.ticketId = ticketId
        amount = data.get('total_payment', False);
        self._amount = amount
        self.app.go_to(3)
        total = f"{self.currency_symbol}{amount:,.2f}"
        self.subTitle.setText(f"Monto:  {total}")
        self.total_remanente_currency = f"{self.currency_symbol}{amount:,.2f}"
        self.totalRemanenteLabelCurrency.setText(self.total_remanente_currency)
        
    def addCoin(self):
        self.total_pagado = self.total_pagado + 10
        
        self.total_pagado_currency = f"{self.currency_symbol}{self.total_pagado:,.2f}"
        self.total_remanente = self._amount - self.total_pagado
        self.total_remanente_currency = f"{self.currency_symbol}{self.total_remanente:,.2f}"
        self.totalRemanenteLabelCurrency.setText(self.total_remanente_currency)
        self.totalPagadoAmountCurrency.setText(self.total_pagado_currency)
        
        cambio = abs(self.total_remanente)
        cambioCurrency = f"{self.currency_symbol}{cambio:,.2f}"
        self.labelChangeSubTitle.setText(f"Cambio: {cambioCurrency}")
        if self.total_pagado >= self._amount:
            self.title.hide()
            self.subTitle.hide()
            self.totales.hide()
            self.loadingContentWidget.show()
            self.addPayment()
            self.cancelarButton.hide()
            self.addCoinButton.hide()
            
    def addPayment(self):
        try:
            url = f"{apiUrl}/api/ticketRoute/payTicket/{self.ticketId}"
            pago = { "pago": self._amount}
            req = requests.patch(url, json=pago)
            data = req.json()
            status = data.get('status', False)
            self.loadingContentWidget.hide()
            if status:
                self.okGifContent.show()
                self.goToStartAferPaymentAplied()
            else:
                self.errorContent.show()
                
        except Exception as e:
            print(f"Error intentando aplicar pago, error: {str(e)}")
            
    def goToStartAferPaymentAplied(self):
        timer = QTimer.singleShot(10000, self.goToStart)