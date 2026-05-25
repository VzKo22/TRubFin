from kivy.uix.screenmanager import Screen


class MenuScreen(Screen):
    # No custom __init__ or layout setup is needed here anymore!

    def open_manual(self):
        if self.manager:
            self.manager.current = 'manual'

    def open_scanner(self):
        if self.manager:
            self.manager.current = 'scanner'
