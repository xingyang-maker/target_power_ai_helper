# Suspend Diagnosis Report

**Collection Directory**: `C:\Users\xingya\OneDrive - Qualcomm\Desktop\AI_tools\suspend_mvp\cases\suspend\blocked_bywakelock`  
**Time**: 2025-11-23T18:01:54.929086

---

## 🔴 CONCLUSION: Suspend Failure Detected

**Root Cause**: Root cause: Active wakelocks preventing suspend: PowerManagerService.Display, PowerManager.SuspendLockout, a600000.hsusb

---

## Step 2️⃣: Wakelock Analysis
**Purpose**: Check for active wakelocks preventing suspend  
**File**: `dumpsys suspend_control_internal` → `dumpsys_suspend.txt`

❌ **Result**: Active wakelocks found (ROOT CAUSE)
**Active Wakelocks**:
- `PowerManagerService.Display`
- `PowerManager.SuspendLockout`
- `a600000.hsusb`

**Analysis stops here** - Root cause identified

### 原始 Wakelock Dump (关键片段)
```text
 |                                                                                           WAKELOCK STATS                                                                                        | 
 | NAME                           | PID    | TYPE   | STATUS   | ACTIVE COUNT | TOTAL TIME   | MAX TIME     | EVENT COUNT  | WAKEUP COUNT | EXPIRE COUNT | PREVENT SUSPEND TIME | LAST CHANGE      | 
 | PowerManagerService.WakeLocks  |   1922 | Native | Inactive |            0 |      13204ms |       6497ms |          --- |          --- |          --- |                  --- |        1091401ms | 
 | PowerManagerService.Broadcasts |   1922 | Native | Inactive |            0 |        168ms |        141ms |          --- |          --- |          --- |                  --- |         810554ms | 
 | PowerManagerService.Display    |   1922 | Native | Active   |            1 |     941874ms |     653247ms |          --- |          --- |          --- |                  --- |        1099043ms | 
 | PowerManager.SuspendLockout    |   1922 | Native | Active   |            1 |     941839ms |     653211ms |          --- |          --- |          --- |                  --- |        1099043ms | 
 | radio-interface                |   1263 | Native | Inactive |            0 |        227ms |        217ms |          --- |          --- |          --- |                  --- |         140169ms | 
 | ApmOutput                      |   2453 | Native | Inactive |            0 |       1023ms |         44ms |          --- |          --- |          --- |                  --- |         137884ms | 
 | PowerManagerService.Booting    |   1922 | Native | Inactive |            0 |      52860ms |      52860ms |          --- |          --- |          --- |                  --- |         137126ms | 
 | qms_event_Handler_wakeLock_    |   1413 | Native | Inactive |            0 |        607ms |        445ms |          --- |          --- |          --- |                  --- |         124920ms | 
 | ApmAudio                       |   2453 | Native | Inactive |            0 |        498ms |         88ms |          --- |          --- |          --- |                  --- |         102870ms | 
 | ApmOutput                      |   1209 | Native | Inactive |            0 |         10ms |          4ms |          --- |          --- |          --- |                  --- |          89723ms | 
 | ApmAudio                       |   1209 | Native | Inactive |            0 |        222ms |         71ms |          --- |          --- |          --- |                  --- |          89717ms | 
 | qcril_pre_client_init          |   1263 | Native | Inactive |            0 |       1388ms |       1388ms |          --- |          --- |          --- |                  --- |          78474ms | 
 | event3                         |    --- | Kernel | Inactive |            4 |          3ms |          1ms |            4 |            0 |            0 |                  0ms |         810533ms | 
 | [timerfd]                      |    --- | Kernel | Inactive |            0 |          0ms |          0ms |            0 |            0 |            0 |                  0ms |              0ms | 
 | c42d000.qcom,spmi:pmw6100@0:pon_hlos@1300:pwrkey |    --- | Kernel | Inactive |            0 |          0ms |          0ms |            0 |            0 |            0 |                  0ms |              0ms | 
 | usb                            |    --- | Kernel | Inactive |            2 |        144ms |         98ms |            2 |            0 |            0 |                  0ms |          78847ms | 
 | fastrpc-non_secure             |    --- | Kernel | Inactive |            0 |          0ms |          0ms |            0 |            0 |            0 |                  0ms |              0ms | 
 | rmt_storage_541074766912       |    --- | Kernel | Inactive |            2 |         78ms |         75ms |            2 |            0 |            0 |                  0ms |         167621ms | 
... (truncated)
```

