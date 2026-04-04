# Model/Puzzle.py

class Puzzle:
    def __init__(self, question, solution, clues_required=None):
        """
        Represents a puzzle tied to clues.
        :param question: Puzzle prompt/question
        :param solution: Correct answer
        :param clues_required: List of Clue objects required to solve
        """
        self.question = question
        self.solution = solution
        self.clues_required = clues_required if clues_required else []
        self.solved = False

    def attempt(self, answer, player):
        """
        Attempt to solve the puzzle.
        :param answer: Player's answer
        :param player: Player object (to check collected clues)
        :return: True if solved, False otherwise
        """
        if self.clues_required:
            # Ensure player has collected all required clues
            for clue in self.clues_required:
                if clue not in player.inventory:
                    return False

        if answer.strip().lower() == self.solution.strip().lower():
            self.solved = True
            return True
        return False

    def is_solved(self):
        """Return whether puzzle is solved."""
        return self.solved
