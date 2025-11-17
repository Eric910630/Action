#!/bin/bash
# 监控小红书热点抓取日志

echo "=== 监控小红书热点抓取日志 ==="
echo "按 Ctrl+C 退出"
echo ""

tail -f logs/celery-worker.log | grep --line-buffered -E "xiaohongshu|小红书|xhs|平台.*抓取|抓取失败|总共抓取" | while read line; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $line"
done
