import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import json

def whatsapp_watcher():
    """
    WhatsApp Web watcher that monitors for new messages and creates Markdown files
    in vault/Needs_Action/ with source, sender, timestamp, and raw message content.
    """
    # Use absolute paths based on the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level to project root

    input_dir = os.path.join(project_root, "input")  # Keep input dir for compatibility
    output_dir = os.path.join(project_root, "vault", "inbox")  # Updated to new structure
    profile_dir = os.path.join(project_root, "playwright_profile")

    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(profile_dir, exist_ok=True)

    print("Starting WhatsApp Web watcher...")
    print("Attempting to use persistent context...")

    with sync_playwright() as p:
        # Create browser context once and keep it open
        try:
            context = p.chromium.launch_persistent_context(
                profile_dir,
                headless=False,
                viewport={'width': 1280, 'height': 800},
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--allow-running-insecure-content',
                    '--disable-extensions-http-throttling',
                    '--disable-ipc-flooding-protection',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            page = context.new_page()
            print("Using persistent context (login will be saved)")
        except Exception as e:
            print(f"Failed to use persistent context: {str(e)}")
            print("Using regular browser context instead...")
            # Fall back to regular browser
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--allow-running-insecure-content',
                    '--disable-extensions-http-throttling',
                    '--disable-ipc-flooding-protection',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            page = context.new_page()

        # Navigate to WhatsApp Web
        page.goto('https://web.whatsapp.com/')

        # Wait for user to manually log in via QR code
        print("Please scan the QR code to log in manually...")
        print("Look for the QR code on the browser window that just opened.")

        # Wait for WhatsApp main UI to load - use a variety of selectors
        print("Waiting for WhatsApp UI to load...")

        # Try multiple selectors to detect when WhatsApp is ready
        selectors_to_try = [
            'div[data-testid="chat-list"]',
            'div[role="grid"]',
            '[data-testid="default-user"]',
            'span[title="New chat"]',
            'div[aria-label="Chat list"]',
            'div[tabindex="-1"][role="button"]'
        ]

        ui_loaded = False
        for selector in selectors_to_try:
            try:
                page.wait_for_selector(selector, timeout=120000)  # Wait up to 120 seconds
                print("WhatsApp UI loaded successfully!")
                ui_loaded = True
                break
            except:
                continue

        if not ui_loaded:
            print("Could not detect WhatsApp UI after waiting. Please make sure you're logged in.")
            context.close()
            return

        print("Login detected. Starting message monitoring...")

        # Track processed messages to prevent duplicates (file-based)
        processed_messages_file = os.path.join(profile_dir, "processed_messages.json")

        # Load previously processed messages
        if os.path.exists(processed_messages_file):
            with open(processed_messages_file, 'r') as f:
                processed_messages = set(json.load(f))
        else:
            processed_messages = set()

        print("Monitoring WhatsApp for new messages...")
        print("Browser stays open and continuously monitors for new messages...")
        print("Press Ctrl+C to stop the watcher.")

        try:
            while True:
                # Every 5 seconds scan chat list for unread messages
                time.sleep(5)

                # Silently scan for unread messages (no print to avoid messy terminal)

                # Try to find all chat items using various selectors
                chat_selectors = [
                    'div[tabindex="-1"][role="button"]',  # Most common chat item selector
                    'div[role="row"]',  # Alternative chat row selector
                    '[data-testid="chat-list-item"]',  # Chat list item
                    'div[tabindex="-1"]'  # General chat container
                ]

                chat_elements = []
                for selector in chat_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            chat_elements = elements
                            break
                    except:
                        continue

                if not chat_elements:
                    # Silently skip if no chat elements found
                    continue

                # Silently check chat elements (removed print to keep terminal clean)

                for i, chat_element in enumerate(chat_elements):
                    try:
                        # Check if this chat has an unread indicator
                        # Look for various possible unread indicators
                        unread_indicators = [
                            '[data-testid="icon-unread"]',  # Unread icon
                            '[data-icon="chat-unread"]',  # Alternative unread icon
                            '[class*="unread"]',  # Classes containing 'unread'
                            '[aria-label*="unread"]',  # ARIA labels with unread
                            'span[style*="background"]'  # Sometimes unread badges have background color
                        ]

                        has_unread = False
                        for indicator_selector in unread_indicators:
                            try:
                                if chat_element.query_selector(indicator_selector):
                                    has_unread = True
                                    break
                            except:
                                continue

                        if has_unread:
                            # Get sender name using multiple selectors
                            sender = None
                            name_selectors = [
                                '[title]',  # Title attribute
                                'span[title]',  # Span with title
                                'div[title]',  # Div with title
                                'span[dir="auto"]',  # Auto-direction span
                                'div:nth-child(2) span:first-child',  # First span in second child div
                                'div span:first-child'  # First span in the chat element
                            ]

                            for selector in name_selectors:
                                try:
                                    name_element = chat_element.query_selector(selector)
                                    if name_element:
                                        name_text = name_element.inner_text().strip()
                                        if name_text and len(name_text) > 0:
                                            sender = name_text
                                            break
                                except:
                                    continue

                            if sender:
                                # Silently process unread message (removed print to keep terminal clean)

                                # Click on the chat to open it
                                try:
                                    chat_element.click()
                                    page.wait_for_timeout(2000)  # Wait for chat to load

                                    # Get the most recent incoming message
                                    # Look for messages that are not from the user (message-out)
                                    message_selectors = [
                                        'div.message-in span.selectable-text',  # Incoming messages
                                        'div.copyable-text span',  # Copyable message text
                                        'span[dir="ltr"]',  # Left-to-right text (incoming)
                                        'div[data-pre-plain-text] span',  # Messages with sender info
                                        'div[tabindex="-1"] span',  # General message spans
                                        '.copyable-text'  # Copyable text elements
                                    ]

                                    message_text = ""
                                    for msg_selector in message_selectors:
                                        try:
                                            message_elements = page.query_selector_all(msg_selector)
                                            if message_elements:
                                                # Get the last (most recent) message
                                                last_message_element = message_elements[-1]
                                                message_text = last_message_element.inner_text().strip()
                                                if message_text and len(message_text) > 0:
                                                    break
                                        except:
                                            continue

                                    if message_text:
                                        # Create a unique identifier for this message
                                        message_id = f"{sender}_{message_text[:30]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                                        # Check if this message was already processed
                                        if message_id not in processed_messages:
                                            processed_messages.add(message_id)

                                            # Save processed messages to file
                                            with open(processed_messages_file, 'w') as f:
                                                json.dump(list(processed_messages), f)

                                            # Create a detailed timestamp
                                            detailed_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                            # Create markdown file
                                            output_filename = f"whatsapp_{sender.replace(' ', '_').replace('/', '_').replace(':', '_').replace('|', '_').replace('\\', '_')}_{int(time.time())}.md"
                                            output_path = os.path.join(output_dir, output_filename)

                                            with open(output_path, 'w', encoding='utf-8') as f:
                                                f.write(f"# WhatsApp Message\n\n")
                                                f.write(f"**Source**: WhatsApp\n\n")
                                                f.write(f"**Sender**: {sender}\n\n")
                                                f.write(f"**Timestamp**: {detailed_timestamp}\n\n")
                                                f.write("**Message**:\n")
                                                f.write("```\n")
                                                f.write(message_text)
                                                f.write("\n```\n")

                                            # Silently saved (removed print to keep terminal clean)
                                        else:
                                            # Silently skip already processed messages
                                            pass

                                    # Go back to chat list
                                    page.wait_for_timeout(1000)
                                    # Stay on the main page to continue monitoring
                                    # We don't need to navigate back since we'll scan the chat list again

                                except Exception as e:
                                    # Silently handle errors to keep terminal clean
                                    pass
                            else:
                                # Silently skip chats without sender name
                                pass

                    except Exception as e:
                        # Skip problematic chats silently
                        continue

                # Silently wait before next scan (removed print to keep terminal clean)

        except KeyboardInterrupt:
            print("\nStopping WhatsApp watcher...")

        finally:
            # Save processed messages before exiting
            with open(processed_messages_file, 'w') as f:
                json.dump(list(processed_messages), f)
            context.close()
            print("WhatsApp watcher stopped.")

if __name__ == "__main__":
    whatsapp_watcher()