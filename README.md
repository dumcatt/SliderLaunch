# SliderLaunch
![preview](Image/prog.png)
Select and launch a list of games from an ini file with your controller of choice. Works with all devices supported by slidershim.

# Requirements
- [Python 3.13](https://www.python.org/downloads/)
- [PyGame](https://www.pygame.org/wiki/GettingStarted#Pygame%20Installation)
- [PyWin32api](https://pypi.org/project/pywin32/)
- [slidershim](https://github.com/4yn/slidershim)

# Configuration
If you didn't use slidershim's MSI installer, the path to slidershim can be changed on `slidershim_path` in `launcher.py`
The amount of time before it automatically launches the game can also be configured on `AUTO_LAUNCH_DELAY` in the same file.

# Slidershim Setup
![Configuration](Image/slidershim_cfg.png)  
Change "Input Device" to the controller that you are using and change "Output Mode" to "Keyboard 16-zone, Linear"
