import copy
import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        if not self.ac3():
            return None
        assignment = self.backtrack(dict())
        return assignment

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            domains = copy.deepcopy(self.domains.get(variable))
            for domain in domains:
                if len(domain) != variable.length:
                    self.domains[variable].remove(domain)

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        (i, j) = self.crossword.overlaps[x, y]
        updated_domain_x = set()
        for domain_x in self.domains[x]:
            for domain_y in self.domains[y]:
                is_match_found = True if domain_x[i] == domain_y[j] else False
                if is_match_found:
                    updated_domain_x.add(domain_x)
                    break

        if updated_domain_x != self.domains[x]:
            self.domains[x] = updated_domain_x
            return True
        return False

    def initial_arcs(self):
        """
        if an overlap exist between variable x and y then add (x,y) (y,x)
        to the arc list
        :return: list of arcs
        """
        arcs = list()
        for variable_x in self.crossword.variables:
            for variable_y in self.crossword.variables:
                if variable_x != variable_y and self.crossword.overlaps[variable_x, variable_y] is not None:
                    arcs.append((variable_x, variable_y))
                    arcs.append((variable_y, variable_x))
        return arcs

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = self.initial_arcs()
        while len(arcs) > 0:
            (x, y) = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x):
                    if neighbor is not y:
                        arcs.append((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable in assignment:
                if variable.length != len(assignment[variable]):
                    return False
                neighbors = self.crossword.neighbors(variable)
                for neighbor in neighbors:
                    (i, j) = self.crossword.overlaps[variable, neighbor]
                    if neighbor in assignment and assignment[variable][i] != assignment[neighbor][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = self.domains.get(var)
        for neighbor in self.crossword.neighbors(var):
            if neighbor in assignment and assignment[neighbor] in values:
                values.remove(assignment[neighbor])
        lcv_score = dict()
        for value in values:
            lcv_score[value] = 0
            for neighbor in self.crossword.neighbors(var):
                (i, j) = self.crossword.overlaps[var, neighbor]
                for domain_value in self.domains.get(neighbor):
                    if value[i] != domain_value[j]:
                        lcv_score[value] += 1
        lcv_score = dict(sorted(lcv_score.items(), key=lambda item: item[1]))
        return list(lcv_score.keys())

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = list()
        for var in self.crossword.variables:
            if var not in assignment:
                unassigned_variables.append(var)
        # sort unassigned variables by minimum number of domain values, highest number of neighbors, random
        unassigned_variables = sorted(unassigned_variables,
                                      key=lambda var: (len(self.domains.get(var)), -len(self.crossword.neighbors(var))))
        return unassigned_variables[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        variable = self.select_unassigned_variable(assignment)
        possible_values = self.order_domain_values(variable, assignment)
        for value in possible_values:
            assignment[variable] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return assignment
            assignment.pop(variable)
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
