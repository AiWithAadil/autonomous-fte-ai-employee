"""
Reply Suggester Skill for Bronze-level Personal AI Employee
Generates suggested replies based on content
"""

def suggest_reply(content, sender=None, return_structured=False):
    """
    Generate suggested replies based on content

    Args:
        content (str): The content to generate reply suggestions for
        sender (str, optional): The sender of the original message
        return_structured (bool, optional): If True, return structured data for Silver mode.
                                           If False (default), return markdown for Bronze mode.

    Returns:
        str or dict: Markdown-formatted reply suggestions (Bronze mode) or
                    structured dict with suggestions (Silver mode)
    """
    content_lower = content.lower()

    # Determine message type based on keywords
    message_type = "general"

    # Check for greetings first
    if any(keyword in content_lower for keyword in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
        message_type = "greeting"
    # Check for requests (before problems, as "can you help" should be request not problem)
    elif any(keyword in content_lower for keyword in ["can you", "could you", "please", "need you to", "would you", "request"]):
        message_type = "request"
    # Check for problems/issues
    elif any(keyword in content_lower for keyword in ["issue", "problem", "error", "bug", "broken", "not working", "fix"]):
        message_type = "problem"
    elif any(keyword in content_lower for keyword in ["urgent", "asap", "immediately", "now"]):
        message_type = "urgent"
    elif any(keyword in content_lower for keyword in ["question", "ask", "wonder", "?"]):
        message_type = "question"
    elif any(keyword in content_lower for keyword in ["meeting", "appointment", "schedule", "when", "time"]):
        message_type = "meeting"
    elif any(keyword in content_lower for keyword in ["thank", "thanks", "appreciate"]):
        message_type = "appreciation"
    elif any(keyword in content_lower for keyword in ["congrat", "well done", "great job"]):
        message_type = "compliment"

    # Generate reply suggestions based on message type
    suggestions = []

    if message_type == "greeting":
        suggestions.extend([
            "Hello! How can I help you today?",
            "Hi! Thanks for reaching out. What can I assist you with?",
            "Hey! Good to hear from you. What do you need?"
        ])
    elif message_type == "problem":
        suggestions.extend([
            "I understand you're experiencing an issue. Let me look into this and help you resolve it.",
            "Thanks for reporting this problem. I'll investigate and get back to you with a solution.",
            "I see there's an issue. Can you provide more details so I can help fix it?"
        ])
    elif message_type == "request":
        suggestions.extend([
            "I'd be happy to help with that. Let me take care of it for you.",
            "Sure, I can assist with this request. I'll get started right away.",
            "Absolutely, I'll handle this for you. Give me a moment to process it."
        ])
    elif message_type == "urgent":
        suggestions.extend([
            "I acknowledge receipt of your urgent message. I will prioritize addressing this and get back to you shortly.",
            "Understood. I'm looking into this matter right away and will provide an update within the next hour.",
            "I've received your urgent request and am treating it with the highest priority."
        ])
    elif message_type == "question":
        suggestions.extend([
            "Thank you for your question. Let me look into this and get back to you with a detailed response.",
            "I understand you have a question. I'll review the details and provide an answer soon.",
            "Thanks for reaching out with this question. I need to gather some information before responding."
        ])
    elif message_type == "meeting":
        suggestions.extend([
            "I've noted the meeting request. I'll check my calendar and confirm my availability.",
            "Thank you for the meeting invitation. I'll review my schedule and respond shortly.",
            "I acknowledge the meeting request. I'll confirm my attendance once I've checked my availability."
        ])
    elif message_type == "appreciation":
        suggestions.extend([
            "Thank you for your kind words. I appreciate the recognition.",
            "I'm grateful for your appreciation. Thank you for taking the time to share this feedback.",
            "Your appreciation means a lot. Thank you for the positive feedback."
        ])
    elif message_type == "compliment":
        suggestions.extend([
            "Thank you for the compliment. I appreciate the recognition.",
            "I'm honored by your kind words. Thank you for taking the time to acknowledge this.",
            "Your feedback is much appreciated. Thank you for the encouraging words."
        ])
    else:
        # General purpose suggestions
        suggestions.extend([
            "Thank you for your message. I have received it and will respond shortly.",
            "I acknowledge receipt of your message. I'm reviewing the details and will get back to you soon.",
            "Thank you for sharing this information. I'll process it and provide a response.",
            "I've received your message and understand the request. I'll address this as soon as possible.",
            "Thanks for the update. I'm reviewing the information and will follow up shortly."
        ])

    # Add personalized touch if sender is known
    sender_part = f" {sender}" if sender else ""

    # Silver mode: Return structured data for action preparation
    if return_structured:
        return {
            'message_type': message_type,
            'suggestions': suggestions[:3],  # Top 3 suggestions
            'sender': sender,
            'raw_suggestions': suggestions  # All suggestions
        }

    # Bronze mode: Return markdown-formatted output (default behavior)
    reply_output = f"""# Reply Suggestions

## Message Type: {message_type.title()}

## Suggested Replies:

"""

    for i, suggestion in enumerate(suggestions[:3], 1):  # Limit to top 3 suggestions
        reply_output += f"### Option {i}:\n{suggestion}\n\n"

    reply_output += f"""## Action Required:
These are suggested replies based on the content analysis. Please review and select the most appropriate response, or craft your own using these as inspiration. Remember to personalize the response{sender_part} and ensure it addresses all points raised in the original message.
"""

    return reply_output


if __name__ == "__main__":
    # Example usage
    sample_content = """Hey, could you quickly check if the quarterly report is ready for tomorrow's meeting?"""

    result = suggest_reply(sample_content, sender="Colleague")
    print(result)