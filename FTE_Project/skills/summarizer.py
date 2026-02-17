"""
Summarizer Skill for Bronze-level Personal AI Employee
Generates concise summaries of incoming content with key points highlighted
"""

def summarize_content(content, return_structured=False):
    """
    Generate a summary of the provided content

    Args:
        content (str): The content to summarize
        return_structured (bool): If True, return dict instead of markdown

    Returns:
        str or dict: Formatted summary with key points
    """
    return generate_summary(content, return_structured)


def generate_summary(content, return_structured=False):
    """
    Generate a summary of the provided content

    Args:
        content (str): The content to summarize
        return_structured (bool): If True, return dict instead of markdown

    Returns:
        str or dict: Formatted summary with key points
    """
    # Simple implementation - in a real scenario, this could use more advanced NLP
    lines = content.split('\n')

    # Extract key points based on length and importance indicators
    key_points = []
    summary_lines = []

    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            # Add lines that seem important (longer lines or those starting with bullet points)
            if len(line) > 50 or line.startswith(('-', '*', '•', '#')):
                summary_lines.append(line)

            # Look for potential key points
            if any(keyword in line.lower() for keyword in ['important', 'urgent', 'key', 'critical', 'main']):
                key_points.append(f"- {line}")

    # If no key points were identified, pick the longest lines as key points
    if not key_points:
        sorted_lines = sorted(summary_lines, key=len, reverse=True)
        key_points = [f"- {line}" for line in sorted_lines[:min(3, len(sorted_lines))]]

    # Create summary from first few lines if no specific important lines were found
    if not summary_lines:
        words = content.split()
        summary_text = ' '.join(words[:min(50, len(words))]) + ('...' if len(words) > 50 else '')
    else:
        summary_text = ' '.join(summary_lines[:min(3, len(summary_lines))])

    # Extract keywords
    words = content.lower().split()
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [w for w in set(words) if len(w) > 4 and w not in common_words][:5]

    # Return structured data if requested
    if return_structured:
        return {
            "summary": summary_text,
            "key_points": [kp.replace("- ", "") for kp in key_points] if key_points else [],
            "keywords": keywords
        }

    # Format the summary as markdown
    summary_output = f"""# Summary

## Content Overview
{summary_text}

## Key Points
"""

    if key_points:
        summary_output += '\n'.join(key_points)
    else:
        summary_output += "- No specific key points identified in the content."

    return summary_output


if __name__ == "__main__":
    # Example usage
    sample_content = """Hello team,

We need to schedule an urgent meeting tomorrow at 2 PM to discuss the quarterly budget proposal. The main concerns are around the marketing spend allocation and the new hire positions we planned for Q3.

Please confirm your availability and come prepared with your department's budget breakdown.

Best regards,
Manager
"""

    print(generate_summary(sample_content))