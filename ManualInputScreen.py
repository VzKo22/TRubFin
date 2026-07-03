from collections import Counter

from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.label import Label

from RubiksCube import RubiksCube


def is_valid_cube_string(s):
    if len(s) != 54:
        return False, "Cube string must be 54 characters"

    allowed = set("WRGYOB")
    if any(c not in allowed for c in s):
        return False, "Invalid colors detected"

    # Must have exactly 9 of each color
    count = Counter(s)
    for c in allowed:
        if count[c] != 9:
            return False, "Each color must appear 9 times"

    return True, ""


class ManualInputScreen(Screen):
    palette_layout = ObjectProperty(None)
    net_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_color = 'W'

        self.colors = {
            'W': (1, 1, 1, 1),
            'Y': (1, 1, 0, 1),
            'R': (1, 0, 0, 1),
            'O': (1, 0.5, 0, 1),
            'G': (0, 1, 0, 1),
            'B': (0, 0, 1, 1),
        }

        self.cube_data = {
            'U': [['W'] * 3 for _ in range(3)],
            'R': [['R'] * 3 for _ in range(3)],
            'F': [['G'] * 3 for _ in range(3)],
            'D': [['Y'] * 3 for _ in range(3)],
            'L': [['O'] * 3 for _ in range(3)],
            'B': [['B'] * 3 for _ in range(3)],
        }

        self.stickers = {}
        self._initialized = False

    def on_enter(self, *args):
        """
        Runs whenever the screen shifts into view. We delay layout generation
        by 0.05 seconds to ensure Kivy's layout engine has finalized sizes.
        """
        if not self._initialized:
            Clock.schedule_once(self.initialize_dynamic_layouts, 0.05)
            self._initialized = True
        else:
            self.refresh_sticker_colors()

    def initialize_dynamic_layouts(self, _dt=None):
        # Double check to prevent crashes if KV isn't ready
        if not self.palette_layout or not self.net_layout:
            return

        self.palette_layout.clear_widgets()
        self.net_layout.clear_widgets()

        # 1. Populate Palette Buttons
        for color_name, rgba in self.colors.items():
            btn = Button(
                background_normal='',
                background_color=rgba
            )
            btn.bind(on_press=lambda inst, c=color_name: self.select_color(c))
            self.palette_layout.add_widget(btn)

        # 2. Force grid rules
        self.net_layout.cols = 12
        self.net_layout.rows = 9

        # 3. Build layout matrix stickers
        self.build_cube_net()

    def select_color(self, color):
        self.selected_color = color

    def build_cube_net(self):
        layout = {
            'U': (3, 0),
            'L': (0, 3),
            'F': (3, 3),
            'R': (6, 3),
            'B': (9, 3),
            'D': (3, 6)
        }

        for row in range(9):
            for col in range(12):
                added = False
                for face, (fx, fy) in layout.items():
                    if fx <= col < fx + 3 and fy <= row < fy + 3:
                        r = row - fy
                        c = col - fx

                        sticker = Button(
                            background_normal='',
                            background_color=self.colors[self.cube_data[face][r][c]]
                        )
                        sticker.face = face
                        sticker.row = r
                        sticker.col = c
                        sticker.bind(on_press=self.paint_sticker)

                        self.stickers[(face, r, c)] = sticker
                        self.net_layout.add_widget(sticker)
                        added = True
                        break

                if not added:
                    self.net_layout.add_widget(Widget())

    def refresh_sticker_colors(self):
        for (face, r, c), sticker in self.stickers.items():
            color_letter = self.cube_data[face][r][c]
            sticker.background_color = self.colors[color_letter]

    def reset_cube(self):
        self.cube_data = {
            'U': [['W'] * 3 for _ in range(3)],
            'R': [['R'] * 3 for _ in range(3)],
            'F': [['G'] * 3 for _ in range(3)],
            'D': [['Y'] * 3 for _ in range(3)],
            'L': [['O'] * 3 for _ in range(3)],
            'B': [['B'] * 3 for _ in range(3)],
        }
        self.refresh_sticker_colors()
        self.selected_color = 'W'

    def go_back(self):
        if self.parent:
            self.parent.current = 'menu'

    def set_face(self, face, data):
        self.cube_data[face] = data
        self.refresh_sticker_colors()

    def paint_sticker(self, sticker):
        if sticker.row == 1 and sticker.col == 1:
            return

        color = self.selected_color
        sticker.background_color = self.colors[color]
        self.cube_data[sticker.face][sticker.row][sticker.col] = color

    def generate_cube_string(self):
        cube_string = ''
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            for row in self.cube_data[face]:
                cube_string += ''.join(row)
        return cube_string

    def show_toast(self, message, duration=3):
        toast = Label(
            text=message,
            font_size="24sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
            pos_hint={"center_x": 0.5, "y": 0.5}
        )

        with toast.canvas.before:
            Color(0, 0, 0, 0.7)
            toast.bg = Rectangle(pos=toast.pos, size=toast.size)

        toast.bind(pos=lambda *a: setattr(toast.bg, "pos", toast.pos),
                   size=lambda *a: setattr(toast.bg, "size", toast.size))

        self.add_widget(toast)

        Clock.schedule_once(lambda dt: self.remove_widget(toast), duration)

    def continue_to_solver(self):
        cube_string = self.generate_cube_string()
        valid, msg = is_valid_cube_string(cube_string)

        if not valid:
            self.show_toast(msg)
            return

        # 1. Grab the CubeGUI screen directly from the manager
        cube_screen = self.manager.get_screen('cube')

        # 2. Update its internal RubiksCube object data with the new string
        cube_screen.cube = RubiksCube(cube_string)

        # 3. Reset the move solution steps index
        cube_screen.index = 0
        cube_screen.solution = []
        cube_screen.solution_label.text = "Solution: "

        # 4. Clear the layout canvas and force a fresh frame draw
        cube_screen.draw_cube()

        # 5. Switch over to the screen view
        self.manager.current = 'cube'
