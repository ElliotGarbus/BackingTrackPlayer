from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty


Builder.load_string("""
<MidiLine>
    orientation: 'horizontal'
    size_hint: 1, None
    height: dp(12)
    Button:
        text: root.raw
    Button:
        text: root.action
    
<MidiMonitorScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: dp(24)
            Label:
                text: 'MIDI Message'
            Label:
                text: 'Action'
        RecycleView:
            viewclass: 'MidiLine'
            data: root.rv_list
            scroll_type: ['bars','content']
            bar_width: dp(20)
            do_scroll_x: False
            RecycleBoxLayout:
                id: rbl
                orientation: 'vertical'
                size_hint: None, None
                default_size: None, dp(16)
                default_size_hint: 1, None
                height: self.minimum_height
""")


class MidiMonitorScreen(Screen):
    rv_list = ListProperty([{'raw': 'Midi Message', 'action': 'Action'}])

    def add_line(self, msg):
        print(msg)
        print(f'Ch:{msg.channel + 1}, CC#{msg.control}, value: {msg.value}')
        raw = f'Ch:{msg.channel + 1}, CC#{msg.control}, value: {msg.value}'
        action = 'TBD'
        self.rv_list.append({'raw': raw, 'action': action})


class MidiLine(BoxLayout):
    raw = StringProperty()
    action = StringProperty()