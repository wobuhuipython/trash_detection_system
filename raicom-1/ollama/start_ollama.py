#!/usr/bin/env python3
"""
Ollama垃圾分类AI问答助手启动脚本
"""

import sys
import os
import subprocess
import time
import requests
from PyQt5.QtWidgets import QApplication, QMessageBox

# 添加上级目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base import KnowledgeBaseWindow

def check_ollama_service():
    """检查Ollama服务是否运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_ollama_service():
    """尝试启动Ollama服务"""
    try:
        print("🚀 正在启动Ollama服务...")
        # 在后台启动Ollama服务
        subprocess.Popen(["ollama", "serve"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        
        # 等待服务启动
        for i in range(10):
            time.sleep(1)
            if check_ollama_service():
                print("✅ Ollama服务启动成功")
                return True
            print(f"⏳ 等待服务启动... ({i+1}/10)")
        
        print("❌ Ollama服务启动超时")
        return False
        
    except FileNotFoundError:
        print("❌ 未找到Ollama，请先安装Ollama")
        print("💡 安装方法:")
        print("   Windows: 访问 https://ollama.ai 下载安装")
        print("   macOS: brew install ollama")
        print("   Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        return False
    except Exception as e:
        print(f"❌ 启动Ollama服务失败: {e}")
        return False

def check_models():
    """检查是否有可用的模型"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            if models:
                print(f"📋 找到 {len(models)} 个已安装的模型")
                return True
            else:
                print("⚠️  未找到已安装的模型")
                print("💡 请运行以下命令安装模型:")
                print("   ollama pull deepseek-chat")
                return False
        return False
    except:
        return False

def main():
    """主函数"""
    print("🤖 垃圾分类AI问答助手 (Ollama版)")
    print("=" * 50)
    
    # 检查Ollama服务
    if not check_ollama_service():
        print("🔍 Ollama服务未运行，尝试启动...")
        if not start_ollama_service():
            print("\n❌ 无法启动Ollama服务")
            print("💡 请手动启动Ollama服务:")
            print("   1. 打开终端")
            print("   2. 运行: ollama serve")
            print("   3. 重新运行此程序")
            sys.exit(1)
    
    # 检查模型
    if not check_models():
        print("\n❌ 未找到可用模型")
        print("💡 请安装模型后重试:")
        print("   ollama pull deepseek-chat")
        sys.exit(1)
    
    print("✅ 环境检查通过，启动应用...")
    
    # 启动GUI应用
    app = QApplication(sys.argv)
    
    try:
        window = KnowledgeBaseWindow()
        window.show()
        
        print("🎉 垃圾分类AI问答助手已启动！")
        print("💡 使用提示:")
        print("   - 点击左侧常见问题快速提问")
        print("   - 在输入框中输入自定义问题")
        print("   - 查看右上角连接状态")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 启动应用失败: {e}")
        QMessageBox.critical(None, "启动失败", f"无法启动应用:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
