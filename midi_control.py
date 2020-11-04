import mido
import mido.backends.rtmidi  # required for pyinstaller to create an exe
from kivy.app import App


class MidiControl:
    def __init__(self):
        self.midi_channel = None
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
            self.midi_in_port.close()
            self.midi_in_port = None
        try:
            self.midi_in_port = mido.open_input(input_port)
        except (RuntimeError, OSError) as e:
            print(f'APPLICATION: set_midi_port(): {e}')
            app = App.get_running_app()
            app.root.ids.file.text = 'Error: Cannot connect to MIDI'

    def set_midi_channel(self, ch: str):
        self.midi_channel = int(ch) - 1

    def read_midi_callback(self, dt):
        app = App.get_running_app()
        p = app.root
        if self.midi_in_port:
            for msg in self.midi_in_port.iter_pending():
                if msg.type == 'control_change' and msg.channel == self.midi_channel:
                    if msg.control == 1:  # play or stop
                        if msg.value == 0:
                            p.play()
                        elif msg.value == 127:
                            p.stop()
                    elif msg.control == 2 and msg.value == 127:  # Restart
                        p.restart()
                    elif msg.control == 3:  # Adjust playback volume
                        p.set_volume(msg.value)

