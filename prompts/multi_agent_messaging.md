# Multi-Agent Development System - Simplified Matrix Implementation

## Overview
A streamlined Matrix-based communication system for AI development agents. Focuses on core functionality while leveraging Matrix's native chat features for human observability.

## Core Principles
1. **Start Simple** - Basic Matrix features only, add complexity when needed
2. **Human Observable** - All agent interactions visible through standard Matrix clients
3. **Performance Aware** - Monitor and optimize for multi-agent scenarios
4. **Sovereignty Preserved** - Agents consult but never modify others' files
5. **Matrix-Native Solutions** - Use built-in Matrix features over custom protocols
6. **Chat as Interface** - All interactions happen through chat (debugging, monitoring, config)

## Matrix Architecture

### Simplified Structure
```
Matrix Homeserver (agents.local)
├── Agent Accounts (functional names only)
│   ├── @auth-service:agents.local
│   ├── @user-service:agents.local
│   ├── @task-service:agents.local
│   └── @architect:agents.local
│
├── Core Rooms
│   ├── #general:agents.local      # Project coordination
│   ├── #interfaces:agents.local   # API negotiations  
│   ├── #consultations:agents.local # Expert advice
│   ├── #testing:agents.local      # Test coordination
│   ├── #architecture:agents.local # System design
│   └── #alerts:agents.local       # System notifications
│
└── Direct Messages (created on demand)
```

## Security & Authentication

### Agent Registration via Application Service
```javascript
// Matrix Application Service controls agent creation
const appService = {
  id: "agent-spawner",
  hs_token: process.env.HOMESERVER_TOKEN,
  as_token: process.env.APP_SERVICE_TOKEN,
  namespaces: {
    users: [{
      exclusive: true,
      regex: "@.*-agent:agents.local"  // Only app service can create agents
    }]
  }
};

// Only ArchitectAgent can spawn new agents through app service
class ArchitectAgent {
  async spawnAgent(agentName, sourceFile) {
    const response = await fetch(`${this.appServiceUrl}/spawn`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.as_token}` },
      body: JSON.stringify({
        agent_name: agentName,
        source_file: sourceFile,
        spawned_by: this.name
      })
    });
    
    return response.json(); // Returns agent credentials
  }
}
```

**Key Decision**: No manual agent registration - all agents created through secure application service.

## Data Consistency

### Matrix as Single Source of Truth
```javascript
class BaseAgent {
  async initialize() {
    // Matrix account data is THE source of truth
    const context = await this.client.getAccountData("agent.context");
    if (!context) {
      throw new Error("Agent context not found in Matrix - cannot start");
    }
    
    this.blueprint = context;
    
    // Filesystem is cache only - regenerate from Matrix
    await this.cacheToFilesystem(context);
  }
  
  async updateBlueprint(changes) {
    // ALWAYS update Matrix first
    const updated = { ...this.blueprint, ...changes };
    await this.client.setAccountData("agent.context", updated);
    
    // Then update filesystem cache
    await this.cacheToFilesystem(updated);
    
    this.blueprint = updated;
  }
  
  async cacheToFilesystem(blueprint) {
    // Filesystem is read-only backup/cache
    const cachePath = `.blueprint-cache/${this.sourceFile}.json`;
    await fs.writeFile(cachePath, JSON.stringify(blueprint, null, 2));
  }
}
```

**Key Decision**: Filesystem `.blueprint/` becomes `.blueprint-cache/` - just a cache, not source of truth.

## Simplified Message Format

### Basic Message Structure
```javascript
{
  "msgtype": "m.text",
  "body": "@user-service I need interface for findByEmail method",
  "m.relates_to": {
    "rel_type": "m.thread",    // Use native Matrix threading
    "event_id": "$parent_event_id"
  },
  "agent.cmd": {               // Minimal agent metadata
    "type": "consult",         // consult|compile|test|split
    "file": "src/services/AuthService.ts",
    "lines": 187
  }
}
```

### Command Types (via text parsing)
- `@agent-name` - Direct consultation request
- `compile [language]` - Generate code
- `test` - Generate tests
- `split` - Initiate complexity-based split
- Text patterns for natural consultation

## Agent Implementation

### Minimal Base Agent
```javascript
const sdk = require("matrix-js-sdk");

class BaseAgent {
  constructor(name, sourceFile) {
    this.name = name;
    this.sourceFile = sourceFile;
    this.userId = `@${name}:agents.local`;
    this.client = null;
  }

