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
        detailed_analysis: Optional[dict] = None,
    ) -> str:
        """
        Build a Markdown report based on analysis results following strict 3-step process.
        
        Args:
            case_dir: Directory containing collected evidence
            failed: Whether suspend failure was detected
            reasons: List of reasons for suspend failure
            ai_md: AI-generated analysis text (if available)
            artifacts: Dictionary mapping filenames to their paths
            detailed_analysis: Detailed step-by-step analysis results
            
        Returns:
            str: Path to the generated Markdown file
        """
        md = [
            "# Suspend Diagnosis Report\n\n",
            f"**Collection Directory**: `{case_dir}`  \n",
            f"**Time**: {datetime.datetime.now().isoformat()}\n\n",
            "---\n\n",
        ]
        
        # Overall conclusion
        if failed:
            md.append("## 🔴 CONCLUSION: Suspend Failure Detected\n\n")
        else:
            md.append("## 🟢 CONCLUSION: Suspend Working Normally\n\n")
        
        if detailed_analysis and detailed_analysis.get("conclusion"):
            md.append(f"**Root Cause**: {detailed_analysis['conclusion']}\n\n")
        
        md.append("---\n\n")
        
        # Step 1: Suspend Stats Analysis
        md.append("## Step 1️⃣: Suspend Statistics Check\n")
        md.append("**Purpose**: Check if suspend succeeded or failed  \n")
        md.append("**File**: `/d/suspend_stats` → `suspend_stats.txt`\n\n")
        
        if detailed_analysis and "step1_suspend_stats" in detailed_analysis:
            step1 = detailed_analysis["step1_suspend_stats"]
            if step1.get("success"):
                md.append("✅ **Result**: Suspend is working normally\n")
                md.append(f"- {step1.get('message', 'No details available')}\n")
                md.append("- **Analysis stops here** - No further investigation needed\n\n")
            else:
                md.append("❌ **Result**: Suspend has failures\n")
                md.append(f"- {step1.get('message', 'No details available')}\n")
                md.append("- **Continue to Step 2** - Check for wakelocks\n\n")
        else:
            step1_reasons = [r for r in reasons if "Step 1" in r]
            if step1_reasons:
                md.append("❌ **Result**: Suspend has failures\n")
                for reason in step1_reasons:
                    md.append(f"- {reason}\n")
            else:
                md.append("⚠️ **Result**: Unable to determine suspend status\n")
        
        # 原始 Suspend Stats 日志（仅在 suspend 失败时展示） 
        if ( (detailed_analysis and "step1_suspend_stats" in detailed_analysis and not detailed_analysis["step1_suspend_stats"].get("success")) 
                 or (step1_reasons) ):
            if "suspend_stats.txt" in artifacts:
                try:
                    raw = Path(artifacts["suspend_stats.txt"]).read_text(encoding="utf-8", errors="ignore")
                    lines = raw.splitlines()
                    # Filter lines containing key terms
                    keywords = ["fail", "error", "suspend", "warning", "critical"]
                    filtered = [line for line in lines if any(k in line.lower() for k in keywords)]
                    # Use filtered lines if any, else fallback to first 20 lines
                    selected = filtered[:20] if filtered else lines[:20]
                    truncated = "\n".join(selected)
                    if len(selected) < len(lines):
                        truncated += "\n... (truncated)"
                    md.append("### 原始 Suspend Stats (关键片段)\n")
                    md.append("```text\n")
                    md.append(truncated)
                    md.append("\n```\n\n")
                except Exception:
                    pass
        md.append("---\n\n")
        
        # Step 2: Wakelock Analysis (only if Step 1 failed)
        md.append("## Step 2️⃣: Wakelock Analysis\n")
        md.append("**Purpose**: Check for active wakelocks preventing suspend  \n")
        md.append("**File**: `dumpsys suspend_control_internal` → `dumpsys_suspend.txt`\n\n")
        
        if detailed_analysis and "step2_wakelocks" in detailed_analysis:
            step2 = detailed_analysis["step2_wakelocks"]
            if step2.get("has_active"):
                wakelocks = step2.get("wakelocks", [])
                md.append("❌ **Result**: Active wakelocks found (ROOT CAUSE)\n")
                md.append("**Active Wakelocks**:\n")
                for wakelock in wakelocks:
                    md.append(f"- `{wakelock}`\n")
                md.append("\n**Analysis stops here** - Root cause identified\n\n")
            else:
                md.append("✅ **Result**: No active wakelocks found\n")
                md.append("- All wakelocks are in 'Inactive' state\n")
                md.append("- **Continue to Step 3** - Check kernel logs\n\n")
        else:
            step2_reasons = [r for r in reasons if "Step 2" in r]
            if any("Active wakelocks found" in r for r in step2_reasons):
                md.append("❌ **Result**: Active wakelocks found (ROOT CAUSE)\n")
                for reason in step2_reasons:
                    if "Active wakelocks found" in reason:
                        md.append(f"- {reason}\n")
            elif step2_reasons:
                md.append("✅ **Result**: No active wakelocks found\n")
                for reason in step2_reasons:
                    md.append(f"- {reason}\n")
            else:
                md.append("⚠️ **Result**: Wakelock analysis not performed\n")
        
        # 原始 Wakelock Dump 日志（仅在检测到活跃 wakelock 时展示）
        if detailed_analysis and "step2_wakelocks" in detailed_analysis and detailed_analysis["step2_wakelocks"].get("has_active"):
            if "dumpsys_suspend.txt" in artifacts:
                try:
                    raw = Path(artifacts["dumpsys_suspend.txt"]).read_text(encoding="utf-8", errors="ignore")
                    lines = raw.splitlines()
                    # Filter lines containing key terms relevant to wakelocks
                    keywords = ["wakelock", "active", "error", "fail", "warning", "blocked"]
                    filtered = [line for line in lines if any(k in line.lower() for k in keywords)]
                    selected = filtered[:20] if filtered else lines[:20]
                    truncated = "\n".join(selected)
                    if len(selected) < len(lines):
                        truncated += "\n... (truncated)"
                    md.append("### 原始 Wakelock Dump (关键片段)\n")
                    md.append("```text\n")
                    md.append(truncated)
                    md.append("\n```\n\n")
                except Exception:
                    pass
        md.append("---\n\n")
        
        # Step 3: Kernel Log Analysis (only if Steps 1&2 didn't find root cause)
        md.append("## Step 3️⃣: Kernel Log Analysis\n")
        md.append("**Purpose**: Check for suspend entry and failure details  \n")
        md.append("**File**: `dmesg -T` → `dmesg.txt`\n\n")
        
        if detailed_analysis and "step3_dmesg" in detailed_analysis:
            step3 = detailed_analysis["step3_dmesg"]
            if not step3.get("has_suspend_entry"):
                md.append("❌ **Result**: No suspend entry found\n")
                md.append("- System did not attempt to enter suspend\n")
                md.append("- Check if suspend is triggered properly\n\n")
            elif step3.get("has_suspend_failure"):
                md.append("❌ **Result**: Suspend entry failed in kernel\n")
                md.append("**Failure Messages**:\n")
                for msg in step3.get("failure_messages", [])[:3]:
                    md.append(f"- `{msg}`\n")
                md.append("\n")
            else:
                md.append("✅ **Result**: Suspend entry found, no clear failures\n")
                md.append("- Suspend process appears normal in kernel logs\n")
                md.append("- Root cause may be elsewhere\n\n")
        else:
            step3_reasons = [r for r in reasons if "Step 3" in r]
            if step3_reasons:
                if any("No suspend entry found" in r for r in step3_reasons):
                    md.append("❌ **Result**: No suspend entry found\n")
                elif any("Suspend entry failed" in r for r in step3_reasons):
                    md.append("❌ **Result**: Suspend entry failed in kernel\n")
                else:
                    md.append("✅ **Result**: Kernel log analyzed\n")
                for reason in step3_reasons:
                    md.append(f"- {reason}\n")
            else:
                md.append("⚠️ **Result**: Kernel log analysis not performed\n")
        
        # 原始 dmesg 日志（仅在 suspend 入口缺失或失败时展示）
        if detailed_analysis and "step3_dmesg" in detailed_analysis:
            step3 = detailed_analysis["step3_dmesg"]
            if not step3.get("has_suspend_entry") or step3.get("has_suspend_failure"):
                if "dmesg.txt" in artifacts:
                    try:
                        raw = Path(artifacts["dmesg.txt"]).read_text(encoding="utf-8", errors="ignore")
                        lines = raw.splitlines()
                        # Filter lines containing key terms relevant to suspend/kernel issues
                        keywords = ["suspend", "error", "fail", "warning", "critical", "blocked"]
                        filtered = [line for line in lines if any(k in line.lower() for k in keywords)]
                        selected = filtered[:20] if filtered else lines[:20]
                        truncated = "\n".join(selected)
                        if len(selected) < len(lines):
                            truncated += "\n... (truncated)"
                        md.append("### 原始 dmesg 日志 (关键片段)\n")
                        md.append("```text\n")
                        md.append(truncated)
                        md.append("\n```\n\n")
                    except Exception:
                        pass
        md.append("---\n\n")
        # 总结
        md.append("## 📋 总结\n")
        if detailed_analysis and detailed_analysis.get("conclusion"):
            md.append(f"**结论**: {detailed_analysis['conclusion']}\n\n")
        else:
            md.append("**结论**: 未检测到明确的根因，请参考上述分析。\n\n")
        md.append("---\n\n")

        # Add AI comprehensive analysis section if available
        if ai_md:
            md.append("## 🤖 AI Comprehensive Analysis\n\n")
            md.append(ai_md)
            md.append("\n\n---\n\n")

        # Add evidence files section
        md.append("## 📁 Evidence Files\n\n")
        for k, v in artifacts.items():
            md.append(f"- **{k}**: `{v}`\n")

        # Add verification checklist
        md.append("\n---\n\n")
        md.append("## ✅ Verification Checklist\n\n")
        if failed:
            md.extend([
                "After fixing the identified issue:\n\n",
                "1. **Re-run diagnosis**: Collect new evidence and verify the issue is resolved\n",
                "2. **Check suspend_stats**: Verify success count increases and fail count remains 0\n",
                "3. **Check wakelocks**: Ensure no active wakelocks in dumpsys output\n",
                "4. **Measure power**: Compare power consumption before/after fix (expect ≥3% reduction)\n",
            ])
        else:
            md.extend([
                "Suspend appears to be working normally:\n\n",
                "1. **Monitor**: Continue monitoring suspend_stats for any new failures\n",
                "2. **Power measurement**: Verify actual power consumption meets expectations\n",
                "3. **Stress test**: Test under various conditions (charging, apps running, etc.)\n",
            ])

        # Write the report to a file
        md_path = Path(case_dir) / "suspend_diagnosis_report.md"
        Path(md_path).write_text("".join(md), encoding="utf-8")
        return str(md_path)
