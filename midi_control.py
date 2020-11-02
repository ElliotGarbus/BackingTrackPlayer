import mido
import mido.backends.rtmidi  # required for pyinstaller to create an exe
from kivy.app import App


class MidiControl:
    def __init__(self):
        self.midi_channel = None
        self.midi_in_port_name = None
        self.midi_in_names = None  # Names of all of the midi input ports
        self.midi_in_port = None

    def get_midi_ports(self):
        try:
            self.midi_in_names = mido.get_input_names()
        except RuntimeError as e:
            print(f'APPLICATION: get_midi_ports(): {e}')
            self.midi_in_names = None
        return self.midi_in_names

    def set_midi_port(self, input_port: str):
        """Set up midi input port and channel"""
        if input_port not in self.midi_in_names:
            self.midi_in_port = None
            return
        if self.midi_in_port:
            self.close_ports()
            self.midi_in_port = None
        try:
            self.midi_in_port = mido.open_input(input_port)
        except RuntimeError as e:
            print(f'APPLICATION: set_midi(): {e}')

    def set_midi_channel(self, ch: str):
        self.midi_channel = int(ch) - 1

    def read_midi_callback(self, dt):
        if self.midi_in_port:
            for msg in self.midi_in_port.iter_pending():
                print(msg)
