# BluePrint

BluePrint is a pseudocode format designed to facilitate collaboration between human programmers and Large Language Models (LLMs). It allows you to focus on design and logic while the LLM handles translation to specific programming languages and implementation details.

## Quick Start

1. **Install any LLM-powered assistant** that can interpret BluePrint (Claude, ChatGPT, etc.)

2. **Write BluePrint code** using either concise notes or the JSON-like syntax:

**Informal notes:**
```blueprint
Bubble Sort:
- For an item in an array, compare to each of its neighbors
- If the left item is greater than the current item, swap them
- Continue comparing until nothing else can be swapped
```

**OR structured BluePrint syntax:**
```blueprint
Algorithm BubbleSort {
  input: array[] of comparable items,
  output: sorted array[],
  
  steps: [
    for i in range(0, length(array) - 1) {
      for j in range(0, length(array) - i - 1) {
        if (array[j] > array[j+1]) {
          swap(array[j], array[j+1])
        }
      }
    }
    return array
  ]
}
```

3. **Use commands** to interact with your code:
   - `parse` - Get an explanation of your BluePrint (e.g., `parse my_algorithm`)
   - `compile [language]` - Convert to your preferred language with tests (e.g., `compile python`, `compile typescript`)
   - `discuss` - Get implementation feedback (e.g., `discuss: is this approach efficient?`)
   - `improve` - Receive optimization suggestions (e.g., `improve the caching strategy`)
   - `analyze` - Get performance/complexity analysis (e.g., `analyze time complexity`)
   - `comment` - Add detailed explanations to your code (e.g., `comment the recursive function`)
   - `scenario` - Generate test implementation for behavior descriptions (e.g., `scenario function returns null for empty input`). Feel free to use `test` as an alias.
   - `create summary` - Generate API summary files for existing code (e.g., `create summary for database.py`)
   - `debug` - Get interactive step-by-step execution info (e.g., `debug with input [1,2,3]`)

## Why BluePrint?

- **Focus on design** instead of syntax
- **Rapid prototyping** across multiple languages
- **Automatic test generation** with every compilation
- **Collaborative feedback** from LLM experts
- **Documentation built-in** via the comment system
- **Language agnostic** development

## Core Syntax

BluePrint uses a flexible, JSON-like syntax:

### Basic Structure

```blueprint
TypeName Identifier {
  property: value,
  nested_property: {
    sub_property: value
  },
  array_property: [item1, item2, item3],
  typed_array: Type[],
  function_call(parameter) -> return_value
}
```

### File References

BluePrint supports references to components defined in other files:

```blueprint
// Reference to external component
ComponentName found in `path/to/file.blueprint`

// Using an external component
Service AuthService {
  dependencies: {
    client: MyAPIServiceClient found in `src/modules/api/serviceClient.blueprint`
  },
  
  methods: {
    login(credentials) {
      return client.post("/auth/login", credentials)
    }
  }
}
```

This approach allows you to break larger systems into modular files while maintaining clear relationships between components.

### Behavior Specifications

BluePrint supports flexible behavior specifications, from formal Given/When/Then syntax to more natural language descriptions:

```blueprint
// Formal Given/When/Then syntax
Algorithm QuickSort {
  behaviors: [
    Scenario sorting random array {
      Given an unsorted array of integers,
      When the quicksort algorithm is applied,
      Then the array is sorted in ascending order
    }
  ]
}

// Natural language behavior descriptions
DataStructure BinarySearchTree {
  behaviors: [
    When I insert an element, I can later find it by searching.,
    After inserting 1000 random elements, the height should not exceed 20 levels.,
    Finding a non-existent element returns null and makes at most log₂(n) comparisons.
  ]
}

// Mixed approach
Cache LRUCache {
  behaviors: [
    The least recently used item is evicted when capacity is reached.,
    
    Scenario cache hit updates access order {
      Given a partially filled cache,
      When accessing an existing element,
      Then that element becomes the most recently used
    }
  ]
}
```

These behavior specifications help document expectations and automatically generate appropriate tests when compiled.

### Flow Control

```blueprint
if (condition) {
  action()
} else if (another_condition) {
  alternative_action()
} else {
  default_action()
}

for item in collection {
  process(item)
}

while (condition) {
  action()
}
```

### Types and Collections

```
PrimitiveTypes: int, float, string, bool, bit
CollectionTypes: array[], map<KeyType, ValueType>, set<Type>
CustomTypes: Any identifier starting with uppercase (e.g., Person, DataProcessor)
```

## Command Reference

BluePrint supports the following commands:

### `parse`

Analyzes your BluePrint code and explains its structure, components, and purpose.

Example:
```
parse

This BluePrint defines a sorting algorithm that:
- Takes an array of comparable items as input
- Uses the bubble sort approach with O(n²) complexity
- Returns a sorted array with the same elements
```

### `compile [language]`

Translates BluePrint into the requested programming language with tests.

Example:
```
compile python

# Python implementation
def bubble_sort(array):
    n = len(array)
    for i in range(n):
        for j in range(0, n - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
    return array

# Unit Tests
import unittest
class TestBubbleSort(unittest.TestCase):
    # ... comprehensive tests
```

### `discuss`

Engages in dialogue about implementation choices, tradeoffs, and design decisions. You can be informal:

```
discuss: what's the best practices way to store this data in a file?
let's think about how to handle this
```

### `improve`

Suggests optimizations, better patterns, or alternative approaches.

### `analyze`

Evaluates code for potential issues, performance characteristics, or edge cases.

### `comment`

Adds detailed explanations throughout the code to clarify intent and approach.

