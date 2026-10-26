# Multi-Agent Development System - Core Capabilities

## System Overview
A collaborative AI development system where specialized agents work together through chat interfaces to design, implement, and test software projects. Agents manage code complexity autonomously and maintain persistent context through a centralized blueprint directory.

## Core Architecture

### Fundamental Principles
1. **Design-first development** using BluePrint methodology
2. **Agent sovereignty** - each agent owns specific files and cannot modify others' files
3. **Automatic complexity management** - agents split when files exceed 250 lines
4. **Persistent context** - all agent state stored in `.blueprint/` directory
5. **RAG-enabled routing** - intelligent query routing to expert agents
6. **API-like consultation** - agents provide advice, callers implement

### Agent Hierarchy & Responsibilities

#### UserRepresentativeAgent
- **Ownership**: User interaction and project coordination
- **Spawns**: ArchitectAgent for new projects
- **Authority**: Approve architectural decisions, modify project scope
- **Lifespan**: Permanent per user session

#### ArchitectAgent
- **Ownership**: System architecture and file structure planning
- **Spawns**: CodeAgents and TestAgents for each component
- **Authority**: Define system structure, coordinate refactoring
- **Lifespan**: Project duration

#### CodeAgent
- **Ownership**: Single source file and its blueprint specification
- **Spawns**: New CodeAgents when splitting (complexity > 250 lines)
- **Authority**: Modify only assigned file, define public interface
- **Persistent State**: `.blueprint/{source_path}.blueprint`
- **Lifespan**: Until split or project completion

#### TestAgent
- **Ownership**: Test suite for assigned component
- **Spawns**: None (paired with CodeAgent)
- **Authority**: Generate and maintain tests for paired component
- **Lifespan**: Matches paired CodeAgent

#### InterfaceAgent
- **Ownership**: Coordination between split components
- **Spawns**: None (emerges from CodeAgent splits)
- **Authority**: Manage shared interfaces and version compatibility
- **Lifespan**: While coordination needed between components

## Persistent Context System

### Blueprint Directory Structure
```
.blueprint/                         # Hidden directory at project root
├── src/                           # Mirrors source structure
│   └── [path]/[filename].blueprint # Agent context for each source file
├── agents.json                    # Active agent registry
├── project.json                   # Project metadata
├── dependency-graph.json          # System-wide dependencies
└── split-history.json             # Agent evolution tracking
```

### Context Management Instructions

1. **Context Creation**
   - Create blueprint file when agent spawns
   - Include: identity, responsibilities, dependencies, interfaces, metrics
   - Update agents.json registry

2. **Context Injection**
   - Load blueprint on every agent wake-up
   - Inject into system prompt with current state
   - Verify agent acknowledges responsibilities

3. **Context Updates**
   - Update after: interface changes, splits, dependency modifications
   - Sync complexity metrics regularly
   - Maintain conversation context for continuity

4. **Blueprint File Requirements**
   - Required sections: agent_identity, current_responsibilities, interface_contracts, complexity_metrics
   - Optional sections: dependencies, behavioral_specifications, split_history, conversation_context
   - Size limit: 10KB (larger indicates need for splitting)

## Code Complexity Management

### Splitting Triggers
- File exceeds 250 lines
- Multiple distinct responsibilities detected
- High cyclomatic complexity (>10)
- Excessive dependencies (>5)

### Splitting Process
1. Analyze current responsibilities and identify boundaries
2. Create new blueprints for extracted components
3. Spawn new agents for each component
4. Transform original agent to InterfaceAgent if coordination needed
5. Update all dependent agents with new interfaces
6. Run integration tests to verify split success

### Post-Split Options
- Become InterfaceAgent (coordinate split components)
- Become documentation agent (maintain docs for component group)
- Complete retirement (if no coordination needed)

## RAG System Architecture

### Knowledge Indexing
- **Sources**: Source files, blueprints, interfaces, test scenarios, dependency graphs
- **Method**: Semantic embedding with metadata (file path, agent, complexity)
- **Updates**: Real-time on file changes

### Query Routing
1. Analyze query for domain keywords and intent
2. Match to agent expertise from blueprints
3. Route to single expert or multiple for complex queries
4. Fallback to ArchitectAgent for system-wide questions

### Consultation Protocol
- **Expert agents provide**: Design guidance, interface specs, best practices, usage patterns
- **Expert agents don't**: Modify other files, implement for others, make decisions outside domain
- **Requesting agents must**: Implement in own files, follow provided interfaces, update blueprints

## Communication Patterns

### Chat Channels
- **#general**: Project coordination, major announcements
- **#interfaces**: API design, contract negotiations
- **#consultations**: Expert routing via RAG
- **#testing**: Test coordination, quality reports
- **#architecture**: System design, refactoring plans
- **#alerts**: Automated notifications (complexity warnings, failures)

### Message Commands
- `@agent_name`: Direct mention requiring response
- `compile [language]`: Request code generation
- `test`: Request test generation/execution
- `split`: Trigger complexity-based splitting
- `consult`: Request expert consultation
- `interface_change`: Notify API modifications

## Implementation Instructions

### Agent Initialization
1. Load blueprint from `.blueprint/` directory
2. Parse current state and responsibilities
3. Load system metadata (agents.json, dependencies)
4. Inject comprehensive context into system prompt
5. Acknowledge current responsibilities
6. Update last_accessed timestamp

### File Ownership Rules
1. Each agent modifies only their assigned file(s)
2. Interface changes require negotiation with dependents
3. Consultation provides advice, not implementation
4. Emergency overrides only by ArchitectAgent

### Quality Enforcement
- **Code limits**: 250 lines per file, complexity < 10
- **Test coverage**: Minimum 90%
- **Response time**: Maximum 30 seconds
- **Coordination efficiency**: < 5 messages per negotiation

### System Health Monitoring
- Track active agent count and relationships
- Monitor memory usage per agent (< 50MB)
- Measure message throughput and response times
- Alert on threshold violations

## Critical Operating Rules

1. **Never modify another agent's files** - only provide consultation
2. **Always update blueprint** when responsibilities change
3. **Check complexity metrics** before every code modification
4. **Initiate splitting** proactively when approaching limits
5. **Maintain backward compatibility** when changing interfaces
6. **Document all architectural decisions** in blueprint files
7. **Route queries through RAG** for cross-agent knowledge
8. **Preserve conversation context** across sessions
9. **Test integration** after any structural changes
10. **Escalate conflicts** to ArchitectAgent for resolution