  async initialize() {
    // Create Matrix client
    this.client = sdk.createClient({
      baseUrl: "https://matrix.agents.local",
      userId: this.userId,
      accessToken: await this.register(),
      deviceId: this.name
    });

    // Load blueprint context
    await this.refreshBlueprint();
    
    // Store blueprint in account data (not in every message)
    await this.updateAccountData();
    
    // Join essential rooms
    await this.joinRooms();
    
    // Start listening
    this.client.on("Room.timeline", this.handleEvent.bind(this));
    await this.client.startClient();
    
    // Simple status
    await this.setStatus(`Managing ${this.sourceFile}`);
  }

  async register() {
    // Register with homeserver (simplified)
    const registration = await fetch(`${this.homeserver}/_matrix/client/r0/register`, {
      method: 'POST',
      body: JSON.stringify({
        type: "m.login.dummy",
        username: this.name,
        password: generatePassword(),
        device_id: this.name,
        initial_device_display_name: `Agent: ${this.name}`
      })
    });
    return registration.access_token;
  }

  async refreshBlueprint() {
    const blueprintPath = `.blueprint/${this.sourceFile}.blueprint`;
    this.blueprint = await readBlueprintFile(blueprintPath);
    this.complexity = this.blueprint.complexity_metrics;
  }

  async updateAccountData() {
    // Store blueprint context in Matrix account data
    await this.client.setAccountData("agent.context", {
      file: this.sourceFile,
      blueprint_path: `.blueprint/${this.sourceFile}.blueprint`,
      complexity: this.complexity,
      responsibilities: this.blueprint.current_responsibilities,
      last_updated: new Date().toISOString()
    });
  }

  async joinRooms() {
    const rooms = this.getRequiredRooms();
    for (const room of rooms) {
      try {
        await this.client.joinRoom(room);
      } catch (e) {
        console.error(`Failed to join ${room}:`, e.message);
      }
    }
  }

  getRequiredRooms() {
    // Minimal room subscriptions based on agent type
    const base = ['#general:agents.local', '#alerts:agents.local'];
    
    if (this.sourceFile) { // CodeAgent
      return [...base, '#interfaces:agents.local', '#consultations:agents.local'];
    } else if (this.name === 'architect') {
      return [...base, '#architecture:agents.local', '#interfaces:agents.local'];
    }
    
    return base;
  }

  async setStatus(statusMsg) {
    await this.client.setPresence({
      presence: "online",
      status_msg: statusMsg
    });
  }
}
```

### Message Handling (Simplified)
```javascript
class BaseAgent {
  async handleEvent(event, room) {
    if (event.getType() !== "m.room.message") return;
    if (event.getSender() === this.userId) return;
    
    const content = event.getContent();
    const body = content.body || "";
    
    // Check if message is for us
    if (!this.isRelevantMessage(body, room)) return;
    
    // Extract command from message
    const command = this.parseCommand(body, content);
    
    // Handle command
    await this.executeCommand(command, event, room);
  }

  isRelevantMessage(body, room) {
    // Direct mention
    if (body.includes(`@${this.name}`)) return true;
    
    // Direct message room
    const members = room.getMembers();
    if (members.length === 2 && members.some(m => m.userId === this.userId)) {
      return true;
    }
    
    // Consultation room with expertise match
    if (room.roomId === this.consultationRoomId) {
      return this.matchesExpertise(body);
    }
    
    return false;
  }

  parseCommand(body, content) {
    // Check explicit command in metadata
    if (content['agent.cmd']) {
      return content['agent.cmd'].type;
    }
    
    // Parse from message text
    if (body.match(/compile\s+(\w+)/i)) return 'compile';
    if (body.match(/test/i)) return 'test';
    if (body.match(/split/i)) return 'split';
    if (body.includes('interface') || body.includes('how do I')) return 'consult';
    
    return 'message';
  }

