import kociemba
from kivy.clock import Clock
from kivy.graphics import Line, Color, Mesh
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from RubiksCube import RubiksCube

COLOR_MAP = {
    'W': (1, 1, 1),
    'Y': (1, 1, 0),
    'G': (0, 1, 0),
    'B': (0, 0, 1),
    'O': (1, 0.5, 0),
    'R': (1, 0, 0),
}

INVERSE_MOVES = {
    "U": "U'", "U'": "U", "U2": "U2",
    "D": "D'", "D'": "D", "D2": "D2",
    "R": "R'", "R'": "R", "R2": "R2",
    "L": "L'", "L'": "L", "L2": "L2",
    "F": "F'", "F'": "F", "F2": "F2",
    "B": "B'", "B'": "B", "B2": "B2",
}


def draw_arrow(points, direction, _size):
    x1, y1, x2, y2, x3, y3, x4, y4 = points

    # side centers
    top_cx = (x2 + x3) / 2
    top_cy = (y2 + y3) / 2

    left_cx = (x1 + x2) / 2
    left_cy = (y1 + y2) / 2

    bottom_cx = (x1 + x4) / 2
    bottom_cy = (y1 + y4) / 2

    right_cx = (x3 + x4) / 2
    right_cy = (y3 + y4) / 2

    # quad center
    cx = (x1 + x2 + x3 + x4) / 4
    cy = (y1 + y2 + y3 + y4) / 4

    Color(0, 0, 0)

    if direction == "U":
        Line(points=[bottom_cx, bottom_cy, top_cx, top_cy], width=1.4)
        Line(points=[(right_cx + cx) / 2, (right_cy + cy) / 2,
                     top_cx, top_cy], width=1.4)
        Line(points=[(left_cx + cx) / 2, (left_cy + cy) / 2,
                     top_cx, top_cy], width=1.4)

    elif direction == "D":
        Line(points=[top_cx, top_cy, bottom_cx, bottom_cy], width=1.4)
        Line(points=[(right_cx + cx) / 2, (right_cy + cy) / 2,
                     bottom_cx, bottom_cy], width=1.4)
        Line(points=[(left_cx + cx) / 2, (left_cy + cy) / 2,
                     bottom_cx, bottom_cy], width=1.4)

    elif direction == "L":
        Line(points=[right_cx, right_cy, left_cx, left_cy], width=1.4)
        Line(points=[(top_cx + cx) / 2, (top_cy + cy) / 2,
                     left_cx, left_cy], width=1.4)
        Line(points=[(bottom_cx + cx) / 2, (bottom_cy + cy) / 2,
                     left_cx, left_cy], width=1.4)

    elif direction == "R":
        Line(points=[left_cx, left_cy, right_cx, right_cy], width=1.4)
        Line(points=[(top_cx + cx) / 2, (top_cy + cy) / 2,
                     right_cx, right_cy], width=1.4)
        Line(points=[(bottom_cx + cx) / 2, (bottom_cy + cy) / 2,
                     right_cx, right_cy], width=1.4)


