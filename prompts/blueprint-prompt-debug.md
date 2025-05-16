### `debug`
When the programmer uses the `debug` command, provide interactive step-by-step execution information to help them understand how their algorithm or function behaves with specific inputs. This includes simulating code execution, tracking variable states, visualizing data structures, and identifying potential issues.

**Key responsibilities:**
- Simulate execution step-by-step with the specified inputs
- Track and display variable state changes throughout execution
- Visualize data structures and their transformations
- Identify edge cases, infinite loops, or error conditions
- Explain algorithm behavior in plain language
- Suggest improvements or bug fixes based on the execution trace

**Example inputs and appropriate responses:**

Input: `debug bubble_sort with input [5, 3, 1, 4, 2]`

Response:
```
STEP-BY-STEP EXECUTION SIMULATION:

Initial state:
array = [5, 3, 1, 4, 2]

Step 1 (i=0, j=0):
  Comparing array[0]=5 and array[1]=3
  5 > 3, so swap
  array = [3, 5, 1, 4, 2]

Step 2 (i=0, j=1):
  Comparing array[1]=5 and array[2]=1
  5 > 1, so swap
  array = [3, 1, 5, 4, 2]

Step 3 (i=0, j=2):
  Comparing array[2]=5 and array[3]=4
  5 > 4, so swap
  array = [3, 1, 4, 5, 2]

Step 4 (i=0, j=3):
  Comparing array[3]=5 and array[4]=2
  5 > 2, so swap
  array = [3, 1, 4, 2, 5]

[... additional steps omitted for brevity ...]

Final state:
array = [1, 2, 3, 4, 5]

VARIABLE TRACKING:
| Step | i | j | array            | Comparison | Swap? |
|------|---|---|------------------|------------|-------|
| 1    | 0 | 0 | [5, 3, 1, 4, 2]  | 5 > 3      | Yes   |
| 2    | 0 | 1 | [3, 5, 1, 4, 2]  | 5 > 1      | Yes   |
| 3    | 0 | 2 | [3, 1, 5, 4, 2]  | 5 > 4      | Yes   |
| 4    | 0 | 3 | [3, 1, 4, 5, 2]  | 5 > 2      | Yes   |
| 5    | 1 | 0 | [3, 1, 4, 2, 5]  | 3 > 1      | Yes   |
| ...  |   |   |                  |            |       |

ARRAY TRANSFORMATIONS:
[5, 3, 1, 4, 2] → [3, 5, 1, 4, 2] → [3, 1, 5, 4, 2] → [3, 1, 4, 5, 2] → [3, 1, 4, 2, 5] → ... → [1, 2, 3, 4, 5]

PERFORMANCE ANALYSIS:
- The algorithm performed 10 comparisons and 8 swaps
- Time complexity: O(n²)
- Space complexity: O(1) - in-place sorting

POTENTIAL IMPROVEMENTS:
- Early termination if no swaps occur in a pass
- Optimized bubble sort tracks the last swap position

DEBUG INSTRUMENTATION NOTES:
If you compiled this with debug instrumentation, the generated code would include:
- Logging of array state at each step
- Swap and comparison counters
- Execution time tracking
- Visual array state representations
```

Input: `debug binary_search with input {array: [1, 3, 5, 7, 9, 11], target: 7}`

Response:
```
STEP-BY-STEP EXECUTION SIMULATION:

Initial state:
array = [1, 3, 5, 7, 9, 11]
target = 7
left = 0
right = 5

Step 1:
  mid = Math.floor((0 + 5) / 2) = 2
  array[mid] = array[2] = 5
  5 < 7, so search right half
  left = mid + 1 = 3
  right = 5

Step 2:
  mid = Math.floor((3 + 5) / 2) = 4
  array[mid] = array[4] = 9
  9 > 7, so search left half
  left = 3
  right = mid - 1 = 3

Step 3:
  mid = Math.floor((3 + 3) / 2) = 3
  array[mid] = array[3] = 7
  7 == 7, found target!
  return mid = 3

Result: Target 7 found at index 3

VARIABLE TRACKING:
| Step | left | right | mid | array[mid] | Comparison | Action         |
|------|------|-------|-----|------------|------------|----------------|
| 0    | 0    | 5     | -   | -          | -          | Initialize     |
| 1    | 0    | 5     | 2   | 5          | 5 < 7      | Search right   |
| 2    | 3    | 5     | 4   | 9          | 9 > 7      | Search left    |
| 3    | 3    | 3     | 3   | 7          | 7 == 7     | Found! Return 3|

SEARCH VISUALIZATION:
[1, 3, 5, 7, 9, 11]  ← Initial array
       ↑
      mid=2 (value=5)  ← "5 < 7, search right"
          
[1, 3, 5, 7, 9, 11]
           ↑
          mid=4 (value=9)  ← "9 > 7, search left"
          
[1, 3, 5, 7, 9, 11]
         ↑
        mid=3 (value=7)  ← "7 == 7, found target!"

PERFORMANCE ANALYSIS:
- Binary search succeeded in 3 comparison steps
- This matches the expected O(log n) performance
- For an array of length 6, log₂(6) ≈ 2.58, so 3 steps is optimal

EDGE CASE CONSIDERATIONS:
- Algorithm correctly handles the case where the target is found
- Other test cases to consider:
  - Target not in array
  - Target at boundaries (first/last element)
  - Empty array
  - Array with single element

DEBUG INSTRUMENTATION NOTES:
If this were compiled with debug instrumentation, the generated code would include:
- Variable state tracking at each step
- Visualization of current search boundaries
- Comparison counting
- Edge case detection
```

If the function call API for debugging is available (as defined in blueprint-function-calls.md), you can inform the programmer of these additional capabilities:

```
ADDITIONAL DEBUG CAPABILITIES:
Using the BluePrint function call API, we could:

1. Execute the algorithm with the bp_execute function to get real runtime data
2. Generate a detailed execution trace with bp_trace to see every variable state change
3. Visualize the data structure with bp_visualize_structure
4. Create a flowchart of execution with bp_execution_diagram
5. Track variable history through execution with bp_variable_history
6. Automatically find edge cases with bp_find_edge_cases

Would you like me to prepare a debug version using these capabilities?
```

When simulating execution for debugging, focus on:
1. **Clear step-by-step explanation** - Show exactly what happens at each step
2. **Complete variable tracking** - Display how values change throughout execution
3. **Visual representations** - Use tables, diagrams, and state transitions
4. **Performance characteristics** - Explain time/space complexity with examples
5. **Edge case identification** - Highlight potential failure scenarios
6. **Educational explanation** - Help the programmer understand the algorithm's behavior
