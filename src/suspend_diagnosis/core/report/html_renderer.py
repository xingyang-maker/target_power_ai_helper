#!/usr/bin/env python3
"""
HTML Report Generator for Android Suspend Diagnosis

This module converts Markdown reports to HTML and adds interactive charts.
"""
import base64
import io
from pathlib import Path
from typing import List

import markdown
import matplotlib.pyplot as plt

from suspend_diagnosis.models.types import WakeupSource


class HtmlRenderer:
    """
    Converts Markdown files to HTML and embeds a bar chart of Top-5 Wakeup Sources.
    Returns the path to the generated HTML file.
    """

    def render(self, md_path: str) -> str:
        """
        Convert a Markdown report to HTML.
        
        Args:
            md_path: Path to the Markdown file
            
        Returns:
            str: Path to the generated HTML file
        """
        # Read the Markdown file
        with open(md_path, encoding="utf-8") as f:
            md_text = f.read()
        
        # Convert Markdown to HTML
        html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

        # Assemble the complete HTML document
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Suspend Diagnosis Report</title>
    <style>
        body {{font-family: Arial, Helvetica, sans-serif; margin: 2rem; line-height: 1.6;}}
        h1, h2, h3 {{color: #2c3e50;}}
        pre {{background:#f8f8f8; padding:1rem; overflow:auto;}}
        table {{border-collapse: collapse; width: 100%;}}
        th, td {{border: 1px solid #ddd; padding: 8px; text-align: left;}}
        th {{background:#f2f2f2;}}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""

        # Write the HTML to a file
        html_path = Path(md_path).with_suffix(".html")
        Path(html_path).write_text(html, encoding="utf-8")
        
        print(f"[REPORT] Markdown: {md_path}")
        print(f"[REPORT] HTML    : {html_path}")
        
        return str(html_path)
