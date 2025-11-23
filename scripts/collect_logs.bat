@echo off
setlocal enabledelayedexpansion

REM Android Suspend 日志收集脚本 (Windows版本)
REM 使用方法: collect_logs.bat [输出目录]

echo 🔍 Android Suspend 日志收集工具
echo.

REM 设置默认输出目录
if "%1"=="" (
    set "OUTPUT_DIR=collected_logs"
) else (
    set "OUTPUT_DIR=%1"
)

echo 输出目录: %OUTPUT_DIR%
echo.

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM 检查ADB是否可用
echo 📱 检查ADB和设备连接...
adb version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: ADB未找到或未安装
    echo 请确保ADB已安装并添加到PATH环境变量中
    pause
    exit /b 1
)

REM 检查设备连接
adb devices | findstr "device" >nul
if errorlevel 1 (
    echo ❌ 错误: 未找到连接的Android设备
    echo 请确保:
    echo   1. 设备已通过USB连接
    echo   2. 已开启USB调试
    echo   3. 已授权调试连接
    echo.
    adb devices
    pause
    exit /b 1
)

REM 获取设备信息
for /f "tokens=*" %%i in ('adb shell getprop ro.product.model 2^>nul') do set "DEVICE_MODEL=%%i"
if "!DEVICE_MODEL!"=="" set "DEVICE_MODEL=Unknown"
echo ✅ 设备已连接: !DEVICE_MODEL!
echo.

REM 收集设备信息
echo 📋 收集设备信息...
(
    echo Collection Time: %date% %time%
    for /f "tokens=*" %%i in ('adb shell getprop ro.product.model 2^>nul') do echo Device Model: %%i
    for /f "tokens=*" %%i in ('adb shell getprop ro.build.version.release 2^>nul') do echo Android Version: %%i
    for /f "tokens=*" %%i in ('adb shell uname -r 2^>nul') do echo Kernel Version: %%i
    for /f "tokens=*" %%i in ('adb shell dumpsys battery 2^>nul ^| findstr level') do echo Battery Level: %%i
    for /f "tokens=*" %%i in ('adb shell whoami 2^>nul') do echo ADB User: %%i
) > "%OUTPUT_DIR%\collection_info.txt"

REM 1. 收集 suspend_stats
echo 📊 收集 suspend 统计信息...
adb shell "test -r /d/suspend_stats" >nul 2>&1
if not errorlevel 1 (
    adb shell cat /d/suspend_stats > "%OUTPUT_DIR%\suspend_stats.txt" 2>nul
    if errorlevel 1 (
        echo ⚠️  无法读取 /d/suspend_stats，尝试替代路径...
        adb shell cat /sys/kernel/debug/suspend_stats > "%OUTPUT_DIR%\suspend_stats.txt" 2>nul
        if errorlevel 1 (
            echo ❌ 无法访问 suspend_stats，可能需要root权限
            type nul > "%OUTPUT_DIR%\suspend_stats.txt"
        )
    )
) else (
    echo ⚠️  /d/suspend_stats 不存在或无权限访问
    type nul > "%OUTPUT_DIR%\suspend_stats.txt"
)

REM 检查文件内容
for %%F in ("%OUTPUT_DIR%\suspend_stats.txt") do (
    if %%~zF gtr 0 (
        for /f %%A in ('type "%OUTPUT_DIR%\suspend_stats.txt" ^| find /c /v ""') do echo ✅ suspend_stats.txt 收集成功 ^(%%A 行^)
    ) else (
        echo ⚠️  suspend_stats.txt 为空
    )
)

REM 2. 收集 dumpsys suspend
echo 🔒 收集 wakelock 信息...
adb shell dumpsys suspend_control_internal > "%OUTPUT_DIR%\dumpsys_suspend.txt" 2>nul
if not errorlevel 1 (
    for %%F in ("%OUTPUT_DIR%\dumpsys_suspend.txt") do (
        if %%~zF gtr 0 (
            for /f %%A in ('type "%OUTPUT_DIR%\dumpsys_suspend.txt" ^| find /c /v ""') do echo ✅ dumpsys_suspend.txt 收集成功 ^(%%A 行^)
        ) else (
            echo ⚠️  dumpsys_suspend.txt 为空，尝试其他dumpsys服务...
            adb shell dumpsys power > "%OUTPUT_DIR%\dumpsys_power.txt" 2>nul
        )
    )
) else (
    echo ❌ 无法执行 dumpsys suspend_control_internal
    type nul > "%OUTPUT_DIR%\dumpsys_suspend.txt"
)

REM 3. 收集 dmesg
echo 🖥️  收集内核日志...
adb shell "dmesg -T" > "%OUTPUT_DIR%\dmesg.txt" 2>nul
if not errorlevel 1 (
    for %%F in ("%OUTPUT_DIR%\dmesg.txt") do (
        if %%~zF gtr 0 (
            for /f %%A in ('type "%OUTPUT_DIR%\dmesg.txt" ^| find /c /v ""') do echo ✅ dmesg.txt 收集成功 ^(%%A 行^)
        ) else (
            echo ⚠️  dmesg -T 输出为空，尝试不带时间戳...
            adb shell dmesg > "%OUTPUT_DIR%\dmesg.txt" 2>nul
            if errorlevel 1 (
                echo ❌ 无法获取dmesg，可能需要更高权限
                type nul > "%OUTPUT_DIR%\dmesg.txt"
            )
        )
    )
) else (
    echo ⚠️  dmesg -T 失败，尝试标准dmesg...
    adb shell dmesg > "%OUTPUT_DIR%\dmesg.txt" 2>nul
    if errorlevel 1 (
        echo ❌ 无法获取dmesg
        type nul > "%OUTPUT_DIR%\dmesg.txt"
    )
)

REM 收集额外的有用信息
echo 📱 收集额外信息...

REM 电源管理相关
adb shell "cat /sys/power/state" > "%OUTPUT_DIR%\power_state.txt" 2>nul || type nul > "%OUTPUT_DIR%\power_state.txt"
adb shell "cat /sys/power/mem_sleep" > "%OUTPUT_DIR%\mem_sleep.txt" 2>nul || type nul > "%OUTPUT_DIR%\mem_sleep.txt"

REM Wakeup sources
adb shell "cat /sys/kernel/debug/wakeup_sources" > "%OUTPUT_DIR%\wakeup_sources.txt" 2>nul || type nul > "%OUTPUT_DIR%\wakeup_sources.txt"

echo.
echo 📁 收集完成! 文件保存在: %OUTPUT_DIR%
echo.
echo 📋 收集的文件:
dir /b "%OUTPUT_DIR%"

echo.
echo 🔍 文件内容检查:
for %%f in (suspend_stats.txt dumpsys_suspend.txt dmesg.txt) do (
    for %%F in ("%OUTPUT_DIR%\%%f") do (
        if %%~zF gtr 0 (
            for /f %%A in ('type "%OUTPUT_DIR%\%%f" ^| find /c /v ""') do echo   ✅ %%f: %%A 行
        ) else (
            echo   ❌ %%f: 空文件
        )
    )
)

echo.
echo 🚀 使用收集的日志进行分析:
echo   python bin/suspend_diagnosis --case-dir %OUTPUT_DIR%
echo.
echo 📖 详细的日志收集指南请参考: LOG_COLLECTION_GUIDE.md
echo.
pause
