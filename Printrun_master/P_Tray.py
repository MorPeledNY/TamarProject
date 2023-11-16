from printrun.printcore import printcore
from printrun import gcoder
import time
import signal
from printrun.plugins import PRINTCORE_HANDLER

def signal_handler(signum, frame):
    print("exiting0")
    p.cancelprint()
    time.sleep(3)
    p.send("G92 E0")
    time.sleep(1)
    p.send("M107")
    time.sleep(1)
    p.send("M104 S0")
    time.sleep(1)
    p.send("G28 X0")
    time.sleep(1)
    p.send("M84")
    time.sleep(1)
    p.send("M140 S0")
    time.sleep(5)
    p.disconnect()
    exit()

def end_callback():
    global print_in_progress
    print("end")
    print_in_progress = False
    time.sleep(20)

def start_callback(printer):
    global print_in_progress
    print("start")
    print_in_progress = True

def add_new_p(gcode_list: list):
    gcode_list.insert(0, "G91;")
    gcode_list.insert(1, "G1 X1 Y0.5 F3000 ;")
    gcode_list.insert(2, "G1 Z0.1 ;")
    gcode_list.insert(3, "G90 ;Absolute positioning")
    gcode_list.insert(4, "G92 E0 X0 Y0 ; Reset Extruder")
    return gcode_list

# configure printer for communication
print_in_progress = False
p = printcore()
p.connect('COM3', 115200, True)
p.startcb = start_callback
p.endcb = end_callback
signal.signal(signal.SIGINT, signal_handler)

# startprint silently exits if not connected yet
while not p.online:
  time.sleep(0.1)
p.send_now("M117 welcome")
print("online!")

# prepare and print first layer
gcode=[i.strip() for i in open('retangel0.5mm.gcode')] # or pass in your own array of gcode lines instead of reading from a file
gcode = gcoder.LightGCode(gcode)
p.startprint(gcode)
time.sleep(0.5)

# start continues printing
layer_template =[i.strip() for i in open('retangel0.5mm_rel.gcode')] # or pass in your own array of gcode lines instead of reading from a file
layer_number = 1
while True:

    # are we still printing a layer? if not start a new layer
    if not print_in_progress:

        # get the template layer and add the prefix gcode before we start the layer
        new_layer = layer_template
        new_layer = add_new_p(new_layer)
        new_layer = gcoder.LightGCode(new_layer)
        p.startprint(new_layer)
        layer_number += 1
        p.send_now(f'M117 printing layer number {layer_number}')

    time.sleep(0.1)