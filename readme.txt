JUNGLE ESCAPE - PYTHON TUTOR SKILL TEST PROJECT

ABOUT
Jungle Escape is an original 2D platformer made with Pygame Zero.
Collect all four coins, avoid the ground slimes and flying bat, and reach
the golden exit gate to win. Losing all three health points ends the game.

REQUIREMENTS
- Python 3.8 or newer
- Pygame Zero

LIBRARIES USED BY THE GAME
- Pygame Zero (provided by the pgzero runner)
- math (Python standard library)
- random (Python standard library)

No direct pygame import is used.

HOW TO INSTALL
1. Install Python.
2. Open a terminal in this project folder.
3. Install Pygame Zero:
       pip install pgzero

HOW TO RUN
Run:
       pgzrun main.py

CONTROLS
- Left / Right arrows or A / D: move
- Space: jump
- Enter: restart after winning or losing
- Escape: return to the main menu
- Main menu buttons: start, toggle sound, or exit

PROJECT CONTENTS
- main.py: game code and object-oriented game classes
- images/: original pixel-art animation frames
- sounds/: sound effects
- music/: background music

NOTES
The player, ground enemy, and flying enemy each use cyclic multi-frame
sprite animations. Enemies patrol within their own horizontal boundaries.
The game includes a menu, sound toggle, coin collection, health, collision,
a win condition, and a loss condition.
