"""
FTE Agent - Personal AI Employee
Main entry point for the agent system

Usage:
    python main.py              # Start interactive mode
    python main.py --watch      # Start with folder watcher
    python main.py --whatsapp   # Start with WhatsApp watcher
    python main.py --demo       # Run demo with sample message
"""
import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import FTEAgent
from config import (
    VAULT_INBOX,
    VAULT_PROCESSED,
    VAULT_ACTIONS,
    VAULT_LOGS,
    validate_config
)

# Import WhatsApp watcher
try:
    from watchers.whatsapp_watcher import whatsapp_watcher
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False


class FTEOrchestrator:
    """
    Main orchestrator for FTE Agent
    Manages Bronze (observation) and Silver (agent analysis + approval) workflows
    """

    def __init__(self):
        """Initialize the orchestrator"""
        try:
            validate_config()
            self.agent = FTEAgent()
            self.running = True
            print("SUCCESS: FTE Agent initialized")
        except ValueError as e:
            print(f"ERROR: Configuration error - {e}")
            print("\nPlease follow these steps:")
            print("1. Copy .env.example to .env")
            print("2. Add your OpenRouter API key to .env")
            print("3. Get a free API key at: https://openrouter.ai/keys")
            sys.exit(1)

    def display_banner(self):
        """Display welcome banner"""
        print("\n" + "=" * 60)
        print("  FTE AGENT - Personal AI Employee")
        print("  Bronze: Observation | Silver: Agent Analysis + Approval")
        print("=" * 60 + "\n")

    def analyze_with_skills(self, message: str, sender: str = "Unknown"):
        """
        Analyze message using skills directly (no agent brain needed)

        Args:
            message: Message content
            sender: Sender name

        Returns:
            Analysis result dict
        """
        from skills.summarizer import summarize_content
        from skills.priority_detector import detect_priority
        from skills.categorizer import categorize_content
        from skills.reply_suggester import suggest_reply
        from skills.task_extractor import extract_tasks

        # Call all skills
        summary_result = summarize_content(message, return_structured=True)
        priority_result = detect_priority(message, return_structured=True)
        category_result = categorize_content(message, return_structured=True)
        reply_result = suggest_reply(message, sender, return_structured=True)
        tasks_result = extract_tasks(message, return_structured=True)

        # Build result
        result = {
            'sender': sender,
            'message': message,
            'summary': summary_result.get('summary', ''),
            'priority': priority_result.get('priority', 'MEDIUM'),
            'category': category_result.get('category', 'other'),
            'suggested_reply': reply_result.get('suggestions', [None])[0] if reply_result.get('suggestions') else None,
            'tasks': tasks_result.get('tasks', []),
            'actions': []
        }

        # Determine actions
        if result['suggested_reply']:
            result['actions'].append({
                'type': 'send_reply',
                'description': 'Send suggested reply',
                'data': {'reply': result['suggested_reply'], 'recipient': sender}
            })

        for task in result['tasks']:
            task_title = task if isinstance(task, str) else task.get('title', str(task))
            result['actions'].append({
                'type': 'create_task',
                'description': f'Create task: {task_title}',
                'data': {'task': task_title, 'priority': result['priority']}
            })

        return result
        """Display welcome banner"""
        print("\n" + "=" * 60)
        print("  FTE AGENT - Personal AI Employee")
        print("  Bronze: Observation | Silver: Agent Analysis + Approval")
        print("=" * 60 + "\n")

    def watch_folder(self):
        """
        Bronze Layer: Watch input folder for new messages
        """
        print(f"[BRONZE] Watching {VAULT_INBOX} for new messages...")
        print("Place .txt files in vault/inbox/ to process them")
        print("Press Ctrl+C to stop\n")

        processed_files = set()

        try:
            while self.running:
                # Check for new files
                inbox_files = list(VAULT_INBOX.glob("*.txt")) + list(VAULT_INBOX.glob("*.md"))

                for file_path in inbox_files:
                    if file_path not in processed_files:
                        print(f"\n[BRONZE] New message detected: {file_path.name}")
                        self.process_message_file(file_path)
                        processed_files.add(file_path)

                time.sleep(2)  # Check every 2 seconds

        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Stopping watcher...")
            self.running = False

    def watch_whatsapp(self):
        """
        Start WhatsApp watcher + folder processor
        WhatsApp watcher saves messages to vault/inbox/
        Folder watcher processes them with agent
        """
        if not WHATSAPP_AVAILABLE:
            print("ERROR: WhatsApp watcher not available")
            print("Make sure playwright is installed: pip install playwright")
            print("Then run: playwright install chromium")
            return

        print("[WHATSAPP] Starting WhatsApp watcher...")
        print("[BRONZE] Starting message processor...")
        print("\nWhatsApp will open in browser. Scan QR code to login.")
        print("New messages will be analyzed automatically.\n")

        # Start WhatsApp watcher in background thread
        whatsapp_thread = threading.Thread(target=whatsapp_watcher, daemon=True)
        whatsapp_thread.start()

        # Give WhatsApp time to start
        time.sleep(3)

        # Start folder watcher to process messages
        self.watch_folder()

    def process_message_file(self, file_path: Path):
        """
        Process a message file through Bronze → Silver workflow

        Args:
            file_path: Path to message file
        """
        try:
            # Read message
            with open(file_path, 'r', encoding='utf-8') as f:
                message = f.read()

            # Extract sender from filename or content
            sender = self.extract_sender(file_path.name, message)

            # Silver Layer: Direct skill analysis (no agent brain needed)
            print(f"[SILVER] Analyzing message...")

            # Use skills directly
            result = self.analyze_with_skills(message, sender)

            # Display results
            self.display_analysis(result)

            # Approval flow
            if result.get("actions"):
                approved_actions = self.approval_flow(result)

                if approved_actions:
                    self.execute_actions(approved_actions, result)

            # Move to processed
            processed_path = VAULT_PROCESSED / file_path.name
            file_path.rename(processed_path)
            print(f"\n[BRONZE] Message moved to processed: {processed_path.name}")

        except Exception as e:
            print(f"ERROR: Failed to process message - {e}")
            import traceback
            traceback.print_exc()

    def extract_sender(self, filename: str, content: str) -> str:
        """Extract sender from filename or content"""
        # Try to extract from filename (e.g., "message_from_john.txt")
        if "_from_" in filename:
            sender = filename.split("_from_")[1].replace(".txt", "").replace("_", " ").title()
            return sender

        # Try to extract from content (look for "From:" line)
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.lower().startswith("from:"):
                return line.split(":", 1)[1].strip()

        return "Unknown"

    def display_analysis(self, result: dict):
        """
        Display agent analysis in clean format

        Args:
            result: Analysis result from agent
        """
        print("\n" + "=" * 60)
        print("  AGENT ANALYSIS")
        print("=" * 60)

        # Handle errors
        if "error" in result:
            print(f"\nERROR: {result['error']}")
            return

        # Display key information
        print(f"\n[FROM] {result.get('sender', 'Unknown')}")
        print(f"[PRIORITY] {result.get('priority', 'MEDIUM')}")
        print(f"[CATEGORY] {result.get('category', 'other').upper()}")

        # Summary
        if result.get('summary'):
            print(f"\n[SUMMARY]")
            print(f"{result['summary']}")

        # Suggested reply
        if result.get('suggested_reply'):
            print(f"\n[SUGGESTED REPLY]")
            print(f"{result['suggested_reply']}")

        # Tasks
        if result.get('tasks'):
            print(f"\n[EXTRACTED TASKS]")
            for i, task in enumerate(result['tasks'], 1):
                print(f"  {i}. {task}")

        # Agent synthesis
        if result.get('analysis'):
            print(f"\n[AGENT NOTES]")
            print(f"{result['analysis']}")

        print("\n" + "=" * 60)

    def approval_flow(self, result: dict) -> list:
        """
        Interactive approval flow for suggested actions

        Args:
            result: Analysis result with actions

        Returns:
            List of approved actions
        """
        actions = result.get('actions', [])
        if not actions:
            return []

        print("\n" + "-" * 60)
        print("  APPROVAL REQUIRED")
        print("-" * 60)

        approved = []

        for i, action in enumerate(actions, 1):
            print(f"\n[ACTION {i}] {action['description']}")

            # Show action details
            if action['type'] == 'send_reply':
                print(f"  Reply: {action['data']['reply'][:100]}...")
            elif action['type'] == 'create_task':
                print(f"  Task: {action['data']['task']}")

            # Ask for approval
            response = input(f"\n  Approve this action? [Y/n]: ").strip().lower()

            if response in ['y', 'yes', '']:
                approved.append(action)
                print("  -> APPROVED")
            else:
                print("  -> REJECTED")

        return approved

    def execute_actions(self, actions: list, result: dict):
        """
        Execute approved actions

        Args:
            actions: List of approved actions
            result: Original analysis result
        """
        print("\n" + "-" * 60)
        print("  EXECUTING ACTIONS")
        print("-" * 60)

        for action in actions:
            try:
                if action['type'] == 'send_reply':
                    self.execute_send_reply(action, result)
                elif action['type'] == 'create_task':
                    self.execute_create_task(action, result)

                print(f"SUCCESS: {action['description']}")

            except Exception as e:
                print(f"ERROR: Failed to execute {action['description']} - {e}")

        # Log execution
        self.log_execution(actions, result)

    def execute_send_reply(self, action: dict, result: dict):
        """Execute send reply action (creates draft)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reply_draft_{timestamp}.txt"
        output_path = VAULT_ACTIONS / filename

        content = f"""Reply Draft
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
To: {action['data']['recipient']}
Priority: {result.get('priority', 'MEDIUM')}

