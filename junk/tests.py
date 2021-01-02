from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

import mido
import mido.backends.rtmidi

kv = """
BoxLayout:
    Button:
        text: 'WTF'
"""


class TestApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inport = None

    def build(self):
        return Builder.load_string(kv)

    def on_start(self):
        print(mido.get_input_names())
        self.inport = mido.open_input('SSCOM 0')
        Clock.schedule_interval(self.read_midi_callback, .1)

    def read_midi_callback(self, dt):
        for msg in self.inport.iter_pending():
            print(msg)

TestApp().run()