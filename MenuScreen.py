from kivy.uix.screenmanager import Screen


class MenuScreen(Screen):

    def open_manual(self):
        if self.manager:
            self.manager.current = 'manual'

    def open_scanner(self):
        if self.manager:
            self.manager.current = 'scanner'
