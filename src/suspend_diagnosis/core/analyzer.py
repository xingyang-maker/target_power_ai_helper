#!/usr/bin/env python3
"""
Log Analysis Module for Android Suspend Diagnosis

This module provides functionality to analyze Android logs for suspend failures
and extract information about wakeup sources.
"""
import re
from typing import List, Tuple, Dict

from suspend_diagnosis.models.types import WakeupSource, SuspendAnalysisResult


class SimpleAnalyzer:
    """
    Business logic layer: Parses logs to determine if suspend failed following a strict 3-step process.
    """

    @staticmethod
    def analyze_suspend_stats(suspend_stats_txt: str) -> Tuple[bool, str]:
        """
        Step 1: Check suspend_stats to see if suspend succeeded or failed.
        
        Args:
            suspend_stats_txt: Content of /d/suspend_stats
            
        Returns:
            Tuple[bool, str]: (is_successful, analysis_message)
        """
        if not suspend_stats_txt.strip():
            return False, "suspend_stats file is empty or not available"
        
        # Parse the stats
        stats = {}
        for line in suspend_stats_txt.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                stats[key.strip()] = value.strip()
        
        # Check success count
        success_count = int(stats.get("success", "0"))
        fail_count = int(stats.get("fail", "0"))
        
        if success_count > 0 and fail_count == 0:
            return True, f"Suspend is working normally (success: {success_count}, fail: {fail_count})"
        else:
            return False, f"Suspend has failures (success: {success_count}, fail: {fail_count})"
    
    @staticmethod
    def analyze_wakelocks(dumpsys_suspend_txt: str) -> Tuple[bool, List[str]]:
        """
        Step 2: Check for active wakelocks that prevent suspend.
        Only called if Step 1 shows suspend failure.
        
        Args:
            dumpsys_suspend_txt: Content of dumpsys suspend_control_internal
            
        Returns:
            Tuple[bool, List[str]]: (has_active_wakelocks, list_of_active_wakelocks)
        """
        active_wakelocks = []
        
        # Scan every line for Active wakelocks
        for line in dumpsys_suspend_txt.splitlines():
            line = line.strip()
            if not line or not "|" in line:
                continue
                
            # Look for "Active" status in the line
            if "Active" in line:
                parts = line.split("|")
                # Expected format: | NAME | PID | TYPE | STATUS | ...
                if len(parts) >= 5:
                    name = parts[1].strip()  # NAME is in column 1 (0-indexed)
                    status = parts[4].strip()  # STATUS is in column 4 (0-indexed)
                    
                    # Check if STATUS column contains "Active" and we have a valid name
                    if "Active" in status and name:
                        # Skip header lines and separators
                        if (not name.startswith("-") and 
                            name.lower() != "name" and 
                            "wakelock stats" not in name.lower() and
                            len(name) > 0):
                            active_wakelocks.append(name)
        
        return len(active_wakelocks) > 0, active_wakelocks
    
    @staticmethod
    def analyze_dmesg(dmesg_txt: str) -> Dict[str, any]:
        """
        Step 3: Analyze dmesg for suspend entry and failure details.
        Only called if Step 1 shows failure AND Step 2 shows no active wakelocks.
        
        Args:
            dmesg_txt: Content of dmesg log
            
        Returns:
            Dict with keys:
                - has_suspend_entry: bool
                - has_suspend_failure: bool
                - failure_messages: List[str]
        """
        result = {
            "has_suspend_entry": False,
            "has_suspend_failure": False,
            "failure_messages": []
        }
        
        # Check for suspend entry
        if "PM: suspend entry" in dmesg_txt or "PM: Syncing filesystems" in dmesg_txt:
            result["has_suspend_entry"] = True
        
        # Check for suspend failures
        failure_patterns = [
            "PM: suspend entry failed",
            "suspend entry failed",
            "PM: Some devices failed to suspend",
            "PM: Device .* failed to suspend",
        ]
        
        for line in dmesg_txt.splitlines():
            for pattern in failure_patterns:
                if pattern in line:
                    result["has_suspend_failure"] = True
                    result["failure_messages"].append(line.strip())
        
        return result
    
    @staticmethod
    def parse_suspend_failed(dmesg_txt: str, dumpsys_suspend_txt: str, suspend_stats_txt: str = "") -> Tuple[bool, List[str], Dict[str, any]]:
        """
        Main analysis function following strict 3‑step process.
        Handles missing log files gracefully – if a file is empty or not provided,
        the corresponding step is skipped and a note is added to the reasons.
        
        Args:
            dmesg_txt: Content of dmesg log (may be empty)
            dumpsys_suspend_txt: Content of dumpsys suspend_control_internal (may be empty)
            suspend_stats_txt: Content of /d/suspend_stats (may be empty)
            
        Returns:
            Tuple[bool, List[str], Dict]: (failed, reasons, detailed_analysis)
        """
        failed = False
        reasons = []
        detailed_analysis = {
            "step1_suspend_stats": {},
            "step2_wakelocks": {},
            "step3_dmesg": {},
            "conclusion": ""
        }
        
        # Step 1: Check suspend_stats (if available)
        if suspend_stats_txt.strip():
            stats_success, stats_msg = SimpleAnalyzer.analyze_suspend_stats(suspend_stats_txt)
            detailed_analysis["step1_suspend_stats"] = {
                "success": stats_success,
                "message": stats_msg
            }
            if stats_success:
                # Suspend is working, no need to check further
                detailed_analysis["conclusion"] = "Suspend is working normally. No further analysis needed."
                return False, ["Suspend is working normally"], detailed_analysis
            # Suspend failed, continue
            failed = True
            reasons.append(f"Step 1: {stats_msg}")
        else:
            # No suspend_stats file – cannot determine step 1, skip but note
            detailed_analysis["step1_suspend_stats"] = {
                "success": False,
                "message": "suspend_stats file not available"
            }
            failed = True
            reasons.append("Step 1: suspend_stats file not available, skipping step 1 analysis")
        
        # Step 2: Check for active wakelocks (if file provided)
        if dumpsys_suspend_txt.strip():
            has_wakelocks, wakelock_list = SimpleAnalyzer.analyze_wakelocks(dumpsys_suspend_txt)
            detailed_analysis["step2_wakelocks"] = {
                "has_active": has_wakelocks,
                "wakelocks": wakelock_list
            }
            if has_wakelocks:
                reasons.append(f"Step 2: Active wakelocks found: {', '.join(wakelock_list)}")
                detailed_analysis["conclusion"] = f"Root cause: Active wakelocks preventing suspend: {', '.join(wakelock_list)}"
                return failed, reasons, detailed_analysis
            else:
                reasons.append("Step 2: No active wakelocks found")
        else:
            detailed_analysis["step2_wakelocks"] = {
                "has_active": False,
                "wakelocks": []
            }
            reasons.append("Step 2: dumpsys_suspend.txt not available, skipping wakelock analysis")
        
        # Step 3: Analyze dmesg (if file provided)
        if dmesg_txt.strip():
            dmesg_result = SimpleAnalyzer.analyze_dmesg(dmesg_txt)
            detailed_analysis["step3_dmesg"] = dmesg_result
            if not dmesg_result["has_suspend_entry"]:
                reasons.append("Step 3: No suspend entry found in dmesg - system did not attempt to suspend")
                detailed_analysis["conclusion"] = "Root cause: System did not attempt to enter suspend"
            elif dmesg_result["has_suspend_failure"]:
                reasons.append(f"Step 3: Suspend entry failed - {len(dmesg_result['failure_messages'])} failure(s) found")
                for msg in dmesg_result["failure_messages"][:3]:
                    reasons.append(f"  - {msg}")
                detailed_analysis["conclusion"] = "Root cause: Suspend entry failed in kernel"
            else:
                reasons.append("Step 3: Suspend entry found but no clear failure in dmesg")
                detailed_analysis["conclusion"] = "Suspend failed but root cause unclear from logs"
        else:
            detailed_analysis["step3_dmesg"] = {
                "has_suspend_entry": False,
                "has_suspend_failure": False,
                "failure_messages": []
            }
            reasons.append("Step 3: dmesg.txt not available, skipping dmesg analysis")
        
        return failed, reasons, detailed_analysis
