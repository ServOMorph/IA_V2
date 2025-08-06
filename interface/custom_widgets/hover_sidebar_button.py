from kivy.uix.button import Button
from kivy.core.window import Window


class HoverSidebarButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.hover_color = (0.3, 0.3, 0.3, 1)
        self.default_color = (0, 0, 0, 0)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside:
            self.background_color = self.hover_color
            Window.set_system_cursor("hand")
        else:
            self.background_color = self.default_color
            Window.set_system_cursor("arrow")
