from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

from Game.game import Game

"""
# デフォルトに使用するフォントを変更する
resource_add_path('fonts')
# 日本語が使用できるように日本語フォントを指定する
LabelBase.register(DEFAULT_FONT, 'mplus-2c-regular.ttf')

"""


class SampleGridLayout(GridLayout):
    def loop(self, dt):
        stage, move = self.g.loop()
        l = stage.stage_list(move_puyo=True)
        for y in range(len(l)):
            for x in range(len(l[0])):
                puyo = str(l[y][x])
                self.labels[y][x].text = puyo

    def __init__(self, g:Game):
        super().__init__()
        self.g = g
        self.interval = self.g.interval
        self.g.next()

        self.labels = []
        self.rows = self.g.stage.height()
        self.cols = self.g.stage.width()

        for y in range(self.rows):
            self.labels.append([])
            for x in range(self.cols):
                label = Label(text=f"{x},{y}")
                self.add_widget(label)
                self.labels[y].append(label)

        Clock.schedule_interval(self.loop, 0.5)


class MainScreen(BoxLayout):
    def pushbutton(self,b):
        self.g.move_to = b

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.g = Game()
        self.grid = SampleGridLayout(self.g)
        self.add_widget(self.grid)
        self.boxlayout = BoxLayout(orientation = "vertical")
        self.add_widget(self.boxlayout)

        # blに追加する３つのボタンを用意
        right = Button(text="right")
        left = Button(text="left")
        t_right = Button(text="turn right")
        t_left = Button(text="turn left")

        right.bind(on_press=lambda button: self.pushbutton('r'))
        left.bind(on_press=lambda button: self.pushbutton('l'))
        t_right.bind(on_press=lambda button: self.pushbutton('t_r'))
        t_left.bind(on_press=lambda button: self.pushbutton('t_l'))
        self.boxlayout.add_widget(right)
        self.boxlayout.add_widget(left)
        self.boxlayout.add_widget(t_right)
        self.boxlayout.add_widget(t_left)

class MainApp(App):
    def build(self):
        MS = MainScreen()
        return MS


if __name__ == "__main__":
    MainApp().run()
