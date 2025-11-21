#!/usr/bin/env python3
"""
Markdown Report Generator for Android Suspend Diagnosis

This module generates a Markdown report based on the analysis results.
"""
import datetime
from pathlib import Path
from typing import List, Optional

from suspend_diagnosis.models.types import WakeupSource, ArtifactMap


class MarkdownBuilder:
    """
    Generates a Markdown file based on analysis results.
    Returns the absolute path to the generated Markdown file.
    """

    def build(
        self,
        case_dir: str,
        failed: bool,
        reasons: List[str],
        ai_md: Optional[str],
        artifacts: ArtifactMap,
    ) -> str:
        """
        Build a Markdown report based on analysis results.
        
        Args:
            case_dir: Directory containing collected evidence
            failed: Whether suspend failure was detected
            reasons: List of reasons for suspend failure
            ai_md: AI-generated analysis text (if available)
            artifacts: Dictionary mapping filenames to their paths
            
        Returns:
            str: Path to the generated Markdown file
        """
        md = [
            "# Suspend Diagnosis Report\n",
            f"**Collection Directory**: `{case_dir}`  ",
            f"**Time**: {datetime.datetime.now().isoformat()}\n\n",
            "## Conclusion\n",
            ("**Assessment**: Suspend failure detected\n\n" if failed else "**Assessment**: No clear suspend failure detected\n\n"),
            "### Rule-based Criteria\n",
            "- " + "\n- ".join(reasons) if reasons else "- No significant failure indicators",
        ]

        # Add evidence files section
        md.append("\n\n## Evidence Files\n")
        for k, v in artifacts.items():
            md.append(f"- {k}: `{v}`")

        # Add AI analysis section if available
        if ai_md:
            md.append("\n\n## AI Analysis\n")
            md.append(ai_md)

        # Add verification checklist
        md.append("\n\n## Verification Checklist\n")
        md.extend(
            [
                "1. Reproduce the same case/scenario and collect the same evidence again",
                "2. Confirm `dumpsys suspend_control_internal` shows `last_failed_suspend == 0`",
                "3. Compare average power/current curves, confirm reduction >= 3%",
            ]
        )

        # Write the report to a file
        md_path = Path(case_dir) / "suspend_diagnosis_report.md"
        Path(md_path).write_text("\n".join(md), encoding="utf-8")
        return str(md_path)
