# Android Suspend 日志收集规范

本文档详细说明如何正确收集Android设备suspend诊断所需的日志文件。

## 概述

Suspend诊断工具需要三个关键的日志文件来进行系统性的3步分析：

1. **suspend_stats.txt** - Suspend统计信息 (来自 `/d/suspend_stats`)
2. **dumpsys_suspend.txt** - Suspend控制内部状态 (来自 `dumpsys suspend_control_internal`)
3. **dmesg.txt** - 内核消息日志 (来自 `dmesg`)

## 前置条件

### 设备要求
- Android设备已开启USB调试
- 设备已通过USB连接到电脑
- ADB工具已安装并可用

### 权限要求
- Root权限 (用于访问 `/d/suspend_stats`)
- 或者具有系统级权限的shell访问

### 验证连接
```bash
# 检查设备连接
adb devices

# 检查shell权限
adb shell whoami
```

## 日志收集步骤

### 方法一：使用诊断工具自动收集 (推荐)

```bash
# 自动收集所有必需的日志
python bin/suspend_diagnosis

# 或指定特定设备
python bin/suspend_diagnosis --device DEVICE_SERIAL
```

### 方法二：使用快速收集脚本

我们提供了便捷的脚本来快速收集日志：

**Linux/macOS:**
```bash
# 使用默认目录 (collected_logs)
./scripts/collect_logs.sh

# 指定输出目录
./scripts/collect_logs.sh my_logs
```

**Windows:**
```cmd
# 使用默认目录 (collected_logs)
scripts\collect_logs.bat

# 指定输出目录
scripts\collect_logs.bat my_logs
```

这些脚本会：
- 自动检查设备连接和ADB可用性
- 收集所有必需的日志文件
- 提供详细的收集状态反馈
- 验证收集的文件质量
- 收集额外的有用信息

### 方法二：手动收集日志

如果需要手动收集日志，请按以下步骤操作：

#### 1. 收集 Suspend 统计信息

```bash
# 方法1: 直接读取 (需要root权限)
adb shell "su -c 'cat /d/suspend_stats'" > suspend_stats.txt

# 方法2: 如果没有root权限，尝试以下命令
adb shell cat /d/suspend_stats > suspend_stats.txt

# 方法3: 如果上述都不行，尝试
adb shell "cat /sys/kernel/debug/suspend_stats" > suspend_stats.txt
```

**预期内容示例：**
```
success_count: 1234
fail_count: 5
failed_suspend: 2
failed_resume: 3
last_failed_dev: some_device
last_failed_errno: -16
last_failed_step: suspend_enter
```

#### 2. 收集 Wakelock 信息

```bash
# 收集suspend控制内部状态
adb shell dumpsys suspend_control_internal > dumpsys_suspend.txt
```

**预期内容示例：**
```
Suspend Control Internal State:
Active wakelocks:
  AudioOut: Active
  WifiLock: Inactive
  Location: Inactive

Last failed suspend: 0
Suspend blocked by: none
```

#### 3. 收集内核日志

```bash
# 方法1: 收集带时间戳的dmesg (推荐)
adb shell "dmesg -T" > dmesg.txt

# 方法2: 如果不支持-T参数
adb shell dmesg > dmesg.txt

# 方法3: 收集最近的内核日志
adb shell "dmesg | tail -n 500" > dmesg.txt
```

**预期内容示例：**
```
[2023-11-23 17:30:15] PM: suspend entry (deep)
[2023-11-23 17:30:15] Suspending console(s) (use no_console_suspend to debug)
[2023-11-23 17:30:16] PM: suspend of devices complete after 1234.567 msecs
[2023-11-23 17:30:16] PM: suspend exit
```

## 日志质量检查

### 检查文件完整性

收集完成后，请验证每个文件的内容：

```bash
# 检查文件大小 (不应为空)
ls -la suspend_stats.txt dumpsys_suspend.txt dmesg.txt

# 检查文件内容
head -10 suspend_stats.txt
head -10 dumpsys_suspend.txt  
head -10 dmesg.txt
```

### 关键内容验证

