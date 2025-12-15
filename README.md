# BluePrint

BluePrint is a **collaborative specification framework** where you and an LLM work together to design software through conversation. You describe what you want to build; the LLM asks focused questions, authors structured specifications, and helps you think through design decisions—all before writing a single line of code.

Think of BluePrint as **design-first development** with an AI engineering partner. The LLM acts as a professional peer who helps you:
- Clarify requirements through dialectic questioning
- Author comprehensive specifications in BluePrint notation
- Identify edge cases and design gaps
- Derive test descriptions that validate the design
- Generate implementation only when you're ready

Currently implemented as prompt files for use with any LLM (Claude, ChatGPT, etc.). Future plans include IDE integration and command-line tools.

## Quick Start

1. **Set up your LLM** with the BluePrint prompt:
   - Use `prompts/blueprint-prompt.md` as your system prompt with Claude, ChatGPT, or similar LLMs
   - For smaller/local models, use `prompts/blueprint-mini.md` instead

2. **Start a design conversation** - Simply describe what you want to build:
   - "I need to build a user authentication system"
   - "Let's design a caching layer for the API"
   - "Help me spec out a file upload feature"

3. **Engage in dialectic refinement** - The LLM will:
   - Ask you **one focused question** at a time
   - Update the specification based on your answer
   - Show you the changes it made
   - Ask the next question
   - Repeat until the design is solid

4. **Review the specification** - The LLM walks through the design section-by-section:
   - Explains each component
   - Derives test descriptions that would verify the behavior
   - Highlights potential issues or gaps
   - You approve or request changes

5. **Compile to code** - When you're satisfied with the design:
   - Issue `compile [language]` (e.g., `compile python`)
   - The LLM generates implementation code with comprehensive tests
   - Tests match the behaviors defined in the specification

## Example Conversation Flow

**You:** "I need a user authentication system"

**LLM:** "What should happen after a user successfully authenticates—should they get a session token, JWT, or something else?"

**You:** "JWT tokens"

**LLM:** "Got it. I've updated the specification:

```blueprint
Service AuthenticationService {
  methods: {
    authenticate(credentials: Credentials) -> AuthResult {
      postconditions: [JWT token issued, expiration set to 24 hours]
    }
  }
}
```

Next question: How should failed login attempts be handled—should there be rate limiting or account lockout?"

**You:** "Lock the account after 3 failed attempts for 15 minutes"

**LLM:** "Updated:

```blueprint
Service AuthenticationService {
  configuration: {
    maxFailedAttempts: 3,
    lockoutDuration: 15 minutes
  },

  methods: {
    authenticate(credentials: Credentials) -> AuthResult {
      preconditions: [account not locked],
      postconditions: [
        success -> JWT issued,
        failure -> attempt logged,
        3rd failure -> account locked for 15 minutes
      ],
      errors: [InvalidCredentials, AccountLocked]
    }
  }
}
```

Should the system notify the user when their account is locked, or just return an error?"

...and so on until the specification is complete.

## Commands You Can Use

During the specification process and review, you can use these commands:

- **`parse`** - Ask the LLM to explain the current specification structure
- **`discuss`** - Open dialogue about tradeoffs and design decisions (e.g., "discuss: is this approach efficient?")
- **`improve`** - Request optimization suggestions for the design
- **`analyze`** - Get analysis of edge cases, complexity, or potential issues
- **`comment`** - Ask for detailed annotations throughout the specification
- **`scenario` / `test`** - Describe a behavior and get a test description (e.g., "scenario: function returns null for empty input")
- **`create summary`** - Generate API summary files for existing code (e.g., "create summary for database.py")
- **`design project [name]`** - Create a comprehensive architecture document
- **`plan development [name]`** - Generate an implementation roadmap
- **`compile [language]`** - **Generate actual code** with tests (e.g., "compile python", "compile typescript")

**Important:** The LLM stays in specification mode until you issue `compile`. This ensures design review happens before implementation.

## Why BluePrint?

- **Design before code** - Think through requirements, edge cases, and behaviors before implementation
- **Collaborative refinement** - An AI partner helps you identify gaps and improve designs
- **Test-driven from the start** - Tests are derived from specifications, ensuring coverage
- **Clear documentation** - The specification IS the documentation
- **Language agnostic** - Specify once, compile to any language
- **Reduced rework** - Catch design issues before they become code bugs
- **Professional dialogue** - The LLM challenges assumptions and suggests better patterns
- **Incremental progress** - Build specifications step-by-step through focused questions

## BluePrint Notation Reference

The LLM authors specifications using BluePrint notation—a flexible, JSON-like syntax. You don't need to write this yourself; the LLM generates it during your conversation. However, understanding the notation helps you review specifications effectively.

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

## The Dialectic Review Process

After the LLM has built a specification through iterative questioning, it will walk you through a **dialectic review**. This is where the real value emerges:

### What Happens During Review

1. **Section-by-section walkthrough** - The LLM presents each part of the specification clearly
2. **Derived test descriptions** - For each behavior, the LLM shows what tests would verify it
3. **Gap identification** - Missing tests reveal missing specifications
4. **Shared understanding** - You and the LLM align on what "done" means

### Example Review

