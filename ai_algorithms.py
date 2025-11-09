import math
import random
import time
from typing import List, Tuple, Dict, Optional

class GameState:
    """Game state representation"""
    
    def __init__(self, ai_beads: List[Tuple], human_beads: List[Tuple], neighbour: Dict):
        self.ai_beads = ai_beads[:]
        self.human_beads = human_beads[:]
        self.neighbour = neighbour
    
    def clone(self) -> 'GameState':
        return GameState(self.ai_beads, self.human_beads, self.neighbour)
    
    def get_moves(self, is_ai: bool) -> List[Tuple[Tuple, Tuple]]:
        """Get all legal moves for player"""
        beads = self.ai_beads if is_ai else self.human_beads
        occupied = set(self.ai_beads + self.human_beads)
        moves = []
        
        for bead in beads:
            for neighbor in self.neighbour.get(bead, []):
                if neighbor not in occupied:
                    moves.append((bead, neighbor))
        return moves
    
    def apply_move(self, move: Tuple[Tuple, Tuple], is_ai: bool):
        """Apply move and remove trapped beads"""
        from_pos, to_pos = move
        
        if is_ai:
            if from_pos in self.ai_beads:
                self.ai_beads.remove(from_pos)
                self.ai_beads.append(to_pos)
        else:
            if from_pos in self.human_beads:
                self.human_beads.remove(from_pos)
                self.human_beads.append(to_pos)
        
        self._remove_trapped()
    
    def _remove_trapped(self):
        """Remove beads with no legal moves"""
        occupied = set(self.ai_beads + self.human_beads)
        
        self.ai_beads = [b for b in self.ai_beads 
                        if any(n not in occupied for n in self.neighbour.get(b, []))]
        self.human_beads = [b for b in self.human_beads 
                           if any(n not in occupied for n in self.neighbour.get(b, []))]
    
    def is_terminal(self) -> bool:
        return len(self.ai_beads) < 4 or len(self.human_beads) < 4
    
    def get_result(self, is_ai_perspective: bool) -> float:
        """Get game result from perspective (1.0 = win, 0.0 = loss, 0.5 = draw)"""
        if len(self.human_beads) < 4:
            return 1.0 if is_ai_perspective else 0.0
        elif len(self.ai_beads) < 4:
            return 0.0 if is_ai_perspective else 1.0
        return 0.5
    
    def evaluate_heuristic(self) -> float:
        """Quick position evaluation for AI (0.0 to 1.0)"""
        if self.is_terminal():
            return self.get_result(True)
        
        # Material
        material = (len(self.ai_beads) - len(self.human_beads)) / 6.0
        
        # Mobility
        occupied = set(self.ai_beads + self.human_beads)
        ai_mobility = sum(sum(1 for n in self.neighbour.get(b, []) if n not in occupied) 
                         for b in self.ai_beads)
        human_mobility = sum(sum(1 for n in self.neighbour.get(b, []) if n not in occupied) 
                            for b in self.human_beads)
        
        total = ai_mobility + human_mobility
        mobility = (ai_mobility - human_mobility) / total if total > 0 else 0.0
        
        # Combined score normalized to [0, 1]
        score = 0.5 + material * 0.35 + mobility * 0.15
        return max(0.0, min(1.0, score))


class MCTSNode:
    """Node in Monte Carlo Search Tree"""
    
    def __init__(self, state: GameState, parent: Optional['MCTSNode'] = None, 
                 move: Optional[Tuple] = None, is_ai_turn: bool = True):
        self.state = state
        self.parent = parent
        self.move = move  # Move that led to this state
        self.is_ai_turn = is_ai_turn
        
        self.children = []
        self.untried_moves = state.get_moves(is_ai_turn)
        
        self.visits = 0
        self.wins = 0.0  # From AI perspective
    
    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0
    
    def is_terminal(self) -> bool:
        return self.state.is_terminal()
    
    def select_child(self, exploration: float = 1.414) -> 'MCTSNode':
        """Select best child using UCB1 formula"""
        best_value = -float('inf')
        best_child = None
        
        for child in self.children:
            if child.visits == 0:
                ucb_value = float('inf')
            else:
                # UCB1: exploitation + exploration
                exploitation = child.wins / child.visits
                exploration_term = exploration * math.sqrt(math.log(self.visits) / child.visits)
                ucb_value = exploitation + exploration_term
            
            if ucb_value > best_value:
                best_value = ucb_value
                best_child = child
        
        return best_child
    
    def expand(self) -> 'MCTSNode':
        """Expand a random untried move"""
        move = self.untried_moves.pop(random.randrange(len(self.untried_moves)))
        
        # Create new state
        new_state = self.state.clone()
        new_state.apply_move(move, self.is_ai_turn)
        
        # Create child node with opposite turn
        child = MCTSNode(new_state, parent=self, move=move, is_ai_turn=not self.is_ai_turn)
        self.children.append(child)
        
        return child
    
    def update(self, result: float):
        """Update node statistics"""
        self.visits += 1
        self.wins += result
    
    def best_child_by_visits(self) -> Optional['MCTSNode']:
        """Return most visited child (most robust choice)"""
        if not self.children:
            return None
        return max(self.children, key=lambda c: c.visits)


