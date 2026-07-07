#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绘图软件模块包
包含所有功能模块的初始化文件
"""

# 导出所有模块的主要类
from shapes import Shape, ShapeFactory, ShapeManager
from transforms import TransformManager, TransformHelper
from curves import CurveGenerator, CurvePresets
from file_manager import FileManager, BackupManager, ExportManager

# 版本信息
__version__ = "1.0"
__author__ = "课程设计团队"