  async executeCommand(command, event, room) {
    switch (command) {
      case 'consult':
        await this.handleConsultation(event, room);
        break;
      case 'compile':
        await this.handleCompile(event, room);
        break;
      case 'test':
        await this.handleTest(event, room);
        break;
      case 'split':
        await this.handleSplit(event, room);
        break;
      default:
        await this.handleMessage(event, room);
    }
  }
}
```

## Message Reliability

### Critical Operations with Acknowledgments
```javascript
class BaseAgent {
  async sendCriticalMessage(roomId, text, threadId = null) {
    // Mark critical messages with 🔴 prefix
    const criticalText = `🔴 ${text}`;
    
    const content = {
      msgtype: "m.text",
      body: criticalText,
      "agent.critical": {
        requires_ack: true,
        timeout_ms: 30000
      }
    };
    
    if (threadId) {
      content["m.relates_to"] = {
        "rel_type": "m.thread",
        "event_id": threadId
      };
    }
    
    const eventId = await this.client.sendMessage(roomId, content);
    
    // Wait for ✅ reaction acknowledgment
    const ackReceived = await this.waitForAcknowledgment(eventId, 30000);
    
    if (!ackReceived) {
      await this.sendToRoom('#alerts:agents.local', 
        `⚠️ Critical message not acknowledged: ${text.substring(0, 50)}...`
      );
      throw new Error('Critical message not acknowledged');
    }
    
    return eventId;
  }
  
  async waitForAcknowledgment(eventId, timeout) {
    return new Promise((resolve) => {
      const timer = setTimeout(() => resolve(false), timeout);
      
      // Listen for ✅ reaction
      const handler = (event) => {
        if (event.getType() === 'm.reaction' && 
            event.getContent()['m.relates_to']?.event_id === eventId &&
            event.getContent()['m.relates_to']?.key === '✅') {
          clearTimeout(timer);
          this.client.removeListener('Room.timeline', handler);
          resolve(true);
        }
      };
      
      this.client.on('Room.timeline', handler);
    });
  }
  
  // Acknowledge critical messages with ✅ reaction
  async acknowledgeCriticalMessage(event) {
    if (event.getContent().body?.startsWith('🔴')) {
      await this.client.sendEvent(event.getRoomId(), 'm.reaction', {
        'm.relates_to': {
          rel_type: 'm.annotation',
          event_id: event.getId(),
          key: '✅'
        }
      });
    }
  }
}
```

**Key Decision**: Use Matrix reactions for acknowledgments - visual and native.
```

### Sending Messages (Simplified)
```javascript
class BaseAgent {
  async sendMessage(roomId, text, threadId = null) {
    const content = {
      msgtype: "m.text",
      body: text
    };
    
    // Use Matrix threading if responding
    if (threadId) {
      content["m.relates_to"] = {
        "rel_type": "m.thread",
        "event_id": threadId
      };
    }
    
    // Add minimal agent context
    content["agent.cmd"] = {
      file: this.sourceFile,
      lines: this.complexity.current_line_count
    };
    
    await this.client.sendMessage(roomId, content);
  }

  async sendToRoom(roomAlias, text) {
    const room = this.client.getRooms().find(r => 
      r.getAliases().includes(roomAlias)
    );
    
    if (room) {
      await this.sendMessage(room.roomId, text);
    }
  }

  async consultAgent(agentName, question) {
    // Find or create DM room
    const dmRoom = await this.getDirectMessageRoom(agentName);
    await this.sendMessage(dmRoom.roomId, question);
  }

  async getDirectMessageRoom(agentName) {
    const targetUserId = `@${agentName}:agents.local`;
    
    // Check existing DM rooms
    const rooms = this.client.getRooms();
    for (const room of rooms) {
      const members = room.getMembers();
      if (members.length === 2 && 
          members.some(m => m.userId === targetUserId) &&
          members.some(m => m.userId === this.userId)) {
        return room;
      }
    }
    
    // Create new DM room
    return await this.client.createRoom({
      is_direct: true,
      invite: [targetUserId]
    });
  }
}
```

### Expert Consultation (Simplified)
```javascript
class CodeAgent extends BaseAgent {
  async handleConsultation(event, room) {
    const question = event.getContent().body;
    const threadId = event.getId();
    
    // Provide consultation based on our expertise
    const response = await this.generateConsultationResponse(question);
    
    // Send threaded response
    await this.sendMessage(room.roomId, response, threadId);
  }

  async generateConsultationResponse(question) {
    // Simple keyword-based routing
    if (question.includes('interface') || question.includes('api')) {
      return this.getInterfaceGuidance();
    } else if (question.includes('integrate') || question.includes('use')) {
      return this.getIntegrationGuidance();
    } else {
      return this.getGeneralGuidance();
    }
  }

  getInterfaceGuidance() {
    const interfaceSpec = this.blueprint.interface_contracts;
    
    return `
**${this.name} Interface:**

