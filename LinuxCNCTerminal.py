import curses
import linuxcnc 
from terminaltables import AsciiTable
from art import *
import time

def initialize_linuxcnc():
    c = linuxcnc.command()
    s = linuxcnc.stat()
    try:
        s.poll()
    except Exception as e:
        print("Error in poll():", e)
        sys.exit(1)

    return c, s

def xyzaTable(stat):
    data = []
    data.append(['X', stat.position[0]])
    data.append(['Y', stat.position[1]])
    data.append(['Z', stat.position[2]])
    data.append(['A', stat.position[3]])
    data.append(['B', stat.position[4]])
    data.append(['Velocity', stat.velocity])
    data.append(['State', stat.interp_state])
    data.append(['                ', '                '])
    table = AsciiTable(data)
    table.title = "XYZA Coords"
    table.inner_row_border = False
    table.inner_heading_row_border = False
    return table.table

def jointsTable(stat):
    data = []
    joints = stat.joint_position
    data.append(['X-0', joints[0]])
    data.append(['Y-1', joints[1]])
    data.append(['Shoulder-2', joints[2]])
    data.append(['Elbow-3', joints[3]])
    data.append(['Wrist-4', joints[4]])
    data.append(['                ', '                '])
    table = AsciiTable(data)
    table.title = "Joint Positions"
    table.inner_row_border = False
    table.inner_heading_row_border = False
    return table.table

def combineTables(stat, stdscr):
    xyza = xyzaTable(stat)
    joints = jointsTable(stat)
    data = []
    data.append([xyza, joints])
    table = AsciiTable(data)
    table.inner_row_border = False
    table.inner_heading_row_border = False
    table.outer_border = False
    table.inner_column_border = False
    stdscr.addstr(6,0,table.table)

def main(stdscr):
    # Set up curses
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    # Initialize LinuxCNC
    cmd, stat = initialize_linuxcnc()

    stdscr.timeout(100)
    while True:
        stdscr.clear()

        # Get and display LinuxCNC status
        stat.poll()
        
        header = text2art("LinuxCNC")
        stdscr.addstr(0,0,header)
        combineTables(stat,  stdscr)

        # Refresh the screen
        stdscr.refresh()

        # Handle user input
        key = stdscr.getch()

        # Quit the application when 'q' is pressed
        if key == ord('q'):
            break

        time.sleep(0.1)

if __name__ == "__main__":
    curses.wrapper(main)

