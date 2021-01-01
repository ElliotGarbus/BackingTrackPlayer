import configstartup
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

from midi_control import MidiControl
import playscreen
import monitorscreen

# TODO: Update configstartup to ensure a clean start.  Preserve Window size

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
    width: 75
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
    width: 60
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
            text: 'Midi Monitor'
            on_release: sm.current = 'midi_monitor'
"""


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

    def _dropfile_action(self, _, path):
        self.root.set_backing_track(path.decode())

    def on_start(self):
        names = self.mc.get_midi_ports()
        self.root.ids.midi_devices.values = names
        m_input = self.config.getdefault('MIDI', 'input', 'None')
        ch = self.config.get('MIDI', 'channel')
        song = self.config.get('Track', 'song')
        self.root.ids.sm.get_screen('play_screen').set_backing_track(song)
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

    def get_application_config(self, defaultpath='%(appdir)s/%(appname)s.ini'):
        if platform == 'macosx':  # mac will not write into app folder
            s = '~/.%(appname)s.ini'
        else:
            s = defaultpath
        return super().get_application_config(defaultpath=s)

    def on_stop(self):
        p = self.root.ids.sm.get_screen('play_screen').track_path
        if p:
            self.config.set('Track', 'song', p)
            self.config.write()
        if self.mc.midi_in_port and self.mc.midi_channel:
            self.config.set('MIDI', 'input', self.mc.midi_in_port.name)
            self.config.set('MIDI', 'channel', self.mc.midi_channel)
            self.config.write()


BackingTrackPlayerApp().run()
