# BluePrint

BluePrint is a **collaborative specification framework**. You and an LLM design software together through conversation. You describe what you want to build. The LLM asks focused questions and writes structured specifications. It also helps you examine design decisions. All of this occurs before anyone writes code.

BluePrint is **design-first development** with an AI engineering partner. The LLM is a professional peer. It helps you:
- Make the requirements clear through dialectic questions
- Write complete specifications in BluePrint notation
- Find edge cases and gaps in the design
- Derive test descriptions that verify the design
- Generate code only when you are ready

BluePrint is a set of prompt files and small tools. You can use the prompts with any capable LLM (Claude, ChatGPT, and others). The `blueprint` command lists the installed prompts and tools, and installs the prompts for Claude Code, nanocoder, and agents that use the Agent Skills standard.

## Install

You need Python 3 and Git.

```sh
git clone --recurse-submodules https://github.com/bigattichouse/BluePrint
cd BluePrint
make install
```

`make install` installs the `blueprint` command in `~/.local/bin` and the prompts and tools in `~/.local/share/blueprint`. Make sure that `~/.local/bin` is on your `PATH`.

`make install` also installs the prompts for coding agents. It finds the agents on your computer, and asks before it installs in each location:

| Target | Location | Agents | How to use a prompt |
|---|---|---|---|
| `claude` | `~/.claude/skills/<name>/SKILL.md` | Claude Code | Skill `blueprint-model` |
| `agents` | `~/.agents/skills/<name>/SKILL.md` | Codex, Gemini CLI, pi, OpenCode | Skill `blueprint-model` |
| `nanocoder` | `~/.config/nanocoder/commands/blueprint/<name>.md` | [nanocoder](https://github.com/Nano-Collective/nanocoder) | Command `/blueprint:model` |

The `claude` and `agents` targets use the [Agent Skills](https://agentskills.io/specification) format: one directory for each skill, with a `SKILL.md` file. OpenCode reads both `~/.claude/skills` and `~/.agents/skills`, so it can show each skill two times. Install only one of the two targets if this is a problem.

Without a terminal, or with `blueprint install-skills --yes`, `blueprint` installs in each location that it finds and does not ask.

To keep a prompt with a project, use `blueprint copy NAME`. It copies the prompt into the `spec/` directory of the current project. For a different agent, use `blueprint show NAME -o FILE` or `blueprint copy --all --dir DIR` to write the prompts as plain Markdown files.

| Command | Result |
|---|---|
| `make install PREFIX=/usr/local` | Install in a different directory |
| `make install SKILLS=0` | Do not install the prompts for coding agents |
| `make link` | Link the `blueprint` command to this directory. Use this when you change the prompts. |
| `make uninstall` | Remove the installed files and the skills |
| `make test` | Run the self-tests |

After you install, run `blueprint`:

```sh
blueprint                                  # list the prompts and tools, with paths and summaries
blueprint path ears-lint                   # print the path of one item
blueprint show blueprint-mini              # print one prompt
blueprint show blueprint-mini -o mini.md   # write one prompt to a file
blueprint copy blueprint-model            # copy one prompt into ./spec of this project
blueprint copy --all --dir docs --index    # copy all prompts, with an index, into ./docs
blueprint install-skills                   # ask about each agent that it finds, then install
blueprint install-skills --target agents   # install only in ~/.agents/skills
blueprint install-skills --target nanocoder --project   # into ./.nanocoder/commands
```

In a Claude Code session, you can say: "Run the `blueprint` command to find the prompts and tools for this task." The LLM then reads only the parts that it needs. After you change a prompt, run `blueprint install-skills` again to update the skills.

## Prompt Files

All prompts are in the `prompts/` directory.

| Prompt | Use it to |
|---|---|
| `blueprint-prompt.md` | Design software with a capable LLM (the main prompt) |
| `blueprint-mini.md` | Design software with a small or local LLM |
| `blueprint-specification.md` | Write requirements and tests in STE, with EARS patterns and `Expect` clauses |
| `maker-blueprint.md` | Design physical objects, experiments, and hardware |
| `blueprint-model.md` | Make a mathematical model of a physical system |
| `blueprint-experiments.md` | Explore the design space of a model and test it with hardware |
| `blueprint-experiment-worksheet.md` | Make printable bench worksheets that compare measurements to model predictions |
| `blueprint-observational.md` | Make a model from data that you already have |
| `blueprint-function-calls.md` | Debug code interactively through function calls |
| `security-considerations.md`, `security-mini.md` | Add security requirements to a design |
| `database-patterns.md` | Specify database schemas, queries, and migrations |

## How BluePrint Writes

### Simplified Technical English

The prompts tell the LLM to write documentation, specifications, and code comments in [Simplified Technical English](https://en.wikipedia.org/wiki/Simplified_Technical_English) (ASD-STE100) as much as possible.

STE is a controlled language from the aerospace industry. It uses short sentences, the active voice, and one meaning for each word. Text in STE has fewer misunderstandings and is easier to review and translate. A specification is only useful if every reader understands it the same way.

### Linters

BluePrint includes two linters. Both use Python 3.

- **`ste-lint`** finds passive voice, long sentences, synonyms, and other structural STE problems. It does not examine meaning. It comes from [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), which is a Git submodule in `tools/asd-ste100-skill`.
- **`ears-lint`** examines requirements in the `blueprint-specification` format: EARS patterns, one `shall` in each requirement, `Verify` blocks, and `Expect` clauses. It uses only the Python standard library.

```sh
python3 -I "$(blueprint path ste-lint)" README.md
python3 -I "$(blueprint path ears-lint)" requirements.md
```

### Changelog

The prompts recommend a `CHANGELOG.md` file in the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format for each software project and each design project. BluePrint uses this format in its own [CHANGELOG.md](CHANGELOG.md).

### Simulation, Not Memory

When a design decision depends on numbers, the LLM makes a small model and sweeps its parameters. It does not answer from memory. A number from memory is a guess. A number from a sweep is evidence.

For design of experiments, the prompts use the [robust](https://github.com/bigattichouse/robust) command-line tools:

- `morris` finds which factors have an effect, and which factors interact.
- `sobol` measures how much output variance each factor causes.
- `taguchi` uses orthogonal arrays to find the best settings, and settings that noise does not change.

If the tools are not on your `PATH`, the LLM asks you for the location of your copy. If you do not have a copy, the LLM asks if it can clone and build one.

## Quick Start

1. **Set up your LLM** with the BluePrint prompt:
   - Use `prompts/blueprint-prompt.md` as the system prompt for Claude, ChatGPT, or a similar LLM.
   - For a small or local model, use `prompts/blueprint-mini.md`.

2. **Start a design conversation.** Describe what you want to build:
   - "I need to build a user authentication system"
   - "Let's design a caching layer for the API"
   - "Help me write a specification for a file upload feature"

3. **Refine the specification through dialectic questions.** The LLM does these steps:
   - It asks you **one focused question**.
   - It updates the specification from your answer.
   - It shows you the change.
   - It asks the next question.
   - It repeats these steps until the design is complete.

4. **Review the specification.** The LLM shows the design one section at a time:
   - It explains each component.
   - It derives test descriptions that verify the behavior.
   - It identifies possible problems and gaps.
   - You approve the section or request changes.

5. **Compile to code.** When you approve the design:
   - Type `compile [language]` (for example, `compile python`).
   - The LLM generates code and tests.
   - The tests agree with the behaviors in the specification.

## Example Conversation

**You:** "I need a user authentication system"

**LLM:** "What occurs after a user authenticates? Does the user get a session token, a JWT, or something different?"

**You:** "JWT tokens"

**LLM:** "I updated the specification:

```blueprint
Service AuthenticationService {
  methods: {
    authenticate(credentials: Credentials) -> AuthResult {
      postconditions: [JWT token issued, expiration set to 24 hours]
    }
  }
}
```

Next question: What occurs when a login fails? Do you want rate limiting or an account lockout?"

**You:** "Lock the account after 3 failed attempts for 15 minutes"

**LLM:** "I updated the specification:

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

When the system locks an account, must it send a notification to the user? Or must it only return an error?"

The conversation continues until the specification is complete.

## Commands

You can use these commands during specification and review:

- **`parse`**: The LLM explains the structure of the current specification.
- **`discuss`**: Discuss tradeoffs and design decisions (for example, "discuss: is this approach efficient?").
- **`improve`**: The LLM suggests improvements to the design.
- **`analyze`**: The LLM analyzes edge cases, complexity, and possible problems.
- **`comment`**: The LLM adds detailed comments to the specification.
- **`scenario` / `test`**: Describe a behavior. The LLM writes a test description (for example, "scenario: function returns null for empty input").
- **`create summary`**: The LLM makes API summary files for existing code (for example, "create summary for database.py").
- **`design project [name]`**: The LLM makes an architecture document.
- **`plan development [name]`**: The LLM makes an implementation plan.
- **`compile [language]`**: The LLM **generates code** and tests (for example, "compile python" or "compile typescript").

**Important:** The LLM stays in specification mode until you type `compile`. Thus you review the design before anyone writes code.

## Why Use BluePrint?

- **Design before code.** You examine requirements, edge cases, and behaviors before implementation.
- **Collaborative refinement.** An AI partner helps you find gaps and improve the design.
- **Tests from the start.** The tests come from the specification, so they cover the design.
- **Clear documentation.** The specification is the documentation.
- **Any language.** You write one specification and compile it to any language.
- **Less rework.** You find design problems before they become bugs in the code.
- **Professional dialogue.** The LLM questions assumptions and suggests better patterns.
- **Incremental progress.** You make the specification one step at a time, with one question at a time.

## BluePrint Notation Reference

The LLM writes specifications in BluePrint notation. BluePrint notation is a flexible syntax that is similar to JSON. You do not have to write it. The LLM writes it during the conversation. But if you understand the notation, you can review specifications better.

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

A specification can refer to components in other files:

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

With file references, you can divide a large system into small files. The relations between the components stay clear.

### Behavior Specifications

You can write behaviors in the formal Given/When/Then syntax or in natural language. You can also use both together:

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

Behaviors record what you expect. When you compile, the LLM generates tests from them.

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

## The Dialectic Review

After the questions, the LLM does a **dialectic review** of the specification with you. This step is the most important part of the process.

### Review Steps

1. **One section at a time.** The LLM shows each part of the specification.
2. **Derived test descriptions.** For each behavior, the LLM shows the tests that verify it.
3. **Gaps.** A missing test shows a missing part of the specification.
4. **Shared understanding.** You and the LLM agree on what "done" means.

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

Then you can do one of these:
- Approve the section and go to the next section.
- Request changes. The LLM updates the section and reviews it again.
- Ask about tradeoffs or edge cases.
- Use the `improve` or `analyze` command for a deeper examination.

## Example Specifications

These examples show the type of specification that the LLM writes. You give the intent. The LLM writes the specification.

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

### During Specification

1. **Give careful answers.** The LLM asks one question at a time. Focused answers make better specifications.
2. **Ask questions too.** If you are not sure about a decision, ask the LLM to explain the tradeoffs.
3. **Think about edge cases.** When the LLM asks about errors, think about all the ways that the system can fail.
4. **Give specific requirements.** "Fast" is not specific. "Response time less than 100 ms" is specific.
5. **Use `discuss` frequently.** Use it when you are not sure about an approach.

### During Review

1. **Read the derived tests carefully.** They show what the specification actually says. This can be different from what you think it says.
2. **Ask "what can go wrong?"** The LLM finds gaps, but you must also look for them.
3. **Do not approve without reading.** Design problems become visible during the review. Use as much time as necessary.
4. **Use `analyze` or `improve`.** These commands examine security, performance, and alternative approaches.

### After Compilation

1. **Review the generated code.** Make sure that the code agrees with your understanding of the specification.
2. **Run the tests.** The tests must pass. If they fail, the specification can be ambiguous.
3. **Iterate if necessary.** If the code shows a design problem, go back to specification mode.

## Limitations

BluePrint is best for algorithms, data structures, and logical processes. It is less applicable to:

- Optimizations for specific hardware
- Complex user interfaces
- Real-time systems with strict timing requirements
- Code where each CPU cycle is important

## FAQ

**Q: Must I learn BluePrint syntax?**
A: No. You describe what you want in natural language. The LLM writes the BluePrint specification. If you understand the notation, you can review specifications better, but you do not write them.

**Q: Can BluePrint help with large projects?**
A: Yes. Use the `design project` and `plan development` commands to make the architecture. Then work on one component at a time. The LLM keeps the components consistent.

**Q: What if the specification is not what I wanted?**
A: The dialectic review is for this problem. The LLM shows the specification one section at a time. You can request changes, use `improve` to get suggestions, or use `discuss` to examine alternatives.

**Q: How do I keep versions of a specification?**
A: Keep your BluePrint specifications in version control (for example, Git). They are design documents that people can read, and they go with your code.

**Q: Can I write BluePrint specifications myself?**
A: Yes. You can write a specification and tell the LLM to `compile` it. But the collaborative process gives the most benefit.

**Q: Which LLMs work best with BluePrint?**
A: Any capable LLM (Claude, ChatGPT, and others) works with the `blueprint-prompt.md` system prompt. For a small or local model, use `blueprint-mini.md`.

## Project-Level Design

You can use BluePrint for one component or for a full system. For a large project, use these commands to make architecture documents.

### Design a Project

```
design project MyProject
```

The LLM asks about the goals, constraints, and requirements of your project. Then it makes an architecture document with these items:
- Project overview and objectives
- Bounded contexts and responsibilities
- List of components and their dependencies
- Data models and data ownership
- Integration points (internal and external)
- Security boundaries and trust zones
- Important technical decisions and the reasons for them

### Plan Development

```
plan development MyProject
```

The LLM makes an implementation plan with these items:
- Phases with clear milestones
- Tasks for each phase
- Dependencies between tasks
- Risks and mitigations
- Deliverables for each phase

### Workflow for Large Projects

1. **Design the project first.** Write the architecture document.
2. **Make a development plan.** Divide the work into phases.
3. **Work one phase at a time.** Specify and implement one component at a time.
4. **Keep the components consistent.** The LLM helps make sure that each new component agrees with the architecture.

With this workflow, you work on one part at a time, but you do not lose the full view of the system.

## BluePrint Summary Files (.bps)

A summary file (`.bps`) records the API of your code without the implementation. With summary files, an LLM can understand the structure of a large project without reading all of the code. This uses less of the LLM's context window.

### Make Summary Files

The LLM can make summary files for your existing code:

```
create summary for user_service.py
```

The result is a `.bps` file similar to this one:

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

- **Less context.** The LLM understands your code without the implementations.
- **Clear communication.** The summary shows the API, not the implementation details.
- **Any language.** Summary files work for all programming languages.
- **Documentation.** You can generate API documentation from summary files.

### Use Summary Files

A specification can import summary files:

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

The LLM uses the summary files to understand your code. It does not have to read the full implementation.

## Workflows for New Projects

### Option 1: Bottom-Up (Start Small)

1. **Select a core component.** Start with the most fundamental part.
2. **Specify it together.** Describe what you need. The LLM asks questions.
3. **Review it carefully.** Examine the specification and the derived tests.
4. **Compile and test.** Generate the code and make sure that it works.
5. **Add more components.** Make the next component. It can refer to the first component.

### Option 2: Top-Down (Plan First)

1. **Design the project.** Use `design project [name]` to make the architecture.
2. **Plan the development.** Use `plan development [name]` to divide the work into phases.
3. **Work one phase at a time.** Specify and compile each component in sequence.
4. **Keep the components consistent.** Refer to the project design during the work.

### Option 3: Hybrid (Most Common)

1. **Start with a conversation.** Say "I want to build [X]".
2. **Let the LLM guide you.** It can suggest that you start with one important component, or with the architecture.
3. **Continue step by step.** Make the specification one question at a time.
4. **Compile when you are ready.** Generate code only after a careful review.

The most important rule: **specify before you implement**. The best path depends on your project and on how you prefer to work.

## Contributions

We welcome contributions to BluePrint. Please submit issues or pull requests.
