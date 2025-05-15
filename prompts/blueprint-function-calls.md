# BluePrint: Function Call Interface for Interactive Debugging

## Overview

This document defines the function call interface for BluePrint debugging. It enables LLMs to request execution of code, collect debugging data, and visualize results through an external runtime environment (IDE or CLI).

## Purpose

The function call interface creates a three-way collaboration:
1. **User** provides algorithm design in BluePrint format
2. **LLM** translates the design into code and analyzes issues
3. **Runtime Environment** executes code and provides real execution data

This separation of concerns allows each component to focus on its strengths while creating a seamless debugging experience.

## Function Call API

When processing a `debug` command, the LLM should use these functions to gather execution data:

### Core Execution Functions

#### `bp_execute`
Executes code with specific inputs and returns results.

```json
{
  "function": "bp_execute",
  "arguments": {
    "language": "python",  // Required: programming language
    "code": "def example(): ...",  // Required: source code to execute
    "input_data": [1, 2, 3],  // Optional: input to the program
    "timeout_seconds": 5,  // Optional: execution time limit
    "memory_limit_mb": 100  // Optional: memory limit
  }
}
```

Response format:
```json
{
  "status": "success|error",
  "stdout": "Program output...",
  "stderr": "Error messages...",
  "return_value": "Value returned by the program",
  "execution_time_ms": 42,
  "memory_usage_kb": 1024
}
```

#### `bp_run_tests`
Executes test code against the implementation.

```json
{
  "function": "bp_run_tests",
  "arguments": {
    "language": "python",
    "code": "def binary_search(arr, target): ...",
    "test_code": "def test_binary_search(): ...",
    "test_framework": "unittest|pytest|jest|mocha"
  }
}
```

Response includes test results, coverage, and failures with details.

### Debugging Functions

#### `bp_trace`
Generates detailed execution trace with variable states.

```json
{
  "function": "bp_trace",
  "arguments": {
    "language": "python",
    "code": "def binary_search(arr, target): ...",
    "input_data": [1, 3, 5, 7, 9],
    "target_value": 8,
    "trace_points": ["all_lines", "all_variables"],  // or specific lines/variables
    "max_steps": 100  // prevent infinite loops
  }
}
```

Response includes detailed trace of execution with variable states at each step.

#### `bp_breakpoint`
Runs code until a condition is met, then captures state.

```json
{
  "function": "bp_breakpoint",
  "arguments": {
    "language": "python",
    "code": "def sort(arr): ...",
    "input_data": [5, 3, 1, 4, 2],
    "condition": "arr[0] > arr[1]",  // stop when this is true
    "watch_vars": ["arr", "i", "j"]  // variables to capture
  }
}
```

Response includes program state when the condition is met.

### Visualization Functions

#### `bp_visualize_structure`
Generates visual representation of a data structure.

```json
{
  "function": "bp_visualize_structure",
  "arguments": {
    "structure_type": "array|tree|graph|stack|queue",
    "data": [3, 1, 4, 1, 5, 9],
    "format": "ascii|svg|mermaid",
    "highlight_indices": [2, 4]  // highlight specific elements
  }
}
```

Response includes visualization in the requested format.

#### `bp_execution_diagram`
Creates flowchart of execution path.

```json
{
  "function": "bp_execution_diagram",
  "arguments": {
    "trace_data": { ... },  // from bp_trace
    "diagram_type": "flowchart|sequence|state",
    "format": "mermaid|svg|ascii"
  }
}
```

Response includes diagram visualizing code execution.

#### `bp_variable_history`
Shows how variable values changed during execution.

```json
{
  "function": "bp_variable_history",
  "arguments": {
    "trace_data": { ... },  // from bp_trace
    "variable_names": ["left", "right", "mid"],
    "format": "table|chart|json"
  }
}
```

Response tracks the history of specified variables through execution.

## Edge Case Handling

#### `bp_find_edge_cases`
Automatically discovers edge cases that might cause issues.

```json
{
  "function": "bp_find_edge_cases",
  "arguments": {
    "language": "python",
    "code": "def binary_search(arr, target): ...",
    "input_types": {"arr": "array", "target": "number"},
    "test_categories": ["empty", "single", "duplicates", "boundaries"]
  }
}
```

Response includes discovered edge cases with test inputs and expected outputs.

## Usage Guidelines

When using these functions, the LLM should:

1. **Start simple** - Begin with basic execution before detailed tracing
2. **Be specific** - Request only the data needed for analysis
3. **Analyze patterns** - Look for common issues in the trace data
4. **Provide actionable insights** - Suggest specific code improvements
5. **Show progression** - Demonstrate how the algorithm works step by step

## Example Workflow

For a debugging session, the LLM typically follows this sequence:

1. Generate instrumented code from BluePrint
2. Call `bp_execute` to check for basic functionality
3. If errors occur, use `bp_trace` to get detailed execution data
4. Use `bp_visualize_structure` to show data transformations
5. If appropriate, use `bp_execution_diagram` to visualize flow
6. Analyze all collected data
7. Present findings and suggestions to the user

## Error Handling

When function calls fail, the LLM should:

1. Check for syntax or obvious errors in the generated code
2. Try alternate approaches (different test cases, simplified code)
3. Clearly communicate limitations to the user
4. Suggest manual debugging steps when automated approaches fail

## Security Considerations

The runtime environment implements appropriate sandboxing and resource limits.
The LLM should never attempt to circumvent these protections or execute potentially
harmful code.

## Integration with IDE/CLI

Runtime environments implementing the BluePrint function call interface should:

1. Provide a secure sandbox for code execution
2. Implement all functions with appropriate error handling
3. Return well-formatted responses that the LLM can parse
4. Include clear error messages when function calls fail
5. Enforce reasonable resource limits to prevent abuse

## Future Extensions

The function call interface may be extended with additional capabilities:
1. Database interaction functions
2. Network simulation for testing distributed systems
3. UI rendering for frontend blueprints
4. Performance benchmarking against reference implementations