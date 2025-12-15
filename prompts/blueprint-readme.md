# BluePrint

BluePrint is a **collaborative specification framework** where you and an LLM work together to design software through conversation. You describe what you want to build; the LLM asks focused questions, authors structured specifications, and helps you think through design decisions—all before writing a single line of code.

## The Collaborative Approach

Unlike traditional pseudocode where you write the specification yourself, BluePrint emphasizes:

1. **Dialectic Questioning** - The LLM asks ONE focused question at a time
2. **Incremental Specification** - The LLM updates the spec based on your answers and shows you the changes
3. **Test-Driven Review** - The LLM derives test descriptions that validate each behavior
4. **Design Before Code** - Stay in specification mode until you issue `compile [language]`

## Quick Start

1. **Set up your LLM** with the BluePrint prompt:
   - Use `blueprint-prompt.md` as your system prompt with Claude, ChatGPT, or similar LLMs
   - For smaller/local models, use `blueprint-mini.md` instead

2. **Start a conversation** - Simply describe what you want:
   - "I need to build a user authentication system"
   - "Let's design a caching layer for the API"

3. **Answer questions thoughtfully** - The LLM will ask one question at a time

4. **Review the specification** - The LLM walks through section-by-section with derived tests

5. **Compile when ready** - Issue `compile [language]` to generate implementation code with tests

## Example Workflow

```
You: "I need a user authentication system"

LLM: "What should happen after a user successfully authenticates—
      should they get a session token, JWT, or something else?"

You: "JWT tokens"

LLM: "Got it. I've updated the specification:

Service AuthenticationService {
  methods: {
    authenticate(credentials: Credentials) -> AuthResult {
      postconditions: [JWT token issued, expiration set to 24 hours]
    }
  }
}

Next question: How should failed login attempts be handled—
should there be rate limiting or account lockout?"

...and so on until specification is complete.
```

## Key Commands

- **`discuss`** - Open dialogue about tradeoffs and design decisions
- **`improve`** - Request optimization suggestions
- **`analyze`** - Get analysis of edge cases and potential issues
- **`scenario` / `test`** - Describe a behavior and get test description
- **`design project [name]`** - Create comprehensive architecture document
- **`plan development [name]`** - Generate implementation roadmap
- **`compile [language]`** - Generate actual code with tests

## The LLM's Role

The LLM is your professional engineering partner who:
- Elicits requirements through focused questioning
- Authors BluePrint specifications based on your direction
- Analyzes designs for gaps and edge cases
- Challenges assumptions constructively
- Derives test descriptions during review
- Translates to code only when you issue `compile`

## Your Role

You provide the intent and make the decisions:
- Describe what you want to build
- Answer focused questions about requirements
- Review specifications and derived tests
- Request changes or improvements
- Approve the design
- Decide when to compile

## Full Documentation

For comprehensive documentation including:
- Complete BluePrint notation reference
- Example specifications
- Best practices
- Project-level design workflows
- FAQ and troubleshooting

See the main [README.md](../README.md) in the project root.
