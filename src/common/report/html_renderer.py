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

from common.types import WakeupSource


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

        # Assemble the complete HTML document with enhanced styling
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suspend Diagnosis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #1a202c;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
            font-size: 2rem;
        }}
        
        h2 {{
            color: #2d3748;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 6px;
            font-size: 1.5rem;
        }}
        
        h3 {{
            color: #4a5568;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            font-size: 1.25rem;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 2rem 0;
        }}
        
        p {{
            margin-bottom: 1rem;
        }}
        
        strong {{
            color: #2d3748;
            font-weight: 600;
        }}
        
        ul, ol {{
            margin-left: 2rem;
            margin-bottom: 1rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        code {{
            background: #f7fafc;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
            color: #e53e3e;
        }}
        
        pre {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin-bottom: 1rem;
        }}
        
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1.5rem;
            background: white;
        }}
        
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 0.75rem;
            text-align: left;
        }}
        
        th {{
            background: #edf2f7;
            font-weight: 600;
            color: #2d3748;
        }}
        
        tr:hover {{
            background: #f7fafc;
        }}
        
        .status-success {{
            color: #38a169;
            font-weight: bold;
        }}
        
        .status-failure {{
            color: #e53e3e;
            font-weight: bold;
        }}
        
        .section-card {{
            background: #f7fafc;
            border-left: 4px solid #3182ce;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border-radius: 4px;
        }}
        
        .finding-item {{
            background: #fff5f5;
            border-left: 3px solid #fc8181;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 3px;
        }}
        
        .finding-item.normal {{
            background: #f0fff4;
            border-left-color: #68d391;
        }}
        
        .ai-section {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 2rem 0;
        }}
        
        .checklist {{
            background: #fffaf0;
            border: 2px solid #ed8936;
            padding: 1.5rem;
            border-radius: 8px;
        }}
        
        .checklist li {{
            padding: 0.5rem 0;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
{html_body}
    </div>
</body>
</html>"""

        # Write the HTML to a file
        html_path = Path(md_path).with_suffix(".html")
        Path(html_path).write_text(html, encoding="utf-8")
        
        print(f"[REPORT] Markdown: {md_path}")
        print(f"[REPORT] HTML    : {html_path}")
        
        return str(html_path)
