import sys

from crossword import *

BACKTRACK_COUNTER = 0
WORDS_TESTED = 0


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
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable, domain in self.domains.items():
            consistent_words = set()

            for word in domain:
                if len(word) == variable.length:
                    consistent_words.add(word)

            self.domains[variable] = consistent_words

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # If there is no overlap between variables x and y, no revision is needed.
        if not self.crossword.overlaps[x, y]:
            return False
        
        # Initialize a flag to track if any revision was made.
        revised = False
        # Create a list to hold the new domain of x after removing inconsistent values.
        new_domain = set()
        # Retrieve the positions (i, j) where x and y overlap.
        i, j = self.crossword.overlaps[x, y]
        
        for word_x in self.domains[x]:
            # Initialize a flag to check if word_x satisfies the constraint with any word_y.
            satisfies_constraint = False

            for word_y in self.domains[y]:
                # Check the constraint (characters at the overlap positions must match).
                if word_x[i] == word_y[j]:
                    satisfies_constraint = True
                    break

            # At least one word in the domain of y satisfies the constraint with word_x
            if satisfies_constraint:
                new_domain.add(word_x)
                continue

            # No word in the domain of y satisfies the constraint with word_x
            revised = True
        
        self.domains[x] = new_domain
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If no initial list of arcs is provided, create a list of all arcs
        if arcs is None:
            arcs = [vars for vars, overlap in self.crossword.overlaps.items() if overlap is not None]

        while arcs:
            # Remove the first arc from the list
            x, y = arcs.pop(0)

            # Revise the domain of x based on the domain of y
            if not self.revise(x, y):
                continue

            # If revising x's domain made it empty, arc consistency is not possible
            if not self.domains[x]:
                return False

            # If x's domain was revised, add all arcs (z, x) back to the list of arcs to ensure consistency
            for z in self.crossword.neighbors(x):
                # Prevent adding the same arc in the reverse order
                if z != y:
                    arcs.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all words in the assignment are distinct
        words = assignment.values()
        if len(words) != len(set(words)):
            return False

        # Check if all words have the correct length
        for variable, word in assignment.items():
            if len(word) != variable.length:
                return False
        
        # Check for conflicts between neighboring variables
        for variable in assignment:
            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[variable, neighbor]
                    if assignment[variable][i] != assignment[neighbor][j]:
                        return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Dictionary to count the number of values ruled out for each value in var's domain
        values_counts = dict()

        for value in self.domains[var]:
            # Initialize the count for current value
            values_counts[value] = 0

            for neighbor in self.crossword.neighbors(var):
                # Skip neighbors that are already assigned a value
                if neighbor in assignment:
                    continue

                # Overlap positions between var and the neighbor
                i, j = self.crossword.overlaps[var, neighbor]

                # Count the number of neighbor's values that this value rules out
                for neighbor_value in self.domains[neighbor]:
                    if value[i] != neighbor_value[j]:
                        values_counts[value] += 1 

        # Sort the values by the count of values they rule out (ascending order)
        return sorted(values_counts, key=values_counts.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Set of variables that are not yet assigned
        remaining_variables = self.crossword.variables - set(assignment.keys())
 
        best_var = None
        min_domain_size = float('inf')
        highest_degree = -1

        for var in remaining_variables:
            domain_size = len(self.domains[var])
            degree = len(self.crossword.neighbors(var))
            
            # Check if the current variable has a smaller domain size or higher degree
            if domain_size < min_domain_size or (domain_size == min_domain_size and degree > highest_degree):
                best_var = var
                min_domain_size = domain_size
                highest_degree = degree
        
        return best_var
    
    def inference(self, var, assignment):
        # Restrict domain of `var` based on current assignment
        self.domains[var] = {assignment[var]}

        # Enforce arc consistency
        if not self.ac3(arcs=[(neighbor, var) for neighbor in self.crossword.neighbors(var)]):
            return None
        
        # Collect variables with singleton domains (exactly one value left)
        return {variable: list(domain)[0] for variable, domain in self.domains.items() if len(domain) == 1}

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        global WORDS_TESTED
        global BACKTRACK_COUNTER
        BACKTRACK_COUNTER += 1
        
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        # Copy current domains before making changes
        domains_copy = self.domains.copy()
        
        for value in self.order_domain_values(var, assignment):
            WORDS_TESTED += 1
            assignment[var] = value

            # Check if value is consistent with assignment
            if self.consistent(assignment):
                # Perform inference to reduce domain sizes
                inferences = self.inference(var, assignment)

                # Check if inference is successful
                if inferences is not None:
                    # Copy current assignment before making changes
                    assignment_copy = assignment.copy()

                    # Add inferences to current assignment
                    assignment.update(inferences)

                    # Check if the new assignment is consistent
                    if self.consistent(assignment):
                        # Recursively call backtrack with updated assignment
                        result = self.backtrack(assignment)
                        if result:
                            return result

                    # Remove inferences from current assignment
                    assignment = assignment_copy
     
                # Remove inferences from domains
                self.domains = domains_copy.copy()

            # Remove value from assignment
            del assignment[var]
        
        # If no assignment was successful, return None
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
            
    print("Words tested:", WORDS_TESTED)
    print("Backtrack counter:", BACKTRACK_COUNTER)


if __name__ == "__main__":
    main()
