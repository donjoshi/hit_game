import random
from re import T
from kivy import platform
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.properties import StringProperty, BooleanProperty
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.properties import Clock
from kivy.properties import NumericProperty
from kivy.graphics.vertex_instructions import Rectangle, Ellipse, Quad, Triangle
from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')


class MainWidget(Widget):

    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 30
    V_LINES_SPACING = .05  # in screen width
    vertical_lines = []

    H_NB_LINES = 50
    H_LINES_SPACING = .06  # in screen width
    horizontal_lines = []

    SPEED = 4

    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 3
    current_speed_x = 0
    current_offset_x = 0

    NB_TILES = 12
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_tiles()
        self.init_ship()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(
                self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True

        return False

    def init_ship(self):
        with self.canvas:
            Color(1, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y*self.height
        ship_half_width = self.SHIP_WIDTH*self.width / 2
        ship_height = self.SHIP_HEIGHT*self.height

        x1, y1 = self.transform(center_x-ship_half_width, base_y)
        x2, y2 = self.transform(center_x, base_y + ship_height)
        x3, y3 = self.transform(center_x+ship_half_width, base_y)

        self.ship.points = {x1, y1, x2, y2, x3, y3}

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)

            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 25):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_y = 0

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_y = last_coordinates[1]+1

        print("foo1")

        for i in range(len(self.tiles_coordinates), self.NB_TILES):

            start_index = -int(self.V_NB_LINES/2)+1
            end_index = start_index+self.V_NB_LINES-1

            r = random.randint(-10, 10)

            if r < start_index:
                r = start_index
            if r > end_index:
                r = end_index-1

            self.tiles_coordinates.append((r, last_y))
            last_y += 1

        print("foo2")

    def init_vertical_line(self):
        with self.canvas:
            Color(1, 1, 1)
            #self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING*self.width
        offset = index-0.5
        line_x = central_line_x+offset*spacing+self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING*self.height
        line_y = index*spacing_y-self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y-self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)

        return x, y

    def update_tiles(self):

        for i in range(0, self.NB_TILES):

            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(
                tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(
                tile_coordinates[0]+1, tile_coordinates[1]+1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):

        start_index = -int(self.V_NB_LINES/2)+1

        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_line(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):

        start_index = -int(self.V_NB_LINES/2)+1
        end_index = start_index+self.V_NB_LINES-1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)

        #spacing_y = self.H_LINES_SPACING*self.height
        for i in range(0, self.H_NB_LINES):

            line_y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)

            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        # print("update")
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        self.current_offset_y += self.SPEED*time_factor

        spacing_y = self.H_LINES_SPACING*self.height
        if self.current_offset_y > spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1
            self.generate_tiles_coordinates()
            print("loop : " + str(self.current_y_loop))

        self.current_offset_x += self.current_speed_x*time_factor


class Hit_game(App):
    pass


Hit_game().run()
