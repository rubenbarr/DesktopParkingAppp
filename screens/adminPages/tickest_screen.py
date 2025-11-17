from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QGridLayout, QLineEdit, QFrame, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QIntValidator, QMovie
from settings import kioscoData, kioscoInfo, errorLogs
from datetime import datetime
from api.apiroutes import getTicketsFromKioskURL
import requests
import json
import copy

class TicketsScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.tickets  = []
        self.kioskInf = {}

        self.kioscoId = None
        self.kioscoToken = None
        self.locationId = None
        self.page = 1
        self.limit = 10
        self.can_load_more = True
        self.fromDateString = str(datetime.now().isoformat().split("T")[0])
        self.toDateString = str(datetime.now().isoformat().split("T")[0])
        
        self.setStyleSheet("""
                            QPushButton {
                                background-color: #086972; 
                                color: white; 
                                padding: 4px 8px; 
                                border-radius: 8px;
                            }
                            QPushButton:hover {
                                background-color: #c0c0c0;
                            }
                            QPushButton:pressed {
                                background-color: #055056; 
                            }
                           """)
        
        
        with open (kioscoInfo, 'r') as info :
            self.kioskInf = json.load(info) 
            self.kioscoId = self.kioskInf['kioscoId']
            self.kioskToken = self.kioskInf['kioscoToken']
            self.locationId = self.kioskInf['locationId']
        
        mainHeaderLayout = QVBoxLayout()
        
        mainHeaderLayout.setAlignment(Qt.AlignTop)
        mainHeaderTitle = QLabel('Consulta de tickets')
        mainHeaderTitle.setStyleSheet('color: #086972;')
        mainHeaderTitle.setAlignment(Qt.AlignCenter)
        mainHeaderTitle.setFont(QFont("Arial", 30))
        
        mainHeaderSub = QLabel('Consulte los tickets registrados a la entrada')
        mainHeaderSub.setStyleSheet("background-color: #086972; color:white; padding: 10px; font-size: 20px;")
        mainHeaderSub.setAlignment(Qt.AlignCenter)
        mainHeaderSub.setFont(QFont("Arial", 30))
        
        mainHeaderLayout.addWidget(mainHeaderTitle)
        mainHeaderLayout.addWidget(mainHeaderSub)
        
        dateLayout = QHBoxLayout()
        dateLayout.setAlignment(Qt.AlignCenter)
        
        fromLabel = QLabel('Desde:')
        fromLabel.setFont(QFont('Arial', 15))
        
        self.fromDate = QDateEdit()
        self.fromDate.setCalendarPopup(True)
        self.fromDate.setDate(QDate.currentDate().addDays(-7))
        self.fromDate.setFont(QFont("Arial", 15))
        
        toLabel = QLabel('Hasta:')
        toLabel.setFont(QFont('Arial', 15))
        
        self.toDate = QDateEdit()
        self.toDate.setCalendarPopup(True)
        self.toDate.setDate(QDate.currentDate())
        self.toDate.setFont(QFont("Arial", 15))
        
        
        self.searchBtn = QPushButton("Buscar")
        # self.searchBtn.setStyleSheet("background-color: #086972; color: white; padding: 8px 20px; border-radius: 10px;")
        self.searchBtn.setFont(QFont('Arial', 15))
        self.searchBtn.clicked.connect(self.getTicketsFromDate)
        
        self.goBackButton = QPushButton("Regresar")
        # self.goBackButton.setStyleSheet("background-color: #086972; color: white; padding: 8px 20px; border-radius: 10px; margin-left:10px")
        self.goBackButton.setFont(QFont('Arial', 15))
        self.goBackButton.clicked.connect(lambda: self.app.go_to(5))
        
        dateLayout.addWidget(fromLabel)
        dateLayout.addWidget(self.fromDate)
        dateLayout.addWidget(toLabel)
        dateLayout.addWidget(self.toDate)
        dateLayout.addWidget(self.searchBtn)
        dateLayout.addWidget(self.goBackButton)
        
        
        self.ticketsTable = QTableWidget()
        self.ticketsTable.setColumnCount(7)
        self.ticketsTable.setHorizontalHeaderLabels(['Entrada', 'puerta', 'Estado', 'Pagado', 'Salida' , 'Monto', 'accion' ])
        self.ticketsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ticketsTable.setStyleSheet("font-size: 14px; border: 1px solid #ccc;")
        
        # ======== columna para cargar mas =========#
        dataInfoLayout = QHBoxLayout()
        dataInfoLayout.setAlignment(Qt.AlignCenter)    
        
        self.totalLabelTitle = QLabel(f'Total de tickets: {len(self.tickets)}')
        self.totalLabelTitle.setFont(QFont('Arial', 13))
        dataInfoLayout.addWidget(self.totalLabelTitle)
        self.LoadMoreButton = QPushButton("Cargar Mas")
        # self.LoadMoreButton.setStyleSheet("background-color: #086972; color: white; padding: 8px 20px; border-radius: 10px; margin-left:10px")
        self.LoadMoreButton.setFont(QFont('Arial', 15))
        self.LoadMoreButton.clicked.connect(lambda: self.loadMore())
        dataInfoLayout.addWidget(self.LoadMoreButton)
        
        # ======== FIIN columna para cargar mas =========#
        
        

        mainHeaderLayout.addLayout(dateLayout)
        mainHeaderLayout.addLayout(dataInfoLayout)
        mainHeaderLayout.addWidget(self.ticketsTable) 
                
        # ===== component injection to layout ===== #
    
        self.setLayout(mainHeaderLayout)
            
        # ======= loading content ============= #
        
        self.loadingOverLay = QWidget(self)
        self.loadingOverLay.setStyleSheet("""
                                          background-color: rgba(255,255,255, 200)
                                          """
                                          )
        self.loadingOverLay.setGeometry(self.rect())
        self.loadingOverLay.setVisible(False)
        self.loadingOverLay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        over_layout = QVBoxLayout(self.loadingOverLay)
        over_layout.setAlignment(Qt.AlignCenter)
        
        self.spinnerIcon = QLabel(self.loadingOverLay)
        self.spinnerIcon.setAlignment(Qt.AlignCenter)
        
        self.loadingIcon = QMovie("assets/loadingIcon.gif")
        self.loadingIcon.setScaledSize(QSize(300,300))
        self.loadingIcon.start()
        self.spinnerIcon.setMovie(self.loadingIcon)
        
        over_layout.addWidget(self.spinnerIcon)
        self.loadingOverLay.raise_()
        
    def loadMore(self):
        nextPage = self.page + 1
        self.page = nextPage

        self.getTickets(nextPage, self.limit)


    def getTicketsFromDate(self):
       self.fromDateString = self.fromDate.date().toString("yyyy-MM-dd")
       self.toDateString = self.toDate.date().toString("yyyy-MM-dd")
       self.getTickets(self.page, self.limit)
       

    
    def getTickets(self, page, limit):
        self.loadingOverLay.setGeometry(self.rect())
        self.loadingOverLay.raise_()
        self.loadingOverLay.setVisible(True)
        self.worker = GetTicketClass(self.kioscoId, self.kioskToken, self.locationId, page, limit, self.fromDateString, self.toDateString)
        self.worker.done.connect(self.onSuccessTicketsCall)
        self.worker.failed.connect(self.onErrorTicketCall)
        self.worker.start()
    
    def onSuccessTicketsCall(self, res):
        self.loadingOverLay.setVisible(False)
        self.ticketsTable.setRowCount(0)
        
        data = res.get('data', [])
        state = res.get('state')
        if state:
            if len(data) > 0:
                for d in data:
                    self.tickets.append(d)
            if len(self.tickets) > 0 :
                self.totalLabelTitle.setText(f'Total de tickets: {len(self.tickets)}')
                self.ticketsTable.setRowCount(len(self.tickets))
                for row, ticket in enumerate(self.tickets):
                    montoPagado = ticket.get('montoPagado')
                    if montoPagado:
                        montoPagado = str(f"${montoPagado:.2f}")
                    else:
                        montoPagado = '-'
                    self.ticketsTable.setItem(row, 0, QTableWidgetItem(ticket.get("fechaEntrada", "-")))
                    self.ticketsTable.setItem(row, 1, QTableWidgetItem(ticket.get("gateLabel", "-")))
                    self.ticketsTable.setItem(row, 2, QTableWidgetItem(ticket.get("estado", "-")))
                    self.ticketsTable.setItem(row, 3, QTableWidgetItem(ticket.get("fechaPago", "-")))
                    self.ticketsTable.setItem(row, 4, QTableWidgetItem(ticket.get("fechaSalida", "-")))
                    self.ticketsTable.setItem(row, 5, QTableWidgetItem(montoPagado))
            
                    btn = QPushButton("Reimprimir")
                    # btn.setStyleSheet("background-color: #086972; color: white; padding: 4px 8px; border-radius: 8px;")
                    btn.clicked.connect(lambda _, t=ticket: self.handleTicketAction(t))
                    self.ticketsTable.setCellWidget(row, 6, btn)
                    
    def handleTicketAction(self, ticket):
        print(f"Action triggered for ticket ID: {ticket}")
        # Add your custom logic here (e.g., open detail modal, mark as exited, etc.)
                    
                
    def onErrorTicketCall(self, res):
        self.loadingOverLay.setVisible(False)


    def showEvent(self, event):
        super().showEvent(event)
        self.tickets = []
        self.page = 1
        self.getTickets(1, 10)

class GetTicketClass(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)
    
    def __init__(self, kioscoId, kioscoToken, locationId, page, limit, fromDate, toDate):
        super().__init__()
        self.kioscoId = kioscoId
        self.kioscoToken = kioscoToken
        self.locationId = locationId
        self.page = page
        self.limit = limit
        self.fromDate = fromDate
        self.toDate = toDate
    
    def run(self):
        try:
            headers = { 'token': self.kioscoToken, 'locationId': self.locationId }
            req = requests.get(f'{getTicketsFromKioskURL}/{self.kioscoId}?page={self.page}&limit={self.limit}&fromDate={self.fromDate}&toDate={self.toDate}', headers=headers, timeout=6000)
            res = req.json()
            self.done.emit(res)
        except Exception as e:
            newError = {
                'action': 'Obteniendo tickets',
                'fecha': str(datetime.now()),
                'error': str(e)
            }
            with open(errorLogs, 'r')  as currentErrors:
                initialErrors = json.load(currentErrors)
                initialErrors['logs'].append(newError)
                with open(errorLogs, 'w') as w:
                    json.dump(initialErrors, w)
                    self.failed.emit(str(e))