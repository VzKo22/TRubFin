from kivy.uix.screenmanager import Screen

""" MenuScreen კლასი, რომელიც user-ს სთავაზობს მექანიკურად კუბის ფერების ხელით შეტანას ან სკანირებას"""
class MenuScreen(Screen):

    def open_manual(self):
        if self.manager:
            self.manager.current = 'manual'

    def open_scanner(self):
        if self.manager:
            self.manager.current = 'scanner'
