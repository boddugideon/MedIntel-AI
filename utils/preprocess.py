import re

def clean_text(text):
    # Remove trailing spaces from each line
    lines = [line.strip() for line in text.splitlines()]

    # Remove empty lines
    lines = [line for line in lines if line]

    # Join lines back with newline
    cleaned_text = "\n".join(lines)

    return cleaned_text