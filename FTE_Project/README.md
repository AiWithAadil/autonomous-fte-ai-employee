# FTE Agent - Personal AI Employee

A clean, agent-based Personal AI Employee system that satisfies Hackathon 0 Bronze and Silver requirements.

## 🎯 What is FTE Agent?

FTE Agent is a Personal AI Employee that helps you manage incoming messages through two layers:

- **Bronze Layer (Observation)**: Watches for new messages and stores them
- **Silver Layer (Agent Analysis)**: Uses AI to analyze messages, suggest replies, extract tasks, and recommend actions with human approval

## 🏗️ Architecture

```
fte_agent/
├── main.py                    # ONE COMMAND entry point
├── .env                       # OpenRouter API key (create from .env.example)
├── requirements.txt           # Dependencies
│
├── agent/                     # Agent Brain (OpenRouter-powered)
│   ├── brain.py              # Agent with reasoning loop
│   ├── tools.py              # Skills registered as tools
│   └── prompts.py            # System prompts
│
├── skills/                    # Analysis Skills
│   ├── summarizer.py         # Content summarization
│   ├── reply_suggester.py    # Reply suggestions
│   ├── task_extractor.py     # Task extraction
│   ├── priority_detector.py  # Priority detection
│   └── categorizer.py        # Message categorization
│
├── config/                    # Configuration
│   └── settings.py           # Centralized settings
│
└── vault/                     # Data Storage
    ├── inbox/                # Incoming messages
    ├── processed/            # Processed messages
    ├── actions/              # Action outputs (drafts, tasks)
    └── logs/                 # Audit logs
```

## 🧠 How the Agent Works

### Agent Brain (OpenRouter-Powered)

The agent uses OpenRouter API with tool calling:

1. **Receives message** → Agent reads and understands intent
2. **Decides which tools to use** → Selects relevant skills
3. **Calls tools** → Executes summarizer, reply_suggester, task_extractor, etc.
4. **Synthesizes results** → Combines tool outputs into clean analysis
5. **Returns structured output** → One clean result with all insights

### Skills as Tools

Each skill is registered as a tool the agent can invoke:
- `summarizer` → Summarize content
- `reply_suggester` → Suggest replies
- `task_extractor` → Extract tasks
- `priority_detector` → Detect priority (HIGH/MEDIUM/LOW)
- `categorizer` → Categorize message (work/personal/study/finance/other)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get OpenRouter API Key

1. Visit https://openrouter.ai/keys
2. Sign up and get a free API key
3. Copy `.env.example` to `.env`
4. Add your API key to `.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Run the System

**ONE COMMAND to run everything:**

```bash
python main.py
```

This starts interactive mode where you can:
- Enter messages to analyze
- Type `watch` to start folder watcher
- Type `quit` to exit

## 📋 Usage Modes

### Interactive Mode (Default)

```bash
python main.py
```

Enter messages directly and get instant analysis with approval flow.

### Folder Watcher Mode

```bash
python main.py --watch
```

Watches `vault/inbox/` for new `.txt` files and processes them automatically.

### WhatsApp Watcher Mode ⭐

```bash
python main.py --whatsapp
```

Opens WhatsApp Web in browser. Scan QR code to login. New WhatsApp messages are automatically:
1. Saved to `vault/inbox/`
2. Analyzed by agent
3. Shown with approval prompts

### Demo Mode

```bash
python main.py --demo
```

Runs a demo with a sample message to show how the system works.

## 🔄 Complete Workflow

### Bronze Layer (Observation)

1. **Message arrives** →
   - Place `.txt` file in `vault/inbox/`, OR
   - WhatsApp message arrives (if using `--whatsapp` mode)
2. **System detects** → Watcher picks up new file
3. **Message stored** → Saved for processing

### Silver Layer (Agent Analysis + Approval)

1. **Agent analyzes** → Uses OpenRouter to understand message
2. **Tools called** → Summarizer, priority detector, reply suggester, etc.
3. **Results displayed** → Clean output with:
   - Summary
   - Priority level
   - Category
   - Suggested reply
   - Extracted tasks
   - Recommended actions

4. **Human approval** → System asks:
   ```
   [ACTION 1] Send suggested reply
     Reply: "Yes, I'm available at 2pm..."

     Approve this action? [Y/n]:
   ```

5. **Execution** → If approved:
   - Reply drafts saved to `vault/actions/`
   - Tasks created in `vault/actions/`
   - Everything logged to `vault/logs/`

6. **Completion** → Message moved to `vault/processed/`

## 📊 Example Output

```
==============================================================
  AGENT ANALYSIS
==============================================================

[FROM] Sarah
[PRIORITY] HIGH
[CATEGORY] WORK

[SUMMARY]
Need help with quarterly budget report. Review spreadsheet
and provide feedback by tomorrow 2 PM. Board meeting Friday.

[SUGGESTED REPLY]
Hi Sarah, I'll review the budget report today and send you
my feedback by tomorrow 1 PM. I'll also coordinate with the
finance team for the follow-up meeting.

