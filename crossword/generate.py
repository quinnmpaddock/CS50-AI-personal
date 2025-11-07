import sys

from crossword import *


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
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
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # node consistency == each word in a variable's domain must == variable's length
        for var in self.domains:
            self.domains[var] = {w for w in self.domains[var] if len(w) == var.length}
        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False

        i, j = overlap
        removables = set()

        for wordX in self.domains[x]:
            if not any(wordX[i] == wordY[j] for wordY in self.domains[y]):
                removables.add(wordX)

        if removables:
            self.domains[x] -= removables
            return True

        return False
        # raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        from collections import deque

        # populate queue
        if arcs is None:
            queue = deque(
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            )
        else:
            queue = deque(arcs)

        while queue:
            (x, y) = queue.pop()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.appendleft((z, x))

        return True

        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        return len(assignment) == len(self.crossword.variables)

        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        assigned_words = list(assignment.values())

        for v in assignment:
            vlength = v.length
            if len(assignment[v]) != vlength:
                return False

            if len(assigned_words) != len(set(assigned_words)):
                return False

            for n in self.crossword.neighbors(v):
                if n in assignment:
                    overlap = self.crossword.overlaps[v, n]
                    if overlap is None:
                        continue
                    i, j = overlap
                    if assignment[v][i] != assignment[n][j]:
                        return False

        return True
        # raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        total_elim = []
        for word in self.domains[var]:
            elim = 0
            for n in self.crossword.neighbors(var):
                if n not in assignment:
                    overlap = self.crossword.overlaps[var, n]
                    if overlap is None:
                        continue
                    i, j = overlap
                    for wordN in self.domains[n]:
                        if word[i] != wordN[j]:
                            elim += 1

            total_elim.append((word, elim))

        # order tuples by number of elims:
        sorted_list = sorted((total_elim), key=lambda x: x[1])
        # extract just words:
        sorted_words = [word for word, _ in sorted_list]
        return sorted_words

        # raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        var_list = []
        for var in self.crossword.variables:
            if var not in assignment:
                domain_size = len(self.domains[var])
                degree = len(self.crossword.neighbors(var))
                var_list.append((var, domain_size, degree))

        min_domain = min(v[1] for v in var_list)
        min_domain_vars = [v for v in var_list if v[1] == min_domain]

        # check for min-domain tie
        if len(min_domain_vars) > 1:
            max_degree = max(min_domain_vars, key=lambda v: v[2])
            return max_degree[0]

        return min_domain_vars[0][0]
        # raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        import copy

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            if value not in assignment.values():
                assignment[var] = value
                if self.consistent(assignment):
                    saved_domains = copy.deepcopy(self.domains)

                    # inference
                    arcs = [
                        (neighbor, var) for neighbor in self.crossword.neighbors(var)
                    ]
                    inferences = self.ac3(arcs)

                    if inferences:
                        result = self.backtrack(assignment)
                        if result is not None:
                            return result

                    # backtrack
                    self.domains = saved_domains
                del assignment[var]

        return None

        # raise NotImplementedError


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
