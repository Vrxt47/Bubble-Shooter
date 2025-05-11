# Bubble Shooter Game 🎯

A colorful and interactive **Bubble Shooter** game built with Python and Pygame. This version includes **3 unique levels**, each with increasing difficulty and dynamic video backgrounds to enhance the gameplay experience.

---

## 🕹️ Game Description

In this game, you launch colored bubbles from a cannon to match and pop groups of three or more bubbles of the same color. Clear all bubbles before they reach the bottom of the screen to win the level.

### ✨ Features

- 🎮 **Three unique levels** with increasing color complexity:
  - Level 1: 3 bubble colors
  - Level 2: 5 bubble colors
  - Level 3: 7 bubble colors
- 💣 **Bomb Bubble**: Appears after reaching a score threshold and can destroy nearby bubbles.
- 🎥 **Dynamic Video Backgrounds** per level (requires OpenCV).
- 🔊 Background music and pop sound effects.
- 🧠 Grid snapping, collision detection, and intelligent bubble removal.
- 📺 Game over screen with final score and restart option.

---

## 📦 Dependencies

Ensure you have the following Python libraries installed:

- `pygame`
- `numpy`
- `opencv-python`

You can install them via pip:

```bash
pip install pygame numpy opencv-python
