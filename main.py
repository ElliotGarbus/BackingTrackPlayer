import configstartup
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform

from pathlib import Path
import subprocess

from midi_control import MidiControl

# TODO: Update configstartup to ensure a clean start.  Preserve Window size
# TODO: Create popup of Midi commands

kv = """
<LeftLabel@Label>:
    text_size: self.size
    halign: 'right'
    valign: 'center' 
    padding: dp(2), dp(2)

<RightLabel@Label>:
    text_size: self.size
    halign: 'left'
    valign: 'center' 
    padding: dp(2), dp(2)

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
        font_size: sp(20)
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
        Spinner:
            id: speed
            text: root.speeds[2] # 1x
            values: root.speeds
            on_text: root.set_file(self.text)
    # GridLayout:
    #     size_hint_y: .4
    #     cols: 2
    #     LeftLabel:
    #         text: 'Play:'
    #     RightLabel:
    #         text: 'CC#1 0'
    #     LeftLabel:
    #         text: 'Stop:'
    #     RightLabel:
    #         text: 'CC#1 127'
    #     LeftLabel:
    #         text: 'Restart:'
    #     RightLabel:
    #         text: 'CC#2 127'
    #     LeftLabel:
    #         text: 'Volume:'
    #     RightLabel:
    #         text: 'CC#3 0-127'
    #     LeftLabel:
    #         text: 'Speed:'
    #     RightLabel:
    #         text: 'CC#4 0/5/7/12/15  1x/0.5x/.75x/1.25x/1.5x'
    BoxLayout:
        size_hint_y: None
        height: dp(24)
        Label:
            text: 'Drop File in Window'
        Button:
            text: 'Midi Commands'
        Label:
            text: 'Spacebar to Toggle Play/Stop'
"""


class RootBoxLayout(BoxLayout):
    error_msg = 'Invalid File or No File Selected'
    speeds = ['Speed 0.5x', 'Speed 0.75x', 'Speed 1x', 'Speed 1.25x', 'Speed 1.5x']
    time_stretched = ['Speed 0.5x', 'Speed 0.75x', 'Speed 1.25x', 'Speed 1.5x']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.track = None
        self.track_path = None  # holds the name of the 1x speed track
        self.track_stretched = None  # name of stretched track
        self.time_stretch_processes = {}
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar':  # Toggle between play and stop
            self.ids.play_toggle.state = 'down' if self.ids.play_toggle.state == 'normal' else 'normal'

    def set_backing_track(self, path):
        self.ids.speed.text = 'Speed 1x'
        self.track = SoundLoader.load(path)
        if not self.track:
            self.ids.file.text = self.error_msg
            self.track_path = None
        else:
            self.track_path = path
            self.ids.file.text = Path(path).stem
            self.track.loop = True
            self.time_stretch(path)

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
                self.ids.play_toggle.state = 'down'  # change is state cause track to play
            else:
                self.track.seek(0)
                self.track.play()
        except AttributeError:
            self.ids.file.text = self.error_msg

    def set_volume(self, v):  # v is from 0 to 127
        try:
            self.track.volume = v/127
        except AttributeError:
            self.ids.file.text = self.error_msg

    def time_stretch(self, fn):
        # create dir; delete old versions if different...
        Path('speeds').mkdir(exist_ok=True)
        # files are stored with _050, _075, _125, _150 appended to name
        p = Path(fn)
        stem = p.stem
        suffix = p.suffix
        sp = Path('speeds')
        for f in sp.glob('*'):
            if f.stem[:-4] + suffix != p.name:
                f.unlink()              # remove old files
        ts_files = {stem + ext + suffix for ext in ['_050', '_075', '_125', '_150']}
        disk_files = {f.name for f in sp.glob('*')}
        if ts_files <= disk_files:
            return  # use existing time stretch files
        else:
            self._generate_time_stretch(p, sp)  # input path, output path

    def _generate_time_stretch(self, p, sp):
        # p is the full input path, sp is the output path
        speeds = ['0.50', '0.75', '1.50', '1.25']
        self.time_stretch_processes.clear()
        for i, speed in enumerate(speeds):
            cmd = f'ffmpeg -y -i "{p}" -filter:a atempo={speed} "{sp / p.stem}_{speed.replace(".", "")}{p.suffix}"'
            self.time_stretch_processes[self.time_stretched[i]] = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                                                                   stderr=subprocess.DEVNULL)

    def set_file(self, text):
        track_p = Path(self.track_path)
        p = str(Path('speeds') / Path(track_p.stem))
        suffix = track_p.suffix
        file = {'Speed 0.5x': p + '_050' + suffix,
                'Speed 0.75x': p + '_075' + suffix,
                'Speed 1x': self.track_path,
                'Speed 1.25x': p + '_125' + suffix,
                'Speed 1.5x': p + '_150' + suffix}
        self.stop()
        # disable play button if track not yet generated
        self.track_stretched = file[text]
        if text in self.time_stretched and self.time_stretch_processes and \
                self.time_stretch_processes[text].poll() is None:
            self.ids.play_toggle.disabled = self.ids.speed.disabled = True
            self.wait_for_time_stretch()
        else:
            self.continue_set_file()

    def wait_for_time_stretch(self, *args):
        text = self.ids.speed.text
        if self.time_stretch_processes[text].poll() is None:
            # self.tmp_text = self.ids.file.text
            self.ids.file.text = 'Processing Time Stretch'
            Clock.schedule_once(self.wait_for_time_stretch, .1)
        else:
            self.ids.file.text = Path(self.track_path).stem
            self.continue_set_file()

    def continue_set_file(self):
        self.ids.play_toggle.disabled = self.ids.speed.disabled = False
        self.track = SoundLoader.load(self.track_stretched)
        if not self.track:
            self.ids.file.text = self.error_msg
        else:
            self.track.loop = True


class BackingTrackPlayerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mc = MidiControl()

    def build(self):
        self.title = 'Backing Track Player V1.0'
        self.use_kivy_settings = False
        Window.minimum_width = 800
        Window.minimum_height = 375
        Window.size = 800, 375
        Window.bind(on_dropfile=self._dropfile_action)
        return Builder.load_string(kv)

    def _dropfile_action(self, window, path):
        self.root.set_backing_track(path.decode())

    def on_start(self):
        names = self.mc.get_midi_ports()
        self.root.ids.midi_devices.values = names
        m_input = self.config.getdefault('MIDI', 'input', 'None')
        ch = self.config.get('MIDI', 'channel')
        song = self.config.get('Track', 'song')
        self.root.set_backing_track(song)  # before set midi ports - so errors can show in track area
        if m_input in names:
            self.mc.set_midi_port(m_input)
            self.mc.midi_channel = int(ch)
            self.root.ids.midi_devices.text = m_input
            self.root.ids.midi_ch.text = str(int(ch) + 1)
        Clock.schedule_interval(self.mc.read_midi_callback, .1)

    def open_settings(self, *largs):  # kivy control panel will not open
        pass

    def build_config(self, config):
        config.setdefaults('MIDI', {'input': 'None',
                                    'channel': 'None'})
        config.setdefaults('Track', {'song': 'None'})

    def get_application_config(self, defaultpath='%(appdir)s/%(appname)s.ini'):
        if platform == 'macosx':  # mac will not write into app folder
            s = '~/.%(appname)s.ini'
        else:
            s = defaultpath
        return super().get_application_config(defaultpath=s)

    def on_stop(self):
        if self.root.track_path:
            self.config.set('Track', 'song', self.root.track_path)
            if self.mc.midi_in_port and self.mc.midi_channel:
                self.config.set('MIDI', 'input', self.mc.midi_in_port.name)
                self.config.set('MIDI', 'channel', self.mc.midi_channel)
            self.config.write()


BackingTrackPlayerApp().run()
