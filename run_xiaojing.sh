#!/bin/bash

# 定义日志目录
LOG_DIR="/home/cloudwolf/wlk/log"

# 创建日志目录（如果不存在）
mkdir -p "$LOG_DIR"

# 生成时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 进入目标目录
cd /home/cloudwolf/wlk || exit 1

# 激活Python虚拟环境
source wlk/bin/activate

# 执行第一个Python脚本并保存输出
echo "开始执行 xiaojing_901.py..."
python3 xiaojing_901.py > "$LOG_DIR/xiaojing_901_$TIMESTAMP.log" 2>&1
echo "xiaojing_901.py 执行完成，日志保存在: $LOG_DIR/xiaojing_901_$TIMESTAMP.log"

# 执行第二个Python脚本并保存输出
echo "开始执行 xiaojing_902.py..."
python3 xiaojing_902.py > "$LOG_DIR/xiaojing_902_$TIMESTAMP.log" 2>&1
echo "xiaojing_902.py 执行完成，日志保存在: $LOG_DIR/xiaojing_902_$TIMESTAMP.log"

# 可选：停用虚拟环境
deactivate

echo "所有任务执行完成！"
