class RubiksCube:
    def __init__(self, cubeState="WWWWWWWWWRRRRRRRRRGGGGGGGGGYYYYYYYYYOOOOOOOOOBBBBBBBBB"):
        if len(cubeState) != 54:
            print('Wrong input')

        self.startState = cubeState
        parts = [cubeState[i:i + 9] for i in range(0, 54, 9)]

        self.faces = {
            'U': [list(parts[0][i:i + 3]) for i in range(0, 9, 3)],
            'R': [list(parts[1][i:i + 3]) for i in range(0, 9, 3)],
            'F': [list(parts[2][i:i + 3]) for i in range(0, 9, 3)],
            'D': [list(parts[3][i:i + 3]) for i in range(0, 9, 3)],
            'L': [list(parts[4][i:i + 3]) for i in range(0, 9, 3)],
            'B': [list(parts[5][i:i + 3]) for i in range(0, 9, 3)]
        }

        self.finalFaces = {
            'U': [['W'] * 3 for _ in range(3)],
            'D': [['Y'] * 3 for _ in range(3)],
            'L': [['O'] * 3 for _ in range(3)],
            'R': [['R'] * 3 for _ in range(3)],
            'F': [['G'] * 3 for _ in range(3)],
            'B': [['B'] * 3 for _ in range(3)],
        }

        self.move_map = {
            "R": self.R,
            "R_prime": self.R_prime,
            "L": self.L,
            "L_prime": self.L_prime,
            "U": self.U,
            "U_prime": self.U_prime,
            "F": self.F,
            "F_prime": self.F_prime,
            "D": self.D,
            "D_prime": self.D_prime,
            "B": self.B,
            "B_prime": self.B_prime,
        }

    def to_kociemba_string(self):
        color_to_face = {
            'W': 'U',
            'R': 'R',
            'G': 'F',
            'Y': 'D',
            'O': 'L',
            'B': 'B'
        }

        CtF = ''.join(color_to_face[c] for c in self.startState)

        return CtF

    # ---------- Utility -----------------
    def rotate_face_cw(self, face):
        self.faces[face] = [list(x) for x in zip(*self.faces[face][::-1])]

    def rotate_face_ccw(self, face):
        self.faces[face] = [list(x) for x in zip(*self.faces[face])]
        self.faces[face].reverse()

    # ---------- Moves -------------------
    def move(self, m):
        # move dictionary
        moves = {
            'U': self.U, "U'": self.U_prime,
            'D': self.D, "D'": self.D_prime,
            'L': self.L, "L'": self.L_prime,
            'R': self.R, "R'": self.R_prime,
            'F': self.F, "F'": self.F_prime,
            'B': self.B, "B'": self.B_prime,
        }
        moves[m]()

    # ---- U (Up) ----
    def U(self):
        self.rotate_face_cw('U')
        temp = self.faces['F'][0][:]
        self.faces['F'][0] = self.faces['R'][0][:]
        self.faces['R'][0] = self.faces['B'][0][:]
        self.faces['B'][0] = self.faces['L'][0][:]
        self.faces['L'][0] = temp

    def U_prime(self):
        for _ in range(3):
            self.U()

    # ---- D (Down) ----
    def D(self):
        self.rotate_face_cw('D')
        temp = self.faces['F'][2][:]
        self.faces['F'][2] = self.faces['L'][2][:]
        self.faces['L'][2] = self.faces['B'][2][:]
        self.faces['B'][2] = self.faces['R'][2][:]
        self.faces['R'][2] = temp

    def D_prime(self):
        for _ in range(3):
            self.D()

    # ---- L (Left) ----
    def L(self):
        self.rotate_face_cw('L')
        temp = [row[0] for row in self.faces['F']]
        for i in range(3):
            self.faces['F'][i][0] = self.faces['U'][i][0]
        for i in range(3):
            self.faces['U'][i][0] = self.faces['B'][2 - i][2]
        for i in range(3):
            self.faces['B'][i][2] = self.faces['D'][2 - i][0]
        for i in range(3):
            self.faces['D'][i][0] = temp[i]

    def L_prime(self):
        for _ in range(3):
            self.L()

    # ---- R (Right) ----
    def R(self):
        self.rotate_face_cw('R')
        temp = [row[2] for row in self.faces['F']]
        for i in range(3):
            self.faces['F'][i][2] = self.faces['D'][i][2]
        for i in range(3):
            self.faces['D'][i][2] = self.faces['B'][2 - i][0]
        for i in range(3):
            self.faces['B'][i][0] = self.faces['U'][2 - i][2]
        for i in range(3):
            self.faces['U'][i][2] = temp[i]

    def R_prime(self):
        for _ in range(3):
            self.R()

    # ---- F (Front) ----
    def F(self):
        self.rotate_face_cw('F')
        temp = self.faces['U'][2][:]
        self.faces['U'][2] = [self.faces['L'][2 - i][2] for i in range(3)]
        for i in range(3):
            self.faces['L'][i][2] = self.faces['D'][0][i]
        self.faces['D'][0] = [self.faces['R'][2 - i][0] for i in range(3)]
        for i in range(3):
            self.faces['R'][i][0] = temp[i]

    def F_prime(self):
        for _ in range(3):
            self.F()

    # ---- B (Back) ----
    def B(self):
        self.rotate_face_cw('B')
        temp = self.faces['U'][0][:]
        self.faces['U'][0] = [self.faces['R'][i][2] for i in range(3)]
        for i in range(3):
            self.faces['R'][i][2] = self.faces['D'][2][2 - i]
        for i in range(3):
            self.faces['D'][2][i] = self.faces['L'][i][0]
        for i in range(3):
            self.faces['L'][i][0] = temp[2 - i]

    def B_prime(self):
        for _ in range(3):
            self.B()

    def call_move(self, move):
        self.move_map[move]()

    def execute_move(self, move):
        if move.endswith("2"):
            base = move[0]
            self.call_move(base)
            self.call_move(base)

        elif move.endswith("'"):
            base = move[0]
            self.call_move(base + "_prime")

        else:
            self.call_move(move)
