from kivy.lang import Builder

import MenuScreen

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from CubeGUI import CubeGUI
from ManualInputScreen import ManualInputScreen
from ScanCubeForAndroid import ScanCube

from kivy.config import Config

Config.set('graphics', 'width', '405')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', False)


class CubeApp(App):
    def build(self):
        self.title = "Rubik's Cube"

        Builder.load_file('menuscreen.kv')
        Builder.load_file('scancubeforandroid.kv')
        Builder.load_file('manualinputscreen.kv')
        Builder.load_file('cubegui.kv')

        sm = ScreenManager()
        sm.add_widget(MenuScreen.MenuScreen(name='menu'))
        sm.add_widget(ScanCube(name="scanner"))
        sm.add_widget(ManualInputScreen(name='manual'))
        sm.add_widget(CubeGUI(name='cube'))

        return sm


if __name__ == "__main__":
    CubeApp().run()
