import copy
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            old_cells = self.cells
            self.cells.remove(cell)
            self.count = self.count - 1
            print("Previous sentence {}. Old sentence {}".format(old_cells, self.cells))
        else:
            print("{} element not present in the sentence {}".format(cell, self.cells))

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            print("{} element not present in the sentence {}".format(cell, self.cells))

    def get_unknown_cells(self):
        return self.cells

    def get_mine_count(self):
        return self.count


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []
        self.directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)
        uncertain_neighbors = self.get_neighboring_cells(cell)
        sentence = self.simplify_sentence(Sentence(uncertain_neighbors, count))
        self.knowledge.append(sentence)
        is_inferred = True
        while is_inferred:
            inferred_safe_cells, inferred_mine_cells = self.infer_safe_and_mine_cells_from_kb()
            inferred_sentences = self.infer_new_sentence_from_kb()
            if not inferred_safe_cells and not inferred_mine_cells and not inferred_sentences:
                break
            self.update_kb_with_inferred_cells(inferred_safe_cells, inferred_mine_cells)
            self.knowledge.extend(inferred_sentences)
            self.knowledge = [
                sentence for sentence in self.knowledge
                if len(sentence.cells) > 0
            ]

    def update_kb_with_inferred_cells(self, inferred_safe_cells, inferred_mine_cells):
        self.safes.update(inferred_safe_cells)
        self.mines.update(inferred_mine_cells)
        for sentence in self.knowledge:
            for cell in inferred_safe_cells.copy():
                sentence.mark_safe(cell)
            for cell in inferred_mine_cells.copy():
                sentence.mark_mine(cell)

    def simplify_sentence(self, sentence: Sentence):
        simplified_sentence = copy.deepcopy(sentence)
        for cell in sentence.cells:
            if cell in self.safes:
                simplified_sentence.mark_safe(cell)
            if cell in self.mines:
                simplified_sentence.mark_mine(cell)
        return simplified_sentence

    def infer_safe_and_mine_cells_from_kb(self):
        new_safe_cells = set()
        new_mine_cells = set()
        for sentence in self.knowledge:
            for cell in sentence.known_safes():  # returns uncertain cells as safe if count == 0
                if cell not in self.safes:
                    new_safe_cells.add(cell)
            for cell in sentence.known_mines():  # returns uncertain cells as mine if count == number of uncertain cells
                if cell not in self.mines:
                    new_mine_cells.add(cell)
        return new_safe_cells, new_mine_cells

    def infer_new_sentence_from_kb(self):
        new_sentences = list()
        for i in range(0, len(self.knowledge) - 1):
            for j in range(i + 1, len(self.knowledge)):
                set_a = set(self.knowledge[i].cells)
                set_b = set(self.knowledge[j].cells)
                if set_a.issubset(set_b):
                    new_logical_statement = Sentence(set_b - set_a, self.knowledge[j].count - self.knowledge[i].count)
                    if self.is_valid_sentence(new_logical_statement) and new_logical_statement not in new_sentences:
                        new_sentences.append(new_logical_statement)
                elif set_b.issubset(set_a):
                    new_logical_statement = Sentence(set_a - set_b, self.knowledge[i].count - self.knowledge[j].count)
                    if self.is_valid_sentence(new_logical_statement) and new_logical_statement not in new_sentences:
                        new_sentences.append(new_logical_statement)
        return list(new_sentences)

    def is_valid_sentence(self, sentence: Sentence):
        return len(sentence.cells) > 0 and sentence.count >= 0 and sentence not in self.knowledge

    def get_neighboring_cells(self, cell):
        neighbors_cells = []
        for i in range(len(self.directions)):
            row = cell[0] + self.directions[i][0]
            col = cell[1] + self.directions[i][1]
            if self.is_within_boundary(row, col):
                neighbors_cells.append((row, col))
        return neighbors_cells

    def is_within_boundary(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        unused_known_safe_cells = self.safes - self.moves_made
        if unused_known_safe_cells is not None and len(unused_known_safe_cells) > 0:
            return random.choice(list(unused_known_safe_cells))
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        cells_to_choose = self.get_unused_unknown_cells()
        if cells_to_choose is None or len(cells_to_choose) == 0:
            return None
        return random.choice(cells_to_choose)

    def get_unused_unknown_cells(self):
        """
        Returns a set of cells which are not mine and unused cells
        """
        cells_to_exclude = self.moves_made | self.mines
        cells_to_choose = [(x, y) for x in range(self.height) for y in range(self.width) if
                           (x, y) not in cells_to_exclude]
        return cells_to_choose