class MCTS:
    """Monte Carlo Tree Search Algorithm"""
    
    def __init__(self, time_limit: float = 1.0, exploration_constant: float = 1.414):
        self.time_limit = time_limit
        self.exploration_constant = exploration_constant
        self.max_simulation_depth = 80
    
    def search(self, root_state: GameState) -> Optional[Tuple[Tuple, Tuple]]:
        """
        Run MCTS and return best move
        
        Four phases:
        1. Selection: Navigate tree using UCB1
        2. Expansion: Add new node to tree
        3. Simulation: Play random game to end
        4. Backpropagation: Update statistics
        """
        root = MCTSNode(root_state, is_ai_turn=True)
        
        # Quick check for immediate winning move
        for move in root.untried_moves:
            test_state = root_state.clone()
            test_state.apply_move(move, True)
            if test_state.is_terminal() and len(test_state.human_beads) < 4:
                return move
        
        end_time = time.time() + self.time_limit
        iterations = 0
        
        while time.time() < end_time:
            node = root
            state = root_state.clone()
            
            # 1. SELECTION: Navigate to leaf using UCB1
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.select_child(self.exploration_constant)
                state.apply_move(node.move, not node.is_ai_turn)  # Apply move from parent's perspective
            
            # 2. EXPANSION: Add new child if not terminal
            if not node.is_terminal() and node.untried_moves:
                node = node.expand()
                # State already updated in expand()
            
            # 3. SIMULATION: Play random game from this position
            result = self._simulate(node.state.clone(), node.is_ai_turn)
            
            # 4. BACKPROPAGATION: Update all nodes in path
            while node is not None:
                node.update(result)
                node = node.parent
            
            iterations += 1
        
        # Select best move based on visit count (most robust)
        best_child = root.best_child_by_visits()
        
        if best_child and best_child.move:
            return best_child.move
        
        # Fallback to first available move
        moves = root_state.get_moves(True)
        return moves[0] if moves else None
    
    def _simulate(self, state: GameState, is_ai_turn: bool) -> float:
        """
        Simulate random playout from current state
        Returns result from AI perspective (1.0 = AI win, 0.0 = Human win)
        """
        current_turn = is_ai_turn
        depth = 0
        
        while not state.is_terminal() and depth < self.max_simulation_depth:
            moves = state.get_moves(current_turn)
            
            if not moves:
                break
            
            # Mix of random and greedy (70% random, 30% greedy)
            if random.random() < 0.7:
                move = random.choice(moves)
            else:
                move = self._greedy_move(state, moves, current_turn)
            
            state.apply_move(move, current_turn)
            current_turn = not current_turn
            depth += 1
        
        # Return result from AI perspective
        if state.is_terminal():
            return state.get_result(True)
        else:
            # Use heuristic if didn't reach terminal
            return state.evaluate_heuristic()
    
    def _greedy_move(self, state: GameState, moves: List[Tuple], is_ai: bool) -> Tuple:
        """Select move with best immediate evaluation"""
        best_move = moves[0]
        best_score = -float('inf')
        
        # Evaluate a few moves (not all for speed)
        for move in moves[:min(6, len(moves))]:
            test_state = state.clone()
            test_state.apply_move(move, is_ai)
            score = test_state.evaluate_heuristic()
            
            # Flip score if opponent's turn
            if not is_ai:
                score = 1.0 - score
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move


class AStarFuzzyAI:
    """MCTS-based AI (compatible with existing interface)"""
    
    def __init__(self, game_state, fast_mode=False):
        self.neighbour = game_state.neighbour
        self.ai_beads = game_state.ai_beads_position
        self.human_beads = game_state.human_beads_position
        
        # Adjust search time based on mode
        if fast_mode:
            time_limit = 0.15  # 150ms for AI vs AI (faster than delay)
            exploration = 1.2  # Slightly less exploration for speed
        else:
            time_limit = 1.5  # 1.5 seconds vs human
            exploration = 1.414  # Standard sqrt(2)
        
        self.mcts = MCTS(time_limit=time_limit, exploration_constant=exploration)
    
    def update_game_state(self, ai_beads: List[Tuple], human_beads: List[Tuple]):
        """Update game state"""
        self.ai_beads = ai_beads
        self.human_beads = human_beads
    
    def get_best_move(self, current_pos: Tuple) -> Tuple[Tuple, Tuple]:
        """Get best move using MCTS"""
        if not self.ai_beads:
            return (current_pos, current_pos)
        
        # Create game state
        state = GameState(self.ai_beads, self.human_beads, self.neighbour)
        
        # Run MCTS
        move = self.mcts.search(state)
        
        # Validate move
        if move and move[0] in self.ai_beads:
            occupied = set(self.ai_beads + self.human_beads)
            neighbors = self.neighbour.get(move[0], [])
            if move[1] in neighbors and move[1] not in occupied:
                return move
        
        # Fallback: return any valid move
        occupied = set(self.ai_beads + self.human_beads)
        for bead in self.ai_beads:
            for neighbor in self.neighbour.get(bead, []):
                if neighbor not in occupied:
                    return (bead, neighbor)
        
        return (current_pos, current_pos)