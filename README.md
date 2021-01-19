# BackingTrackPlayer
A simple midi controlled audio player designed for playing backing tracks for practice
Release builds for Windows10 and Mac on Release Page: https://github.com/ElliotGarbus/BackingTrackPlayer/releases

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
Volume|3| 0-127
Speed|4|1, 2, 3, 4, 5 for speeds  1x, 0.5x, .75x, 1.25x, 1.5x respectively

Play and Stop use CC#1 to make it easy to set up a midi toggle switch to stop/start.
The audio loops by default.

The app uses kivy for the UI, mido for MIDI, and ffmpeg for time-stretching the audio.
