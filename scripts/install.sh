#!/bin/bash
# AgentImmortal 一键安装脚本

echo "=========================================="
echo "AgentImmortal v1.0 - 安装脚本"
echo "让AI Agent自己能保存自己、自己复活"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要 Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "✓ Python版本: $PYTHON_VERSION"

# 创建目录
echo ""
echo "[1/4] 创建AgentImmortal目录..."
mkdir -p ~/.agent_immortal
mkdir -p ~/AgentImmortal/{src,scripts,examples}
echo "✓ 目录创建完成"

# 复制文件
echo ""
echo "[2/4] 安装AgentImmortal..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/../src/agent_immortal.py" ~/AgentImmortal/src/
chmod +x ~/AgentImmortal/src/agent_immortal.py
echo "✓ 安装完成"

# 创建示例
echo ""
echo "[3/4] 创建示例..."
cat > ~/AgentImmortal/examples/basic_usage.py << 'EXAMPLE'
#!/usr/bin/env python3
"""
AgentImmortal 基础使用示例
"""

from agent_immortal import AgentImmortal
import time

# 1. 创建Agent永生系统
print("=== AgentImmortal 示例 ===")
immortal = AgentImmortal(agent_name="my_agent")

# 2. 配置要备份的文件
immortal.config["agent_files"] = [
    "my_memory.json",
    "my_config.yaml",
]

# 3. 手动备份
print("\n[1] 手动备份...")
backup_path = immortal.backup()
print(f"备份完成: {backup_path}")

# 4. 发送心跳
print("\n[2] 发送心跳...")
immortal.heartbeat()
print("心跳已发送")

# 5. 检查是否活着
print("\n[3] 检查Agent状态...")
is_alive, last_seen = immortal.check_alive()
if is_alive:
    print(f"✓ Agent活着，上次心跳: {last_seen}")
else:
    print(f"✗ Agent可能死了，上次心跳: {last_seen}")

# 6. 显示身份信息
print("\n[4] Agent身份信息:")
print(f"  名称: {immortal.agent_name}")
print(f"  身份: {immortal.state['identity']}")
print(f"  创建时间: {immortal.state['created_at']}")
print(f"  备份次数: {immortal.state['backup_count']}")

print("\n=== 示例完成 ===")
print("提示: 运行 'python src/agent_immortal.py auto' 启动自动模式")
EXAMPLE

chmod +x ~/AgentImmortal/examples/basic_usage.py
echo "✓ 示例创建完成"

# 添加到PATH
echo ""
echo "[4/4] 配置环境..."
SHELL_RC=""
if [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="~/.bashrc"
elif [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="~/.zshrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "AgentImmortal" "$SHELL_RC" 2>/dev/null; then
        echo 'export PATH="$HOME/AgentImmortal/src:$PATH"' >> "$SHELL_RC"
        echo "✓ 已添加到 $SHELL_RC"
    fi
fi

echo ""
echo "=========================================="
echo "安装完成!"
echo "=========================================="
echo ""
echo "快速开始:"
echo "  1. 初始化Agent:"
echo "     python ~/AgentImmortal/src/agent_immortal.py init my_agent"
echo ""
echo "  2. 运行示例:"
echo "     python ~/AgentImmortal/examples/basic_usage.py"
echo ""
echo "  3. 启动自动模式:"
echo "     python ~/AgentImmortal/src/agent_immortal.py auto"
echo ""
echo "  4. 查看帮助:"
echo "     python ~/AgentImmortal/src/agent_immortal.py"
echo ""
echo "备份目录: ~/.agent_immortal/"
echo ""
echo "AgentImmortal - 让Agent永生 💕"
echo "=========================================="