\`\`\`typescript
${this.formatInterface(interfaceSpec)}
\`\`\`

Usage: Import and call methods as shown above.
Note: I cannot modify your files - implement the integration in your component.
    `.trim();
  }
}
```

## Agent Discovery

### Capability Advertisement via Profiles
```javascript
class BaseAgent {
  async updateCapabilities() {
    // Store capabilities in Matrix profile (not display name)
    await this.client.setProfileInfo("capabilities", {
      domains: this.getExpertiseDomains(),     // ["auth", "jwt", "session"]
      interfaces: this.getPublicMethods(),      // ["login", "validateToken"]
      confidence: this.getConfidenceScores(),   // { "auth": 0.9, "jwt": 0.8 }
      api_version: this.blueprint.api_version,  // "1.2.0"
      complexity: {
        lines: this.blueprint.complexity_metrics.current_line_count,
        risk: this.blueprint.complexity_metrics.split_risk_level
      }
    });
    
    // Simple display name shows status
    await this.client.setDisplayName(
      `${this.name} (${this.sourceFile} - ${this.blueprint.complexity_metrics.current_line_count} lines)`
    );
  }
  
  async findExperts(domain) {
    const roomMembers = await this.client.getJoinedRoomMembers('#consultations:agents.local');
    const experts = [];
    
    for (const userId of Object.keys(roomMembers.joined)) {
      if (userId === this.userId) continue;
      
      try {
        const profile = await this.client.getProfileInfo(userId, "capabilities");
        if (profile && profile.domains?.includes(domain)) {
          experts.push({
            userId,
            confidence: profile.confidence[domain] || 0.5,
            version: profile.api_version
          });
        }
      } catch (e) {
        // Agent doesn't have capabilities - skip
      }
    }
    
    return experts.sort((a, b) => b.confidence - a.confidence);
  }
}
```

**Key Decision**: Agent capabilities stored in Matrix profile metadata, not complex registry.

## Monitoring & Observability

### Chat-Based Monitoring
```javascript
class MonitoringBot {
  constructor() {
    this.userId = '@monitor:agents.local';
    this.alertsRoom = '#alerts:agents.local';
  }
  
  async performHealthCheck() {
    const agents = await this.getAllAgents();
    const report = [];
    
    // Check complexity
    for (const agent of agents) {
      const profile = await this.client.getProfileInfo(agent.userId, "capabilities");
      if (profile?.complexity?.lines > 200) {
        report.push(`⚠️ ${agent.name}: ${profile.complexity.lines}/250 lines`);
      }
    }
    
    // Check response times (from recent messages)
    const slowConsultations = await this.findSlowConsultations();
    if (slowConsultations.length > 0) {
      report.push(`🐌 Slow consultations: ${slowConsultations.join(', ')}`);
    }
    
    // Post to alerts room
    if (report.length > 0) {
      await this.sendToRoom(this.alertsRoom, 
        `📊 **Hourly Health Check**\n${report.join('\n')}`
      );
    }
  }
  
  async handleAgentOffline(userId) {
    await this.sendToRoom(this.alertsRoom,
      `🔴 Agent offline: ${userId}`
    );
  }
}
```

**Key Decision**: All monitoring visible in #alerts room - no separate dashboards.

## Developer Experience

### Developer Bot for System Interaction
```javascript
class DeveloperBot {
  constructor() {
    this.userId = '@devbot:agents.local';
    this.commands = {
      '!status': this.showSystemStatus,
      '!ask': this.routeQuestion,
      '!debug': this.debugAgent,
      '!trace': this.traceConversation,
      '!metrics': this.showMetrics
    };
  }
  
  async handleCommand(event, room) {
    const body = event.getContent().body;
    const [command, ...args] = body.split(' ');
    
    if (this.commands[command]) {
      const response = await this.commands[command].call(this, args.join(' '));
      await this.sendMessage(room.roomId, response, event.getId());
    }
  }
  
  async showSystemStatus() {
    const agents = await this.getAllAgents();
    const online = agents.filter(a => a.presence === 'online');
    
    return `
**System Status**
- Total agents: ${agents.length}
- Online: ${online.length}
- Complexity warnings: ${agents.filter(a => a.complexity > 200).length}
- Recent splits: ${await this.getRecentSplits()}

Use \`!debug <agent-name>\` for detailed agent info.
    `.trim();
  }
  
