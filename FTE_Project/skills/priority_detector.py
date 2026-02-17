"""
Priority Detector Skill for Bronze-level Personal AI Employee
Analyzes content to detect urgency level (urgent/normal/low)
"""

def detect_priority(content, return_structured=False):
    """
    Analyze content to detect priority level

    Args:
        content (str): The content to analyze
        return_structured (bool): If True, return simplified dict for agent use

    Returns:
        dict: Dictionary containing priority level and confidence score
    """
    content_lower = content.lower()

    # Define priority indicators
    urgent_indicators = [
        'urgent', 'asap', 'immediately', 'right now', 'today', 'within hours',
        'crucial', 'critical', 'emergency', 'deadline', 'cannot wait',
        'high priority', 'top priority', 'priority 1', 'time sensitive'
    ]

    low_indicators = [
        'whenever', 'whenever convenient', 'take your time', 'optional',
        'nice to have', 'eventually', 'someday', 'not urgent', 'whenever possible'
    ]

    # Count indicators
    urgent_count = sum(indicator in content_lower for indicator in urgent_indicators)
    low_count = sum(indicator in content_lower for indicator in low_indicators)

    # Determine priority based on counts
    if urgent_count > low_count:
        priority = "urgent"
        confidence = min(0.8 + (urgent_count * 0.05), 1.0)  # Max 1.0 confidence
    elif low_count > urgent_count:
        priority = "low"
        confidence = min(0.6 + (low_count * 0.05), 0.9)
    else:
        priority = "normal"
        confidence = 0.6  # Default medium confidence for normal priority

    # Additional context analysis
    words = content.split()

    # Check for time-sensitive language
    time_sensitive_words = ['tomorrow', 'meeting', 'due', 'report', 'review']
    time_sensitive_count = sum(word.lower() in time_sensitive_words for word in words)

    if time_sensitive_count > 2 and priority == "normal":
        priority = "normal_urgent"  # Medium-high priority
        confidence = 0.7

    # Map to standard priority levels for structured output
    priority_map = {
        "urgent": "HIGH",
        "normal_urgent": "MEDIUM",
        "normal": "MEDIUM",
        "low": "LOW"
    }

    # Return structured data if requested
    if return_structured:
        return {
            "priority": priority_map.get(priority, "MEDIUM"),
            "confidence": confidence,
            "reasoning": f"Found {urgent_count} urgent indicators, {low_count} low priority indicators, {time_sensitive_count} time-sensitive terms"
        }

    # Format output
    priority_output = f"""# Priority Analysis

## Detected Priority Level: {priority.upper()}

### Confidence Score: {confidence:.2f}

### Analysis Details:
- Urgent indicators found: {urgent_count}
- Low priority indicators found: {low_count}
- Time-sensitive terms: {time_sensitive_count}

### Recommendation:
Based on the content analysis, this message has been classified as **{priority}** priority.
"""

    return {
        "priority": priority,
        "confidence": confidence,
        "analysis": priority_output
    }


if __name__ == "__main__":
    # Example usage
    sample_content = """URGENT: Please respond immediately. We have a critical issue with the production server that needs to be addressed within the next hour. The system is currently down and affecting customer orders."""

    result = detect_priority(sample_content)
    print(result["analysis"])