# 💎 Diamond Chase - Modern UI Edition

A futuristic, visually stunning reimagining of the Diamond Chase strategy game with glassmorphism effects, particle systems, and smooth animations.

## ✨ New UI Features

### 🎨 Visual Enhancements

#### **Futuristic Background**
- Animated gradient background with depth
- Dynamic grid system that pulses and moves
- Cyberpunk-inspired color palette

#### **Glassmorphism Effects**
- Semi-transparent panels with frosted glass appearance
- Subtle highlights and blur effects
- Modern, premium look throughout the interface

#### **Glowing Elements**
- All game pieces have dynamic glow effects
- Pulsing animations on beads and UI elements
- Multi-layered glow rendering for depth

#### **Particle System**
- Explosive particle effects when beads are captured
- Smooth particle trails during moves
- Celebration particles on victory screen
- Real-time particle physics simulation

#### **Animated Diamond Icon**
- Rotating 3D-style diamond in menus
- Pulsing scale animation
- Gradient fills with dynamic colors

#### **Modern Buttons**
- Glassmorphic button design with hover effects
- Smooth scale animations on interaction
- Glowing borders that pulse
- Color interpolation for smooth transitions

### 📊 Enhanced HUD

#### **Score Panels**
- Glassmorphic score displays
- Pulsing animations synchronized with gameplay
- Clear player identification (AI vs Human / AI 1 vs AI 2)
- Gradient overlays for premium look

#### **Energy Bars** (Framework ready for future features)
- Animated fill with gradient effects
- Glowing edge indicators
- Smooth percentage-based animations

### 🎮 Game Modes

1. **AI vs Human**
   - Choose between Minimax AI or A*+Fuzzy AI
   - Modern opponent selection interface
   - Clear visual feedback for moves

2. **AI vs AI**
   - Watch two AI algorithms battle
   - Fast-paced gameplay (200ms between moves)
   - Real-time strategy visualization

### 🎯 Key UI Improvements

- **Typography**: Clean, futuristic fonts with glow effects
- **Color Palette**: 
  - Primary: Cyan (100, 200, 255)
  - Secondary: Violet (150, 100, 255)
  - AI Color: Red with glow (255, 80, 80)
  - Human Color: Green with glow (80, 255, 150)
  - Accent: Gold (255, 200, 100)

- **Animations**:
  - Smooth 60 FPS rendering
  - Delta-time based animations
  - Interpolated color transitions
  - Pulsing scale effects

- **Feedback**:
  - Particle effects on every move
  - Visual highlighting of valid moves
  - Glowing indicators for selected pieces
  - Screen-wide effects on game over

## 🚀 Installation

### Prerequisites

```bash
pip install pygame --break-system-packages
```

### Files Required

1. `diamond_chase_modern.py` - Main game file with modern UI
2. `modern_ui.py` - UI components (buttons, particles, HUD)
3. `ai_algorithms.py` - AI logic (Minimax and A*+Fuzzy)

## 🎮 How to Run

```bash
python diamond_chase_modern.py
```

The game will launch in fullscreen mode with the new modern interface.

## 🎯 Game Rules

1. **Objective**: Reduce opponent's beads to 3 or fewer
2. **Starting Position**: Each player has 6 beads
3. **Movement**: Beads can move to adjacent intersecting points
4. **Trapping**: A bead surrounded on all sides is eliminated
5. **Victory**: First player to reduce opponent to 3 beads wins

## 🎨 Controls

- **Mouse**: Click to select and move your beads
- **SPACE**: Return to main menu (during gameplay)
- **Click**: Navigate menus and make selections

## 🏗️ Architecture

### Modern UI Components (`modern_ui.py`)

#### **ModernButton**
- Glassmorphic design with transparency
- Hover animations and glow effects
- Customizable colors and sizes

#### **ImageButton**
- Enhanced image buttons with scaling
- Circular glow effects
- Smooth hover animations

#### **ParticleSystem**
- Physics-based particle simulation
- Color and velocity customization
- Lifetime management

#### **HUD**
- Score panel rendering
- Energy bar framework
- Pulsing animations

#### **DiamondAnimation**
- Rotating diamond icon
- Scale pulsing effect
- Gradient rendering

#### **draw_futuristic_background()**
- Animated gradient backgrounds
- Dynamic grid system
- Time-based effects

### Core Functions

#### **draw_glowing_text()**
- Multi-layer text rendering
- Glow effect implementation
- Customizable intensity

#### **draw_glowing_circle()**
- Layered circle rendering
- Radial glow gradients
- Anti-aliasing

#### **draw_glowing_line()**
- Multi-layer line rendering
- Dynamic thickness
- Smooth gradients

#### **draw_glowing_polygon()**
- Complex shape rendering
- Glow effect layers
- Filled and outline modes

## 🤖 AI Algorithms (Unchanged)

### Minimax AI
- Depth-limited search (4 levels for human vs AI)
- Heuristic evaluation
- Strategic positioning

### A* + Fuzzy Logic AI
- Pathfinding with A* algorithm
- Fuzzy logic decision making
- Aggressive positioning
- Trap potential calculation

## 🎨 Color Scheme

```python
COLOR_BACKGROUND = (15, 20, 40)      # Dark blue-gray
COLOR_PRIMARY = (100, 200, 255)      # Bright cyan
COLOR_SECONDARY = (150, 100, 255)    # Violet
COLOR_AI = (255, 80, 80)             # Glowing red
COLOR_HUMAN = (80, 255, 150)         # Glowing green
COLOR_ACCENT = (255, 200, 100)       # Gold
COLOR_OPTION = (196, 215, 255)       # Light cyan
```

## 📈 Performance

- **Target FPS**: 60
- **Particle Count**: Up to 100+ simultaneous particles
- **Render Layers**: 3-5 glow layers per element
- **Animation Smoothness**: Delta-time based

## 🔮 Future Enhancements

- [ ] Sound effects and background music
- [ ] More particle effects (trails, explosions)
- [ ] Additional AI difficulty levels
- [ ] Online multiplayer mode
- [ ] Replay system
- [ ] Statistics tracking
- [ ] Custom themes
- [ ] Tournament mode

## 🎓 Technical Highlights

### Glassmorphism Implementation
```python
# Semi-transparent surfaces with gradients
glass_surface = pygame.Surface((width, height), pygame.SRCALPHA)
pygame.draw.rect(glass_surface, (color_r, color_g, color_b, alpha), rect)

# Highlight gradient for frosted effect
for i in range(height // 3):
    alpha = int(50 * (1 - i / (height // 3)))
    pygame.draw.line(surface, (255, 255, 255, alpha), ...)
```

### Particle Physics
```python
# Update particle position and lifetime
particle['pos'][0] += particle['velocity'][0]
particle['pos'][1] += particle['velocity'][1]
particle['lifetime'] -= 1

# Alpha based on remaining lifetime
alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
```

### Glow Effects
```python
# Multi-layer glow rendering
for i in range(glow_layers, 0, -1):
    alpha = base_alpha // (i + 1)
    glow_color = (*color[:3], alpha)
    glow_radius = base_radius + i * spread
    # Draw layer
```

## 👨‍💻 Credits

**Original Game Logic**: Diamond Chase base implementation
**Modern UI Design**: Futuristic glassmorphism redesign
**AI Algorithms**: Minimax and A*+Fuzzy Logic implementations

## 📝 License

Educational project - Free to use and modify

---

**Enjoy the stunning new Diamond Chase experience!** 💎✨