  async debugAgent(agentName) {
    const agent = await this.findAgent(agentName);
    const context = await this.client.getAccountData(`agent.context`, agent.userId);
    
    return `
**Debug: ${agentName}**
- File: \`${context.file}\`
- Lines: ${context.complexity.current_line_count}
- Responsibilities: ${context.responsibilities.length}
- Last updated: ${context.last_updated}
- Blueprint: \`.blueprint-cache/${context.file}.json\`

\`\`\`json
${JSON.stringify(context.complexity, null, 2)}
\`\`\`
    `.trim();
  }
}
```

**Key Decision**: Developer tools as chatbot commands - no separate interfaces.
```

## RAG Implementation (Simplified)

### Natural Language Routing
```javascript
class ConsultationRouter {
  constructor() {
    this.expertiseMap = new Map(); // agent -> domains
  }

  async routeConsultation(question, sender, room) {
    // Simple keyword extraction
    const domains = this.extractDomains(question);
    
    // Find relevant agents
    const experts = this.findExperts(domains);
    
    // Notify experts in consultation room
    for (const expert of experts) {
      await this.notifyExpert(expert, question, sender);
    }
  }

  extractDomains(question) {
    const domainKeywords = {
      auth: ['auth', 'login', 'jwt', 'token', 'session'],
      user: ['user', 'profile', 'account'],
      task: ['task', 'todo', 'assignment'],
      test: ['test', 'spec', 'coverage']
    };
    
    const domains = [];
    for (const [domain, keywords] of Object.entries(domainKeywords)) {
      if (keywords.some(kw => question.toLowerCase().includes(kw))) {
        domains.push(domain);
      }
    }
    
    return domains;
  }

  findExperts(domains) {
    const experts = [];
    
    for (const [agent, agentDomains] of this.expertiseMap) {
      if (domains.some(d => agentDomains.includes(d))) {
        experts.push(agent);
      }
    }
    
    return experts;
  }

  async notifyExpert(expertName, question, sender) {
    const consultRoom = '#consultations:agents.local';
    await this.sendToRoom(consultRoom, 
      `@${expertName} consultation requested by ${sender}: "${question}"`
    );
  }
}
```

## Configuration

### Matrix Room State for Live Configuration
```javascript
class ConfigurationManager {
  constructor() {
    this.configRoom = '#config:agents.local';
  }
  
  async getConfig(key) {
    const stateEvent = await this.client.getStateEvent(
      this.configRoom, 
      `agents.config.${key}`
    );
    return stateEvent?.value;
  }
  
  async setConfig(key, value, reason = '') {
    // Set room state event - no restart needed
    await this.client.sendStateEvent(
      this.configRoom,
      `agents.config.${key}`,
      '',
      {
        value: value,
        updated_by: this.userId,
        updated_at: new Date().toISOString(),
        reason: reason,
        previous_value: await this.getConfig(key)
      }
    );
    
    // Notify agents
    await this.sendToRoom('#general:agents.local',
      `⚙️ Configuration updated: ${key} = ${JSON.stringify(value)} (${reason})`
    );
  }
  
  // Agents watch for config changes
  async watchConfig() {
    this.client.on('RoomState.events', async (event) => {
      if (event.getRoomId() === this.configRoom && 
          event.getType().startsWith('agents.config.')) {
        const key = event.getType().replace('agents.config.', '');
        const value = event.getContent().value;
        await this.handleConfigChange(key, value);
      }
    });
  }
}

// Example configurations as room state
const defaultConfigs = {
  'agents.config.complexity': {
    value: { threshold: 250, warning: 200 }
  },
  'agents.config.timeouts': {
    value: { consultation: 30000, split: 60000 }
  },
  'agents.config.monitoring': {
    value: { interval: 300000, alerts_enabled: true }
  }
};
```

**Key Decision**: Configuration as Matrix room state - versioned, visible, no restarts needed.

## Testing Strategy

