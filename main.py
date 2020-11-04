import configstartup
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

from pathlib import Path

from midi_control import MidiControl

kv = """
RootBoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        Label:
            text: 'Midi Device & Channel'
        Spinner:
            id: midi_devices
            text: 'Select Midi Device'
            on_text: app.mc.set_midi_port(self.text)
        Spinner:
            id: midi_ch
            text: 'Select Midi Channel'
            values: [str(n) for n in range(1, 17)]
            on_text: app.mc.set_midi_channel(self.text)
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
        self.track_path = None  # holds the name of the track

    def set_backing_track(self, path):
        self.track = SoundLoader.load(path)
        if not self.track:
            self.ids.file.text = self.error_msg
            self.track_path = None
        else:
            self.track_path = path
            self.ids.file.text = Path(path).stem
            self.track.loop = True

    def play(self):
        try:
            self.track.play()
            self.ids.play_toggle.state = 'down'
        except AttributeError:
            self.ids.file.text = self.error_msg

    def stop(self):
        try:
            self.track.stop()
            self.ids.play_toggle.state = 'normal'
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

    def set_volume(self, v):  # v is from 0 to 127
        try:
            self.track.volume = v/127
        except AttributeError:
            self.ids.file.text = self.error_msg


class BackingTrackPlayerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mc = MidiControl()

    def build(self):
        self.title = 'Backing Track Player V1.0'
        self.use_kivy_settings = False
        Window.bind(on_dropfile=self._dropfile_action)
        return Builder.load_string(kv)

    def _dropfile_action(self, window, path):
        self.root.set_backing_track(path.decode())

    def on_start(self):
        names = self.mc.get_midi_ports()
        self.root.ids.midi_devices.values = names
        input = self.config.getdefault('MIDI', 'input', 'None')
        ch = self.config.get('MIDI', 'channel')
        song = self.config.get('Track', 'song')
        if input in names:
            self.root.set_backing_track(song)
            self.mc.set_midi_port(input)
            self.mc.midi_channel = int(ch)
            self.root.ids.midi_devices.text = input
            self.root.ids.midi_ch.text = str(int(ch) + 1)
        Clock.schedule_interval(self.mc.read_midi_callback, .1)

    def open_settings(self, *largs):  # kivy control panel will not open
        pass

    def build_config(self, config):
        config.setdefaults('MIDI', {'input': 'None',
                                    'channel': 'None'})
        config.setdefaults('Track', {'song': 'None'})

    def on_stop(self):
        if self.mc.midi_in_port and self.mc.midi_channel is not None and self.root.track_path:
            self.config.set('MIDI', 'input', self.mc.midi_in_port.name)
            self.config.set('MIDI', 'channel', self.mc.midi_channel)
            self.config.set('Track', 'song', self.root.track_path)
            self.config.write()


BackingTrackPlayerApp().run()
