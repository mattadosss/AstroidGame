#  Asteroid Shooter

A fast-paced 2D arcade-style space shooter built with **Pygame**. Destroy asteroids, collect powerups, and survive as long as possible while leveling up your ship and chasing high scores.

---

##  Features

-  Classic arcade-style gameplay
-  Player-controlled spaceship with size scaling per level
-  Asteroid waves with increasing difficulty
-  Bullet shooting with accuracy-based scoring
-  Explosion effects and animations
-  Power-ups to boost your score
-  Smart difficulty scaling: more asteroids, faster speeds, bigger spaceship
-  Instructions screen and pause menu
-  High score saving with level tracking

---

##  Screenshots

![Menu](assets/screenshots/menu.png)
![Gameplay](assets/screenshots/gameplay.png)
![Game Over](assets/screenshots/gameover.png)

---

##  Setup & Installation

### Requirements

- Python 3.8+
- `pygame` module

### Install Dependencies

```bash
pip install pygame
```
##  Run the Game

```bash
py main.py
```
---

##  Controls

| Action               | Key                          |
|----------------------|-------------------------------|
| Move Left            | `A` or `←` Arrow Key          |
| Move Right           | `D` or `→` Arrow Key          |
| Shoot Bullet         | `Spacebar` (costs 1 point)    |
| Pause Game           | `ESC`                         |
| Restart (Game Over)  | `R`                           |
| Scroll Instructions  | Mouse Wheel / `↑↓` Arrow Keys |

---

##  Game Mechanics

###  Points System

- +2 points per destroyed asteroid  
- -1 point per bullet (refunded if it hits)  
- +3 points per power-up collected

###  Leveling Up

Every 10 points increases difficulty:
- Ship size grows (max 80x80)
- Asteroids get faster
- More asteroids spawn
- Power-up drops appear

###  Game Over

Game ends when:
- You run out of **lives**
- OR your **score reaches zero**

---
## 🗂️ Project Structure
```
asteroid_shooter/
├── main.py
├── highscores.txt
├── res/
│ ├── SpaceShip.png
│ ├── Asteroid1.png, ...
│ ├── explosion.png
│ ├── powerup1.png
│ └── bg.png
└── README.md
```

---

##  High Scores

- High scores and highest level are stored in `highscores.txt`.
- Automatically created/updated after each game over.

---


##  Tips

- Conserve points: only shoot when you’re confident!
- Dodge instead of destroy if low on points.
- Watch for powerups during level transitions.
- The bigger your ship, the easier it is to hit things... and be hit!

