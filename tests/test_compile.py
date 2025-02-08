import sys

sys.path.insert(1, "./")
import pyaces as pyc
import random
from typing import Any, Callable


def test_compile():
    """
    Test for the functionality of the Algebra class and the read_operations function in the pyaces module.

    This test demonstrates the following:

    1. Evaluating algebraic expressions numerically using the `compile()` method of the `Algebra` class. The tests validate that the `compile()` method correctly interprets the input string as a sequence of operations with indices corresponding to elements of the input array.

    2. Indirectly testing the correctness of the `read_operations` function by ensuring that the `compile()` method correctly integrates it for both numerical computation and symbolic representation.

    3. Using a subclass, `StringAlgebra`, to validate the interpretation of algebraic expressions as symbolic strings. This approach ensures that the same `read_operations` function works consistently for symbolic and numerical computations.

    4. Sequential testing of expressions: first testing a subexpression, and then testing a composite expression that builds on the result of the previous one. This validates the correct handling of intermediate results.

    Inputs:
    - array: A random array of integers generated for testing purposes.
    - function1: A lambda function to compute subexpressions of the form `0*1 + 2*3 + 4*5`.
    - function2: A lambda function to compute composite expressions of the form `previous_result*6 + 7`.

    Outputs:
    - Printed verification of each step, showing intermediate results and expected outputs.
    - Assertions to ensure correctness of computations in both numerical and symbolic representations.

    Summary of tests:
    - Test 1: Validate the symbolic string representation of algebraic expressions using `StringAlgebra`.
    - Test 2: Validate the numerical computation of the same expression using `Algebra`.
    - Test 3: Validate a simpler expression numerically using `Algebra`.
    - Test 4: Validate a composite expression by chaining the result of a previous computation with new operations.
    """

    # Generate a random array of integers between 0 and 5, with a length of 8
    array = [random.randint(0, 5) for _ in range(8)]
    print("input array = ", array)

    # Define two example functions to use in testing
    function1 = lambda x0, x1, x2, x3, x4, x5: x0 * x1 + x2 * x3 + x4 * x5
    function2 = lambda y, x6, x7: y * x6 + x7

    # Custom StringAlgebra class for symbolic representation of operations
    class StringAlgebra(pyc.Algebra):
        @staticmethod
        def add(a: Any, b: Any) -> Any:
            """Returns the symbolic addition of two elements."""
            return f"({a} + {b})"

        @staticmethod
        def mult(a: Any, b: Any) -> Any:
            """Returns the symbolic multiplication of two elements."""
            return f"({a} * {b})"

        def compile(self, instruction: str) -> Callable[[list[Any]], Any]:
            """Compiles a string representation of operations into a callable function."""
            return lambda a: pyc.read_operations(self, instruction, a)

    # Test 1: Verify StringAlgebra with a symbolic expression
    print("\n==== Test (0*1+2*3+4*5)*6+7 with StringAlgebra() ====")
    compiled_function = StringAlgebra().compile("(0*1+2*3+4*5)*6+7")
    # Construct the expected symbolic output for comparison
    expected_output = f"(((({array[0]} * {array[1]}) + (({array[2]} * {array[3]}) + ({array[4]} * {array[5]}))) * {array[6]}) + {array[7]})"
    print("[StringAlgebra] expected output =", expected_output)
    output = compiled_function(array)
    print("[StringAlgebra] output =", output)
    # Validate that the output matches the expected symbolic expression
    assert isinstance(output, str) and output == expected_output, (
        "Error in read_operations()"
    )

    # Test 2: Verify Algebra with the same expression using numerical computations
    print("\n==== Test (0*1+2*3+4*5)*6+7 with Algebra() ====")
    compiled_function = pyc.Algebra().compile("(0*1+2*3+4*5)*6+7")
    # Compute the expected numerical output
    expected_output = (
        array[0] * array[1] + array[2] * array[3] + array[4] * array[5]
    ) * array[6] + array[7]
    expected_output_bis = function2(function1(*array[:6]), *array[6:])
    print(
        "[Algebra] expected output =",
        expected_output,
        "which is also: ",
        expected_output_bis,
    )
    output = compiled_function(array)
    print("[Algebra] output =", output)
    # Validate that the output matches the expected numerical result
    assert output == expected_output_bis == expected_output, (
        "Error in read_operations()"
    )

    # Test 3: Verify Algebra with a simpler expression
    print("\n==== Test 0*1+2*3+4*5 with Algebra() ====")
    compiled_function1 = pyc.Algebra().compile("0*1+2*3+4*5")
    # Compute the expected numerical output
    expected_output1 = array[0] * array[1] + array[2] * array[3] + array[4] * array[5]
    expected_output1_bis = function1(*array[:6])
    print(
        "[Algebra] expected output1 =",
        expected_output1,
        "which is also: ",
        expected_output1_bis,
    )
    output1 = compiled_function1(array)
    print("[Algebra] output1 =", output1)
    # Validate that the output matches the expected result
    assert output1 == expected_output1_bis == expected_output1, (
        "Error in read_operations()"
    )

    # Test 4: Verify continuation of a previous result with new indices
    print("\n==== Test previous*6+7 with Algebra() ====")
    compiled_function2 = pyc.Algebra().compile("8*6+7")
    # Compute the expected output by combining the previous result with additional operations
    expected_output2 = expected_output1 * array[6] + array[7]
    expected_output2_bis = function2(expected_output1_bis, *array[6:])
    print(
        "[Algebra] expected output2 =",
        expected_output2,
        "which is also: ",
        expected_output2_bis,
    )
    # Append the previous output1 to the input array at index 8
    output2 = compiled_function2(array + [output1])
    print("[Algebra] output2 =", output2)
    # Validate that the output matches the expected continuation result
    assert output2 == expected_output2_bis == expected_output2, (
        "Error in read_operations()"
    )


if __name__ == "__main__":
    test_compile()
