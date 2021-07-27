from configstartup import window_width, window_top, window_left, window_height
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import Metrics
from kivy.properties import ListProperty

from midi_control import MidiControl
from pathlib import Path
import functools
import playscreen
import monitorscreen


kv = """
#:import Factory kivy.factory.Factory
<MidiCCPopup@Popup>
    title: 'Midi CC Assignments'
    size_hint: .8, .8
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        GridLayout:
            size_hint_y: .4
            cols: 3
            LeftLabel:
                text: 'Action'
                halign: 'center'
                bold: True
            CCLabel:
                text: 'CC#'
                bold: True
            RightLabel:
                text: 'Value & Description'
                halign: 'center'
                bold: True
            
            LeftLabel:
                text: 'Play'
            CCLabel:
                text: 'CC# 1'
            RightLabel:
                text: '0, Play & Stop are both on CC#1, can assigned to a toggle switch'
                
            LeftLabel:
                text: 'Stop'
            CCLabel:
                text: 'CC# 1'
            RightLabel:
                text: '127'
            
            LeftLabel:
                text: 'Volume'
            CCLabel:
                text: 'CC# 3'
            RightLabel:
                text: '0 - 127 can be assigned to a midi exp pedal'
            
            LeftLabel:
                text: 'Speed'
            CCLabel:
                text: 'CC# 4'
            RightLabel:
                text: '1, 2, 3, 4, 5 for speeds  1x, 0.5x, .75x, 1.25x, 1.5x respectively'
        Button:
            size_hint_y: None
            height: dp(48)
            text: 'OK'
            on_release: root.dismiss()


<LeftLabel@Label>:
    size_hint_x: None
    width: dp(75)
    # text_size: self.size
    # halign: 'right'
    # valign: 'center' 
    padding: dp(5), dp(5)
    canvas:
        Color:
            rgb: 1, 1, 1
        Line:
            width: dp(1)
            rectangle: (*self.pos, *self.size)
    
<CCLabel@Label>:
    size_hint_x: None
    width: dp(60)
    canvas:
        Color:
            rgb: 1, 1, 1
        Line:
            width: dp(1)
            rectangle: (*self.pos, *self.size)

<RightLabel@Label>:
    text_size: self.size
    halign: 'left'
    valign: 'center' 
    padding: dp(5), dp(5)
    canvas:
        Color:
            rgb: 1, 1, 1
        Line:
            width: dp(1)
            rectangle: (*self.pos, *self.size)

BoxLayout:
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
    Spinner:
        id: recent
        size_hint_y: None
        height: 48
        text: 'Recent Tracks'
        values: app.recent_track_names
        on_text: app.select_recent_track(self.text)
        
    ScreenManager:
        id: sm
        PlayScreen:
            name: 'play_screen'
        MidiMonitorScreen:
            name: 'midi_monitor'
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        Button:
            text: 'Play Mode'
            on_release: sm.current = 'play_screen'
        Button:
            text: 'Midi Commands'
            on_release: Factory.MidiCCPopup().open()
        Button:
            text: 'Midi Monitor Mode'
            on_release: sm.current = 'midi_monitor'
"""


class BackingTrackPlayerApp(App):
    recent_track_names = ListProperty()  # used to display names in most recent spinner

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mc = MidiControl()
        self.recent_track_paths = []  # holds full path to the track

    def build(self):
        self.title = 'Backing Track Player V1.11'
        # 1.1 added recent track list
        # 1.11 improved responsiveness of recent tracks button
        self.use_kivy_settings = False
        Window.minimum_width = window_width
        Window.minimum_height = window_height
        # Window.size = 800, 375
        Window.bind(on_dropfile=self._dropfile_action)
        Window.bind(on_request_close=self.window_request_close)
        return Builder.load_string(kv)

    def _dropfile_action(self, _, path):
        self.root.ids.sm.get_screen('play_screen').set_backing_track(path.decode())
        self.add_recent(path.decode())

    def add_recent(self, path):
        self.recent_track_paths.insert(0, path)
        if len(self.recent_track_paths) > 5:
            self.recent_track_paths = self.recent_track_paths[:5]
        self.recent_track_names = [Path(p).stem for p in self.recent_track_paths]

    def select_recent_track(self, track):
        if track == 'Recent Tracks':
            return
        self.root.ids.recent.text = 'Recent Tracks'
        self.root.ids.sm.get_screen('play_screen').ids.file.text = Path(track).stem
        pm = functools.partial(self.continue_select_recent_track, track)
        Clock.schedule_once(pm, .5)  # allow the recent tracks spinner to update

    def continue_select_recent_track(self, track, *args):
        self.root.ids.sm.get_screen('play_screen').stop()
        i = self.recent_track_names.index(track)
        p = self.recent_track_paths[i]
        self.root.ids.sm.get_screen('play_screen').set_backing_track(p)


    def on_start(self):
        names = self.mc.get_midi_ports()
        self.root.ids.midi_devices.values = names
        m_input = self.config.getdefault('MIDI', 'input', 'None')
        ch = self.config.get('MIDI', 'channel')
        song = self.config.get('Track', 'song')
        if not Path(song).exists():     # if track that was in config file was no longer exists...
            song = 'None'
        self.root.ids.sm.get_screen('play_screen').set_backing_track(song)
        self.recent_track_paths = [t for t in self.config.get('Recent Tracks','tracks').split(',') if t]
        self.recent_track_names = [Path(p).stem for p in self.recent_track_paths]

        # before set midi ports - so errors can show in track area
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
        config.setdefaults('Window', {'width': window_width,
                                      'height': window_height,
                                      'top': window_top,
                                      'left': window_left})
        config.setdefaults('Recent Tracks', {'tracks': ''})

    def get_application_config(self, defaultpath='%(appdir)s/%(appname)s.ini'):
        if platform == 'win' or platform == 'macosx':    # mac will not write into app folder
            s = self.user_data_dir + '/%(appname)s.ini'  # puts ini in AppData on Windows
        else:
            s = defaultpath
        return super().get_application_config(defaultpath=s)

    def window_request_close(self, _):
        # Window.size is automatically adjusted for density, must divide by density when saving size
        config = self.config
        config.set('Window', 'width', int(Window.size[0]/Metrics.density))
        config.set('Window', 'height', int(Window.size[1]/Metrics.density))
        config.set('Window', 'top', Window.top)
        config.set('Window', 'left', Window.left)
        self.config.write()
        return False

    def on_stop(self):
        p = self.root.ids.sm.get_screen('play_screen').track_path
        # update config file
        if p:
            self.config.set('Track', 'song', p)
            tracks = ','.join(self.recent_track_paths)
            self.config.set('Recent Tracks', 'tracks', tracks)
            self.config.write()
        if self.mc.midi_in_port and self.mc.midi_channel is not None:
            self.config.set('MIDI', 'input', self.mc.midi_in_port.name)
            self.config.set('MIDI', 'channel', self.mc.midi_channel)
            self.config.write()
        # clean up old files
        if p:
            fn = Path(p)
            suffix = fn.suffix
            speed_dir = Path(self.user_data_dir) / 'speeds'
            for f in speed_dir.glob('*'):
                if f.stem[:-4] + suffix != fn.name:
                    f.unlink()  # remove files not related to current track


BackingTrackPlayerApp().run()
