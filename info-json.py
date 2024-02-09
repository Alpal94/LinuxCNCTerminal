import linuxcnc 
import sys
import hal
import time
import json

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

cmd, stat, error = initialize_linuxcnc()
stat.poll()
err = error.poll()
info = {
        "position":stat.position
}
print(json.dumps(info))
