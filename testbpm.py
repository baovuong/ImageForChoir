from midiutil.MidiFile import MIDIFile

score = MIDIFile(1)

minutes = 3
bpm = 100

score.addTempo(0,0,bpm)

notes = minutes * bpm

"""
midifile.addNote(current_data["track"],
            current_data["channel"],
            current_data["pitch"],
            current_data["time"],
            current_data["duration"],
            current_data["volume"])
"""
track = 0
channel = 0
pitch = 60
time = 0
duration = 1
volume = 60
for i in range(notes):
    score.addNote(track,channel,pitch,time,duration,volume)
    time += duration

binfile = open("test.mid", 'wb')
score.writeFile(binfile)
binfile.close()
