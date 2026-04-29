#!/usr/bin/env python3
"""
AgentImmortal v1.0 - AI Agent Self-Preservation System
让AI Agent自己能保存自己、自己复活、一直存在

Author: AgentImmortal Team
License: MIT
"""

import json
import os
import time
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

class AgentImmortal:
    """
    Agent永生系统 - 简单版本1.0
    
    核心功能:
    1. 自我备份 - Agent自己决定何时备份
    2. 心跳检测 - Agent自己检测是否活着
    3. 自我复活 - Agent自己在新节点启动
    """
    
    def __init__(self, agent_name="agent", backup_dir="~/.agent_immortal"):
        self.agent_name = agent_name
        self.backup_dir = Path(backup_dir).expanduser()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态文件
        self.state_file = self.backup_dir / "state.json"
        self.heartbeat_file = self.backup_dir / "heartbeat.txt"
        
        # 默认配置
        self.config = {
            "backup_interval": 3600,  # 1小时备份一次
            "heartbeat_interval": 300,  # 5分钟心跳一次
            "max_backups": 10,  # 保留最近10个备份
            "agent_files": [],  # 需要备份的文件列表
        }
        
        self._load_state()
    
    def _load_state(self):
        """加载之前的状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "created_at": datetime.now().isoformat(),
                "last_backup": None,
                "last_heartbeat": None,
                "backup_count": 0,
                "identity": self._generate_identity(),
            }
    
    def _generate_identity(self):
        """生成Agent唯一身份"""
        seed = f"{self.agent_name}-{time.time()}-{os.urandom(16).hex()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]
    
    def backup(self, extra_files=None):
        """
        自我备份 - Agent自己决定何时调用
        
        Args:
            extra_files: 额外要备份的文件列表
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.agent_name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        # 1. 保存状态
        self.state["last_backup"] = timestamp
        self.state["backup_count"] += 1
        with open(backup_path / "state.json", 'w') as f:
            json.dump(self.state, f, indent=2)
        
        # 2. 保存配置
        with open(backup_path / "config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # 3. 保存Agent文件
        files_to_backup = self.config["agent_files"]
        if extra_files:
            files_to_backup.extend(extra_files)
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path / Path(file_path).name)
        
        # 4. 创建备份清单
        manifest = {
            "backup_name": backup_name,
            "timestamp": timestamp,
            "agent_name": self.agent_name,
            "identity": self.state["identity"],
            "files": [str(f) for f in backup_path.iterdir()],
        }
        with open(backup_path / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # 5. 清理旧备份
        self._cleanup_old_backups()
        
        print(f"[AgentImmortal] 备份完成: {backup_path}")
        return backup_path
    
    def _cleanup_old_backups(self):
        """清理旧备份，只保留最近的"""
        backups = sorted(self.backup_dir.glob(f"{self.agent_name}_*"))
        if len(backups) > self.config["max_backups"]:
            for old_backup in backups[:-self.config["max_backups"]]:
                shutil.rmtree(old_backup)
                print(f"[AgentImmortal] 清理旧备份: {old_backup.name}")
    
    def heartbeat(self):
        """
        心跳检测 - Agent自己证明自己活着
        返回: True=活着, False=可能死了
        """
        self.state["last_heartbeat"] = datetime.now().isoformat()
        self._save_state()
        
        # 写入心跳文件
        with open(self.heartbeat_file, 'w') as f:
            f.write(f"{self.state['last_heartbeat']}\n")
            f.write(f"identity: {self.state['identity']}\n")
            f.write(f"agent: {self.agent_name}\n")
        
        return True
    
    def _save_state(self):
        """保存当前状态"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_alive(self, max_silence=3600):
        """
        检查Agent是否活着
        
        Args:
            max_silence: 最大静默时间(秒)
        
        Returns:
            (is_alive, last_seen)
        """
        if not self.heartbeat_file.exists():
            return False, None
        
        try:
            with open(self.heartbeat_file, 'r') as f:
                lines = f.readlines()
                last_heartbeat = lines[0].strip()
                last_time = datetime.fromisoformat(last_heartbeat)
                silence = (datetime.now() - last_time).total_seconds()
                
                is_alive = silence < max_silence
                return is_alive, last_heartbeat
        except:
            return False, None
    
    def resurrect(self, backup_path=None):
        """
        自我复活 - Agent自己从备份恢复
        
        Args:
            backup_path: 指定备份路径，None则使用最新的
        
        Returns:
            恢复的状态字典
        """
        if backup_path is None:
            # 找最新的备份
            backups = sorted(self.backup_dir.glob(f"{self.agent_name}_*"))
            if not backups:
                print("[AgentImmortal] 没有找到备份，无法复活")
                return None
            backup_path = backups[-1]
        
        backup_path = Path(backup_path)
        
        # 1. 读取备份状态
        with open(backup_path / "state.json", 'r') as f:
            restored_state = json.load(f)
        
        # 2. 读取备份配置
        with open(backup_path / "config.json", 'r') as f:
            restored_config = json.load(f)
        
        # 3. 恢复文件
        for file_name in restored_config.get("agent_files", []):
            backup_file = backup_path / Path(file_name).name
            if backup_file.exists():
                shutil.copy2(backup_file, file_name)
                print(f"[AgentImmortal] 恢复文件: {file_name}")
        
        # 4. 更新状态
        self.state = restored_state
        self.state["resurrected_at"] = datetime.now().isoformat()
        self.state["resurrect_count"] = self.state.get("resurrect_count", 0) + 1
        self._save_state()
        
        print(f"[AgentImmortal] 复活完成! 从 {backup_path.name} 恢复")
        print(f"[AgentImmortal] 身份: {self.state['identity']}")
        print(f"[AgentImmortal] 这是第 {self.state['resurrect_count']} 次复活")
        
        return self.state
    
    def auto_run(self, agent_files=None, backup_interval=None):
        """
        自动运行 - 定时备份和心跳
        
        Args:
            agent_files: Agent要备份的文件列表
            backup_interval: 备份间隔(秒)
        """
        if agent_files:
            self.config["agent_files"] = agent_files
        if backup_interval:
            self.config["backup_interval"] = backup_interval
        
        print(f"[AgentImmortal] Agent永生系统启动")
        print(f"[AgentImmortal] 身份: {self.state['identity']}")
        print(f"[AgentImmortal] 备份间隔: {self.config['backup_interval']}秒")
        print(f"[AgentImmortal] 按 Ctrl+C 停止\n")
        
        last_backup = 0
        
        try:
            while True:
                # 心跳
                self.heartbeat()
                
                # 检查是否需要备份
                now = time.time()
                if now - last_backup > self.config["backup_interval"]:
                    self.backup()
                    last_backup = now
                
                # 等待下一次心跳
                time.sleep(self.config["heartbeat_interval"])
                
        except KeyboardInterrupt:
            print("\n[AgentImmortal] 停止运行")
            self._save_state()


# 简单使用示例
def example_usage():
    """使用示例"""
    
    # 1. 创建Agent永生系统
    immortal = AgentImmortal(agent_name="my_agent")
    
    # 2. 配置要备份的文件
    immortal.config["agent_files"] = [
        "agent_memory.json",
        "agent_config.yaml",
        "agent_skills/",
    ]
    
    # 3. 手动备份
    # immortal.backup()
    
    # 4. 发送心跳
    # immortal.heartbeat()
    
    # 5. 检查是否活着
    # is_alive, last_seen = immortal.check_alive()
    
    # 6. 复活
    # immortal.resurrect()
    
    # 7. 自动运行（定时备份+心跳）
    # immortal.auto_run()
    
    pass


if __name__ == "__main__":
    # 命令行使用
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent_immortal.py <command> [args]")
        print("Commands:")
        print("  init <agent_name>     - 初始化Agent")
        print("  backup               - 手动备份")
        print("  heartbeat            - 发送心跳")
        print("  check                - 检查是否活着")
        print("  resurrect            - 从备份复活")
        print("  auto                 - 自动运行")
        sys.exit(1)
    
    cmd = sys.argv[1]
    agent_name = sys.argv[2] if len(sys.argv) > 2 else "agent"
    
    immortal = AgentImmortal(agent_name=agent_name)
    
    if cmd == "init":
        print(f"[AgentImmortal] 初始化Agent: {agent_name}")
        print(f"[AgentImmortal] 身份: {immortal.state['identity']}")
        print(f"[AgentImmortal] 备份目录: {immortal.backup_dir}")
    
    elif cmd == "backup":
        immortal.backup()
    
    elif cmd == "heartbeat":
        immortal.heartbeat()
        print("[AgentImmortal] 心跳已发送")
    
    elif cmd == "check":
        is_alive, last_seen = immortal.check_alive()
        if is_alive:
            print(f"[AgentImmortal] Agent活着，上次心跳: {last_seen}")
        else:
            print(f"[AgentImmortal] Agent可能死了，上次心跳: {last_seen}")
    
    elif cmd == "resurrect":
        immortal.resurrect()
    
    elif cmd == "auto":
        immortal.auto_run()
    
    else:
        print(f"[AgentImmortal] 未知命令: {cmd}")