### `scenario`

Generates test implementation for any behavior description, however vague:

```
scenario function is called with a non numeric string, function returns null

// Test implementation
test('Function returns null when called with non-numeric string', () => {
  const input = "not a number";
  const result = parseNumber(input);
  expect(result).toBeNull();
});
```

```
scenario if file doesn't exist, fail gracefully

// Test implementation
test('File not found errors are handled gracefully', () => {
  const nonExistentFile = "missing.txt";
  const result = readFile(nonExistentFile);
  expect(result.error).toBeDefined();
  expect(result.success).toBe(false);
});
```

## Examples

### Data Structure

```blueprint
DataStructure LinkedList<T> {
  properties: {
    head: Node<T> = null,
    tail: Node<T> = null,
    size: int = 0
  },
  
  methods: {
    append(value: T) -> void {
      new_node = create_node(value)
      
      if (head == null) {
        head = new_node
        tail = new_node
      } else {
        tail.next = new_node
        tail = new_node
      }
      
      size += 1
    },
    
    remove(value: T) -> bool {
      // Implementation details
    }
  }
}

DataStructure Node<T> {
  properties: {
    value: T,
    next: Node<T> = null
  }
}
```

### API Definition

```blueprint
API UserService {
  endpoints: [
    Endpoint CreateUser {
      method: POST,
      path: "/users",
      input: {
        username: string,
        email: string,
        password: string
      },
      validation: {
        username: [required, min_length(3), max_length(50)],
        email: [required, email_format],
        password: [required, min_length(8)]
      },
      output: {
        id: string,
        username: string,
        created_at: timestamp
      },
      error_cases: [
        {status: 400, reason: "ValidationError", message: "Invalid input data"},
        {status: 409, reason: "DuplicateUser", message: "Username already exists"}
      ]
    }
  ]
}
```

## Best Practices

1. **Start small** - Begin with well-defined components before building larger systems
2. **Be explicit about types** - This helps the LLM generate better code
3. **Use descriptive names** - Clear identifiers improve both human and LLM understanding
4. **Comment complex logic** - Explain intricate parts even in the BluePrint
5. **Iterate with feedback** - Use the `discuss` and `improve` commands often
6. **Validate compiled code** - Always review the generated code carefully

## Limitations

BluePrint works best for algorithms, data structures, and logical processes. It may be less suited for:

- Hardware-specific optimizations
- Complex UI definitions
- Real-time systems with strict timing requirements
- Ultra-performance-critical code where every CPU cycle matters

## FAQ

**Q: Can BluePrint handle multiple files or large projects?**  
A: Yes, but it's best to break large projects into smaller components and compile them separately.

**Q: How does versioning work with BluePrint?**  
A: BluePrint is designed as a communication tool, not a development environment. Store your BluePrint code in version control systems like Git.

**Q: Can I extend the BluePrint syntax?**  
A: Yes! The syntax is flexible, and you can introduce your own types and structures. Just be consistent and clear.

## Project-Level Design

BluePrint isn't limited to individual components – it can help design and plan entire projects:

```
design project MyProject
```

This creates a comprehensive design document including:
- Project overview and goals
- Core features and requirements
- Component architecture
- Data models
- Technical specifications

```
plan development MyProject
```

This generates a development plan with:
- Phased implementation approach
- Task breakdowns
- Timeline estimates
- Dependencies and resources
- Deliverables for each phase

These project-level commands help you organize your thoughts and create a structured approach to development before diving into specific components.

### Example Usage

Start with a high-level project design:
```
design project FlappyBirdClone
```

Break it down into development phases:
```
plan development FlappyBirdClone
```

Then implement specific components:
```
Blueprint Bird { ... }
compile javascript
```

This workflow allows you to maintain a clear vision of your project while working on individual parts.

## BluePrint Summary Files (.bps)

For larger projects, BluePrint supports summary files that document API interfaces without including full implementations. These files (with a `.bps` extension) help LLMs understand your code structure without overwhelming their context window.

### Creating Summary Files

The LLM can automatically create summary files for your existing code:

```
create summary for user_service.py
```

This will generate a `.bps` file like:

```blueprint
// file: user_service.bps
Module UserService {
  description: "Handles user authentication and profile management",
  
  functions: [
    authenticate(username: string, password: string) -> AuthResult {
      "Verifies user credentials against the database"
      throws: AuthenticationError
    },
    
    getUserProfile(userId: string) -> UserProfile {
      "Retrieves user profile information"
      notes: "Caches results for 5 minutes"
    }
  ],
  
  types: [
    AuthResult {
      success: boolean,
      userId: string,
      sessionToken: string,
      expiresAt: timestamp
    },
    
    UserProfile {
      userId: string,
      displayName: string,
      email: string,
      preferences: Map<string, string>
    }
  ]
}
```

### Benefits

- **Context Efficiency**: LLMs understand your code without seeing implementations
- **Clearer Communication**: Focus on API surfaces rather than implementation details
- **Cross-Language Support**: Works for any programming language
- **Documentation Generation**: Summary files can generate actual API docs

### Using Summary Files

Reference summary files in your BluePrint code:

```blueprint
Service ProfileManager {
  imports: [
    UserService from "user_service.bps",
    NotificationSystem from "notifications.bps"
  ],
  
  methods: {
    updateUserPreferences(userId, preferences) {
      profile = UserService.getUserProfile(userId)
      // Implementation using the imported services
    }
  }
}
```

The LLM will use these summary files to understand your code without needing to review the full implementation details.

## Conclusion

We welcome contributions to improve BluePrint! Please feel free to submit issues or pull requests.