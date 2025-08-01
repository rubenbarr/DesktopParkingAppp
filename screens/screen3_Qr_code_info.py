from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize
import requests
from settings import apiUrl


class Screen3_Qr_code_info(QWidget):
    def __init__(self, app):
        
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #ffffff;")
        self._amount = 0
        
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
        title = QLabel("Total a pagar")
        title.setFont(QFont("Arial", 28))
        title.setAlignment(Qt.AlignCenter)
        
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
        
   
        totals_contenedor = QHBoxLayout()
        totals_contenedor.addLayout(total_pagado_col)
        totals_contenedor.addSpacing(40)
        totals_contenedor.addLayout(total_remanente_col)
        
        button = QPushButton('Cancelar')
        button.setFixedHeight(40)
        button.setStyleSheet("""
            font-size: 18px;
            background-color: #086972;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 50px;
            """)
        button.clicked.connect(self.goToStart)
        
        addCoinButton = QPushButton('Agregar dinero')
        addCoinButton.setFixedHeight(40)
        addCoinButton.setStyleSheet("""
            font-size: 18px;
            background-color: #086972;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 50px;
            """)
        
        addCoinButton.clicked.connect(self.addCoin)

        top_container.addWidget(logo)
        top_container.setAlignment(Qt.AlignLeft)
        top_container.setSpacing(0)
             
        outer_layout.addLayout(top_container)
        outer_layout.addSpacing(20)
        outer_layout.addWidget(title)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(self.subTitle)
        outer_layout.addSpacing(10)
        outer_layout.addLayout(totals_contenedor)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(button, alignment=Qt.AlignCenter)
        outer_layout.addSpacing(10)
        outer_layout.addWidget(addCoinButton, alignment=Qt.AlignCenter)
        outer_layout.setAlignment(Qt.AlignTop)

        self.setLayout(outer_layout)
        
    def goToStart(self):
        self.app.go_to(0)
        
    def setTotalAmount(self,data:str):
        amount = data.get('total_payment', False);
        self._amount = amount
        self.app.go_to(3)
        self._amount = f"{self.currency_symbol}{self._amount:,.2f}"
        self.subTitle.setText(f"Monto:  {self._amount}")
        
    def addCoin(self):
        print('adding money')
        self.total_pagado = self.total_pagado + 1
        print(self.total_pagado)
        self.total_pagado_currency = f"{self.currency_symbol}{self.total_pagado:,.2f}"
        self.totalPagadoAmountCurrency.setText(self.total_pagado_currency)