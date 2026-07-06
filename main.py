from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from CubeGUI import CubeGUI
from ManualInputScreen import ManualInputScreen
from MenuScreen import MenuScreen
from ScanCubeForAndroid import ScanCube

from kivy.config import Config

Config.set('graphics', 'width', '405')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', False)

""" CubeApp კლასი, სადაც იტვირთება .kv ფაილები UI-სთვის და  ხდება ეკრანების მართვა"""
class CubeApp(App):
    def build(self):
        self.title = "Rubik's Cube"
        self.icon = "assets/TSU_icon_for_cube.png"

        Builder.load_file('menuscreen.kv')
        Builder.load_file('scancubeforandroid.kv')
        Builder.load_file('manualinputscreen.kv')
        Builder.load_file('cubegui.kv')

        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ScanCube(name="scanner"))
        sm.add_widget(ManualInputScreen(name='manual'))
        sm.add_widget(CubeGUI(name='cube'))

        return sm


if __name__ == "__main__":
    CubeApp().run()
