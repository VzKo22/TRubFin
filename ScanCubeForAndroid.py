import cv2
import numpy as np

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.camera import Camera
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty


def detect_color(hsv):
    h, s, v = hsv
    if s < 40 and v > 150:
        return 'W'
    if h < 10 or h > 170:
        return 'R'
    if 10 <= h <= 20:
        return 'O'
    if 20 < h <= 35:
        return 'Y'
    if 35 < h <= 85:
        return 'G'
    if 85 < h <= 140:
        return 'B'
    return '?'


class ScanCube(Screen):
    # Establish a formal link to the image container defined in KV
    img = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # CAMERA (Instantiated and kept strictly in memory for context textures)
        self.camera = Camera(
            play=True,
            resolution=(1280, 720),
            size_hint=(0.75, 0.75),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # STATE DATA
        self.scan_order = ['U', 'R', 'F', 'D', 'L', 'B']

        self.center_colors = {
            'U': 'W',
            'R': 'R',
            'F': 'G',
            'D': 'Y',
            'L': 'O',
            'B': 'B',
        }

        self.current_face_index = 0
        self.current_face_data = None
        self.captured_faces = {}
        self.face_captured = False

    def on_enter(self):
        self.camera.play = True
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1 / 30)

    def on_leave(self):
        Clock.unschedule(self.update)
        self.camera.play = False

    def update(self, _dt):
        if self.current_face_index >= len(self.scan_order):
            return

        texture = self.camera.texture
        if texture is None:
            return

        size = texture.size
        pixels = texture.pixels

        frame = np.frombuffer(pixels, np.uint8).reshape(size[1], size[0], 4)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.flip(frame, 1)

        h, w = frame.shape[:2]

        # GRID GEOMETRY
        size_grid = size[1] // 2
        cell = size_grid // 3
        start_x = w // 2 - size_grid // 2
        start_y = h // 2 - size_grid // 2

        # DRAW MATRIX LINES
        for i in range(4):
            cv2.line(frame, (start_x + i * cell, start_y), (start_x + i * cell, start_y + size_grid), (255, 255, 255), 2)
            cv2.line(frame, (start_x, start_y + i * cell), (start_x + size_grid, start_y + i * cell), (255, 255, 255), 2)

        face = self.scan_order[self.current_face_index]
        cv2.putText(frame, f"Scan Face: {face}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        status = "Captured" if self.face_captured else "Not Captured"
        cv2.putText(frame, status, (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        face_data = []

        for row in range(3):
            current_row = []
            for col in range(3):
                cx = start_x + col * cell + cell // 2
                cy = start_y + row * cell + cell // 2

                cx = max(0, min(cx, w - 1))
                cy = max(0, min(cy, h - 1))

                hsv = hsv_frame[cy, cx]
                color = detect_color(hsv)
                current_row.append(color)

                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(frame, color, (cx - 10, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            face_data.append(current_row)

        face_data[1][1] = self.center_colors[face]
        self.current_face_data = face_data

        # BLIT DATA TO SCREEN
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        buf = cv2.flip(frame, 0).tobytes()

        texture_out = Texture.create(size=(w, h), colorfmt='rgb')
        texture_out.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

        # Push the fresh openCV texture calculation into our KV layout image placeholder
        if self.img:
            self.img.texture = texture_out

    def capture_face(self):
        if self.current_face_data is None:
            return

        face = self.scan_order[self.current_face_index]
        self.captured_faces[face] = [row[:] for row in self.current_face_data]
        self.face_captured = True

    def next_face(self):
        if not self.face_captured:
            return

        face = self.scan_order[self.current_face_index]
        manual = self.manager.get_screen('manual')
        manual.set_face(face, self.captured_faces[face])

        self.current_face_index += 1
        self.face_captured = False

        if self.current_face_index >= len(self.scan_order):
            if self.manager:
                self.manager.current = 'manual'

    def redo_face(self):
        face = self.scan_order[self.current_face_index]
        if face in self.captured_faces:
            del self.captured_faces[face]
        self.face_captured = False

    def go_back_face(self):
        if self.current_face_index <= 0:
            return

        self.current_face_index -= 1
        face = self.scan_order[self.current_face_index]
        self.face_captured = (face in self.captured_faces)

    def back_to_menu(self):
        if self.parent:
            self.parent.current = 'menu'

