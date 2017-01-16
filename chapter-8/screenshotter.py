import win32gui
import win32ui
import win32con
import win32api

# Grab a handle to the main desktop window
hdesktop = win32gui.GetDesktopWindow()

# Determine the size of the screen in pixels
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

# Create a device context
desktop_dc = win32gui.GetWindowDC(hdesktop)
img_dc = win32ui.CreateDCFromHandle(desktop_dc)

# Create a memory based device context where we will
# temporary store our bitmap bytes to a file
mem_dc = img_dc.CreateCompatibleDC()

# Create a bitmap object
screenshot = win32ui.CreateBitmap()
screenshot.CreateCompatibleBitmap(img_dc, width, height)
# SelectObject sets the memory-based device context to point 
# at the bitmap object that we'are capturing
mem_dc.SelectObject(screenshot)

# Copy the screenshot into our memory device context:
# BitBlt does a bit-for-bit copy of the image and store it in the memory
# based object. (It is like a memcpy call for GDI objects)
mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

# Save the bitmap to a file
screenshot.SaveBitmapFile(mem_dc, 'c:\\Windows\\Temp\\screenshot.bmp')

# Free our objects
mem_dc.DeleteDC()
win32gui.DeleteObject(screenshot.GetHandle())

