# Simple Button Application

A basic Python GUI application that displays a window with a clickable button.

## Requirements
- Python 3.x
- tkinter (usually comes pre-installed with Python)

## How to Run (Python Script)
1. Make sure you have Python installed on your system
2. Open a terminal/command prompt
3. Navigate to the project directory
4. Run the application using:
   ```
   python main.py
   ```

## Creating an Executable (.exe)
1. First, ensure Python is properly installed and added to your system's PATH
2. Open a terminal/command prompt
3. Install PyInstaller using:
   ```
   python -m pip install pyinstaller
   ```
4. Navigate to the project directory
5. Create the executable using:
   ```
   python -m PyInstaller --onefile --windowed main.py
   ```
6. The executable will be created in the `dist` folder
7. You can now run the application by double-clicking the `main.exe` in the `dist` folder

Note: The `--windowed` flag prevents the console window from appearing when running the exe
      The `--onefile` flag creates a single executable file instead of multiple files

## Features
- Clean and simple user interface
- Centered button with click functionality
- Popup message on button click
- Can be converted to standalone executable 