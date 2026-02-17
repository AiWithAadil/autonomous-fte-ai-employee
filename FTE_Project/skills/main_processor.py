"""
Main Processor for Bronze-level Personal AI Employee Skills
Orchestrates all skills to analyze incoming content and generate outputs
"""

import os
from pathlib import Path

from .summarizer import generate_summary
from .priority_detector import detect_priority
from .categorizer import categorize_content
from .reply_suggester import suggest_reply
from .task_extractor import extract_tasks
from .utils import write_analysis_output


def process_content(content, original_filename, sender=None):
    """
    Process content using all available skills and generate analysis outputs

    Args:
        content (str): The content to analyze
        original_filename (str): Name of the original file being processed
        sender (str, optional): The sender of the original message

    Returns:
        list: List of paths to generated analysis files
    """
    output_dir = "vault/Analysis_Outputs"

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    generated_files = []

    # Generate summary
    summary_content = generate_summary(content)
    summary_path = write_analysis_output(
        output_dir, original_filename, "Summary", summary_content
    )
    generated_files.append(summary_path)

    # Detect priority
    priority_result = detect_priority(content)
    priority_path = write_analysis_output(
        output_dir, original_filename, "Priority", priority_result["analysis"]
    )
    generated_files.append(priority_path)

    # Categorize content
    category_result = categorize_content(content)
    category_path = write_analysis_output(
        output_dir, original_filename, "Category", category_result["analysis"]
    )
    generated_files.append(category_path)

    # Suggest replies
    reply_content = suggest_reply(content, sender)
    reply_path = write_analysis_output(
        output_dir, original_filename, "Reply_Suggestions", reply_content
    )
    generated_files.append(reply_path)

    # Extract tasks
    task_content = extract_tasks(content)
    task_path = write_analysis_output(
        output_dir, original_filename, "Extracted_Tasks", task_content
    )
    generated_files.append(task_path)

    return generated_files


def process_file(file_path, sender=None):
    """
    Process a file using all available skills

    Args:
        file_path (str): Path to the file to process
        sender (str, optional): The sender of the original message

    Returns:
        list: List of paths to generated analysis files
    """
    from .utils import read_file_content

    # Read the content of the file
    content = read_file_content(file_path)
    filename = Path(file_path).name

    # Process the content
    return process_content(content, filename, sender)


if __name__ == "__main__":
    # Example usage
    sample_content = """Hello team,

We need to schedule an urgent meeting tomorrow at 2 PM to discuss the quarterly budget proposal. The main concerns are around the marketing spend allocation and the new hire positions we planned for Q3.

Please confirm your availability and come prepared with your department's budget breakdown.

Also, don't forget to submit your expense reports by Friday.

Best regards,
Manager
"""

    print("Processing sample content...")
    generated_files = process_content(sample_content, "sample_message.txt", "Manager")

    print(f"Generated {len(generated_files)} analysis files:")
    for file_path in generated_files:
        print(f"- {file_path}")