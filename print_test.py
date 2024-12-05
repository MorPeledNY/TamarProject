import subprocess


#C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\test.gcode
#C:\\Users\\Mor\\Downloads\\Slic3r-1.3.0.64bit\\test.gcode
subprocess.call([r'D:\\Slic3r-1.3.0.64bit\\Slic3r-console.exe', 'D:\\Slic3r-1.3.0.64bit\\Body1.stl', '--load', 'D:\\Slic3r-1.3.0.64bit\\config.ini', '--output', 'C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\test.gcode'])