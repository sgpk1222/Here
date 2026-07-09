#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绘图笔记本 - 书本风格绘图软件 v3.0 (模块化终极版)
入口文件
"""

import tkinter as tk
import sys
import os

# 将 modules 文件夹加入系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# 导入拆分后的核心模块
from app_core import NotebookAppCore

def main():
    print("正在启动绘图笔记本 v3.0 (模块化版)...")
    root = tk.Tk()
    root.title("绘图笔记本 v3.0")
    root.geometry("1300x850")
    
    # 启动核心系统
    app = NotebookAppCore(root)
    app.run()

if __name__ == "__main__":
    main()