#### suspend_stats.txt 应包含：
- `success_count:` 行
- `fail_count:` 行
- 如果有失败，应包含 `failed_suspend:`, `failed_resume:` 等

#### dumpsys_suspend.txt 应包含：
- "Suspend Control" 相关信息
- Wakelock 状态信息
- 如果有活跃的wakelock，应该能看到 "Active" 状态

#### dmesg.txt 应包含：
- 内核时间戳或序号
- 如果设备尝试过suspend，应包含 "PM: suspend" 相关消息

## 常见问题和解决方案

### 问题1: 权限不足无法访问 /d/suspend_stats

**症状：** `Permission denied` 错误

**解决方案：**
```bash
# 尝试获取root权限
adb root
adb shell cat /d/suspend_stats > suspend_stats.txt

# 或者尝试替代路径
adb shell cat /sys/kernel/debug/suspend_stats > suspend_stats.txt
```

### 问题2: dumpsys 命令不存在或无输出

**症状：** `dumpsys: command not found` 或空输出

**解决方案：**
```bash
# 检查dumpsys是否可用
adb shell dumpsys -l | grep suspend

# 尝试其他相关的dumpsys服务
adb shell dumpsys power > power_dump.txt
adb shell dumpsys batterystats > battery_stats.txt
```

### 问题3: dmesg 输出为空或权限不足

**症状：** 空文件或 `Permission denied`

**解决方案：**
```bash
# 尝试不同的dmesg选项
adb shell "dmesg -w" > dmesg.txt  # 实时监控
adb shell "cat /proc/kmsg" > kmsg.txt  # 替代方案

# 或者使用logcat获取内核日志
adb logcat -b kernel > kernel_log.txt
```

### 问题4: 文件为空或内容不完整

**可能原因：**
- 设备从未尝试suspend
- 日志缓冲区已被清空
- 权限限制

**解决方案：**
1. 手动触发suspend测试：
   ```bash
   # 按电源键让设备进入suspend
   adb shell input keyevent KEYCODE_POWER
   
   # 等待几秒后唤醒
   adb shell input keyevent KEYCODE_POWER
   
   # 重新收集日志
   ```

2. 增加日志详细程度：
   ```bash
   # 启用更详细的suspend日志
   adb shell "echo 1 > /sys/power/pm_debug_messages"
   ```

## 最佳实践

### 收集时机
1. **问题复现后立即收集** - 确保日志包含相关的错误信息
2. **设备空闲时收集** - 避免其他应用干扰suspend过程
3. **多次收集对比** - 收集正常和异常情况下的日志进行对比

### 文件组织
```
case_directory/
├── dmesg.txt              # 内核日志
├── dumpsys_suspend.txt    # Wakelock信息  
├── suspend_stats.txt      # Suspend统计
├── collection_info.txt    # 收集时间和环境信息
└── device_info.txt        # 设备信息
```

### 环境信息记录
创建 `collection_info.txt` 记录收集环境：
```bash
echo "Collection Time: $(date)" > collection_info.txt
echo "Device Model: $(adb shell getprop ro.product.model)" >> collection_info.txt
echo "Android Version: $(adb shell getprop ro.build.version.release)" >> collection_info.txt
echo "Kernel Version: $(adb shell uname -r)" >> collection_info.txt
echo "Battery Level: $(adb shell dumpsys battery | grep level)" >> collection_info.txt
```

## 使用收集的日志

收集完成后，使用以下命令进行分析：

```bash
# 分析收集的日志
python bin/suspend_diagnosis --case-dir /path/to/collected/logs

# 示例
python bin/suspend_diagnosis --case-dir ./my_case_logs
```

## 故障排除检查清单

在提交日志进行分析前，请确认：

- [ ] 所有三个核心文件都已收集 (suspend_stats.txt, dumpsys_suspend.txt, dmesg.txt)
- [ ] 文件不为空且包含预期的内容格式
- [ ] 日志收集时间在问题发生后的合理时间窗口内
- [ ] 设备信息和收集环境已记录
- [ ] 如果可能，已收集问题复现前后的对比日志

遵循此规范可以确保收集到高质量的日志，提高suspend问题诊断的准确性和效率。
