from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from settings import  kioscoData

import json
import matplotlib
matplotlib.use('Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  as FigureCanvas
from matplotlib.figure import Figure

class ScreenGlobalInfoK(QWidget):
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refreshData()
        
    def refreshData(self):
        with open (kioscoData, "r") as info:
            self.KData = json.load(info)
            
        layout = self.layout()
        for i in reversed(range(layout.count() - 1)):
            widget = layout.itemAt(i).widget()
            if widget and isinstance(widget, FigureCanvas):
                layout.removeWidget(widget)
                widget.deleteLater()

        layout.insertWidget(1, self.create_bar_chart_change())
        layout.insertWidget(2, self.create_bar_chart_Income())
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.KData = {}
        
        with open (kioscoData, "r") as info:
            self.KData = json.load(info)

        outer_layout = QVBoxLayout()
        top_container = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)

        self.MainTitle = QLabel("Información global del kiosco")
        self.MainTitle.setFont(QFont("Arial", 28))
        self.MainTitle.setAlignment(Qt.AlignCenter)
        
        top_container.addWidget(logo)
        top_container.addWidget(self.MainTitle)
        top_container.setAlignment(Qt.AlignTop)
        
        goBackButton = QPushButton('Regresar')
        goBackButton.setFont(QFont("Arial", 20))
        goBackButton.setStyleSheet( """
                              QPushButton {
                                  background-color: #086972;
                                  color: white;
                                  border-radius: 10px;
                                  padding: 20px;
                              }
                              QPushButton:hover {
                                  background-color: #055056;
                              }
                              QPushButton:pressed {
                                  background-color: #757575; 
                                }
                              """)
        goBackButton.setFixedHeight(100)
        goBackButton.clicked.connect(lambda: self.app.go_to(5))
        
        change_bar_chart = self.create_bar_chart_change()
        income_bar_chart = self.create_bar_chart_Income()

        outer_layout.addLayout(top_container)
        outer_layout.addWidget(change_bar_chart)
        outer_layout.addWidget(income_bar_chart)
        outer_layout.addWidget(goBackButton)
        
        self.setLayout(outer_layout)
    
    def getKioscoData(self):
        self.app.go_to(6)
    
    
    def create_bar_chart_change(self):
        change = self.KData['change']
        coins = change['coins']
        bills = change['bills']
        coin_labels = list(change['coins'].keys())
        coin_values = list(change['coins'].values())
        bill_labels = list(change['bills'].keys())
        bill_values = list(change['bills'].values())
        
        self.totalCoins = 0
        self.totalBills = 0
        self.total = 0
        for key in coins:
            self.totalCoins += coins[key] * int(key)
        for key in bills:
            self.totalBills += bills[key] * int(key)
            
        
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        all_labels =[f"{c}" for c in coin_labels + bill_labels] 
        all_values_change = coin_values + bill_values
        
        bars = ax.bar(all_labels, all_values_change, color="#3B9AE1", width=0.5)
        self.total = self.totalCoins + self.totalBills
        ax.set_title(f"Cambio disponible en el kiosco \n Total: ${self.total}", fontsize=16, fontweight='bold', color="#333333", pad=20)
        ax.set_xlabel("Denominación (MXN)", fontsize=12)
        ax.set_ylabel("Cantidad (%)", fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height}', ha='center', va='bottom', fontsize=10)

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        return canvas

    def create_bar_chart_Income(self):

        income = self.KData['income']
        
        coins = income['coins']
        bills = income['bills']
        
        coin_labels = list(income['coins'].keys())
        coin_values = list(income['coins'].values())
        
        bill_labels = list(income['bills'].keys())
        bill_values = list(income['bills'].values())
        
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        all_labels =[f"{c}" for c in coin_labels + bill_labels] 
        all_values_change = coin_values + bill_values
        
        bars = ax.bar(all_labels, all_values_change, color="#3B9AE1", width=0.5)
        self.totalCoins = 0
        self.totalBills = 0
        for key in coins:
            self.totalCoins += coins[key] * int(key)
        for key in bills:
            self.totalBills += bills[key] * int(key)
        self.totalIncome = self.totalCoins + self.totalBills
        
        ax.set_title(f"Ingreso disponible en el kiosco\n Total: ${self.totalIncome}", fontsize=16, fontweight='bold', color="#333333", pad=20)
        ax.set_xlabel("Denominación (MXN)", fontsize=12)
        ax.set_ylabel("Cantidad (%)", fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height}', ha='center', va='bottom', fontsize=10)

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        return canvas
    
           