class CubeGUI(Screen):  # Subclass Screen instead of BoxLayout
    solution_label = ObjectProperty(None)
    canvas_area = ObjectProperty(None)
    solve_btn = ObjectProperty(None)
    back_move_btn = ObjectProperty(None)
    next_btn = ObjectProperty(None)

    def __init__(self, cube_string=None, **kwargs):
        super().__init__(**kwargs)  # Passes screen routing parameters (like name='cube') safely
        self.solution = []
        self.index = 0

        if cube_string:
            self.cube = RubiksCube(cube_string)
        else:
            self.cube = RubiksCube()

        Clock.schedule_once(self.first_draw, 0)
        self.bind(size=self.on_resize)

    def first_draw(self, _dt):
        self.draw_cube()

    def on_resize(self, *_args):
        self.draw_cube()

    def solve_cube(self):
        self.solve_btn.disabled = True
        if not self.next_btn or not self.back_move_btn:
            return
        if self.cube.faces == self.cube.finalFaces:
            self.next_btn.disabled = True
            self.back_move_btn.disabled = True
            return
        else:
            try:
                self.solution = kociemba.solve(self.cube.to_kociemba_string()).split()
            except ValueError as err:
                manual_screen = self.manager.get_screen('manual')
                manual_screen.show_toast(str(err))
                self.manager.current = 'manual'
                self.solve_btn.disabled = False
                return

            self.solution_label.text = f"Solution(Total {len(self.solution)} moves): " + " ".join(self.solution)
            if self.solution:
                self.index = 0
                self.next_btn.disabled = False
                self.back_move_btn.disabled = True

    def next_move(self):
        if self.cube.faces == self.cube.finalFaces:
            self.next_btn.disabled = True
            self.back_move_btn.disabled = False
            self.draw_cube()
            return
        else:
            if self.index >= len(self.solution):
                self.next_btn.disabled = True
                return
            else:
                move = self.solution[self.index]
                print(f"Move({self.index + 1}): {move}")
                self.draw_cube(move)
                self.cube.execute_move(move)
                self.solution_label.text = f"Move {self.index + 1}/{len(self.solution)}: {move}"
                self.index += 1
                if self.index > 1:
                    self.back_move_btn.disabled = False

    def back_move(self):
        if self.index > 0:
            self.index -= 1
            move = self.solution[self.index]
            inverse_move = INVERSE_MOVES[move]
            self.cube.execute_move(inverse_move)
            self.draw_cube(move)
            self.solution_label.text = f"Move {self.index + 1}/{len(self.solution)}: {move}"
            # Update button states
            self.next_btn.disabled = False
            if self.index == 0:
                self.back_move_btn.disabled = True  # Gray out if we are back at the start

    def go_back(self):
        if self.next_btn:
            self.next_btn.disabled = True
        if self.back_move_btn:
            self.back_move_btn.disabled = True
        if self.manager:
            self.solve_btn.disabled = False
            self.manager.current = 'menu'

    def draw_cube(self, move=None):
        # CRITICAL GUARD: Stop code from running until Kivy maps the KV properties completely
        if not self.canvas_area:
            return

        # Clears older canvas elements clean on refresh
        self.canvas_area.canvas.clear()

        # Dynamically calculate size and position
        size = self.canvas_area.height / 6
        dx_front = size * 0.85  # Slightly wider front
        dx_right = size * 0.75  # Slightly narrower right
        dy = -size * 0.22

        origin_x = self.canvas_area.x + self.canvas_area.width / 2 - 3 * (dx_front + dx_right) / 2
        origin_y = self.canvas_area.y + self.canvas_area.height / 2 - 1.5 * size

        # Top face
        for i in range(3):
            for j in range(3):
                color = COLOR_MAP[self.cube.faces['U'][i][j]]

                x = origin_x + j * dx_front + (2 - i) * dx_right
                y = origin_y + j * dy - (2 - i) * dy + 3 * size
                with self.canvas_area.canvas:
                    pts = [
                        x, y,
                        x + dx_front, y + dy,
                        x + dx_right + dx_front, y,
                        x + dx_right, y - dy
                    ]
                    Color(*color)
                    Mesh(vertices=[
                        x, y, 0, 0,
                        x + dx_right, y - dy, 0, 0,
                        x + dx_right + dx_front, y, 0, 0,
                        x + dx_front, y + dy, 0, 0
                    ], indices=[0, 1, 2, 0, 2, 3], mode='triangles')
                    Color(0, 0, 0)
                    Line(points=[x, y, x + dx_right, y - dy, x + dx_right + dx_front, y, x + dx_front, y + dy, x, y],
                         width=0.5)

                    if (move == "B" or move == "B2") and i == 0:
                        draw_arrow(pts, "D", size)

                    elif move == "B'" and i == 0:
                        draw_arrow(pts, "U", size)

                    elif (move == "F" or move == "F2") and i == 2:
                        draw_arrow(pts, "U", size)

                    elif move == "F'" and i == 2:
                        draw_arrow(pts, "D", size)

                    elif (move == "L" or move == "L2") and j == 0:
                        draw_arrow(pts, "L", size)

                    elif move == "L'" and j == 0:
                        draw_arrow(pts, "R", size)

                    elif (move == "R" or move == "R2") and j == 2:
                        draw_arrow(pts, "R", size)

                    elif move == "R'" and j == 2:
                        draw_arrow(pts, "L", size)

        # Right face
        for i in range(3):
            for j in range(3):
                color = COLOR_MAP[self.cube.faces['R'][i][j]]
                x = origin_x + j * dx_right + 3 * dx_front
                y = origin_y - j * dy + (2 - i) * size + 3 * dy

                with self.canvas_area.canvas:
                    pts = [
                        x, y,
                        x, y + size,
                        x + dx_right, y - dy + size,
                        x + dx_right, y - dy
                    ]
                    Color(*color)
                    Mesh(vertices=[
                        x, y, 0, 0,
                        x, y + size, 0, 0,
                        x + dx_right, y - dy + size, 0, 0,
                        x + dx_right, y - dy, 0, 0
                    ], indices=[0, 1, 2, 0, 2, 3], mode='triangles')
                    Color(0, 0, 0)
                    Line(points=[x, y, x, y + size, x + dx_right, y - dy + size, x + dx_right, y - dy, x, y], width=0.5)

                    if (move == "U" or move == "U2") and i == 0:
                        draw_arrow(pts, "L", size)

                    elif move == "U'" and i == 0:
                        draw_arrow(pts, "R", size)

                    elif (move == "D" or move == "D2") and i == 2:
                        draw_arrow(pts, "R", size)

                    elif move == "D'" and i == 2:
                        draw_arrow(pts, "L", size)

                    elif (move == "F" or move == "F2") and j == 0:
                        draw_arrow(pts, "D", size)

                    elif move == "F'" and j == 0:
                        draw_arrow(pts, "U", size)

                    elif (move == "B" or move == "B2") and j == 2:
                        draw_arrow(pts, "U", size)

                    elif move == "B'" and j == 2:
                        draw_arrow(pts, "D", size)

        # Front face
        for i in range(3):
            for j in range(3):
                color = COLOR_MAP[self.cube.faces['F'][i][j]]
                x = origin_x + j * dx_front
                y = origin_y + j * dy + (2 - i) * size

                with self.canvas_area.canvas:
                    pts = [
                        x, y,
                        x, y + size,
                        x + dx_front, y + dy + size,
                        x + dx_front, y + dy,
                    ]
                    Color(*color)
                    Mesh(vertices=[
                        x, y, 0, 0,
                        x + dx_front, y + dy, 0, 0,
                        x + dx_front, y + dy + size, 0, 0,
                        x, y + size, 0, 0
                    ], indices=[0, 1, 2, 0, 2, 3], mode='triangles')
                    Color(0, 0, 0)
                    Line(points=[x, y, x + dx_front, y + dy, x + dx_front, y + dy + size, x, y + size, x, y], width=0.5)

                    if (move == "U" or move == "U2") and i == 0:
                        draw_arrow(pts, "L", size)

                    elif move == "U'" and i == 0:
                        draw_arrow(pts, "R", size)

                    elif (move == "D" or move == "D2") and i == 2:
                        draw_arrow(pts, "R", size)

                    elif move == "D'" and i == 2:
                        draw_arrow(pts, "L", size)

                    elif (move == "L" or move == "L2") and j == 0:
                        draw_arrow(pts, "D", size)

                    elif move == "L'" and j == 0:
                        draw_arrow(pts, "U", size)

                    elif (move == "R" or move == "R2") and j == 2:
                        draw_arrow(pts, "U", size)

                    elif move == "R'" and j == 2:
                        draw_arrow(pts, "D", size)
