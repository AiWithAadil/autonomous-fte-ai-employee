"""
Utility functions for Bronze-level Personal AI Employee skills
Provides common functionality for file I/O and formatting
"""

import os
import datetime
from pathlib import Path


def read_file_content(file_path):
    """
    Read content from a file

    Args:
        file_path (str): Path to the file to read

    Returns:
        str: Content of the file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def write_analysis_output(output_dir, original_filename, analysis_type, content):
    """
    Write analysis output to a file in the specified directory

    Args:
        output_dir (str): Directory to write the output file
        original_filename (str): Name of the original file being analyzed
        analysis_type (str): Type of analysis (e.g., 'Summary', 'Priority')
        content (str): Content to write to the file

    Returns:
        str: Path of the created file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate output filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(original_filename).stem
    output_filename = f"{base_name}_{analysis_type}_{timestamp}.md"
    output_path = os.path.join(output_dir, output_filename)

    # Add metadata header
    header = f"""---
original_file: {original_filename}
analysis_type: {analysis_type}
generated_at: {datetime.datetime.now().isoformat()}
---

"""

    # Write content with header
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(header + content)

    return output_path


def format_timestamp():
    """
    Generate a formatted timestamp string

    Returns:
        str: Formatted timestamp
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_filename(filename):
    """
    Create a safe filename by removing or replacing invalid characters

    Args:
        filename (str): Original filename

    Returns:
        str: Safe filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length
    if len(filename) > 200:
        filename = filename[:197] + '...'

    return filename