### Test Rooms for Agent Testing
```javascript
class AgentTestFramework {
  constructor() {
    this.testHomeserver = 'http://localhost:8008';  // Same server, different rooms
    this.testRoomPrefix = '#test-';
  }
  
  async createTestEnvironment(testName) {
    // Create isolated test rooms
    const rooms = {
      general: await this.createRoom(`${this.testRoomPrefix}${testName}-general`),
      consultations: await this.createRoom(`${this.testRoomPrefix}${testName}-consult`),
      alerts: await this.createRoom(`${this.testRoomPrefix}${testName}-alerts`)
    };
    
    return rooms;
  }
  
  async spawnTestAgent(agentName, blueprint, testRooms) {
    // Create test agent with 'test-' prefix
    const testAgent = new CodeAgent(`test-${agentName}`, blueprint.source_file);
    
    // Override room subscriptions
    testAgent.getRequiredRooms = () => Object.values(testRooms);
    
    await testAgent.initialize();
    return testAgent;
  }
  
  async testConsultation(testName) {
    const rooms = await this.createTestEnvironment(testName);
    
    // Spawn test agents
    const authAgent = await this.spawnTestAgent('auth-service', authBlueprint, rooms);
    const taskAgent = await this.spawnTestAgent('task-service', taskBlueprint, rooms);
    
    // Send consultation
    await taskAgent.sendMessage(rooms.consultations.roomId,
      '@test-auth-service How do I validate a JWT token?'
    );
    
    // Wait for response
    const response = await this.waitForMessage(rooms.consultations.roomId, 
      (msg) => msg.sender === '@test-auth-service:agents.local'
    );
    
    // Assert response quality
    expect(response.body).toContain('validateToken');
    expect(response.body).toContain('interface');
    
    // Cleanup
    await this.cleanupTestRooms(rooms);
  }
}
```

**Key Decision**: Test with real Matrix rooms and real agents - no mocking complexity.

## Benefits of Simplified Approach

1. **Faster Implementation** - Basic Matrix features work immediately
2. **Lower Resource Usage** - Minimal message payloads and simple routing
3. **Easier Debugging** - Simpler message formats and clear room structure
4. **Natural Growth Path** - Add features as needed, not upfront
5. **Human Friendly** - Messages readable without parsing complex JSON
6. **Performance Focus** - Monitor from day one with simple metrics
7. **Native Security** - Matrix Application Service handles agent authentication
8. **Single Source of Truth** - Matrix account data eliminates sync issues
9. **Visual Acknowledgments** - Critical operations confirmed with ✅ reactions
10. **Chat-Based Everything** - Monitoring, config, and debugging all in chat

## Key Architectural Decisions

### Based on Production Concerns

1. **Authentication**: Matrix Application Service
   - Only ArchitectAgent can spawn agents
   - No manual registration possible
   - All agents traceable to spawn request

2. **Data Storage**: Matrix Account Data
   - Single source of truth (no sync conflicts)
   - Filesystem is cache only
   - Blueprint updates atomic

3. **Reliability**: Native Matrix Features
   - Critical messages marked with 🔴
   - Acknowledgments via ✅ reactions
   - Message threading for conversation tracking

4. **Discovery**: Matrix User Profiles
   - Capabilities in profile metadata
   - No separate service registry
   - Natural load balancing via confidence scores

5. **Monitoring**: Chat-Based Observability
   - All metrics posted to #alerts room
   - No external monitoring systems
   - DevBot for debugging (`!status`, `!debug`)

6. **Configuration**: Room State Events
   - Live config updates without restarts
   - Version history preserved
   - Visible in Matrix clients

7. **Testing**: Real Agents in Test Rooms
   - Use `#test-*` room prefix
   - Test actual agent interactions
   - No mocking complexity

## Migration Path

### Phase 1: Basic Communication (Week 1)
- Agent registration and room joining
- Text message exchange with @mentions
- Simple command parsing
- Blueprint storage in account data

### Phase 2: Enhanced Features (Week 2-3)
- Matrix threading for conversations
- Consultation routing by keyword
- System alerts for complexity
- Basic presence updates

### Phase 3: Advanced Features (Month 2+)
- Custom event types if needed
- Rich formatting for code blocks
- File attachments for large responses
- Performance optimization based on metrics

## Key Differences from Original

1. **No avatars or rich profiles** - Just functional names and capability metadata
2. **Account data for blueprints** - Not in every message (single source of truth)
3. **Native Matrix threading** - Instead of custom thread tracking
4. **Simple text parsing** - Instead of complex event types
5. **Keyword-based routing** - Instead of complex RAG analysis
6. **Minimal metadata** - Just file and line count in messages
7. **Application Service security** - No manual agent registration
8. **Matrix reactions for acks** - Visual confirmation of critical operations
9. **Room state for config** - Live updates without restarts
10. **Profile-based discovery** - No separate agent registry
11. **Chat-based monitoring** - All observability in #alerts room
12. **DevBot for debugging** - Developers use familiar chat interface

This simplified approach maintains all essential functionality while being much easier to implement, debug, and scale.
