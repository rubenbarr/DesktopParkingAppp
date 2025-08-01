from PyQt5.QtWidgets import QStackedWidget
from screens.screen1_welcome import Screen1Welcome
from screens.screen2_qr_code_scann import Screen2ValidatingTicket
from screens.screen2F_qr_code_scann import Screen2FErrorWhileCheckingTicket
from screens.screen3_Qr_code_info import Screen3_Qr_code_info

class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        
        self.welcome = Screen1Welcome(self)
        self.addWidget(self.welcome)
        
        self.validatingTicket = Screen2ValidatingTicket(self)
        self.addWidget(self.validatingTicket)
        
        self.validatingTicketFailed = Screen2FErrorWhileCheckingTicket(self)
        self.addWidget(self.validatingTicketFailed)
        
        self.paymentScreen3 = Screen3_Qr_code_info(self)
        self.addWidget(self.paymentScreen3)
        
        self.setCurrentIndex(0)
        
        
    def go_to(self,index):
        print(f"Switching to screen {index}")
        self.setCurrentIndex(index)
        
    def pass_data_to_screen_2(self, data):
        self.validatingTicket.get_ticket_data(data)
        
    def pass_data_to_screen_3(self, data):
        self.paymentScreen3.setTotalAmount(data)