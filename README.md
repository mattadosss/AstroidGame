# Asteroid Shooter

A simple 2D space shooter game built with Python and Pygame.

## Features

- Player ship that moves left and right with arrow keys
- Shoot bullets with the spacebar
- Asteroids spawn from the top and fall down
- Collision detection between bullets and asteroids
- 60 FPS gameplay
- Uses actual image assets from the res folder

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```
   python main.py
   ```

2. Controls:
   - **Left Arrow**: Move ship left
   - **Right Arrow**: Move ship right
   - **Spacebar**: Shoot bullets
   - **Close Window**: Quit game

3. Objective:
   - Shoot the falling asteroids before they hit your ship
   - Avoid collisions with asteroids

## Game Assets

The game uses the following assets from the `res` folder:
- `SpaceShip.png` - Player ship
- `Asteroid1.png`, `Asteroid2.png`, `Asteroid3.png`, `Asteroid4.png` - Various asteroid types

## Game Structure

- `main.py` - Main game file with all game logic
- `requirements.txt` - Python dependencies
- `res/` - Game assets folder 