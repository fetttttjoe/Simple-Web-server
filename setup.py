from cx_Freeze import setup, Executable

includefiles = ['templates', 'static', 'deviceManager.py', 'certificates' ]


main_executable = Executable("startServer.py")

setup(name="RemoteControl",
      version="0.1",
      description="RemoteControl",
      options={
      'build_exe': {
          'packages': ['jinja2',
                       'jinja2.ext',
                       'sys',
                       'os'],
          'include_files': includefiles,
          'include_msvcr': True}},
      executables=[main_executable], requires=['flask'])