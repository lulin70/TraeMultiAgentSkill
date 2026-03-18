#!/bin/bash
# Trae Multi-Agent Skill 调用包装脚本
# 
# 使用方法：
# 1. 将此脚本复制到你的项目根目录
# 2. 修改 SKILL_DIR 为你的 skill 实际路径
# 3. 运行：./trae_agent_dispatch.sh --task "你的任务" --agent auto

# 配置：修改为你的 skill 实际路径
SKILL_DIR="$HOME/.trae/skills/trae-multi-agent"

# 检查 skill 目录是否存在
if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 错误：找不到 skill 目录：$SKILL_DIR"
    echo ""
    echo "请编辑此脚本，将 SKILL_DIR 修改为你的 skill 实际路径"
    echo "默认路径：$HOME/.trae/skills/trae-multi-agent"
    exit 1
fi

# 执行 skill 脚本
exec python3 "$SKILL_DIR/scripts/trae_agent_dispatch.py" "$@"
