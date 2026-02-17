"""
Task Extractor Skill for Bronze-level Personal AI Employee
Identifies possible todos/action items from messages
"""

def extract_tasks(content, return_structured=False):
    """
    Extract possible tasks from the content

    Args:
        content (str): The content to analyze for tasks
        return_structured (bool, optional): If True, return structured data for Silver mode.
                                           If False (default), return markdown for Bronze mode.

    Returns:
        str or dict: Markdown-formatted list of extracted tasks (Bronze mode) or
                    structured dict with tasks (Silver mode)
    """
    import re

    # Define patterns that indicate tasks
    task_patterns = [
        r'\b(please|need to|must|have to|should|could)\s+(do|complete|finish|send|review|check|prepare|submit|attend)\b',
        r'\b(to do|todo|to-do|action item|next step|task|assignment)\b',
        r'\b(by\s+\w+\s+\d{1,2}(?:st|nd|rd|th)?|before|after|when|tomorrow|today|later|ASAP|urgent)\b',
        r'(call|email|contact|reach out|respond|reply|follow up|remind|inform|notify)',
        r'(buy|purchase|order|get|obtain|arrange|schedule|book|setup|configure|install|update|change)'
    ]

    # Common task-indicating words
    task_indicators = [
        'action', 'todo', 'task', 'complete', 'finish', 'do', 'perform', 'execute',
        'attend', 'review', 'read', 'watch', 'learn', 'study', 'practice',
        'buy', 'get', 'purchase', 'order', 'request', 'apply', 'register',
        'make', 'create', 'draft', 'write', 'edit', 'proofread', 'submit',
        'organize', 'arrange', 'prepare', 'plan', 'think about', 'decide'
    ]

    # Lines that look like tasks
    potential_tasks = []
    lines = content.split('\n')

    for line in lines:
        line_clean = line.strip()
        if line_clean and not line_clean.startswith('#'):  # Exclude headers
            # Check if line matches any task pattern
            matches_pattern = any(re.search(pattern, line_clean, re.IGNORECASE) for pattern in task_patterns)
            has_indicator = any(indicator in line_clean.lower() for indicator in task_indicators)

            # Check if line contains action-indicating words and potentially a deadline
            has_deadline = bool(re.search(r'(by|before|until|due|tomorrow|today|tonight|week|month|ASAP)', line_clean, re.IGNORECASE))

            if matches_pattern or has_indicator or has_deadline:
                # Clean up the line to make it more task-like
                cleaned_line = re.sub(r'^[-*•]\s*', '', line_clean)  # Remove bullet points
                cleaned_line = re.sub(r'^\d+\.\s*', '', cleaned_line)  # Remove numbered list items
                potential_tasks.append(cleaned_line)

    # Additional processing to extract more implicit tasks
    sentences = re.split(r'[.!?]+', content)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Only consider meaningful sentences
            has_indicator = any(indicator in sentence.lower() for indicator in task_indicators)
            has_deadline = bool(re.search(r'(by|before|tomorrow|today|due)', sentence, re.IGNORECASE))

            if has_indicator and has_deadline:
                cleaned_sentence = re.sub(r'^[-*•]\s*', '', sentence)
                if cleaned_sentence not in potential_tasks:
                    potential_tasks.append(cleaned_sentence)

    # Silver mode: Return structured data for action preparation
    if return_structured:
        structured_tasks = []
        for i, task in enumerate(potential_tasks):
            # Determine priority based on keywords
            priority = 'normal'
            task_lower = task.lower()
            if any(word in task_lower for word in ['urgent', 'asap', 'immediately', 'critical']):
                priority = 'urgent'
            elif any(word in task_lower for word in ['important', 'priority', 'must']):
                priority = 'high'

            structured_tasks.append({
                'title': task[:100],  # First 100 chars as title
                'description': task,
                'priority': priority,
                'index': i
            })

        return {
            'tasks': structured_tasks,
            'count': len(structured_tasks),
            'raw_tasks': potential_tasks
        }

    # Bronze mode: Return markdown-formatted output (default behavior)
    # Format the extracted tasks
    if potential_tasks:
        tasks_output = "# Extracted Tasks\n\n## Possible Action Items:\n\n"

        for i, task in enumerate(potential_tasks, 1):
            tasks_output += f"### Task {i}:\n- {task.strip()}\n\n"
    else:
        tasks_output = "# Extracted Tasks\n\n## Possible Action Items:\n\nNo specific tasks were clearly identified in the content.\n\n## Tips for Task Identification:\n- Look for action words like 'do', 'complete', 'attend', 'review'\n- Check for deadlines or time-sensitive language\n- Identify requests or assignments\n- Consider follow-up actions needed\n"

    tasks_output += """## Review Needed:
Please review these extracted potential tasks and determine which ones require action. Some may be informational rather than actionable. Prioritize based on importance and deadlines."""

    return tasks_output


if __name__ == "__main__":
    # Example usage
    sample_content = """Hello team,

For tomorrow's meeting, we need to prepare the quarterly budget presentation. Please complete the following:

1. Review your department's expense reports
2. Prepare your projected spending for Q2
3. Send your updates to me by 3 PM today

Also, remember to book the conference room for our meeting.

Best regards,
Manager"""

    result = extract_tasks(sample_content)
    print(result)