---

{action['data']['reply']}

---

Note: This is a draft. Review and send manually.
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  -> Draft saved: {output_path}")

    def execute_create_task(self, action: dict, result: dict):
        """Execute create task action"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_{timestamp}.txt"
        output_path = VAULT_ACTIONS / filename

        content = f"""Task
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Priority: {action['data']['priority']}

---

{action['data']['task']}

---

Source: {result.get('sender', 'Unknown')}
Category: {result.get('category', 'other')}
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  -> Task created: {output_path}")

    def log_execution(self, actions: list, result: dict):
        """Log action execution to audit log"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = VAULT_LOGS / f"execution_{timestamp}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": result.get('sender'),
            "priority": result.get('priority'),
            "category": result.get('category'),
            "actions_executed": len(actions),
            "actions": [
                {
                    "type": action['type'],
                    "description": action['description']
                }
                for action in actions
            ]
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2)

    def run_demo(self):
        """Run demo with sample message"""
        self.display_banner()
        print("[DEMO MODE] Running with sample message\n")

        sample_message = """Hi,

I need your help with the quarterly budget report. Can you please review the attached spreadsheet and send me your feedback by tomorrow 2 PM? This is urgent as we have a board meeting on Friday.

Also, please schedule a follow-up meeting with the finance team to discuss the Q3 projections.

