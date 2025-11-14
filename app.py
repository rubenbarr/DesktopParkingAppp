from PyQt5.QtWidgets import QStackedWidget
from screens.screen1_welcome import Screen1Welcome
from screens.screen2_qr_code_scann import Screen2ValidatingTicket
from screens.screen2F_qr_code_scann import Screen2FErrorWhileCheckingTicket
from screens.screen3_Qr_code_info import Screen3_Qr_code_info
from screens.default_screen import DefaultScreen
from screens.screen_admin_home import Screen_Admin_Panel_Home
from screens.adminPages.global_info_screen import ScreenGlobalInfoK
from screens.adminPages.addMoney_screen import AddMoneyScreen
from screens.adminPages.removeMoney_screen import RemoveMoneyScreen
from screens.adminPages.tickest_screen import TicketsScreen

from settings import kioscoInfo

import json
import os



def is_kiosco_activated ():
    if not os.path.exists(kioscoInfo):
        return False
    try:
        with open(kioscoInfo, "r") as f:
            data = json.load(f)
            activated =  data.get('activated', False)
            return activated
    except Exception as e:
        print(str(e))
        return False
    
def checkChange():
    if not os.path.exists(kioscoInfo):
        raise Exception ('no se encontró el archivo de la información del kiosco')
    try:
        with open(kioscoInfo,  'r') as info:
            data = json.load(info)
            hasChange =  data.get('hasChange', False)
            return hasChange
    except Exception as e:
        return str(e)


class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.kioscoNotActivate = is_kiosco_activated()
        self.hasChange = checkChange()

        # screen 0 pagina de inicio
        self.welcome = Screen1Welcome(self)
        self.addWidget(self.welcome)
        
        # screen 1 validación de ticket
        self.validatingTicket = Screen2ValidatingTicket(self)
        self.addWidget(self.validatingTicket)
        
        # screen 2 pagina de error de ticket
        self.validatingTicketFailed = Screen2FErrorWhileCheckingTicket(self)
        self.addWidget(self.validatingTicketFailed)
        
        # screen 3
        self.paymentScreen3 = Screen3_Qr_code_info(self)
        self.addWidget(self.paymentScreen3)
        
        # screen 4 pagina para activar el kiosco
        self.defaultScreen = DefaultScreen(self)
        self.addWidget(self.defaultScreen)
        
        #screen 5 admin page
        self.adminScreen = Screen_Admin_Panel_Home(self)
        self.addWidget(self.adminScreen)
        
        #screen 6 global info K
        self.globalInfo = ScreenGlobalInfoK(self)
        self.addWidget(self.globalInfo)
        
        #screen 7 add money to kiosk
        self.add_moneyScreen = AddMoneyScreen(self)
        self.addWidget(self.add_moneyScreen)

        #screen 8 remove money to kiosk
        self.remove_moneyScreen = RemoveMoneyScreen(self)
        self.addWidget(self.remove_moneyScreen)
        
        #screen 9 tickets list
        self.TicketsScreen = TicketsScreen(self)
        self.addWidget(self.TicketsScreen)
        
    
        if self.kioscoNotActivate:
            self.setCurrentIndex(5)
        else: self.setCurrentIndex(4)
        
        
    def go_to(self,index):
        self.setCurrentIndex(index)
        
    def pass_data_to_screen_2(self, data):
        self.validatingTicket.get_ticket_data(data)
        
    def pass_data_to_screen_3(self, data):
        self.paymentScreen3.setTotalAmount(data)
        
    def goToErrorPage(self, errorMessage, errorType, data):
        self.validatingTicketFailed.handleErrorMessage(errorMessage,errorType, data)
    
    def gotToMaintenancePage(self, data):
        self.adminScreen.handleDataFromTicket(data)
        
    def goToGlobalInfo(self):
        self.globalInfo.getKioscoData()