---

## 📋 总结
**结论**: Root cause: Active wakelocks preventing suspend: PowerManagerService.Display, PowerManager.SuspendLockout, a600000.hsusb

---

## 🤖 AI Comprehensive Analysis

## Suspend Status
- **Suspend attempts:** 0  
- **Successful suspends:** 0  
- **Failed suspends:** 0  

The `/d/suspend_stats` file is empty, and the `dumpsys suspend_control_internal` dump shows **no suspend attempts** have been made. This means the system has never entered a suspend cycle since the logs were captured.

## Wakelock Analysis
| Name | PID | Type | Status | Active Count |
|------|-----|------|--------|--------------|
| **PowerManagerService.Display** | 1922 | Native | **Active** | 1 |
| **PowerManager.SuspendLockout** | 1922 | Native | **Active** | 1 |
| **a600000.hsusb** | – | Kernel | **Active** | 1 |

- The **Display** wakelock is held, indicating the screen (or a component that pretends the screen is on) is preventing suspend.  
- The **SuspendLockout** wakelock is also active; this is a system‑level lock that deliberately blocks suspend (often set while a critical operation is in progress).  
- A kernel‑level USB wakelock (`a600000.hsusb`) is active, meaning the USB controller is preventing the device from sleeping.

No other wakelocks are currently active, and the `last_failed_suspend` counter is **0**, confirming that suspend is not failing because of an error – it is simply being blocked by the above wake locks.

## Root Cause (if applicable)
*Not applicable.* Suspend has not failed; it has never been attempted because active wake locks are blocking it.

## Recommendations
1. **Identify why the Display wakelock is held**
   - Verify that the screen is actually on. If the device is in a “screen‑on” state (e.g., a foreground app has requested `FLAG_KEEP_SCREEN_ON`), the wake lock will stay active.
   - Use `adb shell dumpsys activity top` or `adb shell dumpsys window windows` to see which activity is keeping the screen awake.
   - If an app is misbehaving, force‑stop it (`adb shell am force-stop <package>`) or uninstall the offending app.

2. **Investigate the SuspendLockout wakelock**
   - This lock is usually set by the framework during operations such as OTA updates, battery‑saving mode changes, or when a critical system service is initializing.
   - Check recent logs (`adb logcat -b events | grep -i suspendlockout`) for messages that set or clear this lock.
   - If the lock persists after the operation should be finished, a system bug may be present; a reboot often clears it.

3. **Address the active USB wakelock (`a600000.hsusb`)**
   - The USB controller may be held by a connected peripheral (e.g., OTG device, debugging session, or a stuck driver).
   - Run `adb shell dumpsys usb` to see the current USB state. Detach any USB accessories, disable USB debugging, or power‑cycle the device.
   - If the wakelock remains, consider disabling the USB driver temporarily for testing:
     ```
     echo disable > /sys/bus/platform/drivers/usb/uevent
     ```
     (use with caution; re‑enable after testing).

4. **Force a suspend cycle after clearing wakelocks**
   - Once the above locks are cleared, you can manually trigger suspend to verify the path:
     ```
     adb shell dumpsys power suspend now
     ```
   - Or use `adb shell echo mem > /sys/power/state` (requires root).

5. **Long‑term mitigation**
   - **App hygiene:** Encourage developers to release wake locks promptly (`PowerManager.WakeLock.release()`), especially display and partial wake locks.
   - **System updates:** Ensure the device runs the latest security/patch level; many suspend‑related bugs are fixed in newer kernel/PMU releases.
   - **Monitoring:** Set up a periodic script to log wake‑lock status; if a lock remains active for > 5 minutes, automatically dump stack traces for investigation.

By clearing the active **Display**, **SuspendLockout**, and **USB** wake locks, the device will be able to enter suspend normally, and subsequent suspend attempts will be recorded in `/d/suspend_stats`.

---

## 📁 Evidence Files

- **dumpsys_suspend.txt**: `C:\Users\xingya\OneDrive - Qualcomm\Desktop\AI_tools\suspend_mvp\cases\suspend\blocked_bywakelock\dumpsys_suspend.txt`

---

## ✅ Verification Checklist

After fixing the identified issue:

1. **Re-run diagnosis**: Collect new evidence and verify the issue is resolved
2. **Check suspend_stats**: Verify success count increases and fail count remains 0
3. **Check wakelocks**: Ensure no active wakelocks in dumpsys output
4. **Measure power**: Compare power consumption before/after fix (expect ≥3% reduction)
