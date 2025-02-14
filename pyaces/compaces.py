"""
This code defines a set of classes and functions for performing algebraic operations and parsing mathematical expressions involving addition and multiplication. The primary functionalities are as follows:

Classes:
1. class Algebra:
   - A utility class for performing basic algebraic operations, such as addition and multiplication, and compiling instructions into callable functions.

Methods:
- Algebra.add(a: Any, b: Any) -> Any:
   - Performs addition of two elements, returning their sum.

- Algebra.mult(a: Any, b: Any) -> Any:
   - Performs multiplication of two elements, returning their product.

- Algebra.compile(self, instruction: str) -> Callable[[list[Any]], Any]:
   - Compiles an algebraic instruction into a callable function, allowing evaluation with a given input array.

Functions:
2. read_operations(alg: Algebra, instruction: str, array: list[Any], level=0) -> Any:
   - Recursively parses an algebraic instruction string and applies the corresponding operations on the provided input array based on the instruction. Supports nested operations using parentheses.
"""

# =======================================

from typing import Callable, Any

# =======================================


class Algebra(object):
    """
    A utility class for performing basic algebraic operations and compiling instructions into callable functions.
    """

    @staticmethod
    def add(a: Any, b: Any) -> Any:
        """
        Adds two elements and returns their sum.

        Inputs:
            - a (Any): The first element.
            - b (Any): The second element.

        Outputs:
            - Any: The sum of `a` and `b`.

        Example:
            Algebra.add(2, 3) returns 5.
        """
        return a + b

    @staticmethod
    def mult(a: Any, b: Any) -> Any:
        """
        Multiplies two elements and returns their product.

        Inputs:
            - a (Any): The first element.
            - b (Any): The second element.

        Outputs:
            - Any: The product of `a` and `b`.

        Example:
            Algebra.mult(2, 3) returns 6.
        """
        return a * b

    def compile(self, instruction: str) -> Callable[[list[Any]], Any]:
        """
        Compiles an algebraic instruction into a callable function.

        The resulting function can be used to evaluate the instruction with a given input array.

        Inputs:
            - instruction (str): A string representing the algebraic instruction (e.g., "0 + 1 * 2").

        Outputs:
            - Callable[[list[Any]], Any]: A function that evaluates the instruction with a given array.

        Example:
            alg = Algebra()
            func = alg.compile("0 + 1")
            func([10, 20]) returns 30.
        """
        return lambda a: read_operations(self, instruction, a)


# =======================================


def read_operations(
    alg: Algebra, instruction: str, array: list[Any], level: int = 0
) -> Any:
    """
    Recursively parses an algebraic instruction string and applies operations on the input array.

    This function evaluates instructions involving addition and multiplication, supporting nested operations with parentheses. The operations are applied based on their precedence, with addition evaluated before multiplication.

    Inputs:
        - alg (Algebra): An instance of the `Algebra` class for performing operations.
        - instruction (str): A string representing the algebraic instruction (e.g., "0 + (1 * 2)").
        - array (list[Any]): A list of elements to be used in the instruction.
        - level (int): The current depth of nested parentheses (default is 0).

    Outputs:
        - Any: The result of evaluating the instruction on the input array.

    Example:
        alg = Algebra()
        result = read_operations(alg, "0 + 1 * 2", [10, 20, 30])
        result returns 70.
    """
    # Base case: If no operators are present, return the array element at the specified index.
    if all(op not in instruction for op in ["+", "*", "(", ")", " "]):
        return array[int(instruction)]

    # Parse the instruction to identify addition operators at the current level.
    output = {}
    parser = level
    inst = instruction.replace(" ", "")
    for i, s in enumerate(inst):
        if s == "+":
            output[i] = [s, parser]
        elif s == "(":
            parser += 1
        elif s == ")":
            parser -= 1

    pos = [[i, s] for i, [s, p] in output.items() if p == level]
    if not pos:
        # If no addition operators are found, check for multiplication operators.
        output = {}
        parser = level
        for i, s in enumerate(inst):
            if s == "*":
                output[i] = [s, parser]
            elif s == "(":
                parser += 1
            elif s == ")":
                parser -= 1

        pos = [[i, s] for i, [s, p] in output.items() if p == level]
        if not pos:
            # If no operators are found, evaluate the expression inside parentheses.
            return read_operations(alg, inst[1:-1], array, level=level + 1)
        else:
            # Evaluate multiplication at the current level.
            index, symbol = pos[0]
            if symbol == "*":
                return alg.mult(
                    read_operations(alg, inst[:index], array, level=level),
                    read_operations(alg, inst[index + 1 :], array, level=level),
                )
    else:
        # Evaluate addition at the current level.
        index, symbol = pos[0]
        if symbol == "+":
            return alg.add(
                read_operations(alg, inst[:index], array, level=level),
                read_operations(alg, inst[index + 1 :], array, level=level),
            )
