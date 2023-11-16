from printrun.printcore import printcore
from printrun import gcoder
import time
import signal

def get_x_y_e(line : str):
    x_abs, y_abs,x_pos,y_pos, e_pos, e_abs = 0, 0, 0, 0, 0, 0
    line_list = line.split(" ")
    for index,element in enumerate(line_list):
        if 'x' in element.lower():
            x_abs = float(element.lower().replace("x", ''))
            x_pos = index
        elif 'y' in element.lower():
            y_abs = float(element.lower().replace("y", ''))
            y_pos = index
        elif 'e' in element.lower():
            e_abs = float(element.lower().replace("e", ''))
            e_pos = index
    return x_abs,y_abs,x_pos,y_pos, e_pos, e_abs


gcode=[i.strip() for i in open('kav.gcode')] # or pass in your own array of gcode lines instead of reading from a file

offset_line = gcode[0]
x_offset, y_offset, x, y, e_offset, e = get_x_y_e(offset_line)

with open('kav_rel.gcode', 'w') as gcode_file:
    for line in gcode[1:]:
        if line[0] == ';' or ('x' not in line.lower() and 'y' not in line.lower() and 'e' not in line.lower()):
            gcode_file.write(line + '\n')
            continue
        x_abs, y_abs, x_pos, y_pos, e_pos, e_abs = get_x_y_e(line)
        y = round(y_abs - y_offset,3)
        x = round(x_abs - x_offset,3)
        e = round(e_abs- e_offset, 3)

        if 'X' in line:
            line = line.replace(line.split(" ")[x_pos], f"X{x}")
        if 'Y' in line:
            line = line.replace(line.split(" ")[y_pos], f"Y{y}")
        if 'E' in line:
            line = line.replace(line.split(" ")[e_pos], f"E{e}")



        gcode_file.write(line + '\n')

