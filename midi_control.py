import mido
import mido.backends.rtmidi  # required for pyinstaller to create an exe
from kivy.app import App
from kivy.logger import Logger


class MidiControl:
    def __init__(self):
        self.midi_channel = None
        self.midi_in_names = None  # Names of all of the midi input ports
        self.midi_in_port = None

    def get_midi_ports(self):
        try:
            self.midi_in_names = mido.get_input_names()
        except RuntimeError as e:
            Logger.exception(f'APPLICATION: get_midi_ports(): {e}')
            self.midi_in_names = None
        return self.midi_in_names

    def set_midi_port(self, input_port: str):
        """Set up midi input port and channel"""
        if input_port not in self.midi_in_names:
            self.midi_in_port = None
            return
        if self.midi_in_port:
            self.midi_in_port.close()
            self.midi_in_port = None
        try:
            self.midi_in_port = mido.open_input(input_port)
        except (RuntimeError, OSError) as e:
            Logger.exception(f'APPLICATION: set_midi_port(): {e}')
            app = App.get_running_app()
            app.root.ids.sm.get_screen('play_screen').ids.file.text = \
                f'Error: Cannot connect to MIDI port "{input_port}".\nClose and Restart.'

    def set_midi_channel(self, ch: str):
        self.midi_channel = int(ch) - 1

    def read_midi_callback(self, _):  # called from Clock.schedule_interval, does not use dt
        app = App.get_running_app()
        p = app.root.ids.sm.get_screen('play_screen')
        if self.midi_in_port:
            for msg in self.midi_in_port.iter_pending():
                if app.root.ids.sm.current == 'midi_monitor':
                    app.root.ids.sm.get_screen('midi_monitor').add_line(msg)
                if msg.type == 'control_change' and msg.channel == self.midi_channel:
                    if msg.control == 1:  # play or stop
                        if msg.value == 0:
                            p.play()
                        elif msg.value == 127:
                            p.stop()
                    elif msg.control == 3:  # Adjust playback volume
                        p.set_volume(msg.value)
                    elif msg.control == 4:
                        p.set_speed(msg.value)
