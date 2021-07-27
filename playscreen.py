from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import platform

from pathlib import Path
import subprocess
import shlex

Builder.load_string("""
<PlayScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: file
            text: 'Background Track Player'  # Replace with filename
            font_size: sp(20)
        Label:
            size_hint_y: None
            height: dp(24)
            text: 'Drop File in Window'
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
                text: root.speeds[2]
                values: root.speeds
                on_text: root.set_file(self.text)
        Label:
            size_hint_y: None
            height: dp(24)
            text: 'Spacebar to Toggle Play/Stop'
""")


class PlayScreen(Screen):
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
            self.file.text = self.error_msg

    def set_volume(self, v):  # v is from 0 to 127
        try:
            self.track.volume = v / 127
        except AttributeError:
            self.ids.file.text = self.error_msg

    def set_speed(self, value):
        #  value from midi cc message : 1, 2, 3, 4, 5 for speeds  1x, 0.5x, .75x, 1.25x, 1.5x respectively
        if value not in [1, 2, 3, 4, 5]:
            return
        m_speeds = ['Speed 1x', 'Speed 0.5x', 'Speed 0.75x', 'Speed 1.25x', 'Speed 1.5x']
        self.ids.speed.text = m_speeds[value - 1]

    def time_stretch(self, fn):
        # create dir; delete old versions if different...
        app = App.get_running_app()
        speed_dir = Path(app.user_data_dir) / 'speeds'
        speed_dir.mkdir(exist_ok=True)
        # files are stored with _050, _075, _125, _150 appended to name
        p = Path(fn)
        stem = p.stem
        suffix = p.suffix
        # files not related to the current track are deleted in on_stop
        ts_files = {stem + ext + suffix for ext in ['_050', '_075', '_125', '_150']}
        disk_files = {f.name for f in speed_dir.glob('*')}
        if ts_files <= disk_files:
            return  # use existing time stretch files
        else:
            self._generate_time_stretch(p, speed_dir)  # input path, output path

    def _generate_time_stretch(self, p, sp):
        # p is the full input path, sp is the output path
        speeds = ['0.50', '0.75', '1.50', '1.25']
        self.time_stretch_processes.clear()
        cf = subprocess.CREATE_NO_WINDOW if platform == 'win' else 0  # no windows with Popen on Win10
        exe_path = Path(__file__).parent / 'ffmpeg'
        for i, speed in enumerate(speeds):
            cmd = f'"{exe_path}" -y -i "{p}" -filter:a atempo={speed} "{sp / p.stem}_{speed.replace(".", "")}{p.suffix}"'
            self.time_stretch_processes[self.time_stretched[i]] = \
                subprocess.Popen(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, creationflags=cf)

    def set_file(self, text):
        if not self.track_path:
            return
        track_p = Path(self.track_path)
        app = App.get_running_app()
        p = str(Path(app.user_data_dir) / Path('speeds') / track_p.stem)
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
