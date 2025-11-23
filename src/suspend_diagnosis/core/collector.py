#!/usr/bin/env python3
"""
Evidence Collection Module for Android Suspend Diagnosis

This module handles collecting log files and system state information from Android devices
using ADB commands.
"""
import datetime
from pathlib import Path
from typing import Tuple

from suspend_diagnosis.core.utils import adb_shell
from common.types import ArtifactMap


class AdbEvidenceCollector:
    """
    Collects multiple log/state files from Android devices using ADB.
    
    Returns a tuple of (case_dir, artifacts):
        case_dir - Root directory path for this collection (string)
        artifacts - Mapping of {filename: absolute_path}
    """

    def __init__(
        self,
        adb: str = "adb",
        device: str = "",
        out_dir: str = "./reports",
    ):
        """
        Initialize the evidence collector.
        
        Args:
            adb: Path to ADB executable (default: 'adb')
            device: Target device serial number (empty for default device)
            out_dir: Output directory for collected files (default: './reports')
        """
        self.adb = adb
        self.device = device
        self.out_dir = out_dir

    def collect(self) -> Tuple[str, ArtifactMap]:
        """
        Collect evidence files from the device.
        
        Returns:
            Tuple[str, Dict[str, str]]: A tuple containing:
                - case_dir: Path to the directory containing collected files
                - artifacts: Dictionary mapping filenames to their absolute paths
        """
        # Create timestamped directory for this collection
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        case_dir = Path(self.out_dir) / f"suspend_diag_{ts}"
        case_dir.mkdir(parents=True, exist_ok=True)

        artifacts: ArtifactMap = {}

        # Helper function to collect and write a single file
        def _write(name: str, cmd: str) -> None:
            """
            Execute an ADB command and write its output to a file.
            
            Args:
                name: Output filename
                cmd: ADB shell command to execute
            """
            path = str(case_dir / name)
            artifacts[name] = path
            content = adb_shell(self.adb, self.device, cmd)
            Path(path).write_text(content, encoding="utf-8")

        # Collect only three essential evidence files
        _write("dmesg.txt", "dmesg -T")
        _write("dumpsys_suspend.txt", "dumpsys suspend_control_internal")
        _write("suspend_stats.txt", "cat /d/suspend_stats")

        return str(case_dir), artifacts

    def load_existing(self, directory: str) -> Tuple[str, ArtifactMap]:
        """
        Load pre‑collected log files from a specified directory.
        
        The method scans the given directory for the expected evidence files
        (``suspend_stats.txt``, ``dumpsys_suspend.txt`` and ``dmesg.txt``) and
        builds an ``ArtifactMap`` that maps each filename to its absolute path.
        Files that are missing are simply omitted from the map – the downstream
        analysis code already handles absent artifacts gracefully.
        
        Args:
            directory: Path to the directory containing the log files.
        
        Returns:
            Tuple[str, ArtifactMap]: ``case_dir`` (the absolute path of the
            provided directory) and ``artifacts`` (a mapping of found filenames
            to their absolute paths).
        """
        case_dir = Path(directory).resolve()
        artifacts: ArtifactMap = {}
        expected_files = ["suspend_stats.txt", "dumpsys_suspend.txt", "dmesg.txt"]
        for name in expected_files:
            file_path = case_dir / name
            if file_path.is_file():
                artifacts[name] = str(file_path)
        return str(case_dir), artifacts
