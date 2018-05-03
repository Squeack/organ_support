#!/usr/bin/python

from mido import MidiFile
import sys

if len(sys.argv) != 2:
    print "Usage: {0} <midifile>".format(sys.argv[0])
    sys.exit(2)

midifile = sys.argv[1]

print "# Translating {}".format(midifile)

msgqueue = MidiFile(midifile)
timenow = 0.1
timeoffset = -1
channelmap = [2, 1, 0, 3, 4]
channels = ["pedal", "great", "swell", "choir", "posit"]
notes_on = [0, 0, 0, 0, 0]
notes_off = [0, 0, 0, 0, 0]
outputlist = []
for msg in msgqueue:
    timenow += msg.time
    if msg.type == "note_on" and msg.velocity > 0:
        if timeoffset < 0:
            timeoffset = timenow - 0.1
        payload = "N {} {} 1 ".format(channelmap[msg.channel], msg.note)
        target = "{:09.3f}:{}".format(timenow-timeoffset, channels[channelmap[msg.channel]])
        outputlist.append((target, payload))
        notes_on[channelmap[msg.channel]] += 1
    elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
        if timeoffset < 0:
            timeoffset = timenow - 0.1
        payload = "N {} {} 0 ".format(channelmap[msg.channel], msg.note)
        target = "{:09.3f}:{}".format(timenow-timeoffset, channels[channelmap[msg.channel]])
        outputlist.append((target, payload))
        notes_off[channelmap[msg.channel]] += 1
    elif msg.type == "control_change":
        if msg.control == 11:
            if timeoffset < 0:
                timeoffset = timenow - 0.1
            payload = "V {}".format(msg.value)
            target = "{:09.3f}:{}".format(timenow-timeoffset, channels[channelmap[msg.channel]])
            outputlist.append((target, payload))
    #else:
    #    print "# {:09.3f}:{}".format(timenow-timeoffset, msg)
outputlist.append(("END", "END"))
print "# Notes pressed = {}".format(notes_on)
print "# Notes released = {}".format(notes_off)
(prevtarget, payload) = outputlist[0]
for i in range(1, len(outputlist)):
    (newtarget, newpayload) = outputlist[i]
    if newtarget == prevtarget:
        payload += newpayload
    else:
        print "{}:{}".format(prevtarget, payload)
        prevtarget = newtarget
        payload = newpayload
