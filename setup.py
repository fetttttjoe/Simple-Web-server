from cx_Freeze import setup, Executable
from datetime import date
import os

programName = "RemoteControl"
programPath = f"{os.path.abspath('.')}/{programName}"
#
# Folders to include
# Note: possible to add files if in same folder as setup.py
#
includeFiles = [    
                f"{programPath}/templates",
                f"{programPath}/static", 
                f"{programPath}/util",
                f"{programPath}/certificates" ]
excludePackages = ["tkinter", "test", "unittest"]
buildOptions = {
    'build_exe' : f'build/{programName}',
    'excludes' : excludePackages,
    'packages': [ 'jinja2',
                  'jinja2.ext',
                  'sys',
                  'os'],
    'include_files': includeFiles,
    'include_msvcr': True }

today = date.today()
d = today.strftime("%m/%d/%Y")

executable = Executable(script="startServer.py", target_name=f"{programName}.exe")
setup(name = programName,
      version="0.1",
      description= f"RemoteControl BuildDate: {d}",
      options= {'build_exe': buildOptions},
      executables=[executable], requires=['flask'])