# BackingTrackPlayer
A simple midi controlled audio player designed for playing backing tracks for practice

**Directions:**

Drag the backing track file you would like to play onto the app. The file name will be displayed in the center.
Select the midi device (or midi device interface) for controlling the player, and the matching midi channel.

The BackingTrackPlayer can be controlled by the buttons on the app or a MIDI foot controller.

**Configure your MIDI Controller to send CC messages**

The BackingTrackPlayer responds to the following MIDI messages:

Action | CC# | CC Value
-------|-----|---------
Play | 1 | 00
Stop | 1 | 127
Restart|2 |127
Volume|3| 0-127

Play and Stop use CC#1 to make it easy to set up a midi toggle switch to stop/start.
Audio loops by default.
