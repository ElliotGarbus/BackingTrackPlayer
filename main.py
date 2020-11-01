from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window

from pathlib import Path

kv = """
BoxLayout:
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
        Button:
            text: 'Play'
        Button:
            text: 'Stop'
    
    Label:
        text: 'Play: CC#1 00\\nStop: CC#1 127\\nRestart: CC#2 127\\nVol: CC#3 0-127 ' 

"""


class BackingTrackPlayerApp(App):
    def build(self):
        Window.bind(on_dropfile=self._dropfile)
        return Builder.load_string(kv)

    def _dropfile(self, window, path):
        print(path)
        self.root.ids.file.text = Path(path.decode()).stem

BackingTrackPlayerApp().run()