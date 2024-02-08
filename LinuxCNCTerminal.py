import curses
import linuxcnc 
import hal
from terminaltables import AsciiTable
from art import *
import time

def initialize_linuxcnc():
    c = linuxcnc.command()
    s = linuxcnc.stat()
    err = linuxcnc.error_channel()
    try:
        s.poll()
    except Exception as e:
        print("Error in poll():", e)
        sys.exit(1)

    return c, s, err

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
    data.append(['0-X', joints[0]])
    data.append(['1-Y', joints[1]])
    data.append(['2-Shoulder', joints[2]])
    data.append(['3-Elbow', joints[3]])
    data.append(['4-Wrist', joints[4]])
    data.append(['                ', '                '])
    table = AsciiTable(data)
    table.title = "Joint Positions"
    table.inner_row_border = False
    table.inner_heading_row_border = False
    return table.table

def statusTable(stat):
    mdiOK = not stat.estop and stat.enabled and stat.homed and (stat.interp_state == linuxcnc.INTERP_IDLE)
    data = []
    data.append(['OK MDI',  'Homed',    'Enabled',      'EStop',    'ON/OFF'])
    data.append([mdiOK,    stat.homed,  stat.enabled,  stat.estop,  stat.task_state == linuxcnc.STATE_ON])
    data.append(['     ','     ', '     ', '     '])
    table = AsciiTable(data)
    table.title = "Status"
    table.inner_row_border = False
    table.inner_heading_row_border = False
    return table.table

def combineTables(stat, stdscr):
    xyza = xyzaTable(stat)
    joints = jointsTable(stat)
    data = [[xyza, joints]]
    table = AsciiTable(data)
    table.inner_row_border = False
    table.inner_heading_row_border = False
    table.outer_border = False
    table.inner_column_border = False

    status = statusTable(stat)
    data = [[status], [table.table]]
    table2 = AsciiTable(data)
    table2.inner_row_border = False
    table2.inner_heading_row_border = False
    table2.outer_border = False
    table2.inner_column_border = False

    stdscr.addstr(6,0,table2.table)

def historyTable(stat, history, title):
    table = AsciiTable(history)
    table.title = "CLI History"
    table.inner_row_border = False
    table.inner_heading_row_border = False
    table.outer_border = False
    table.inner_column_border = False
    table.title = title
    return table.table

def processCLI(cmd, stat, userInput, stdscr):
    if userInput == "on":
        stdscr.addstr(29, 0, "Turning machine on ...")
        stdscr.refresh()
        cmd.state(linuxcnc.STATE_ESTOP_RESET)
        cmd.state(linuxcnc.STATE_ON)
        return "++ Turn on machine"
    if userInput == "home":
        stdscr.addstr(29, 0, "Homing machine ...")
        stdscr.refresh()
        cmd.mode(linuxcnc.MODE_AUTO)
        for joint in range(len(stat.homed)):
            stdscr.addstr(29, 0, "Homing joint " + str(joint)) 
            stdscr.refresh()
            cmd.home(joint)
        return  "++ Home command initiated"
    if userInput == "unhome":
        stdscr.addstr(29, 0, "Unhoming machine ...")
        stdscr.refresh()
        cmd.state(linuxcnc.STATE_ESTOP)
        for joint in range(len(stat.homed)):
            stdscr.addstr(29, 0, "Unhoming joint " + str(joint)) 
            stdscr.refresh()
            cmd.unhome(joint)
        return  "++ Unhome command initiated"
    if userInput == "quit":
        return "-- Quit"

    return  "-- Invalid command"

def historyErrorTable(history, errors):
    table = AsciiTable([['                                                     ', '                                                     '], [history, errors]])
    table.inner_row_border = False
    table.inner_heading_row_border = False
    table.outer_border = False
    table.inner_column_border = False
    return table.table

def main(stdscr):
    # Set up curses
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    # Initialize LinuxCNC
    cmd, stat, error = initialize_linuxcnc()

    
    userInput = ""
    history = []
    errorList = []
    stdscr.timeout(100)
    while True:
        stdscr.clear()

        # Get and display LinuxCNC status
        stat.poll()
        err = error.poll()
        
        header = text2art("LinuxCNC")
        stdscr.addstr(0,0,header)
        combineTables(stat,  stdscr)
        if err:
            kind, text = err
            typus = "info"
            if kind in (linuxcnc.NML_ERROR, linuxcnc.OPERATOR_ERROR):
                typus = "error"
                stdscr.addstr(26, 0, typus + " " + text)
            errorList.insert(0, [typus + " " + text])
        errorsT = historyTable(stat, errorList, "Errors")
        historyT = historyTable(stat, history, "CLI History")

        stdscr.addstr(30, 0, "CLI:")
        stdscr.addstr(31, 0, userInput)
        stdscr.addstr(32, 0, historyErrorTable(historyT, errorsT))

        # Refresh the screen
        stdscr.refresh()
        # Handle user input
        key = stdscr.getch()
        if key == ord('\n'):
            history.insert(0, [processCLI(cmd, stat, userInput, stdscr)])
            if userInput == "quit":
                break
            userInput = ""
        else:
            if 0 <= key <= 255:
                userInput += chr(key)
        time.sleep(0.1)

if __name__ == "__main__":
    curses.wrapper(main)

