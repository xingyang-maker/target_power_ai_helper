#!/bin/bash

# Android Suspend 日志收集脚本
# 使用方法: ./collect_logs.sh [输出目录]

set -e

# 默认输出目录
OUTPUT_DIR="${1:-./collected_logs}"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "🔍 Android Suspend 日志收集工具"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 检查ADB连接
echo "📱 检查设备连接..."
if ! adb devices | grep -q "device$"; then
    echo "❌ 错误: 未找到连接的Android设备"
    echo "请确保:"
    echo "  1. 设备已通过USB连接"
    echo "  2. 已开启USB调试"
    echo "  3. 已授权调试连接"
    exit 1
fi

DEVICE_MODEL=$(adb shell getprop ro.product.model 2>/dev/null || echo "Unknown")
echo "✅ 设备已连接: $DEVICE_MODEL"
echo ""

# 收集设备信息
echo "📋 收集设备信息..."
{
    echo "Collection Time: $(date)"
    echo "Device Model: $(adb shell getprop ro.product.model 2>/dev/null || echo 'Unknown')"
    echo "Android Version: $(adb shell getprop ro.build.version.release 2>/dev/null || echo 'Unknown')"
    echo "Kernel Version: $(adb shell uname -r 2>/dev/null || echo 'Unknown')"
    echo "Battery Level: $(adb shell dumpsys battery 2>/dev/null | grep level || echo 'Unknown')"
    echo "ADB User: $(adb shell whoami 2>/dev/null || echo 'Unknown')"
} > "$OUTPUT_DIR/collection_info.txt"

# 1. 收集 suspend_stats
echo "📊 收集 suspend 统计信息..."
if adb shell "test -r /d/suspend_stats" 2>/dev/null; then
    adb shell cat /d/suspend_stats > "$OUTPUT_DIR/suspend_stats.txt" 2>/dev/null || {
        echo "⚠️  无法读取 /d/suspend_stats，尝试替代路径..."
        adb shell cat /sys/kernel/debug/suspend_stats > "$OUTPUT_DIR/suspend_stats.txt" 2>/dev/null || {
            echo "❌ 无法访问 suspend_stats，可能需要root权限"
            touch "$OUTPUT_DIR/suspend_stats.txt"
        }
    }
else
    echo "⚠️  /d/suspend_stats 不存在或无权限访问"
    touch "$OUTPUT_DIR/suspend_stats.txt"
fi

# 检查文件内容
if [ -s "$OUTPUT_DIR/suspend_stats.txt" ]; then
    echo "✅ suspend_stats.txt 收集成功 ($(wc -l < "$OUTPUT_DIR/suspend_stats.txt") 行)"
else
    echo "⚠️  suspend_stats.txt 为空"
fi

# 2. 收集 dumpsys suspend
echo "🔒 收集 wakelock 信息..."
if adb shell dumpsys suspend_control_internal > "$OUTPUT_DIR/dumpsys_suspend.txt" 2>/dev/null; then
    if [ -s "$OUTPUT_DIR/dumpsys_suspend.txt" ]; then
        echo "✅ dumpsys_suspend.txt 收集成功 ($(wc -l < "$OUTPUT_DIR/dumpsys_suspend.txt") 行)"
    else
        echo "⚠️  dumpsys_suspend.txt 为空，尝试其他dumpsys服务..."
        adb shell dumpsys power > "$OUTPUT_DIR/dumpsys_power.txt" 2>/dev/null || true
    fi
else
    echo "❌ 无法执行 dumpsys suspend_control_internal"
    touch "$OUTPUT_DIR/dumpsys_suspend.txt"
fi

# 3. 收集 dmesg
echo "🖥️  收集内核日志..."
if adb shell "dmesg -T" > "$OUTPUT_DIR/dmesg.txt" 2>/dev/null; then
    if [ -s "$OUTPUT_DIR/dmesg.txt" ]; then
        echo "✅ dmesg.txt 收集成功 ($(wc -l < "$OUTPUT_DIR/dmesg.txt") 行)"
    else
        echo "⚠️  dmesg -T 输出为空，尝试不带时间戳..."
        adb shell dmesg > "$OUTPUT_DIR/dmesg.txt" 2>/dev/null || {
            echo "❌ 无法获取dmesg，可能需要更高权限"
            touch "$OUTPUT_DIR/dmesg.txt"
        }
    fi
else
    echo "⚠️  dmesg -T 失败，尝试标准dmesg..."
    adb shell dmesg > "$OUTPUT_DIR/dmesg.txt" 2>/dev/null || {
        echo "❌ 无法获取dmesg"
        touch "$OUTPUT_DIR/dmesg.txt"
    }
fi

# 收集额外的有用信息
echo "📱 收集额外信息..."

# 电源管理相关
adb shell "cat /sys/power/state" > "$OUTPUT_DIR/power_state.txt" 2>/dev/null || touch "$OUTPUT_DIR/power_state.txt"
adb shell "cat /sys/power/mem_sleep" > "$OUTPUT_DIR/mem_sleep.txt" 2>/dev/null || touch "$OUTPUT_DIR/mem_sleep.txt"

# Wakeup sources
adb shell "cat /sys/kernel/debug/wakeup_sources" > "$OUTPUT_DIR/wakeup_sources.txt" 2>/dev/null || touch "$OUTPUT_DIR/wakeup_sources.txt"

echo ""
echo "📁 收集完成! 文件保存在: $OUTPUT_DIR"
echo ""
echo "📋 收集的文件:"
ls -la "$OUTPUT_DIR"

echo ""
echo "🔍 文件内容检查:"
for file in suspend_stats.txt dumpsys_suspend.txt dmesg.txt; do
    if [ -s "$OUTPUT_DIR/$file" ]; then
        lines=$(wc -l < "$OUTPUT_DIR/$file")
        echo "  ✅ $file: $lines 行"
    else
        echo "  ❌ $file: 空文件"
    fi
done

echo ""
echo "🚀 使用收集的日志进行分析:"
echo "  python bin/suspend_diagnosis --case-dir $OUTPUT_DIR"
echo ""
echo "📖 详细的日志收集指南请参考: LOG_COLLECTION_GUIDE.md"
