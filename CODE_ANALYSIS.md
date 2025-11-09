# Code Analysis: Function Usage Report

## Diamond_Dual.py Analysis

### ✅ USED FUNCTIONS/CLASSES (Necessary)

#### ModernUI Class - All methods used:
- `draw_glassmorphic_panel()` - Used in ModernButton.draw() and draw_score_panel()
- `draw_glowing_text()` - Used multiple times throughout the game
- `draw_glowing_circle()` - Used in Draw_Circle() and for option highlights
- `draw_glowing_line()` - Used in game playing screen
- `draw_glowing_polygon()` - Used in Draw_Polygon()
- `draw_futuristic_background()` - Called in main game loop

#### ParticleSystem Class - All methods used:
- All methods: `__init__()`, `emit()`, `update()`, `draw()`, `emit_confetti()`

#### FloatingTextSystem Class - All methods used:
- All methods: `__init__()`, `spawn()`, `update()`, `draw()`

#### ModernButton Class - Used:
- Used for menu, back, and restart buttons

#### ImageButton Class - Used:
- Used for game mode and AI type selection buttons

#### DiamondAnimation Class - Used:
- Instantiated and `update()`, `draw()` called in game loop

#### Game Logic Functions - All used:
- `Get_First_Hop_Neighbour()`, `Draw_Circle()`, `Find_Match()`, `Heuristic_Val()`, 
- `Check_Winner()`, `Trap_Beads()`, `Draw_Polygon()`, `Heuristic_Value_Min_Max()`, 
- `Empty_Neighbour()`, `All_Heuristic_Value_Min_Max_Ai()`, `All_Heuristic_Value_Min_Max_Human()`, 
- `Mini_Max_Move()`, `draw_score_panel()`, `Game_Loop()`

### ❌ UNUSED FUNCTIONS/CLASSES (Not Necessary)

1. **`draw_text()`** (lines 684-686)
   - Defined but never called
   - Text rendering is done via `ModernUI.draw_glowing_text()` instead

2. **`draw_centered_text_below()`** (lines 689-693)
   - Defined but never called
   - No usage found in the codebase

3. **`MinimalButton` class** (lines 366-437)
   - Fully implemented but never instantiated
   - Code uses `ModernButton` and `ImageButton` instead

4. **`PillButton` class** (lines 440-508)
   - Fully implemented but never instantiated
   - Not used anywhere in the code

5. **`draw_winner_banner()`** (lines 544-580)
   - Defined but never called
   - Winner text is displayed using `ModernUI.draw_glowing_text()` instead (lines 1359-1370)

6. **Unused image variables:**
   - `ai_img` and `human_img` (lines 924-925) are loaded but never used

7. **Unused variables:**
   - `start_time` (line 894) - assigned but never used
   - `dt` (line 955) - assigned but never used
   - `last_move_effect` (lines 951, 1105, 1113) - assigned but never read/used for rendering

---

## ai_algorithms.py Analysis

### ✅ USED CLASSES/METHODS

#### AStarFuzzyAI Class - Used from Diamond_Dual.py:
- `__init__()` - Instantiated in game loop
- `update_game_state()` - Called multiple times
- `get_best_move()` - Called for AI moves
- `get_fast_move()` - Called internally by get_best_move() in fast_mode
- `evaluate_position()` - Called internally
- `minimax_evaluation()` - Called internally
- `get_all_possible_moves()` - Called internally
- `simulate_move()` - Called internally
- `minimax_search()` - Called internally
- `get_empty_neighbors()` - Called internally
- All methods are necessary

#### AStarAI Class - Used internally by AStarFuzzyAI:
- `__init__()` - Used
- `get_neighbors()` - Called by AStarFuzzyAI (lines 275, 282, 348)
- `is_position_occupied()` - Called by AStarFuzzyAI (lines 282, 349)
- `heuristic()` - Called internally by `find_path()` (lines 38, 67)
- `find_path()` - Called internally by `get_best_move()` (line 87)
- `calculate_strategic_value()` - Called internally by `get_best_move()` (line 83)

### ❌ UNUSED METHODS (Not Called Anywhere)

#### AStarAI Class:
1. **`get_best_move()`** (lines 72-95)
   - This is a standalone method that combines A* pathfinding with strategic evaluation
   - Never called from anywhere (neither from Diamond_Dual.py nor from AStarFuzzyAI)
   - The AStarFuzzyAI class has its own `get_best_move()` that doesn't use this one

#### FuzzyLogicAI Class - Used internally by AStarFuzzyAI:
- `__init__()` - Used
- `calculate_aggression_level()` - Called by AStarFuzzyAI (line 543)
- `calculate_defensive_need()` - Called by AStarFuzzyAI (line 548)
- `calculate_mobility_score()` - Called by AStarFuzzyAI (lines 439, 550)
- `calculate_trap_potential()` - Called by AStarFuzzyAI (lines 435, 443, 455, 518, 539, 554)
- `fuzzy_membership()` - Called internally by `fuzzy_decision_making()` (lines 220-221)

#### FuzzyLogicAI Class - Unused:
2. **`fuzzy_decision_making()`** (lines 210-251)
   - This is a standalone fuzzy logic decision method
   - Never called from anywhere (neither from Diamond_Dual.py nor from AStarFuzzyAI)
   - The AStarFuzzyAI uses individual fuzzy methods but doesn't use this combined method

3. **`is_position_occupied()`** (lines 253-258)
   - Duplicate method (same functionality as AStarAI.is_position_occupied())
   - Never called - AStarFuzzyAI uses `self.astar.is_position_occupied()` instead

---

## Summary

### Diamond_Dual.py:
- **Total functions/classes analyzed:** ~30
- **Unused functions/classes:** 6
- **Unused code percentage:** ~20%

### ai_algorithms.py:
- **Total methods analyzed:** ~25
- **Unused methods:** 3
- **Unused code percentage:** ~12%

### Overall:
- **Total unused code:** ~15% of analyzed functions
- **Recommendation:** Remove unused code to reduce maintenance burden and improve code clarity

---

## Notes

- The unused functions in `ai_algorithms.py` (like `AStarAI.get_best_move()` and `FuzzyLogicAI.fuzzy_decision_making()`) appear to be alternative implementations that were superseded by the combined `AStarFuzzyAI` approach.
- The unused classes in `Diamond_Dual.py` (`MinimalButton`, `PillButton`) appear to be alternative UI implementations that were replaced with `ModernButton` and `ImageButton`.
- Unused variables like `start_time`, `dt`, and `last_move_effect` suggest planned features that weren't completed or were removed during development.