[EXTRACTED TASKS]
  1. Review quarterly budget spreadsheet
  2. Send feedback by tomorrow 2 PM
  3. Schedule meeting with finance team for Q3 projections

[AGENT NOTES]
This is a high-priority work message requiring urgent action
before the board meeting. Two main deliverables: budget review
and team meeting coordination.

==============================================================

--------------------------------------------------------------
  APPROVAL REQUIRED
--------------------------------------------------------------

[ACTION 1] Send suggested reply
  Reply: Hi Sarah, I'll review the budget report today...

  Approve this action? [Y/n]: y
  -> APPROVED

[ACTION 2] Create task: Review quarterly budget spreadsheet
  Task: Review quarterly budget spreadsheet

  Approve this action? [Y/n]: y
  -> APPROVED

--------------------------------------------------------------
  EXECUTING ACTIONS
--------------------------------------------------------------

SUCCESS: Send suggested reply
  -> Draft saved: vault/actions/reply_draft_20260215_143022.txt
SUCCESS: Create task: Review quarterly budget spreadsheet
  -> Task created: vault/actions/task_20260215_143022.txt
```

## ✅ Hackathon 0 Requirements

### Bronze Level ✓

- [x] **Observation Only**: Watches for messages, stores them
- [x] **No Auto Action**: Only observes and saves
- [x] **Message Storage**: All messages saved to vault

### Silver Level ✓

- [x] **Agent Thinking**: OpenRouter-powered agent with reasoning loop
- [x] **Tool Calling**: Skills registered as tools agent can invoke
- [x] **Structured Output**: Clean, actionable insights
- [x] **Human Approval**: Interactive approval before any action
- [x] **Action Execution**: Only executes after approval
- [x] **Audit Logging**: Complete audit trail

### Agent Architecture ✓

- [x] **Agent Brain**: OpenRouter integration with tool calling
- [x] **Skills System**: 5 skills (summarizer, reply_suggester, task_extractor, priority_detector, categorizer)
- [x] **Clean Structure**: Proper agent/ skills/ config/ vault/ organization
- [x] **One Command**: `python main.py` runs everything
- [x] **Demo Ready**: Simple, minimal, professional

## 🔧 Configuration

### Environment Variables (.env)

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free

# Application Settings
APP_NAME=FTE_Agent
LOG_LEVEL=INFO

# Vault Paths
VAULT_INBOX=vault/inbox
VAULT_PROCESSED=vault/processed
VAULT_ACTIONS=vault/actions
VAULT_LOGS=vault/logs
```

### Free OpenRouter Models

- `meta-llama/llama-3.1-8b-instruct:free` (recommended)
- `google/gemma-2-9b-it:free`
- `mistralai/mistral-7b-instruct:free`

## 📁 Vault Structure

```
vault/
├── inbox/              # Place new messages here (.txt files)
├── processed/          # Processed messages moved here
├── actions/            # Action outputs
│   ├── reply_draft_*.txt    # Reply drafts
│   └── task_*.txt           # Created tasks
└── logs/               # Audit logs
    └── execution_*.json     # Execution logs
```

## 🎬 Demo Instructions

### Quick Demo

```bash
python main.py --demo
```

This runs a sample message through the complete workflow.

### Manual Test

1. Create a test message:
   ```bash
   echo "Hi, can you help me with the project report? Need it by tomorrow. Thanks!" > vault/inbox/test_message.txt
   ```

2. Run watcher:
   ```bash
   python main.py --watch
   ```

3. Watch the agent analyze, suggest actions, and ask for approval

## 🛠️ Troubleshooting

### "OPENROUTER_API_KEY not found"

- Copy `.env.example` to `.env`
- Add your API key from https://openrouter.ai/keys

### "Module not found" errors

```bash
pip install -r requirements.txt
```

### Agent not calling tools

- Check API key is valid
- Try a different model in `.env`
- Check OpenRouter dashboard for quota

## 🎯 Key Features

- **One Command**: `python main.py` runs everything
- **Clean Output**: One structured result per message
- **Human Control**: Approval required for all actions
- **Audit Trail**: Complete logging of all operations
- **Local First**: All data stored locally in vault/
- **Agent-Driven**: OpenRouter agent with reasoning loop
- **Tool Calling**: Skills as tools for flexible analysis
- **Demo Ready**: Simple, minimal, professional

## 📝 Notes

- All actions create drafts/files, nothing is sent automatically
- Reply drafts saved to `vault/actions/` for manual review
- Tasks saved to `vault/actions/` for manual execution
- Complete audit trail in `vault/logs/`
- Bronze mode preserved (observation only)
- Silver mode adds agent analysis with approval

## 🚀 Next Steps

After testing the system:
1. Add more action types (calendar events, file operations, etc.)
2. Integrate with real email/messaging APIs
3. Add web interface for approval workflow
4. Implement Gold level (autonomous execution with constraints)

---

**Built for Hackathon 0 - Personal AI Employee (FTE)**

Clean, minimal, agent-based architecture with OpenRouter integration.