```
LLM: "Let's review what we've designed. I'll walk through each part with the tests that would verify it.

AUTHENTICATION FLOW:
Users authenticate via email/password. After 3 failed attempts, the account locks
for 15 minutes. Sessions expire after 24 hours of inactivity.

This implies these tests:
- Valid credentials return session token
- Invalid password returns error (does not reveal whether email exists)
- Third failed attempt locks account
- Locked account rejects valid credentials with "account locked" message
- Locked account accepts login after 15 minutes
- Session valid at 23:59 of inactivity
- Session rejected at 24:01 of inactivity

Does this match your intent? Do the tests capture what you expect?"
```

You can then:
- Approve the section and move to the next
- Request changes (the LLM updates and re-reviews)
- Ask questions about tradeoffs or edge cases
- Use `improve` or `analyze` commands for deeper examination

## Example Specifications

These examples show the kind of structured specifications the LLM produces during your collaboration. You provide the intent; the LLM authors these documents.

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

## Best Practices for Collaborative Design

### During Specification

1. **Answer questions thoughtfully** - The LLM asks one question at a time for a reason; focused answers lead to better specs
2. **Challenge back** - If you're unsure about a design decision, ask the LLM to explain tradeoffs
3. **Think about edge cases** - When the LLM asks about error handling, consider all the ways things could fail
4. **Be specific about requirements** - "Fast" is vague; "sub-100ms response time" is actionable
5. **Use `discuss` liberally** - Open dialogue when you're uncertain about an approach

### During Review

1. **Read derived tests carefully** - They reveal what the spec actually says, not what you think it says
2. **Ask "what could go wrong?"** - The LLM will identify gaps, but you should actively look for them too
3. **Don't rubber-stamp** - The review is where design flaws surface; take your time
4. **Request `analyze` or `improve`** - Get deeper examination of security, performance, or alternative approaches

### After Compilation

1. **Review generated code** - The LLM follows the spec, but verify the implementation matches your understanding
2. **Run the tests** - They should pass; if not, the spec may have been ambiguous
3. **Iterate if needed** - Go back to specification mode if the implementation reveals design issues

## Limitations

BluePrint works best for algorithms, data structures, and logical processes. It may be less suited for:

- Hardware-specific optimizations
- Complex UI definitions
- Real-time systems with strict timing requirements
- Ultra-performance-critical code where every CPU cycle matters

## FAQ

**Q: Do I need to learn BluePrint syntax to use this?**
A: No! You just describe what you want in natural language. The LLM writes the BluePrint specifications. Understanding the notation helps you review specs, but you don't write it yourself.

**Q: Can BluePrint handle large projects?**
A: Yes. Use `design project` and `plan development` commands to architect the system, then work phase-by-phase on individual components. The LLM ensures consistency across components.

**Q: What if the LLM's specification doesn't match what I wanted?**
A: That's what the dialectic review is for! The LLM walks through the spec section-by-section. You can request changes, ask for `improve` suggestions, or use `discuss` to explore alternatives.

**Q: How does versioning work?**
A: Store your BluePrint specifications in version control (Git). They're human-readable design documents that complement your code.

**Q: Can I write BluePrint specifications manually?**
A: Yes! If you prefer, you can write specs yourself and ask the LLM to `compile` them. But the real power is in the collaborative authoring process.

**Q: What LLMs work best with BluePrint?**
A: Any capable LLM (Claude, ChatGPT, etc.) works with the `blueprint-prompt.md` system prompt. For smaller/local models, try `blueprint-mini.md`.

## Project-Level Design

BluePrint scales from individual components to entire systems. For larger projects, use these commands to create comprehensive architecture documents:

### Design a Project

```
design project MyProject
```

The LLM will ask questions about your project goals, constraints, and requirements, then produce an architecture document covering:
- Project overview and objectives
- Bounded contexts and responsibilities
- Component inventory with dependencies
- Data models and ownership
- Integration points (internal and external)
- Security boundaries and trust zones
- Key technical decisions with rationale

### Plan Development

```
plan development MyProject
```

The LLM generates an implementation roadmap with:
- Phased approach with clear milestones
- Task breakdown for each phase
- Dependencies between tasks
- Risk factors and mitigations
- Deliverables per phase

### Workflow for Large Projects

1. **Start with project design** - Get the architecture documented first
2. **Generate development plan** - Break it into phases
3. **Work phase by phase** - Spec and implement one component at a time
4. **Maintain consistency** - The LLM helps ensure new components align with the overall architecture

This approach keeps you focused on one piece at a time while maintaining the big picture.

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

## Recommended Workflow for New Projects

### Option 1: Bottom-Up (Start Small)

1. **Identify a core component** - Pick the most fundamental piece
2. **Spec it collaboratively** - Describe what you need; the LLM asks questions
3. **Review thoroughly** - Walk through the specification and derived tests
4. **Compile and test** - Generate code, verify it works
5. **Expand incrementally** - Build the next component, referencing the first

### Option 2: Top-Down (Plan First)

1. **Design the project** - Use `design project [name]` to create architecture
2. **Plan development** - Use `plan development [name]` to break into phases
3. **Implement phase by phase** - Spec and compile each component systematically
4. **Maintain consistency** - Reference the project design as you build

### Option 3: Hybrid (Most Common)

1. **Start with conversation** - "I want to build [X]"
2. **Let the LLM guide you** - It may suggest starting with a key component or designing the overall architecture first
3. **Follow the natural flow** - Build specifications iteratively
4. **Compile when ready** - Generate code only after thorough review

The key principle: **specification before implementation**. The exact path depends on your project and personal style.


## Conclusion

We welcome contributions to improve BluePrint! Please feel free to submit issues or pull requests.
