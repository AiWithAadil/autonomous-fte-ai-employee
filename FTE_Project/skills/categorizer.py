"""
Categorizer Skill for Bronze-level Personal AI Employee
Classifies content into categories (work/personal/study/finance/other)
"""

def categorize_content(content, return_structured=False):
    """
    Classify content into predefined categories

    Args:
        content (str): The content to categorize
        return_structured (bool): If True, return simplified dict for agent use

    Returns:
        dict: Dictionary containing category and confidence score
    """
    content_lower = content.lower()

    # Define category keywords
    categories = {
        "work": [
            "meeting", "colleague", "boss", "company", "project", "client", "deadline",
            "report", "presentation", "office", "team", "department", "employee", "employer",
            "schedule", "calendar", "work", "business", "corporate", "professional",
            "performance", "review", "task", "assignment", "agenda", "conference"
        ],
        "personal": [
            "family", "friend", "parent", "child", "wife", "husband", "spouse", "relative",
            "birthday", "celebration", "vacation", "holiday", "weekend", "dinner", "party",
            "social", "personal", "relationship", "home", "hobby", "leisure", "fun"
        ],
        "study": [
            "lecture", "professor", "student", "assignment", "homework", "exam", "test",
            "course", "class", "school", "university", "college", "education", "learning",
            "research", "thesis", "paper", "study", "academic", "grade", "degree", "campus"
        ],
        "finance": [
            "money", "payment", "bill", "invoice", "bank", "account", "credit", "debit",
            "budget", "expense", "investment", "loan", "tax", "refund", "fee", "cost",
            "price", "financial", "finances", "cash", "salary", "income", "revenue"
        ]
    }

    # Count occurrences of category-specific words
    scores = {}
    for category, keywords in categories.items():
        count = sum(content_lower.count(keyword) for keyword in keywords)
        scores[category] = count

    # Determine the highest scoring category
    max_category = max(scores, key=scores.get)
    max_score = scores[max_category]

    # Calculate confidence based on total word count
    total_words = len(content.split())
    confidence = min(max_score / max(total_words * 0.1, 1), 1.0) if total_words > 0 else 0.5

    # If no strong indicator found, assign to "other"
    if max_score == 0:
        max_category = "other"
        confidence = 0.3
    elif confidence < 0.2:
        # If confidence is low, consider it as mixed or other
        other_score = sum(scores.values()) / len(scores)
        if max_score < other_score * 1.5:
            max_category = "other"
            confidence = 0.4

    # Format scores string (needed for both structured and markdown output)
    scores_str = ", ".join([f"{cat}: {score}" for cat, score in scores.items()])

    # Return structured data if requested
    if return_structured:
        return {
            "category": max_category,
            "confidence": confidence,
            "reasoning": f"Found {max_score} category-specific keywords. Scores: {scores_str}"
        }

    # Format output
    category_output = f"""# Category Classification

## Primary Category: {max_category.upper()}

### Confidence Score: {confidence:.2f}

### Keyword Counts by Category:
{scores_str}

### Analysis:
The content has been classified as **{max_category}** based on the presence of category-specific keywords.
The system identified {max_score} relevant terms associated with this category.
"""

    return {
        "category": max_category,
        "confidence": confidence,
        "analysis": category_output
    }


if __name__ == "__main__":
    # Example usage
    sample_content = """Hi team, we need to prepare for the quarterly budget meeting scheduled for Friday. Please review your department's expenses and come with proposals for next quarter's allocations."""

    result = categorize_content(sample_content)
    print(result["analysis"])