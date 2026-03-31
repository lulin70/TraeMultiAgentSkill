#!/bin/bash
# Trae Multi-Agent Skill 包装脚本
# 用于从任何项目目录调用 skill

# 获取脚本所在目录（skill 的 scripts 目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 设置技能目录
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 输出调试信息（可选）
# echo "Script dir: $SCRIPT_DIR"
# echo "Skill dir: $SKILL_DIR"

# 执行 Python 脚本，将 skill 目录添加到 Python 路径
exec python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from trae_agent_dispatch import main
sys.exit(main())
" "$@"
