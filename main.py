from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader

from pathlib import Path

kv = """
RootBoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        Label:
            text: 'Midi Device & Channel'
        Spinner:
            text: 'Midi Device'
        Spinner:
            text: 'Midi Ch'
            values: [str(n) for n in range(1, 17)]
    Label:
        id: file
        text: 'Background Track Player'  # Replace with filename
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        Button:
            text: 'Restart'
            on_release: root.restart()
        ToggleButton:
            id: play_toggle
            text: {'normal': 'Play', 'down': 'Stop'} [self.state]
            on_state:
                if self.state == 'down': root.play()
                if self.state == 'normal': root.stop()

    Label:
        size_hint_y: .25
        text: 'Play: CC#1 00\\nStop: CC#1 127\\nRestart: CC#2 127\\nVol: CC#3 0-127 ' 

"""


class RootBoxLayout(BoxLayout):
    error_msg = 'Invalid File or No File Selected'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.track = None

    def set_backing_track(self, path):
        self.track = SoundLoader.load(path)
        if not self.track:
            self.ids.file.text = self.error_msg
        else:
            self.ids.file.text = Path(path).stem
            self.track.loop = True

    def play(self):
        try:
            self.track.play()
        except AttributeError:
            self.ids.file.text = self.error_msg

    def stop(self):
        try:
            self.track.stop()
        except AttributeError:
            self.ids.file.text = self.error_msg

    def restart(self):
        try:
            if self.track.state == 'stop':
                self.ids.play_toggle.state = 'down'
            else:
                self.track.play()
        except AttributeError:
            self.ids.file.text = self.error_msg


class BackingTrackPlayerApp(App):
    def build(self):
        Window.bind(on_dropfile=self._dropfile_action)
        return Builder.load_string(kv)

    def _dropfile_action(self, window, path):
        self.root.set_backing_track(path.decode())


BackingTrackPlayerApp().run()
