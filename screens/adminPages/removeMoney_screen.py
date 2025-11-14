from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QGridLayout, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator, QMovie
from settings import kioscoData, kioscoInfo, errorLogs
from datetime import datetime
from api.apiroutes import patchKioscoDataUrl
import requests
import json
import copy


class RemoveMoneyScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.inputs = {}
        self.changeInit = {}
        self.changeEdit = {}
        self.total_bills = 0
        self.total_coins = 0
        self.total_bills_to_insert = 0
        self.total_coins_to_insert = 0
        self.total_remaining = 0
        
        self.coins_in = {}
        self.bills_in = {}
        self.bill_avail_labels = {}
        self.coin_avail_labels = {}
        self.total_label = None
        self.remaining_label = None
        self.total_label_bills = None
        self.total_label_coins = None
        self.inserted_label_bills = None
        self.inserted_label_coins = None
        self.total_in_kiosco  = None
        self.total_inserted = None
        self.active_input = False
        self.canSubmitBills = True
        self.canSubmitCoins = True
        
        self.billWarningLabel = QLabel("se está intentando retirar más billetes de lo disponible")
        self.billWarningLabel.setFont(QFont("Arial", 28))
        self.billWarningLabel.setStyleSheet('color: red;')
        self.billWarningLabel.setAlignment(Qt.AlignCenter)
        
        self.coinWarningLabel = QLabel("se está intentando retirar más monedas de lo disponible")
        self.coinWarningLabel.setFont(QFont("Arial", 28))
        self.coinWarningLabel.setStyleSheet('color: red;')
        self.coinWarningLabel.setAlignment(Qt.AlignCenter)
        
        self.billWarningLabel.hide()
        self.coinWarningLabel.hide()
        
        
        self.initialData = {
            "coins": { "1": 0, "2": 0, "5": 0, "10": 0 },
            "bills": { "20": 0, "50": 0, "100": 0, "200": 0 }
        }
        self.EditData = {
            "coins": { "1": 0, "2": 0, "5": 0, "10": 0 },
            "bills": { "20": 0, "50": 0, "100": 0, "200": 0 }
        }
        
        with open(kioscoData, 'r') as d:
            data = json.load(d)
            self.changeInit = data.get('change', {})
            self.changeEdit = data.get('change', {})
            self.coins_in = self.changeInit.get('coins', {})
            self.bills_in = self.changeInit.get('bills', {})
    
        for i in self.changeInit:
            for val in self.changeInit[i]:
                if i == 'coins':
                    self.total_coins += int(val) * int(self.changeInit[i][str(val)])
                elif i == 'bills':
                    self.total_bills += int(val) * int(self.changeInit[i][str(val)])
            
        self.setWindowTitle("Retiro de Dinero")
        self.setStyleSheet("""
                           QWidget {
                             background-color: #ffffff;
                             font-family: Arial;
                           }
                           QLabel {
                             color: #003366;  
                             font-size: 20px;
                             font-weight: bold;
                           }
                           QLineEdit {
                            background: #ffffff;
                            border: 1px solid #000000;
                            border-radius: 6px;
                            font-size: 16px;
                            padding: 4px;
                            text-align: center;
                            width: 50px;
                           }
                           QLineEdit:focus {
                            border: 2px solid #2e8bff;
                            background: #cccccc
                           }
                            QPushButton {
                                background-color: #e0e0e0;
                                border-radius: 8px;
                                font-size: 16px;
                                padding: 10px;
                            }
                            QPushButton:hover {
                                background-color: #c0c0c0;
                            }
                            QPushButton:pressed {
                                background-color: #055056; 
                            }
                            QPushButton#acceptBtn {
                                background-color: #2e8bff;
                                color: white;
                            }
                            QPushButton#acceptBtn:hover {
                                background-color: #86a7d1;
                                color: white;
                            }
                            QPushButton#acceptBtn:pressed {
                                background-color: #86a7d1;
                                color: white;
                            }
                            QPushButton#cancelBtn {
                                background-color: #c62828;
                                color: white;
                            }
                            QPushButton#cancelBtn:hover {
                                background-color: #ab5555;
                                color: white;
                            }
                            QPushButton#cancelBtn:pressed {
                                background-color: #ab5555;
                                color: white;
                            }
                           """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        self.leftSide = QVBoxLayout()
        rightSide = QVBoxLayout()
        
        mheader = QLabel("RETIRO")
        mheader.setStyleSheet('color: #086972;')
        mheader.setAlignment(Qt.AlignCenter)
        mheader.setFont(QFont("Arial", 30))
        header = QLabel( "Indique el numero de monedas o billetes a retirar")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 28))
        header.setStyleSheet("background-color: #086972; color:white; padding: 10px; font-size: 20px;")
        layout.addWidget(mheader)
        layout.addWidget(header)
        
        self.bills_frame = self._create_money_section('Billetes', [20, 50, 100, 200])
        self.coins_frame = self._create_money_section('Monedas', [1,2,5,10])
        
        keypad = self.keypad_layout()
        
        self.leftSide.addWidget(self.bills_frame)
        self.leftSide.addWidget(self.coins_frame)
        
        
        acceptBtn = QPushButton('Aceptar')
        acceptBtn.setObjectName('acceptBtn')
        acceptBtn.setFixedSize(150, 50)
        acceptBtn.clicked.connect(self.update_kioskInfo)
        
        cancelBtn = QPushButton('Cancelar')
        cancelBtn.setObjectName('cancelBtn')
        cancelBtn.setFixedSize(150, 50)
        cancelBtn.clicked.connect(lambda: self.app.go_to(5))
        
        btn_layout = QVBoxLayout()
        btn_layout.addLayout(keypad)
        btn_layout.addWidget(acceptBtn)
        btn_layout.addWidget(cancelBtn)
        
        rightSide.addLayout(btn_layout)
        
        central_layout = QHBoxLayout()
        central_layout.addLayout(self.leftSide)
        central_layout.addLayout(rightSide)
        layout.addLayout(central_layout)
        self.setLayout(layout)
        
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

        
    def _create_money_section(self, title, denominations):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("background-color: #F0F0F0; border-radius:10px; padding:10px")
        
        main_layout = QVBoxLayout(frame)
        label_title = QLabel(title)
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("font-size: 16px; color: #004080;")
        
        main_layout.addWidget(label_title)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.setInitialKeyActive = None
        
        for i, val in enumerate(denominations):
            label = QLabel(f"${val:.2f}")
            inp = QLineEdit("0")
            inp.setObjectName(f"{title}&{str(val)}")
            inp.setValidator(QIntValidator(0,999))
            if not self.setInitialKeyActive:
                self.setInitialKeyActive = inp
            
            total_label = QLabel("Disponible")
            currVal = self.bills_in[str(val)] if title == 'Billetes' else self.coins_in[str(val)]
            total_val = QLabel(str(currVal))

            grid.addWidget(label, 0, i)
            grid.addWidget(inp, 1, i)
            grid.addWidget(total_label,2, i)
            grid.addWidget(total_val, 3, i)
            
            self.inputs[val] = inp
            inp.focusInEvent = lambda event, inp=inp:  self.set_active_input(inp)
            
        if self.setInitialKeyActive:
            QTimer.singleShot(100, lambda: self.setInitialKeyActive.setFocus())
            self.active_input = self.setInitialKeyActive

        self.total_in_kiosco = self.total_bills if title == 'Billetes' else self.total_coins
        self.total_inserted = self.total_bills_to_insert if title == 'Billetes' else self.total_coins_to_insert
        
        if title == "Billetes":
            self.total_label_bills = QLabel(f"Total { title} en Kiosco: ${self.total_in_kiosco:.2f}")
            self.total_label = self.total_label_bills
            self.total_label.setObjectName('totalBills')
            self.total_remaining = self.total_in_kiosco - self.total_inserted
        else:
            self.total_label_coins = QLabel(f"Total { title} en Kiosco: ${self.total_in_kiosco:.2f}")
            self.total_label = self.total_label_coins
            self.total_label.setObjectName('totalCoins')
            self.total_remaining = self.total_in_kiosco - self.total_inserted
        

        # self.total_label = QLabel(f"Total { title} en Kiosco: ${total_in_kiosco:.2f}")
        self.total_inserted_label = QLabel(f'Total a remover: ${self.total_inserted:.2f}')    
        self.remaining_label = QLabel(f'Total restante: ${self.total_remaining:.2f}')    
        
        self.total_inserted_label.setAlignment(Qt.AlignLeft)
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("font-size: 20px; color: #333333")
        self.total_inserted_label.setStyleSheet("font-size: 20px; color: #333333")
        if title == "Billetes":
            self.total_inserted_label.setObjectName('totalBillsInsertedLbl')
            self.remaining_label.setObjectName('totalRemainingBillsTag')
        else:
            self.total_inserted_label.setObjectName('totalCoinsInsertedLbl')
            self.remaining_label.setObjectName('totalRemainingCoinsTag')
            
        
        total_row = QHBoxLayout()
        warningLabel = QHBoxLayout()
        
        total_row.addWidget(self.total_label)
        total_row.addWidget(self.total_inserted_label)
        total_row.addWidget(self.remaining_label)
        
        if title == 'Billetes':
            warningLabel.addWidget(self.billWarningLabel)
        else:
            warningLabel.addWidget(self.coinWarningLabel)
        
        main_layout.addLayout(grid)
        main_layout.addLayout(total_row)
        main_layout.addLayout(warningLabel)
        return frame
    
    def keypad_layout(self):
        key_layout = QGridLayout()
        buttons = [
            ('1', 0, 0), ('2', 0, 1) , ('3', 0 , 2),
            ('4', 1, 0), ('5', 1, 1) , ('6', 1 , 2),
            ('7', 2, 0), ('8', 2, 1) , ('9', 2 , 2),
            ('0', 3, 0), ('Del', 3, 1)
        ]
        
        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(90,70)
            key_layout.addWidget(btn, row, col)
            btn.clicked.connect(lambda checked, t=text: self.on_key_press(t))
        return key_layout            
    
    
    def set_active_input(self, key):
        self.active_input = key           
            
    
    def on_key_press(self, key):
        if not self.active_input:
           return

        globalT = self.active_input.objectName()
        typeOfCurrency = globalT.split("&")[0]
        val = globalT.split("&")[1]
        
        text = self.active_input.text()
        if key == 'Del':
            text = text[:-1] if text else ''
        else:
            text += key
            
        if text == "":
            text = '0'
        elif text.startswith('0') and len(text) > 1:
            text = text.lstrip('0')
        
        if typeOfCurrency == 'Billetes':
            if int(text) > 0:
                self.EditData['bills'][str(val)] = int(text)
            elif int(text) == 0:
                self.EditData['bills'][str(val)] = 0
        elif typeOfCurrency == 'Monedas':
            if int(text) > 0:
                self.EditData['coins'][str(val)] = int(text)
            elif int(text) == 0:
                self.EditData['coins'][str(val)] = 0
        self.active_input.setText(text)

        self.total_bills_to_insert = 0
        self.total_coins_to_insert = 0
        for i in self.EditData:
                for vals in self.EditData[i]:
                    if i == 'bills':
                        self.total_bills_to_insert += int(self.EditData[i][str(vals)]) * int(vals)
                    elif i == 'coins':
                        self.total_coins_to_insert += int(self.EditData[i][str(vals)]) * int(vals)                 
        totalbillslabel = self.findChild(QLabel, 'totalBillsInsertedLbl')
        totalCoinslabel = self.findChild(QLabel, 'totalCoinsInsertedLbl')
        
        if typeOfCurrency == 'Billetes':
            if self.bills_in[str(val)] < int(text):
                self.billWarningLabel.show()
                self.canSubmitBills = False
            else:
                self.billWarningLabel.hide()
                self.canSubmitBills = True
        if typeOfCurrency == 'Monedas':
            if self.coins_in[str(val)] < int(text):
                self.canSubmitCoins = False
                self.coinWarningLabel.show()
            else:
                self.canSubmitCoins = True
                self.coinWarningLabel.hide()
            
        
        totalBillsRemaining = self.findChild(QLabel, 'totalRemainingBillsTag')
        totalBCoinsRemaining = self.findChild(QLabel, 'totalRemainingCoinsTag')
        
        
        remainingBills = self.total_bills - self.total_bills_to_insert
        remainingCoins = self.total_coins - self.total_coins_to_insert
        
        totalBillsRemaining.setText(f'Total restante: ${remainingBills:.2f}')
        totalBCoinsRemaining.setText(f'Total restante: ${remainingCoins:.2f}')
        totalbillslabel.setText(f'Total a remover ${self.total_bills_to_insert:.2f}')
        totalCoinslabel.setText(f'Total a remover ${self.total_coins_to_insert:.2f}')
        
        
    def update_kioskInfo (self):
        wasUpdated = self.dataWasUpdated()
        if wasUpdated and self.canSubmitCoins and self.canSubmitBills:
            for i in self.EditData:
                for val in self.EditData[i]:
                    self.changeEdit[i][str(val)] -= int(self.EditData[i][str(val)])       
        else:
            self.changeEdit = copy.deepcopy(self.changeInit)

        if wasUpdated and self.canSubmitCoins and self.canSubmitBills:
            self.loadingOverLay.raise_()
            self.repaint()
            self.change = copy.deepcopy(self.changeEdit)
            self.current = {}
            with open(kioscoData, 'r') as initial:
                self.current = json.load(initial)
            with open(kioscoData, 'w') as w:
                self.current['change'] = copy.deepcopy(self.change)
                json.dump(self.current, w)
            self.checkIfChangeIsEnough(self.change)
            # self.app.go_to(5)
            
    def updateKioscoDataOnDb(self):
        self.kinfo = {}
        self.kioscoData = {}
        with open(kioscoInfo, 'r') as i:
            self.kinfo = json.load(i)
        
        with open(kioscoData, 'r') as i:
            self.kioscoData = json.load(i)
 
        self.loadingOverLay.setVisible(True)
        self.worker = PatchDataRequest(self.kinfo, self.kioscoData)
        self.worker.done.connect(self.onSuccessKioskPatch)
        self.worker.failed.connect(self.onErrorKioskPatch)
        self.worker.start()

    def onSuccessKioskPatch(self):
        self.loadingOverLay.setVisible(False)
        self.app.go_to(5)
    def onErrorKioskPatch(self):
        self.loadingOverLay.setVisible(False)
        self.app.go_to(5)
        
    def dataWasUpdated(self):
        wasUpdate = False
        for t in self.EditData:
            for k in self.EditData[t]:
                if self.EditData[t][str(k)] != self.initialData[t][str(k)]:
                    wasUpdate = True
                    break
        return wasUpdate
    
    def showEvent(self, event):
        super().showEvent(event)
        self.reload_data()

    def resizeOnEvent(self):
        if hasattr(self, 'loadingOverLay'):
            self.loadingOverLay.setGeometry(self.rect())
            self.loadingOverLay.raise_()

    def reload_data(self):
        self.total_bills = 0
        self.total_coins = 0
        with open(kioscoData, 'r') as d:
            data = json.load(d)
            self.changeInit = data.get('change', {})
            self.changeEdit = data.get('change', {})
            self.coins_in = self.changeInit.get('coins', {})
            self.bills_in = self.changeInit.get('bills', {})

        for i in self.changeInit:
            for val in self.changeInit[i]:
                if i == 'coins':
                    self.total_coins += int(val) * int(self.changeInit[i][str(val)])
                elif i == 'bills':
                    self.total_bills += int(val) * int(self.changeInit[i][str(val)])

        self.initialData = {
            "coins": { "1": 0, "2": 0, "5": 0, "10": 0 },
            "bills": { "20": 0, "50": 0, "100": 0, "200": 0 }
        }
        self.EditData = {
            "coins": { "1": 0, "2": 0, "5": 0, "10": 0 },
            "bills": { "20": 0, "50": 0, "100": 0, "200": 0 }
        }
        self.total_bills_to_insert = 0
        self.total_coins_to_insert = 0
        for inp in self.inputs.values():
            inp.setText("0")

        self.refresh_labels()
        

    def refresh_labels(self):
        for i in reversed(range(self.leftSide.count())):
            item = self.leftSide.itemAt(i)
            widget = item.widget()
            if widget is not None:
                self.leftSide.removeWidget(widget)
                widget.deleteLater()
        self.bills_frame = self._create_money_section('Billetes', [20, 50, 100, 200])
        self.coins_frame = self._create_money_section('Monedas', [1, 2, 5, 10])
        
        self.leftSide.addWidget(self.bills_frame)
        self.leftSide.addWidget(self.coins_frame)
        totalbillslabel = self.findChild(QLabel, 'totalBillsInsertedLbl')
        totalCoinslabel = self.findChild(QLabel, 'totalCoinsInsertedLbl')
        
        totalbillslabel.setText(f'Total a insertar ${self.total_bills_to_insert:.2f}')
        totalCoinslabel.setText(f'Total a insertar ${self.total_coins_to_insert:.2f}')
        self.canSubmitBills = True
        self.canSubmitCoins = True
        self.billWarningLabel.hide()
        self.coinWarningLabel.hide()
        self.leftSide.update()
        self.update()
        self.resizeOnEvent()
    
    def checkIfChangeIsEnough(self, data):
        self.hasEnoughChange = True
        coins = data['coins']
        bills = data['bills']
        totalCoins = 0
        totalBills = 0
        minCoins = 8
        minBills = 8
        
        for index in coins:
            totalCoins += int(coins[str(index)])
                
        for index in bills:
            totalBills += int(bills[str(index)])
        
        if totalCoins <= minCoins or totalBills <= minBills:
            self.hasEnoughChange = False
        elif totalCoins >= minCoins and totalBills >= minBills:
            self.hasEnoughChange = True
        self.data = {}
        with open(kioscoInfo, 'r') as kf:
                self.data = json.load(kf)
                self.data['hasChange'] = self.hasEnoughChange
                with open(kioscoInfo, 'w') as kf:
                    json.dump(self.data, kf)
        self.updateKioscoDataOnDb()


class PatchDataRequest(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)
    
    def __init__(self, kioscoInfo, newData):
        super().__init__()
        self.kioscoInfo = kioscoInfo
        self.newData = newData
        
    def run(self):
        try:
            kioscoId = self.kioscoInfo['kioscoId']
            token = self.kioscoInfo['kioscoToken']

            headers = {'kioscoId': kioscoId, 'kioscoToken': token}
            payload = self.newData
            
            req = requests.patch(f'{patchKioscoDataUrl}/{kioscoId}', headers=headers, json=payload, timeout=6000)
            res = req.json()
            self.done.emit(res)
        except Exception as e:
            newError = {
                'action': 'Actualizando los datos en retiro de dinero',
                'fecha': str(datetime.now()),
                'error': str(e)
            }
            with open(errorLogs, 'r')  as currentErrors:
                initialErrors = json.load(currentErrors)
                initialErrors['logs'].append(newError)
                with open(errorLogs, 'w') as w:
                    json.dump(initialErrors, w)
                    self.failed.emit(str(e))