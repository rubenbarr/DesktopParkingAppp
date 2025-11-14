from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QBoxLayout, QGridLayout, QVBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class Screen_Admin_Panel_Home(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app 
        self.setStyleSheet("background-color:white")
        
        outer_layer = QVBoxLayout()
        outer_layer.setSpacing(20)
        outer_layer.setContentsMargins(30, 30, 30, 30)
        
        headerContainer = QVBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logoOriginalsmartparking.png").scaled(400, 100, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignLeft)
        
        title = QLabel('Panel de administración')
        
        title.setFont(QFont("Arial", 24))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black; background-color: white; padding:15px")
        
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        buttons = [
                    { 
                     'title': "Información del kiosco",
                     'action': self.app.goToGlobalInfo
                     }, 
                    { 
                        'title': "Surtir Efectivo", 
                        'action': lambda: self.app.go_to(7)
                     }, 
                    {
                        'title': "Retirar Efectivo", 
                        'action': lambda: self.app.go_to(8)
                    },
                    {
                        'title':  "Tickets", 
                        'action': lambda: self.app.go_to(9)
                    }, 
                    {
                        'title': "Apertura de servicio", 
                        'action': lambda: self.app.go_to(0)
                    },
                    {
                        'title':"Salir",
                        'action': lambda: self.app.go_to(0)
                    }
                   ]
        
        positions = [(i,j) for i in range(3) for j in range(3)]
        for pos, item in zip(positions, buttons):
            btn = QPushButton(item['title'])
            btn.setFont(QFont("Arial", 25))
            btn.setStyleSheet( """
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
            btn.setMinimumHeight(100)
            btn.clicked.connect(item['action'])
            btn.setSizePolicy(btn.sizePolicy().Expanding, btn.sizePolicy().Expanding)
            grid.addWidget(btn, *pos)
        
        headerContainer.addWidget(logo)
        headerContainer.addWidget(title)
        outer_layer.addLayout(headerContainer)
        outer_layer.addLayout(grid)
        outer_layer.setStretch(0,1)
        outer_layer.setStretch(1,10)
        
        self.setLayout(outer_layer)
    
    def handleDataFromTicket(self, data):
        self.app.go_to(5);