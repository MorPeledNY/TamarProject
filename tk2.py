

root = Tk()
root.title("לחצו על אחד הכפתורים לבחירת צבע")
root.geometry("1700x1200")
root.config(bg="white")
root.resizable(0, 0)







def red():
    subprocess.call([r'C:\\Users\\Mor\\Downloads\\Slic3r-1.3.0.64bit\\Slic3r-console.exe',
                     'C:\\Users\\Mor\\Downloads\\Slic3r-1.3.0.64bit\\body1.stl', '--load',
                     'C:\\Users\\Mor\\Downloads\\Slic3r-1.3.0.64bit\\config.ini', '--output',
                     'C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\test1.gcode'])
    root.quit()
#    root.destroy()


def yellow():
    os.startfile("yellow2.mp4")

def green():
    os.startfile("green.mp4")


def blue():
    os.startfile("blue.mp4")



btn1 = Button(root, bg='red', fg='white', width=6, font=('ariel 20 bold'), relief=GROOVE, command=red)
btn1.grid(row = 0, column = 1,  pady = 20, padx=30)
btn2 = Button(root,  bg='green', fg='white', width=10, font=('ariel 20 bold'), relief=GROOVE,
              command=green)
btn2.grid(row = 6, column = 1, pady = 20, padx=30)
btn3 = Button(root,  bg='yellow', fg='white', width=8, font=('ariel 20 bold'), relief=GROOVE,
              command=yellow)
btn3.grid(row = 12, column = 1, pady = 20, padx=30)
btn4 = Button(root,  bg='blue', fg='white', width=6, font=('ariel 20 bold'), relief=GROOVE,
              command=blue)
btn4.grid(row = 20, column = 1, pady = 20, padx=30)
root.mainloop()