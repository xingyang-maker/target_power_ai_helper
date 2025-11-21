#!/usr/bin/env python3
"""
AI Analysis Module for Android Suspend Diagnosis

This module provides AI-powered analysis of Android logs using the QGenie LLM service.
"""
import json
from typing import Optional

from qgenie import ChatMessage, QGenieClient
from suspend_diagnosis.models.types import LogMap


class QGenieReporter:
    """
    Calls the QGenie LLM service and returns text analysis results.
    
    The `endpoint` parameter is kept for compatibility but doesn't affect the actual call.
    If empty, the default QGenie configuration will be used.
    """

    def __init__(self, endpoint: Optional[str] = None):
        """
        Initialize the QGenie reporter.
        
        Args:
            endpoint: Optional QGenie endpoint URL (not used in current implementation)
        """
        self.endpoint = endpoint
        self.client = QGenieClient(max_retries=1, debug=True)

    def generate(self, logs: LogMap) -> Optional[str]:
        """
        Send logs to the model and return the generated text analysis.
        
        Args:
            logs: Dictionary mapping log types to their content
            
        Returns:
            Optional[str]: AI-generated analysis text, or None if an error occurred
        """
        # Construct structured prompt for focused analysis
        prompt = (
            "You are an Android power management and kernel expert. Analyze the following logs in this specific order:\n\n"
            "**Analysis Steps:**\n"
            "1. First, check `/d/suspend_stats` to determine if suspend succeeded or failed\n"
            "   - Look for: success count, fail count, failed_suspend, failed_resume, etc.\n"
            "   - Report: Whether suspend is working or failing\n\n"
            "2. Second, check `dumpsys suspend_control_internal` for wakelocks\n"
            "   - Look for: active wakelocks, last_failed_suspend counter, blocking components\n"
            "   - Report: If any wakelocks are preventing suspend\n\n"
            "3. Third, only if suspend failed AND no wakelocks found, analyze `dmesg` for root cause\n"
            "   - Look for: suspend entry failures, driver errors, kernel messages\n"
            "   - Report: Specific error messages and failing components\n\n"
            "**Output Format:**\n"
            "## Suspend Status\n"
            "[Based on suspend_stats: success/failure counts and status]\n\n"
            "## Wakelock Analysis\n"
            "[Based on dumpsys: any blocking wakelocks or components]\n\n"
            "## Root Cause (if applicable)\n"
            "[Based on dmesg: only if suspend failed without wakelocks]\n\n"
            "## Recommendations\n"
            "[Specific, actionable steps to fix the issue]\n\n"
            "**Logs:**\n"
            + json.dumps(logs, ensure_ascii=False)
        )

        try:
            response = self.client.chat(
                messages=[ChatMessage(role="user", content=prompt)]
            )
            return response.choices[0].message.content
        except Exception as e:
            print("[AI ERROR]", e)
            return None
