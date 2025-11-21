#!/usr/bin/env python3
"""
Android Suspend Diagnosis Tool

This tool collects and analyzes Android device logs to diagnose suspend-related issues.
It generates both Markdown and HTML reports with analysis results.
"""

import argparse
import sys
from pathlib import Path

from suspend_diagnosis.core.collector import AdbEvidenceCollector
from suspend_diagnosis.core.analyzer import SimpleAnalyzer
from suspend_diagnosis.core.ai import QGenieReporter
from suspend_diagnosis.core.report.markdown_builder import MarkdownBuilder
from suspend_diagnosis.core.report.html_renderer import HtmlRenderer
from suspend_diagnosis.cli import build_parser
from suspend_diagnosis.models.types import LogMap

def main(args):
    """
    Main function that orchestrates the suspend diagnosis process.
    
    Args:
        args: Command line arguments parsed by argparse
    """
    # Step 1: Collect evidence from the device
    collector = AdbEvidenceCollector(
        adb=args.adb,
        device=args.device,
        out_dir=args.out,
    )
    case_dir, artifacts = collector.collect()
    
    # Step 2: Read collected files
    txts = {k: Path(v).read_text(encoding='utf-8', errors='ignore') 
            for k, v in artifacts.items()}
    
    # Step 3: Analyze logs for suspend failures
    analyzer = SimpleAnalyzer()
    failed, reasons = analyzer.parse_suspend_failed(
        txts.get("dmesg.txt", ""), 
        txts.get("dumpsys_suspend.txt", "")
    )
    
    # Step 4: AI analysis using QGenieReporter
    reporter = QGenieReporter(endpoint=args.ai_endpoint)
    logs: LogMap = {
        "dmesg": txts.get("dmesg.txt", "")[:4000],
        "dumpsys_suspend": txts.get("dumpsys_suspend.txt", "")[:4000],
        "suspend_stats": txts.get("suspend_stats.txt", "")[:4000],
    }
    ai_md = reporter.generate(logs)
    
    if ai_md:
        print("\n[AI RESPONSE]")
        print(ai_md)
    
    # Step 5: Generate Markdown report
    md_builder = MarkdownBuilder()
    md_path = md_builder.build(case_dir, failed, reasons, ai_md, artifacts)
    
    # Step 6: Generate HTML report
    html_renderer = HtmlRenderer()
    html_path = html_renderer.render(md_path)
    
    print(f"\n[REPORT] Generated: {html_path}")
    return html_path


def main_cli():
    """
    Entry point for the command-line interface.
    This function is used by the setup.py entry_points.
    """
    parser = build_parser()
    args = parser.parse_args()
    main(args)
