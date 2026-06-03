@echo off
echo Installing PyInstaller...
"C:\Users\Admin\AppData\Local\Microsoft\WindowsApps\python3.11.exe" -m pip install pyinstaller

echo Building Pyrics - Python Lyrics Player executable...
"C:\Users\Admin\AppData\Local\Microsoft\WindowsApps\python3.11.exe" -m PyInstaller --noconsole --onefile --icon=favicon/favicon.ico --add-data "favicon;favicon" main.py

echo Done! The executable is located in the 'dist' folder.
pause
