#TODO: Clean this mess
#https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
import win32gui
import win32api
import win32con
import time
import os 
#
# Some Virtual Keyboard codes 
#
VK_CODE = {
    'tab': 0x09,
    'windows': 0x5B,
    'clear': 0x0C,
    'enter': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'delete': 0x2E,
    'back': 0x08,
    'esc': 0x1B,
    'mute': 0xAD,
    'browserBack':	0xA6,
    'browserFavorites': 0xAB,
   	'browserForward': 0xA7,
   	'browserHome': 0xAC,
    'browserRefresh': 0xA8,
    'browserSearch': 0xAA,
    'browserStop': 0xA9,
    'volumeUp': 0xAF,
    'volumeDown': 0xAE,
    'mouseLeft': 0x01,          # TODO: Test if that can subs mouse
    'mouseRight': 0x02,         # TODO: Test if that can subs mouse
    'arrowUp': 0x26,
    'arrowDown': 0x28,
    'arrowRight': 0x27,
    'arrowLeft': 0x25,
    ' ': 0x20, # "special characters"
    '+': 0xBB,
    ',': 0xBC,
    '-': 0xBD,
    '.': 0xBE,
    '/': 0x6F,
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'a': 0x41,
    'b': 0x42,
    'c': 0x43,
    'd': 0x44,
    'e': 0x45,
    'f': 0x46,
    'g': 0x47,
    'h': 0x48,
    'i': 0x49,
    'j': 0x4A,
    'k': 0x4B,
    'l': 0x4C,
    'm': 0x4D,
    'n': 0x4E,
    'o': 0x4F,
    'p': 0x50,
    'q': 0x51,
    'r': 0x52,
    's': 0x53,
    't': 0x54,
    'u': 0x55,
    'v': 0x56,
    'w': 0x57,
    'x': 0x58,
    'y': 0x59,
    'z': 0x5A,
    'F1': 0x70,
    'F2': 0x71,
    'F3': 0x72,
    'F4': 0x73,
    'F5': 0x74,
    'F6': 0x75,
    'F7': 0x76,
    'F8': 0x77,
    'F9': 0x78,
    'F10': 0x79,
    'F11': 0x7A,
    'F12': 0x7B,
}
#
# Function to Send Keyinput Combinations
# TODO: rework this
# usage: key1 is first button pressed and last released
# example: Win + r = execute
def kombiKeyboardInput(key1, key2):
    win32api.keybd_event(VK_CODE[f'{key1}'], 0, 0, 0)
    time.sleep(.05)
    win32api.keybd_event(VK_CODE[f'{key2}'], 0, 0, 0)
    time.sleep(.05)
    win32api.keybd_event(VK_CODE[f'{key2}'], 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(.05)
    win32api.keybd_event(VK_CODE[f'{key1}'], 0, win32con.KEYEVENTF_KEYUP, 0)
#
# Left click with mouse (not needed i think)
#
def mouseLeftlick(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

#
# Right click with mouse (not needed i think)
#
def mouseRightclick(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
    time.sleep(.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

#
# Get current mouse position 
#
def getMousePosition():
   return win32gui.GetCursorPos()

#
# Send Input to Keyboard
#
def keyboardEvent(userInput):
    win32api.keybd_event(VK_CODE[f'{userInput}'], 0, 0, 0)
    time.sleep(.05)
    win32api.keybd_event(VK_CODE[f'{userInput}'], 0, win32con.KEYEVENTF_KEYUP, 0)

#
# Shutdown timer for Windows 
# Input var:
#   time in min     
# return: 0 -> noError
#         != 0 -> something went wrong
#shutdown.exe -s -t %zeit% -f 
def shutdownWindows(seconds):
    minutes = int(seconds) * 60
    command = f"shutdown.exe /s /t {minutes}"
    retCode = os.system(command)
    if retCode == 1190:  # 1190 = shutdown already planed -> abort Shutdown and set new Timer
        abortShutdownWindows()
        retCode = os.system(command) # we want the System to shutdown on new Timer
    return retCode  # better error handling. https://docs.microsoft.com/de-de/windows/win32/debug/system-error-codes--1000-1299-
#
# Abort windows Shutdowntimer with cmd and return error
#
def abortShutdownWindows():
    return os.system("shutdown.exe /a") # better error handling. https://docs.microsoft.com/de-de/windows/win32/debug/system-error-codes--1000-1299-
                                        # 1116 = no Shutdown planned, cant cancel
    