Thanks,
Sarah (Finance Director)
"""

        print("[BRONZE] Sample message received")
        print("[SILVER] Analyzing...\n")

        result = self.analyze_with_skills(sample_message, "Sarah")
        self.display_analysis(result)

        if result.get("actions"):
            print("\n[DEMO] In real mode, you would approve/reject actions here")
            print(f"[DEMO] Found {len(result['actions'])} suggested actions")

    def run_interactive(self):
        """Run in interactive mode"""
        self.display_banner()
        print("Interactive Mode - Enter messages to analyze")
        print("Commands: 'watch' to start folder watcher, 'whatsapp' for WhatsApp, 'quit' to exit\n")

        while self.running:
            try:
                user_input = input("\nEnter message (or command): ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'watch':
                    self.watch_folder()
                    continue
                elif user_input.lower() == 'whatsapp':
                    self.watch_whatsapp()
                    continue

                # Analyze message
                print("\n[SILVER] Analyzing...")
                result = self.analyze_with_skills(user_input)
                self.display_analysis(result)

                # Approval flow
                if result.get("actions"):
                    approved_actions = self.approval_flow(result)
                    if approved_actions:
                        self.execute_actions(approved_actions, result)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="FTE Agent - Personal AI Employee")
    parser.add_argument('--watch', action='store_true', help='Start folder watcher')
    parser.add_argument('--whatsapp', action='store_true', help='Start WhatsApp watcher')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')

    args = parser.parse_args()

    orchestrator = FTEOrchestrator()

    if args.demo:
        orchestrator.run_demo()
    elif args.whatsapp:
        orchestrator.display_banner()
        orchestrator.watch_whatsapp()
    elif args.watch:
        orchestrator.display_banner()
        orchestrator.watch_folder()
    else:
        orchestrator.run_interactive()


if __name__ == "__main__":
    main()
