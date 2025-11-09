# Complete Code Analysis: Diamond Chase Game

## Table of Contents
1. [Game Overview](#game-overview)
2. [Game Architecture](#game-architecture)
3. [Diamond_Dual.py - Complete Analysis](#diamond_dualpy---complete-analysis)
4. [ai_algorithms.py - Complete Analysis](#ai_algorithmspy---complete-analysis)
5. [Game Flow Explanation](#game-flow-explanation)
6. [How Components Interact](#how-components-interact)

---

## Game Overview

**Diamond Chase** is a strategic board game where two players (AI vs Human or AI vs AI) compete by moving beads on a diamond-shaped board. The goal is to trap opponent beads until they have fewer than 4 remaining. Players move beads to adjacent positions, and if a bead's neighbors are all occupied, it gets removed.

---

## Game Architecture

### High-Level Structure:
```
┌─────────────────────────────────────┐
│         Diamond_Dual.py              │
│  ┌────────────────────────────────┐ │
│  │  UI Components                 │ │
│  │  - ModernUI                    │ │
│  │  - Buttons (ModernButton,     │ │
│  │     ImageButton)                │ │
│  │  - ParticleSystem               │ │
│  │  - FloatingTextSystem          │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Game Logic                     │ │
│  │  - GameState                    │ │
│  │  - Move validation              │ │
│  │  - Win condition checking       │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  AI Integration                 │ │
│  │  - Mini_Max_Move (Minimax AI)  │ │
│  │  - AStarFuzzyAI (Hybrid AI)    │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
          │
          │ imports
          ▼
┌─────────────────────────────────────┐
│      ai_algorithms.py                │
│  ┌────────────────────────────────┐ │
│  │  AStarAI                        │ │
│  │  - Pathfinding                 │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  FuzzyLogicAI                   │ │
│  │  - Fuzzy decision making        │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  AStarFuzzyAI                   │ │
│  │  - Combined AI                  │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## Diamond_Dual.py - Complete Analysis

### 1. Initialization & Setup (Lines 1-35)

#### Imports and Screen Setup
```python
import pygame
from ai_algorithms import AStarFuzzyAI
```
- **Purpose**: Imports pygame for graphics and the AI algorithm
- **Screen Setup**: Creates a fullscreen window matching desktop resolution

#### Color Constants
- `COLOR_BG`, `COLOR_PRIMARY`, `COLOR_SECONDARY`: UI colors
- `COLOR_AI`, `COLOR_HUMAN`: Player colors (red for AI, green for human)
- `COLOR_ACCENT`, `COLOR_OPTION`: Highlight colors

---

### 2. ModernUI Class (Lines 37-91)

**Purpose**: Static utility class for drawing modern UI elements with glassmorphic effects

#### Methods:

##### `draw_glassmorphic_panel(surface, rect, color, alpha=180)`
- **What it does**: Draws a frosted glass effect panel
- **How it works**:
  1. Creates a semi-transparent surface
  2. Draws a rounded rectangle with the specified color and alpha
  3. Adds white highlight lines from top (simulating light reflection)
  4. Draws a white border outline
- **Used for**: Score panels, button backgrounds

##### `draw_glowing_text(surface, text, font, color, pos, glow_intensity=1)`
- **What it does**: Renders text with a glowing shadow effect
- **How it works**:
  1. Creates multiple shadow layers with decreasing alpha
  2. Draws shadows in a circular pattern around the text
  3. Renders the main text on top
- **Used for**: Title text, UI labels, winner announcements

##### `draw_glowing_circle(surface, color, center, radius, glow_layers=2)`
- **What it does**: Draws a circle with a glowing halo effect
- **How it works**:
  1. Creates multiple concentric circles with decreasing alpha
  2. Each layer is slightly larger than the previous
  3. Draws the main circle on top
- **Used for**: Game beads, option highlights

##### `draw_glowing_line(surface, color, start, end, width=2)`
- **What it does**: Draws a simple line (glow effect simplified)
- **Used for**: Board connections between nodes

##### `draw_glowing_polygon(surface, color, points, width=2)`
- **What it does**: Draws a polygon outline
- **Used for**: Drawing the diamond-shaped game board

##### `draw_futuristic_background(surface, time_offset=0)`
- **What it does**: Creates an animated gradient background
- **How it works**:
  1. For each horizontal line:
     - Calculates a gradient value based on y position
     - Uses sine waves with different phases for RGB
     - Creates smooth color transitions
  2. `time_offset` allows animation over time
- **Used for**: Main game background

---

### 3. ParticleSystem Class (Lines 94-171)

**Purpose**: Manages particle effects for visual feedback

#### Attributes:
- `self.particles`: List of particle dictionaries

#### Methods:

##### `__init__()`
- Initializes empty particle list

##### `emit(pos, color, count=16, velocity_range=3)`
- **What it does**: Creates particles at a position
- **How it works**:
  1. Generates `count` particles
  2. Each particle has:
     - Random angle (0 to 2π)
     - Random speed based on `velocity_range`
     - Position at `pos`
     - Lifetime (24-48 frames)
     - Random size (2-4 pixels)
  3. Velocity components: `[cos(angle) * speed, sin(angle) * speed]`
- **Used for**: Move animations, button clicks

##### `update()`
- **What it does**: Updates all particles each frame
- **How it works**:
  1. Moves each particle by its velocity
  2. Applies gravity (`velocity[1] += 0.12`)
  3. Decrements lifetime
  4. Handles confetti particles (rotation, spark effects)
  5. Removes particles when lifetime reaches 0
- **Called every frame** in the game loop

##### `draw(surface)`
- **What it does**: Renders all active particles
- **How it works**:
  1. Calculates alpha based on remaining lifetime
  2. Scales size down as particle fades
  3. For confetti: draws rotated rectangles
  4. For regular particles: draws circles
- **Called every frame** after update

##### `emit_confetti(pos, base_color, count=24)`
- **What it does**: Creates confetti particles with spark effects
- **How it works**:
  1. Creates colored confetti pieces with:
     - Jittered colors (variation of base color)
     - Rotation and rotation speed
     - Spark timer for extra effects
  2. Confetti pieces are rectangles that rotate
- **Used for**: Celebration effects when beads are trapped

---

### 4. FloatingTextSystem Class (Lines 174-205)

**Purpose**: Manages floating text that appears and fades away

#### Methods:

##### `spawn(text, pos, color)`
- **What it does**: Creates a floating text item
- **Parameters**:
  - `text`: Text to display (e.g., "+1")
  - `pos`: Starting position (x, y)
  - `color`: Text color
- **Stores**: Position, upward velocity, lifetime

##### `update()`
- **What it does**: Moves text upward and fades it
- **How it works**:
  1. Moves text upward by `vel[1]` (-0.8 pixels/frame)
  2. Decrements lifetime
  3. Removes when lifetime reaches 0

##### `draw(surface)`
- **What it does**: Renders floating text with shadow
- **How it works**:
  1. Calculates alpha based on remaining lifetime
  2. Renders shadow (black) and main text
  3. Draws shadow offset by (2, 2) for depth
- **Used for**: Score notifications ("+1" when trapping beads)

---

### 5. ModernButton Class (Lines 207-280)

**Purpose**: Interactive button with glassmorphic design and animations

#### Attributes:
- `rect`: Button rectangle
- `current_color`: Animated color (smoothly transitions)
- `hover_scale`: Current scale (animates to target)
- `ripple`: Ripple effect on click

#### Methods:

##### `update(mouse_pos, mouse_pressed)`
- **What it does**: Handles button interaction
- **How it works**:
  1. **Hover detection**: If mouse is over button:
     - Sets target scale to 1.05 (5% larger)
     - Smoothly transitions color toward `hover_color`
  2. **Click detection**: If mouse pressed and not already clicked:
     - Triggers action
     - Creates ripple effect at mouse position
  3. **Color animation**: Smoothly interpolates between base and hover colors
  4. **Scale animation**: Smoothly interpolates scale
- **Returns**: `True` if button was clicked this frame

##### `draw(surface)`
- **What it does**: Renders the button with all effects
- **How it works**:
  1. Calculates scaled rectangle size
  2. Draws glassmorphic panel background
  3. Draws multiple border layers (3 layers with decreasing alpha)
  4. Renders text with shadow
  5. Draws ripple effect if active (expanding circle)
- **Visual features**: Glassmorphic effect, smooth scaling, ripple on click

---

### 6. ImageButton Class (Lines 283-363)

**Purpose**: Button with an image icon, circular mask, and glow effect

#### Key Features:
- Circular image (masked to circle)
- Glow effect around button
- Optional text label overlay
- Smooth scale animation on hover

#### Methods:

##### `_make_circular(surf)`
- **What it does**: Converts any surface to a circular mask
- **How it works**:
  1. Creates a square surface (largest dimension)
  2. Centers the image on the square
  3. Creates a circular mask
  4. Applies mask using blend mode
- **Result**: Image appears in a perfect circle

##### `update(mouse_pos, mouse_pressed)`
- Similar to ModernButton but:
  - Scales image instead of rectangle
  - Regenerates circular mask on each update

##### `draw(surface)`
- **What it does**: Draws glowing circular button
- **How it works**:
  1. Draws 5 glow layers (decreasing alpha, increasing radius)
  2. Draws circular image
  3. Draws optional text label with outline
- **Used for**: Game mode selection buttons

---

### 7. DiamondAnimation Class (Lines 510-541)

**Purpose**: Animated diamond icon for the main menu

#### Attributes:
- `rotation`: Current rotation angle (increments each frame)
- `pulse_scale`: Scale that pulses using sine wave

#### Methods:

##### `update()`
- **What it does**: Updates animation
- **How it works**:
  1. Increments rotation by 0.02 radians per frame
  2. Calculates pulse: `1.0 + 0.1 * sin(time * 0.003)`
   - Creates smooth pulsing effect

##### `draw(surface)`
- **What it does**: Draws rotating, pulsing diamond
- **How it works**:
  1. Calculates 4 corner points of diamond based on rotation and pulse
  2. Draws 3 glow layers (offset, decreasing alpha)
  3. Draws main diamond polygon
  4. Draws outline polygon

---

### 8. Board Setup (Lines 610-675)

#### Board Structure:
The game board is a diamond shape with nodes arranged in a specific pattern:

```
       top
        |
   top_l top_r
    |     |
left_t - center_t_up
    |     |
left - center - right
    |     |
left_b - center_t_down
    |     |
  bottom_l bottom_r
        |
     bottom
```

#### Key Variables:
- `center_x`, `center_y`: Center of screen
- `bigger_side`: Distance from center to outer nodes
- `rhombus_width`, `rhombus_height`: Size of rhombus shapes
- `top`, `bottom`, `left`, `right`: Main corner positions
- `center`: Center node position
- Various `_l`, `_r`, `_t` positions: Sub-nodes

##### `Get_First_Hop_Neighbour()`
- **What it does**: Creates a dictionary mapping each node to its valid neighbors
- **How it works**:
  1. For each node, defines which nodes are directly connected
  2. Returns a dictionary: `{node: (neighbor1, neighbor2, ...)}`
- **Critical for**: Move validation, AI pathfinding

**Example**:
```python
{
    top: (top_l, top_r, top_t),  # top connects to 3 neighbors
    center: (center_l, center_r, center_t_up, center_t_down)  # center connects to 4
}
```

#### Initial Positions:
- `ai_beads_position`: 6 beads starting at top positions
- `human_beads_position`: 6 beads starting at bottom positions

---

### 9. Game Logic Functions

#### `Find_Match(ara, pos)` (Lines 701-707)
- **What it does**: Finds if a position matches any bead in an array (with tolerance)
- **How it works**:
  - Checks if `pos` is within 40 pixels of any bead in `ara`
  - Returns `(x, y)` if found, `(-1, -1)` if not
- **Used for**: Click detection, move validation

#### `Heuristic_Val(pos, neighbour, ai_beads, human_beads)` (Lines 710-723)
- **What it does**: Calculates mobility heuristic for Minimax
- **How it works**:
  1. Gets all neighbors of `pos`
  2. Counts how many neighbors are empty (not occupied)
  3. Returns count (0 = completely blocked, higher = more mobile)
- **Used for**: Minimax AI evaluation

#### `Check_Winner(ai_beads_position, human_beads_position)` (Lines 726-732)
- **What it does**: Checks win condition
- **Returns**:
  - `0`: Human wins (AI has < 4 beads)
  - `1`: AI wins (Human has < 4 beads)
  - `-1`: Game continues
- **Win condition**: A player wins when opponent has fewer than 4 beads remaining

#### `Trap_Beads(x, y, neighbour, color, ai_beads, human_beads)` (Lines 735-754)
- **What it does**: Checks if a bead at position `(x, y)` is trapped
- **How it works**:
  1. Gets all neighbors of the bead
  2. Counts how many neighbors are occupied (`count`)
  3. Counts how many opponent beads are neighbors (`count2`)
  4. **Trap condition**: If `count == 0`, the bead has no empty neighbors (trapped!)
- **Returns**: `(count, count2)`
  - `count == 0`: Bead is trapped
  - `count2 > 0`: Opponent beads nearby (good for trapping)
- **Used for**: Removing trapped beads each frame

#### `Draw_Circle(ara, color)` (Lines 696-698)
- **What it does**: Draws all beads in an array
- **How it works**: Calls `ModernUI.draw_glowing_circle()` for each position

#### `Draw_Polygon()` (Lines 757-763)
- **What it does**: Draws the game board structure
- **How it works**: Draws 6 polygons representing the board sections
- **Visual**: Creates the diamond-shaped board outline

#### `Empty_Neighbour(node, ai_beads, human_beads)` (Lines 777-790)
- **What it does**: Gets all valid (empty) neighboring positions
- **How it works**:
  1. Gets all neighbors from the neighbor dictionary
  2. Filters out positions occupied by any bead
  3. Returns list of empty neighbors
- **Used for**: Showing valid moves, AI move generation

---

### 10. Minimax AI Functions

#### `Heuristic_Value_Min_Max(pos, ara_ai, ara_human)` (Lines 766-774)
- **What it does**: Calculates heuristic value for a position
- **How it works**: Similar to `Heuristic_Val` but for Minimax evaluation
- **Returns**: Number of empty neighbors

#### `All_Heuristic_Value_Min_Max_Ai(ara_ai, ara_human)` (Lines 793-798)
- **What it does**: Gets heuristic values for all AI beads
- **Returns**: List of heuristic values

#### `All_Heuristic_Value_Min_Max_Human(ara_ai, ara_human)` (Lines 801-806)
- **What it does**: Gets heuristic values for all human beads
- **Returns**: List of heuristic values

#### `Mini_Max_Move(ara_ai, ara_human, depth, maxPlayer)` (Lines 809-864)
- **What it does**: Minimax algorithm with alpha-beta pruning
- **How it works**:

**Algorithm Overview**:
1. **Base case** (depth == 0):
   - Calculates heuristic for all beads
   - Returns: `(AI_score - Human_score) + (AI_count - Human_count)`

2. **Maximizing player** (AI's turn):
   - Tries all possible moves for AI beads
   - For each move:
     - Creates a temporary game state
     - Recursively evaluates with depth-1 (minimizing turn)
     - Keeps track of best move
   - Returns best move and score

3. **Minimizing player** (Human's turn):
   - Tries all possible moves for human beads
   - For each move:
     - Creates a temporary game state
     - Recursively evaluates with depth-1 (maximizing turn)
     - Keeps track of worst move (for AI)
   - Returns worst move and score

**Parameters**:
- `depth`: How many moves ahead to look (4 for human game, 2 for AI vs AI)
- `maxPlayer`: `True` for AI turn, `False` for human turn

**Returns**: `(score, best_item, best_node)`
- `best_item`: Target position to move to
- `best_node`: Source position to move from

**Time Complexity**: O(b^d) where b = branching factor, d = depth
- With alpha-beta pruning, many branches are cut early

---

### 11. GameState Class (Lines 867-871)

**Purpose**: Holds the current game state

#### Attributes:
- `ai_beads_position`: List of (x, y) positions for AI beads
- `human_beads_position`: List of (x, y) positions for human beads
- `neighbour`: Neighbor dictionary (from `Get_First_Hop_Neighbour()`)

---

### 12. Game Loop - Game_Loop() (Lines 888-1381)

**Purpose**: Main game loop that handles everything

#### State Variables:
```python
current_screen = GAME_MODE_SELECTION  # Current screen state
game_mode = None  # AI_VS_HUMAN or AI_VS_AI
ai_type = None  # MINIMAX_AI or ASTAR_FUZZY_AI
ai_move = True  # Whose turn it is
human_move = False
```

#### Screen States:
- `GAME_MODE_SELECTION`: Main menu (choose AI vs Human or AI vs AI)
- `AI_TYPE_SELECTION`: Choose AI type (Minimax or A*+Fuzzy)
- `GAME_PLAYING`: Active gameplay
- `GAME_OVER`: End game screen

#### Main Loop Structure:

```python
while running:
    # 1. Get input (mouse, keyboard)
    # 2. Update game state (AI moves, particle systems)
    # 3. Handle events (clicks, key presses)
    # 4. Draw everything
    # 5. Update display
```

#### Detailed Flow:

##### 1. Input Gathering (Lines 955-958)
```python
dt = clock.get_time()  # Frame delta time
current_time = pygame.time.get_ticks()  # Current time in ms
mouse_pos = pygame.mouse.get_pos()  # Mouse position
mouse_pressed = pygame.mouse.get_pressed()[0]  # Mouse button state
```

##### 2. Fullscreen Check (Lines 960-968)
- Checks every second if screen size changed
- Resets fullscreen if monitor resolution changed

##### 3. AI Move Handling (Lines 971-1117)

**AI vs AI Mode** (Lines 972-1085):
1. **Timing control**: Waits `simulation_delay` (200ms) between moves
2. **Stuck detection**: If no valid moves for `max_stuck_moves` (10) turns, declares draw
3. **AI 1 (Minimax) turn**:
   - Calls `Mini_Max_Move()` with depth 2
   - Applies strategic filtering:
     - Checks trap potential
     - Evaluates mobility
     - Prefers moves that trap opponents
   - If Minimax move is risky, uses fallback strategy
4. **AI 2 (A*+Fuzzy) turn**:
   - Updates game state
   - Calls `astar_fuzzy_ai.get_best_move()`
   - Validates move (prevents repeating last 4 moves)

**AI vs Human Mode** (Lines 1086-1117):
- **AI turn** (when `ai_move == False` and `human_move == True`):
  - **If Minimax AI**:
    - Calls `Mini_Max_Move()` with depth 4
    - Applies best move
  - **If A*+Fuzzy AI**:
    - Updates game state
    - Calls `astar_fuzzy_ai_full.get_best_move()`
    - Applies best move
    - Falls back to first valid move if AI returns invalid move

##### 4. Event Handling (Lines 1119-1251)

**Keyboard Events**:
- **ESC**: 
  - If in game: Returns to menu
  - Otherwise: Exits game
- **F11**: Forces fullscreen refresh

**Mouse Events** (button clicks):
- **Game Mode Selection**:
  - "AI vs Human": Goes to AI type selection
  - "AI vs AI": Starts AI vs AI game immediately
  
- **AI Type Selection**:
  - "Minimax AI": Starts game with Minimax AI
  - "A*+Fuzzy AI": Starts game with A*+Fuzzy AI
  - "Back": Returns to mode selection

- **In-Game (Human mode only)**:
  - **First click** (`count_human == 0`):
    - Finds if clicked on a human bead
    - If yes: Sets `count_human = 1`, stores position
    - Highlights valid moves (`Empty_Neighbour()`)
  - **Second click** (`count_human == 1`):
    - Checks if clicked on a valid move position
    - If yes: Moves bead, triggers AI turn
    - If no: Resets selection
  - **Back button**: Returns to AI type selection or menu
  - **Restart button**: Resets game state

- **Game Over**:
  - "Back to Menu": Returns to main menu, resets game

##### 5. Update Systems (Lines 1253-1256)
```python
particle_system.update()  # Move particles, apply gravity
floating_texts.update()   # Move floating text upward
diamond_anim.update()     # Rotate and pulse diamond
```

##### 6. Drawing (Lines 1258-1376)

**Background**: Always draws futuristic animated background

**Game Mode Selection Screen**:
- Draws animated diamond
- Draws "DIAMOND CHASE" title
- Draws two mode selection buttons

**AI Type Selection Screen**:
- Draws "Select AI Type" title
- Draws two AI type buttons
- Draws back button

**Game Playing Screen**:
1. **Trap Detection** (Lines 1287-1303):
   - Loops through all beads
   - Calls `Trap_Beads()` for each
   - If trapped (`count == 0`):
     - Removes bead
     - Emits particle explosion
     - Emits confetti
     - Spawns "+1" floating text
   
2. **Score Display**:
   - Calculates scores: `6 - opponent_beads`
   - Uses smooth interpolation for count-up animation
   - Draws two score panels (left and right)
   
3. **Board Rendering**:
   - Draws center lines (vertical and horizontal)
   - Draws all polygons (board structure)
   - Draws all beads (circles)
   - Draws valid move highlights (if human selected a bead)
   
4. **UI Elements**:
   - Instruction text
   - Back and Restart buttons (if not AI vs AI)

5. **Win Check**:
   - Calls `Check_Winner()` each frame
   - If winner detected, transitions to GAME_OVER screen

**Game Over Screen**:
- Determines winner
- Displays appropriate message ("YOU WIN!", "AI WINS!", etc.)
- Draws "Back to Menu" button

**Always Drawn**:
- Particle effects (on top of everything)
- Floating text (score notifications)

##### 7. Display Update (Lines 1378-1379)
```python
pygame.display.flip()  # Update screen
clock.tick(60)         # Limit to 60 FPS
```

---

## ai_algorithms.py - Complete Analysis

### 1. AStarAI Class (Lines 6-115)

**Purpose**: A* pathfinding algorithm for finding optimal paths between positions

#### Methods:

##### `heuristic(pos1, pos2)`
- **What it does**: Calculates Manhattan distance
- **Formula**: `|x1 - x2| + |y1 - y2|`
- **Used for**: A* algorithm's f-score calculation

##### `get_neighbors(pos)`
- **What it does**: Gets valid neighboring positions
- **Returns**: List of positions from the neighbor dictionary
- **Used by**: Pathfinding algorithm

##### `is_position_occupied(pos)`
- **What it does**: Checks if position is within 40 pixels of any bead
- **Returns**: `True` if occupied, `False` otherwise
- **Used for**: Avoiding occupied positions in pathfinding

##### `find_path(start, goal)`
- **What it does**: A* pathfinding algorithm
- **How it works**:
  
  **A* Algorithm**:
  1. **Initialization**:
     - `open_set`: Priority queue of positions to explore (sorted by f-score)
     - `g_score`: Cost from start to each position
     - `f_score`: Estimated total cost (g + heuristic)
     - `came_from`: Tracks path
     
  2. **Main loop**:
     ```python
     while open_set not empty:
         current = node with lowest f-score
         if current == goal:
             reconstruct path and return
         
         for each neighbor:
             if neighbor is visited or occupied:
                 skip
             
             tentative_g = g_score[current] + 1  # Each step costs 1
             if tentative_g < g_score[neighbor]:
                 # Found better path!
                 update g_score, f_score, came_from
                 add to open_set
     ```
  
  3. **Path reconstruction**:
     - Follows `came_from` dictionary from goal to start
     - Reverses to get start-to-goal path
     
  **Returns**: List of positions from start to goal, or empty list if no path

**Note**: This method is currently UNUSED in the game

##### `calculate_strategic_value(pos)`
- **What it does**: Evaluates how strategically valuable a position is
- **Factors**:
  - Empty neighbors (mobility): +1 per empty neighbor
  - Trap opportunities: +3 if can trap opponent
  - Danger: -2 if can be trapped
- **Returns**: Integer score (higher = better)

##### `get_best_move(current_pos)`
- **What it does**: Uses A* to find best strategic move
- **How it works**:
  1. Gets all empty neighbors
  2. For each neighbor:
     - Calculates strategic value
     - Uses A* to find path (if strategic value > 0)
     - Scores: `path_length - strategic_value`
  3. Returns move with best score
- **Note**: This method is currently UNUSED in the game

---

### 2. FuzzyLogicAI Class (Lines 118-258)

**Purpose**: Fuzzy logic system for decision making under uncertainty

#### Methods:

##### `fuzzy_membership(value, low, mid, high)`
- **What it does**: Calculates fuzzy membership values
- **How it works**:
  
  **Triangular Membership Function**:
  ```
        low    mid    high
         |      |      |
        /       |       \
       /        |        \
      /         |         \
     /          |          \
    0           0           0
  ```
  
  - **Low membership**: 1.0 if value ≤ low, decreases to 0 at mid
  - **Medium membership**: Peaks at mid, 0 at low and high
  - **High membership**: 0 until mid, increases to 1.0 at high
  
- **Returns**: Dictionary `{'low': float, 'medium': float, 'high': float}`
- **Example**: If aggression = 0.7, might return `{'low': 0.0, 'medium': 0.4, 'high': 0.6}`

##### `calculate_aggression_level(ai_beads, human_beads)`
- **What it does**: Determines how aggressive AI should be
- **How it works**:
  1. **Edge cases**:
     - If human eliminated: return 0.0 (no need to be aggressive)
     - If AI eliminated: return 1.0 (maximum aggression)
  2. **Base calculation**:
     - Ratio = `ai_count / human_count`
     - Base aggression = `(ratio - 0.3) * 3`, clamped to [0, 1]
  3. **Adjustments**:
     - If behind: +0.3
     - If tied: +0.2
  4. **Returns**: Float in [0, 1]
- **Used for**: Deciding whether to play aggressively or defensively

##### `calculate_defensive_need(ai_beads, human_beads)`
- **What it does**: Determines how defensive AI should be
- **How it works**:
  1. **Edge cases**:
     - If AI eliminated: return 1.0 (maximum defense)
     - If human eliminated: return 0.0 (no defense needed)
  2. **Calculation**:
     - Ratio = `human_count / ai_count`
     - Defensive need = `(ratio - 0.5) * 2`, clamped to [0, 1]
  3. **Returns**: Float in [0, 1]
- **Logic**: Higher when AI has fewer beads (needs to be more careful)

##### `calculate_mobility_score(pos)`
- **What it does**: Calculates how mobile a position is
- **Formula**: `empty_neighbors / total_neighbors`
- **Returns**: Float in [0, 1]
  - 1.0 = all neighbors empty (very mobile)
  - 0.0 = all neighbors occupied (trapped)

##### `calculate_trap_potential(pos, is_ai_move)`
- **What it does**: Calculates how likely a position can trap opponents
- **How it works**:
  1. Gets all neighbors of position
  2. Counts how many opponent beads are neighbors
  3. Returns: `opponent_neighbors / total_neighbors`
- **Parameters**:
  - `is_ai_move`: `True` if checking AI's trap potential, `False` if checking danger from opponent
- **Returns**: Float in [0, 1]
  - Higher = more trap potential (or more dangerous)

##### `fuzzy_decision_making(current_pos, possible_moves)`
- **What it does**: Uses fuzzy logic to choose best move
- **How it works**:
  1. Calculates game state factors:
     - Aggression level
     - Defensive need
  2. Gets fuzzy membership values for these factors
  3. **Fuzzy Rules**:
     - **Rule 1**: If aggression is high → prioritize trap potential (60%) + mobility (40%)
     - **Rule 2**: If defense need is high → prioritize mobility (70%) + trap potential (30%)
     - **Rule 3**: Balanced → equal weight to mobility and trap potential (50/50)
     - **Rule 4**: Avoid dangerous positions → reduce score by 70% if trap potential > 0.6
  4. Scores each possible move
  5. Returns move with highest score
- **Note**: This method is currently UNUSED (AStarFuzzyAI uses individual methods instead)

---

### 3. AStarFuzzyAI Class (Lines 261-577)

**Purpose**: Hybrid AI combining Minimax, A*, and Fuzzy Logic

#### Initialization:
```python
self.astar = AStarAI(game_state)      # A* pathfinding
self.fuzzy = FuzzyLogicAI(game_state) # Fuzzy logic
self.depth = 1 if fast_mode else 2   # Minimax depth
```

#### Methods:

##### `evaluate_position(pos, ai_beads, human_beads)`
- **What it does**: Advanced position evaluation (heuristic for Minimax)
- **How it works**:
  
  **Scoring Factors**:
  1. **Mobility**: `empty_neighbors * 4.0`
  2. **Trap potential**:
     - 2+ opponent neighbors: +25.0
     - 1 opponent neighbor: +8.0
  3. **Safety**:
     - 2+ AI neighbors: +12.0
     - 1 AI neighbor: +4.0
  4. **Strategic positions**:
     - Center positions: +8.0
     - Corner positions: +6.0
  5. **Game state bonuses**:
     - If ahead: score × 1.5
     - If behind: score × 1.8 (more aggressive when losing)
  
- **Returns**: Float score (higher = better position)

##### `minimax_evaluation(ai_beads, human_beads)`
- **What it does**: Final evaluation function for Minimax
- **How it works**:
  1. **Terminal states**:
     - AI < 4 beads: return -2000.0 (AI loses)
     - Human < 4 beads: return +2000.0 (AI wins)
  2. **Position evaluation**:
     - Sums `evaluate_position()` for all AI beads
     - Sums `evaluate_position()` for all human beads (from human perspective)
     - Difference: `ai_score - human_score`
  3. **Bead count bonus**:
     - `(ai_count - human_count) * 15.0`
  4. **Game state multipliers**:
     - If ahead: total × 1.3
     - If behind: total × 1.6
- **Returns**: Float score (positive = AI advantage, negative = AI disadvantage)

##### `get_all_possible_moves(beads)`
- **What it does**: Generates all valid moves for a set of beads
- **Returns**: List of `(source_pos, target_pos)` tuples

##### `simulate_move(ai_beads, human_beads, move, is_ai_turn)`
- **What it does**: Simulates a move without modifying actual game state
- **How it works**:
  1. Deep copies both bead lists
  2. If AI turn: moves AI bead
  3. If human turn: moves human bead
  4. Returns new game state
- **Used for**: Minimax tree exploration

##### `minimax_search(ai_beads, human_beads, depth, is_maximizing, alpha, beta)`
- **What it does**: Minimax algorithm with alpha-beta pruning
- **How it works**:

  **Minimax Algorithm**:
  ```
  function minimax(state, depth, maximizing, alpha, beta):
      if depth == 0 or terminal_state:
          return evaluate(state)
      
      if maximizing:  # AI's turn
          max_eval = -∞
          for each move:
              new_state = simulate_move(state, move)
              eval = minimax(new_state, depth-1, False, alpha, beta)
              max_eval = max(max_eval, eval)
              alpha = max(alpha, eval)
              if beta <= alpha:
                  break  # Alpha-beta pruning
          return max_eval
      
      else:  # Human's turn
          min_eval = +∞
          for each move:
              new_state = simulate_move(state, move)
              eval = minimax(new_state, depth-1, True, alpha, beta)
              min_eval = min(min_eval, eval)
              beta = min(beta, eval)
              if beta <= alpha:
                  break  # Alpha-beta pruning
          return min_eval
  ```
  
  **Alpha-Beta Pruning**:
  - Prunes branches that won't affect final decision
  - Significantly improves performance
  - Doesn't change result, just faster

**Parameters**:
- `depth`: How many moves ahead to look
- `is_maximizing`: `True` for AI, `False` for human
- `alpha`: Best value maximizing player can achieve
- `beta`: Best value minimizing player can achieve

##### `get_fast_move(current_pos)`
- **What it does**: Fast move selection for AI vs AI mode
- **How it works**:
  
  **Scoring Factors** (in priority order):
  1. **Trap potential**: ×200.0 (highest priority)
  2. **Mobility**: ×30.0
  3. **Safety**: -50.0 × danger (avoid being trapped)
  4. **Center control**: +15.0 if near center
  5. **Opponent threats**: -25.0 per dangerous opponent position
  6. **Game state bonuses**:
     - If behind: score × 1.8, +100 × trap_potential
     - If ahead: score × 2.5, +300 × trap_potential, +50 × mobility
     - If tied: score × 1.2
  7. **Pattern breaking**: -50% if same as last move
  
  **Returns**: Best move based on composite score

##### `get_best_move(current_pos)`
- **What it does**: Main move selection (combines Minimax + Fuzzy Logic)
- **How it works**:

  **If fast_mode**:
  - Returns `get_fast_move()` (for AI vs AI)
  
  **Otherwise** (full AI):
  1. **Move categorization**:
     - Separates moves into "trap moves" (trap_potential > 0.5) and "safe moves"
     - Prioritizes trap moves first
   
  2. **For each move**:
     - Simulates the move
     - **Minimax evaluation**: Calls `minimax_search()` to look ahead
     - **Fuzzy bonuses**:
       - Trap potential: +50.0 × trap_potential
       - Aggression bonus: +30.0 × trap_potential (if aggression > threshold)
       - Defense bonus: +25.0 × mobility (if defense need > 0.5)
       - Danger penalty: -15.0 (if danger > 0.8)
       - Game state multipliers:
         - Ahead: ×1.4
         - Behind: ×2.0
     
     - Total score = minimax_score + fuzzy_bonus
   
  3. Returns move with highest total score

##### `update_game_state(ai_beads, human_beads)`
- **What it does**: Updates internal game state for both A* and Fuzzy components
- **Called**: Before each AI move to sync with actual game state

---

## Game Flow Explanation

### 1. Application Startup
1. Initialize pygame
2. Create fullscreen window
3. Define board positions
4. Create neighbor dictionary
5. Initialize game state
6. Call `Game_Loop()`

### 2. Main Menu Flow
```
User sees:
- Animated diamond icon
- "DIAMOND CHASE" title
- "AI vs Human" button
- "AI vs AI" button

User clicks "AI vs Human":
→ Goes to AI Type Selection

User clicks "AI vs AI":
→ Immediately starts AI vs AI game
```

### 3. AI Type Selection (Only for AI vs Human)
```
User sees:
- "Select AI Type" title
- "Minimax AI" button
- "A*+Fuzzy AI" button
- "Back" button

User selects AI type:
→ Starts game with chosen AI
```

### 4. Gameplay Flow

#### Human Turn (AI vs Human mode):
1. **Player clicks a bead**:
   - System finds clicked bead using `Find_Match()`
   - Gets valid moves using `Empty_Neighbour()`
   - Highlights valid positions
   
2. **Player clicks valid move**:
   - Validates move is in valid list
   - Moves bead: `remove(old_pos), append(new_pos)`
   - Emits particle effect
   - Sets `human_move = True`, `ai_move = False`
   - Triggers AI turn

#### AI Turn:
1. **Minimax AI**:
   - Calls `Mini_Max_Move()` with depth 4
   - Returns best move
   - Applies move
   
2. **A*+Fuzzy AI**:
   - Updates game state
   - Calls `get_best_move()`
   - Applies move

#### After Each Move:
1. **Trap detection** (every frame):
   - Checks all beads using `Trap_Beads()`
   - If bead has 0 empty neighbors → removes it
   - Adds visual effects (particles, confetti, "+1" text)
   
2. **Score update**:
   - Calculates: `score = 6 - opponent_beads`
   - Smoothly animates score count-up
   
3. **Win check**:
   - Calls `Check_Winner()` each frame
   - If winner found → transitions to GAME_OVER

### 5. AI vs AI Flow
- Two AI players alternate moves
- 200ms delay between moves (for visibility)
- AI 1 uses Minimax (depth 2)
- AI 2 uses A*+Fuzzy (fast mode)
- Stuck detection prevents infinite loops

---

## How Components Interact

### Data Flow Example: Making a Move

```
User clicks bead
    ↓
Find_Match() → finds bead position
    ↓
Empty_Neighbour() → gets valid moves
    ↓
User clicks destination
    ↓
Validate move → update game_state
    ↓
particle_system.emit() → visual feedback
    ↓
Set human_move = True, ai_move = False
    ↓
[Next frame]
    ↓
AI detects its turn
    ↓
Update AI game state
    ↓
AI.get_best_move() → calculates move
    ↓
Update game_state → move AI bead
    ↓
Trap_Beads() → check for trapped beads
    ↓
If trapped → remove bead, add effects
    ↓
Check_Winner() → check game over
    ↓
Continue or show game over screen
```

### AI Decision Making Flow (A*+Fuzzy):

```
AI's turn triggered
    ↓
update_game_state() → sync with game
    ↓
get_all_possible_moves() → generate options
    ↓
For each move:
    ├─ simulate_move() → try move
    ├─ minimax_search() → look ahead
    ├─ fuzzy.calculate_trap_potential() → assess trap
    ├─ fuzzy.calculate_mobility_score() → assess mobility
    ├─ fuzzy.calculate_aggression_level() → game state
    └─ Combine scores → total_score
    ↓
Select move with highest score
    ↓
Apply move to game_state
```

### Visual Effects Flow:

```
Move happens
    ↓
particle_system.emit() → create particles
    ↓
[Each frame]
particle_system.update() → move particles, apply gravity
particle_system.draw() → render particles
    ↓
Bead trapped
    ↓
particle_system.emit_confetti() → celebration
floating_texts.spawn("+1") → score notification
    ↓
[Each frame]
floating_texts.update() → move text upward
floating_texts.draw() → render with fade
```

---

## Key Algorithms Summary

### 1. Minimax
- **Purpose**: Look ahead to find optimal moves
- **Depth**: 2-4 moves ahead
- **Time**: O(b^d) where b = branching factor, d = depth
- **Optimization**: Alpha-beta pruning

### 2. A* Pathfinding
- **Purpose**: Find optimal path between positions
- **Heuristic**: Manhattan distance
- **Note**: Currently unused but available

### 3. Fuzzy Logic
- **Purpose**: Make decisions under uncertainty
- **Factors**: Aggression, defense need, mobility, trap potential
- **Output**: Scores for different moves

### 4. Hybrid AI (AStarFuzzyAI)
- **Combines**: Minimax lookahead + Fuzzy logic scoring
- **Best of both**: Strategic depth + flexible decision making
- **Performance**: Adjustable depth for speed vs quality

---

## Performance Considerations

### Optimizations:
1. **Alpha-beta pruning**: Cuts Minimax tree exploration
2. **Fast mode**: Reduced depth for AI vs AI
3. **Move history**: Prevents repetitive moves
4. **Early exits**: Stuck detection for deadlock situations

### Frame Rate:
- Target: 60 FPS
- Managed by: `clock.tick(60)`
- Components updated each frame:
  - Particle system
  - Floating text
  - Animations
  - AI (when it's their turn)

---

## Conclusion

This game demonstrates:
- **Complex AI**: Multiple algorithms (Minimax, A*, Fuzzy Logic)
- **Modern UI**: Glassmorphic design, particle effects, animations
- **Game Architecture**: Clean separation of concerns
- **User Experience**: Smooth interactions, visual feedback

The code is well-structured with clear responsibilities for each component. The AI systems work together to provide challenging gameplay while maintaining performance.

