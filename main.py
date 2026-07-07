#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绘图与图形管理软件 - 主程序入口
功能：整合所有模块，实现完整的绘图应用
作者：课程设计团队

模块结构：
    shapes.py         - 图形类定义模块
    transforms.py     - 图形变换模块
    curves.py         - 特殊曲线生成模块
    file_manager.py   - 文件管理模块
    ui_components.py  - UI界面组件模块
    main.py           - 主程序入口（本文件）
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# 导入各个模块
from shapes import Shape, ShapeFactory, ShapeManager
from transforms import TransformManager, TransformHelper
from curves import CurveGenerator, CurvePresets
from file_manager import FileManager, BackupManager
from ui_components import (
    ToolbarPanel, ColorPanel, WidthPanel,
    StatusBar, MenuBar, DialogHelper, RainbowBrush
)


# ============================================
# 主应用类 - 整合所有功能
# ============================================

class DrawingApplication:
    """
    绘图应用程序主类
    负责整合所有模块，协调界面交互与数据处理
    """
    
    def __init__(self):
        """初始化应用程序"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("绘图与图形管理软件 v1.0")
        self.root.geometry("1200x800")
        
        # 初始化核心组件
        self.shape_manager = ShapeManager()   # 图形管理器
        self.rainbow_brush = RainbowBrush()   # 彩虹画笔
        
        # 状态变量
        self.current_tool = 'line'            # 当前绘图工具
        self.current_color = 'black'          # 当前颜色
        self.current_width = 2                # 当前线宽
        
        # 绘图状态
        self.is_drawing = False               # 是否正在绘制
        self.start_point = None               # 绘图起始点
        self.temp_points = []                 # 临时点列表
        self.temp_shape_id = None             # 临时图形ID
        
        # 移动状态
        self.is_moving = False                # 是否正在移动图形
        self.move_start = None                # 移动起始点
        
        # 创建界面
        self._create_ui()
        
        # 绑定快捷键
        self._bind_shortcuts()
    
    def _create_ui(self):
        """创建用户界面"""
        # 创建菜单栏
        self._create_menu()
        
        # 创建左侧工具栏区域
        self._create_sidebar()
        
        # 创建画布区域
        self._create_canvas()
        
        # 创建状态栏
        self._create_statusbar()
    
    def _create_menu(self):
        """创建菜单栏"""
        # 定义菜单命令回调
        callbacks = {
            'new_canvas': self._on_new_canvas,
            'open_file': self._on_open_file,
            'save_file': self._on_save_file,
            'copy_shape': self._on_copy_shape,
            'delete_shape': self._on_delete_shape,
            'clear_canvas': self._on_clear_canvas,
            'set_tool': self._set_tool_from_menu,
            'draw_sine': self._on_draw_sine_curve,
            'draw_spiral': self._on_draw_spiral,
            'draw_heart': self._on_draw_heart,
            'draw_lissajous': self._on_draw_lissajous,
            'draw_flower': self._on_draw_flower,
            'scale_shape': self._on_scale_shape,
            'rotate_shape': self._on_rotate_shape,
            'flip_shape': self._on_flip_shape,
            'fill_shape': self._on_fill_shape,
            'add_shadow': self._on_add_shadow,
            'generate_pattern': self._on_generate_pattern,
            'show_help': self._on_show_help,
            'show_about': self._on_show_about
        }
        
        self.menu_bar = MenuBar(self.root, callbacks)
    
    def _create_sidebar(self):
        """创建左侧边栏"""
        # 左侧边栏框架
        sidebar_frame = tk.Frame(self.root, relief='raised', bd=2)
        sidebar_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # 绘图工具面板
        self.toolbar = ToolbarPanel(sidebar_frame, self._on_tool_change)
        
        # 分隔线
        tk.Frame(sidebar_frame, height=2, bg='gray').pack(fill='x', pady=5)
        
        # 颜色选择面板
        self.color_panel = ColorPanel(sidebar_frame, self._on_color_change)
        
        # 分隔线
        tk.Frame(sidebar_frame, height=2, bg='gray').pack(fill='x', pady=5)
        
        # 线宽调节面板
        self.width_panel = WidthPanel(sidebar_frame, self._on_width_change)
        
        # 分隔线
        tk.Frame(sidebar_frame, height=2, bg='gray').pack(fill='x', pady=5)
        
        # 操作按钮区域
        self._create_action_buttons(sidebar_frame)
    
    def _create_action_buttons(self, parent):
        """创建操作按钮"""
        tk.Label(parent, text="操作", font=('微软雅黑', 10, 'bold')).pack(pady=5)
        
        actions = [
            ('复制', self._on_copy_shape),
            ('删除', self._on_delete_shape),
            ('清空', self._on_clear_canvas)
        ]
        
        for text, command in actions:
            btn = tk.Button(parent, text=text, width=8, command=command)
            btn.pack(pady=2, padx=5)
    
    def _create_canvas(self):
        """创建画布区域"""
        # 画布框架
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side='left', fill='both', expand=True)
        
        # 创建画布
        self.canvas = tk.Canvas(canvas_frame, bg='white', cursor='cross')
        self.canvas.pack(fill='both', expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<B1-Motion>', self._on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_canvas_release)
        self.canvas.bind('<Motion>', self._on_canvas_motion)
    
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusbar = StatusBar(self.root)
    
    def _bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind('<Control-n>', lambda e: self._on_new_canvas())
        self.root.bind('<Control-s>', lambda e: self._on_save_file())
        self.root.bind('<Control-o>', lambda e: self._on_open_file())
        self.root.bind('<Control-c>', lambda e: self._on_copy_shape())
        self.root.bind('<Delete>', lambda e: self._on_delete_shape())
        self.root.bind('<Escape>', lambda e: self._cancel_selection())
    
    # ============================================
    # 工具和属性设置回调
    # ============================================
    
    def _on_tool_change(self, tool):
        """工具切换回调"""
        self.current_tool = tool
        self._cancel_selection()
        
        tool_names = {
            'select': '选择工具',
            'line': '直线工具',
            'rectangle': '矩形工具',
            'circle': '圆形工具',
            'pencil': '画笔工具',
            'rainbow': '彩虹画笔',
            'eraser': '橡皮擦'
        }
        
        self.statusbar.set_status(f"当前工具: {tool_names.get(tool, tool)}")
        
        # 重置彩虹画笔
        if tool == 'rainbow':
            self.rainbow_brush.reset()
    
    def _on_color_change(self, color):
        """颜色切换回调"""
        self.current_color = color
        self.statusbar.set_status(f"当前颜色: {color}")
    
    def _on_width_change(self, width):
        """线宽切换回调"""
        self.current_width = width
        self.statusbar.set_status(f"当前线宽: {width}")
    
    def _set_tool_from_menu(self, tool):
        """从菜单设置工具"""
        self.toolbar.set_active_tool(tool)
        self._on_tool_change(tool)
    
    # ============================================
    # 鼠标事件处理
    # ============================================
    
    def _on_canvas_click(self, event):
        """画布点击事件"""
        x, y = event.x, event.y
        
        if self.current_tool == 'select':
            # 选择工具模式
            self._select_shape_at(x, y)
            if self.shape_manager.selected_shape:
                self.is_moving = True
                self.move_start = (x, y)
        else:
            # 绘图模式
            self.is_drawing = True
            self.start_point = (x, y)
            self.temp_points = [(x, y)]
    
    def _on_canvas_drag(self, event):
        """画布拖拽事件"""
        x, y = event.x, event.y
        
        if self.is_drawing:
            # 绘图模式
            self._handle_drawing_drag(x, y)
        
        elif self.is_moving and self.shape_manager.selected_shape:
            # 移动图形
            dx = x - self.move_start[0]
            dy = y - self.move_start[1]
            TransformManager.move(self.shape_manager.selected_shape, dx, dy)
            self.move_start = (x, y)
            self._redraw_all()
    
    def _on_canvas_release(self, event):
        """画布释放事件"""
        x, y = event.x, event.y
        
        if self.is_drawing:
            # 完成绘图
            self._finalize_drawing(x, y)
            self.is_drawing = False
        
        self.is_moving = False
        self.move_start = None
        self._update_shape_count()
    
    def _on_canvas_motion(self, event):
        """画布移动事件"""
        self.statusbar.set_coordinates(event.x, event.y)
    
    def _handle_drawing_drag(self, x, y):
        """处理绘图拖拽"""
        # 清除临时图形
        if self.temp_shape_id:
            self.canvas.delete(self.temp_shape_id)
        
        # 根据工具绘制预览
        if self.current_tool == 'line':
            self.temp_shape_id = self.canvas.create_line(
                self.start_point[0], self.start_point[1], x, y,
                fill=self.current_color, width=self.current_width
            )
        
        elif self.current_tool == 'rectangle':
            self.temp_shape_id = self.canvas.create_rectangle(
                self.start_point[0], self.start_point[1], x, y,
                outline=self.current_color, width=self.current_width
            )
        
        elif self.current_tool == 'circle':
            cx = (self.start_point[0] + x) / 2
            cy = (self.start_point[1] + y) / 2
            rx = abs(x - self.start_point[0]) / 2
            ry = abs(y - self.start_point[1]) / 2
            self.temp_shape_id = self.canvas.create_oval(
                cx - rx, cy - ry, cx + rx, cy + ry,
                outline=self.current_color, width=self.current_width
            )
        
        elif self.current_tool == 'pencil':
            self.temp_points.append((x, y))
            if len(self.temp_points) > 1:
                self.temp_shape_id = self.canvas.create_line(
                    self.temp_points[-2][0], self.temp_points[-2][1],
                    self.temp_points[-1][0], self.temp_points[-1][1],
                    fill=self.current_color, width=self.current_width
                )
        
        elif self.current_tool == 'rainbow':
            self.temp_points.append((x, y))
            if len(self.temp_points) > 1:
                color = self.rainbow_brush.get_next_color()
                self.temp_shape_id = self.canvas.create_line(
                    self.temp_points[-2][0], self.temp_points[-2][1],
                    self.temp_points[-1][0], self.temp_points[-1][1],
                    fill=color, width=self.current_width
                )
        
        elif self.current_tool == 'eraser':
            self.temp_shape_id = self.canvas.create_rectangle(
                x - self.current_width * 2,
                y - self.current_width * 2,
                x + self.current_width * 2,
                y + self.current_width * 2,
                fill='white', outline='white'
            )
    
    def _finalize_drawing(self, x, y):
        """完成绘图，创建最终图形"""
        # 清除临时图形
        if self.temp_shape_id:
            self.canvas.delete(self.temp_shape_id)
            self.temp_shape_id = None
        
        # 根据工具创建图形
        if self.current_tool == 'line':
            shape = ShapeFactory.create_line(
                self.start_point, (x, y),
                self.current_color, self.current_width
            )
            self.shape_manager.add_shape(shape)
        
        elif self.current_tool == 'rectangle':
            shape = ShapeFactory.create_rectangle(
                self.start_point, (x, y),
                self.current_color, self.current_width
            )
            self.shape_manager.add_shape(shape)
        
        elif self.current_tool == 'circle':
            cx = (self.start_point[0] + x) / 2
            cy = (self.start_point[1] + y) / 2
            rx = abs(x - self.start_point[0]) / 2
            ry = abs(y - self.start_point[1]) / 2
            shape = ShapeFactory.create_ellipse(
                (cx, cy), rx, ry,
                self.current_color, self.current_width
            )
            self.shape_manager.add_shape(shape)
        
        elif self.current_tool == 'pencil' and len(self.temp_points) > 1:
            shape = ShapeFactory.create_pencil_path(
                self.temp_points.copy(),
                self.current_color, self.current_width
            )
            self.shape_manager.add_shape(shape)
        
        elif self.current_tool == 'rainbow' and len(self.temp_points) > 1:
            # 彩虹画笔存储为特殊类型
            shape = Shape('rainbow', self.temp_points.copy(),
                         self.current_color, self.current_width)
            self.shape_manager.add_shape(shape)
        
        self._redraw_all()
    
    # ============================================
    # 图形选择和管理
    # ============================================
    
    def _select_shape_at(self, x, y):
        """选择指定位置的图形"""
        shape = self.shape_manager.get_shape_at(x, y)
        
        if shape:
            self.shape_manager.select_shape(shape)
            self.statusbar.set_status(f"已选中: {shape.shape_type}")
        else:
            self.shape_manager.deselect_all()
            self.statusbar.set_status("未选中任何图形")
        
        self._redraw_all()
    
    def _cancel_selection(self):
        """取消选择"""
        self.shape_manager.deselect_all()
        self._redraw_all()
    
    # ============================================
    # 文件操作
    # ============================================
    
    def _on_new_canvas(self):
        """新建画布"""
        if self.shape_manager.count() > 0:
            if messagebox.askyesno("确认", "画布上有图形，确定要新建吗？"):
                self.shape_manager.clear_all()
                self._redraw_all()
                self._update_shape_count()
                self.statusbar.set_status("新建画布")
    
    def _on_save_file(self):
        """保存文件"""
        if self.shape_manager.count() == 0:
            messagebox.showinfo("提示", "画布为空，无需保存")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filepath:
            if FileManager.save_to_file(self.shape_manager.shapes, filepath):
                self.statusbar.set_status(f"已保存: {filepath}")
                messagebox.showinfo("成功", "文件保存成功！")
            else:
                messagebox.showerror("错误", "保存失败")
    
    def _on_open_file(self):
        """打开文件"""
        filepath = filedialog.askopenfilename(
            title="打开文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filepath:
            shapes = FileManager.load_from_file(filepath)
            if shapes:
                self.shape_manager.clear_all()
                for shape in shapes:
                    self.shape_manager.add_shape(shape)
                self._redraw_all()
                self._update_shape_count()
                self.statusbar.set_status(f"已打开: {filepath}")
            else:
                messagebox.showerror("错误", "文件加载失败")
    
    # ============================================
    # 编辑操作
    # ============================================
    
    def _on_copy_shape(self):
        """复制图形"""
        selected = self.shape_manager.get_selected_shape()
        
        if not selected:
            messagebox.showinfo("提示", "请先选择要复制的图形")
            return
        
        # 复制并偏移
        new_shape = TransformManager.copy_and_offset(selected, 20, 20)
        self.shape_manager.add_shape(new_shape)
        
        # 选中新图形
        self.shape_manager.select_shape(new_shape)
        
        self._redraw_all()
        self._update_shape_count()
        self.statusbar.set_status("图形已复制")
    
    def _on_delete_shape(self):
        """删除图形"""
        selected = self.shape_manager.get_selected_shape()
        
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的图形")
            return
        
        self.shape_manager.remove_shape(selected)
        self._redraw_all()
        self._update_shape_count()
        self.statusbar.set_status("图形已删除")
    
    def _on_clear_canvas(self):
        """清空画布"""
        if self.shape_manager.count() > 0:
            if messagebox.askyesno("确认", "确定要清空画布吗？"):
                self.shape_manager.clear_all()
                self._redraw_all()
                self._update_shape_count()
                self.statusbar.set_status("画布已清空")
    
    # ============================================
    # 特殊曲线绘制
    # ============================================
    
    def _on_draw_sine_curve(self):
        """绘制正弦曲线"""
        # 创建参数对话框
        DialogHelper.create_parameter_dialog(
            self.root,
            "正弦曲线参数",
            [
                {'name': 'amplitude', 'label': '振幅', 'type': 'int',
                 'default': 50, 'min': 10, 'max': 150},
                {'name': 'period', 'label': '周期', 'type': 'int',
                 'default': 200, 'min': 50, 'max': 400},
                {'name': 'cycles', 'label': '周期数', 'type': 'int',
                 'default': 2, 'min': 1, 'max': 5}
            ],
            self._create_sine_curve
        )
    
    def _create_sine_curve(self, params):
        """创建正弦曲线"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        points = CurveGenerator.generate_sine_curve(
            50, canvas_height // 2,
            params['amplitude'],
            params['period'],
            params['cycles']
        )
        
        shape = Shape('sine', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self._redraw_all()
        self._update_shape_count()
    
    def _on_draw_spiral(self):
        """绘制阿基米德螺线"""
        DialogHelper.create_parameter_dialog(
            self.root,
            "阿基米德螺线参数",
            [
                {'name': 'a', 'label': '内径参数', 'type': 'int',
                 'default': 5, 'min': 1, 'max': 20},
                {'name': 'b', 'label': '螺距参数', 'type': 'int',
                 'default': 10, 'min': 5, 'max': 30},
                {'name': 'turns', 'label': '圈数', 'type': 'int',
                 'default': 3, 'min': 1, 'max': 10}
            ],
            self._create_spiral
        )
    
    def _create_spiral(self, params):
        """创建螺线"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        points = CurveGenerator.generate_archimedean_spiral(
            canvas_width // 2, canvas_height // 2,
            params['a'], params['b'], params['turns']
        )
        
        shape = Shape('spiral', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self._redraw_all()
        self._update_shape_count()
    
    def _on_draw_heart(self):
        """绘制心形曲线"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        points = CurveGenerator.generate_heart_curve(
            canvas_width // 2, canvas_height // 2, size=50
        )
        
        shape = Shape('heart', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self._redraw_all()
        self._update_shape_count()
    
    def _on_draw_lissajous(self):
        """绘制利萨如曲线"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        points = CurveGenerator.generate_lissajous_curve(
            canvas_width // 2, canvas_height // 2,
            a=80, b=80, frequency_x=3, frequency_y=2
        )
        
        shape = Shape('lissajous', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self._redraw_all()
        self._update_shape_count()
    
    def _on_draw_flower(self):
        """绘制花瓣曲线"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        points = CurveGenerator.generate_flower_curve(
            canvas_width // 2, canvas_height // 2,
            radius=80, petals=5
        )
        
        shape = Shape('flower', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self._redraw_all()
        self._update_shape_count()
    
    # ============================================
    # 图形变换
    # ============================================
    
    def _on_scale_shape(self):
        """缩放图形"""
        selected = self.shape_manager.get_selected_shape()
        
        if not selected:
            messagebox.showinfo("提示", "请先选择要缩放的图形")
            return
        
        DialogHelper.create_parameter_dialog(
            self.root,
            "缩放参数",
            [
                {'name': 'scale_x', 'label': '水平比例', 'type': 'float',
                 'default': 1.5, 'min': 0.1, 'max': 3.0},
                {'name': 'scale_y', 'label': '垂直比例', 'type': 'float',
                 'default': 1.5, 'min': 0.1, 'max': 3.0}
            ],
            self._apply_scale
        )
    
    def _apply_scale(self, params):
        """应用缩放"""
        selected = self.shape_manager.get_selected_shape()
        if selected:
            cx, cy = selected.get_center()
            TransformManager.scale(selected, cx, cy,
                                   params['scale_x'], params['scale_y'])
            self._redraw_all()
    
    def _on_rotate_shape(self):
        """旋转图形"""
        selected = self.shape_manager.get_selected_shape()
        
        if not selected:
            messagebox.showinfo("提示", "请先选择要旋转的图形")
            return
        
        DialogHelper.create_parameter_dialog(
            self.root,
            "旋转参数",
            [
                {'name': 'angle', 'label': '旋转角度', 'type': 'int',
                 'default': 45, 'min': -180, 'max': 180}
            ],
            self._apply_rotate
        )
    
    def _apply_rotate(self, params):
        """应用旋转"""
        selected = self.shape_manager.get_selected_shape()
        if selected:
            cx, cy = selected.get_center()
            TransformManager.rotate(selected, cx, cy, params['angle'])
            self._redraw_all()
    
    def _on_flip_shape(self, direction):
        """翻转图形"""
        selected = self.shape_manager.get_selected_shape()
        
        if not selected:
            messagebox.showinfo("提示", "请先选择要翻转的图形")
            return
        
        if direction == 'horizontal':
            TransformManager.flip_horizontal(selected)
        else:
            TransformManager.flip_vertical(selected)
        
        self._redraw_all()
        self.statusbar.set_status(f"图形已{'水平' if direction == 'horizontal' else '垂直'}翻转")
    
    # ============================================
    # 创意功能
    # ============================================
    
    def _on_fill_shape(self):
        """填充图形"""
        selected = self.shape_manager.get_selected_shape()
        
        if not selected:
            messagebox.showinfo("提示", "请先选择要填充的图形")
            return
        
        DialogHelper.create_parameter_dialog(
            self.root,
            "填充颜色",
            [
                {'name': 'fill_color', 'label': '填充颜色', 'type': 'color',
                 'default': 'lightblue'}
            ],
            self._apply_fill
        )
    
    def _apply_fill(self, params):
        """应用填充"""
        selected = self.shape_manager.get_selected_shape()
        if selected:
            selected.fill_color = params['fill_color']
            self._redraw_all()
            self.statusbar.set_status("图形已填充")
    
    def _on_add_shadow(self):
        """添加阴影"""
        selected = self.shape_manager.get_selected_shape()
        
        if not selected:
            messagebox.showinfo("提示", "请先选择要添加阴影的图形")
            return
        
        # 创建阴影图形
        shadow = TransformHelper.create_shadow_shape(selected)
        
        # 插入到原图形之前
        shapes = self.shape_manager.shapes
        index = shapes.index(selected)
        shapes.insert(index, shadow)
        
        self._redraw_all()
        self._update_shape_count()
        self.statusbar.set_status("阴影已添加")
    
    def _on_generate_pattern(self):
        """生成图案"""
        # 生成同心圆图案
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx = canvas_width // 2
        cy = canvas_height // 2
        
        for r in range(20, 150, 20):
            shape = ShapeFactory.create_circle(
                (cx, cy), r,
                self.current_color, self.current_width
            )
            self.shape_manager.add_shape(shape)
        
        self._redraw_all()
        self._update_shape_count()
        self.statusbar.set_status("图案已生成")
    
    # ============================================
    # 帮助信息
    # ============================================
    
    def _on_show_help(self):
        """显示帮助"""
        help_text = """
绘图与图形管理软件 - 使用说明

【基本操作】
1. 选择左侧工具栏中的绘图工具
2. 在画布上拖拽鼠标绘制图形
3. 使用颜色面板和线宽滑块调整属性

【图形选择】
- 点击"选择"工具后，点击图形进行选择
- 选中后可拖拽移动图形

【快捷键】
Ctrl+N - 新建画布
Ctrl+S - 保存文件
Ctrl+O - 打开文件
Ctrl+C - 复制图形
Delete - 删除图形
Esc - 取消选择
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("500x400")
        
        text_widget = tk.Text(help_window, wrap='word', padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
    
    def _on_show_about(self):
        """显示关于"""
        messagebox.showinfo(
            "关于",
            "绘图与图形管理软件 v1.0\n\n"
            "功能：绘图、变换、特殊曲线、文件管理\n\n"
            "模块化设计，便于维护和扩展\n\n"
            "© 2024 课程设计作品"
        )
    
    # ============================================
    # 绘制和更新
    # ============================================
    
    def _redraw_all(self):
        """重绘所有图形"""
        self.canvas.delete('all')
        
        for shape in self.shape_manager.shapes:
            self._draw_shape(shape)
    
    def _draw_shape(self, shape):
        """绘制单个图形"""
        if not shape.points:
            return
        
        # 准备坐标
        coords = []
        for point in shape.points:
            coords.extend(point)
        
        # 根据类型绘制
        if shape.shape_type == 'line':
            self.canvas.create_line(
                coords,
                fill=shape.color,
                width=shape.width
            )
        
        elif shape.shape_type == 'rectangle':
            self.canvas.create_polygon(
                coords,
                outline=shape.color,
                fill=shape.fill_color or '',
                width=shape.width
            )
        
        elif shape.shape_type == 'ellipse':
            self.canvas.create_polygon(
                coords,
                outline=shape.color,
                fill=shape.fill_color or '',
                width=shape.width
            )
        
        elif shape.shape_type == 'pencil':
            self.canvas.create_line(
                coords,
                fill=shape.color,
                width=shape.width,
                smooth=True
            )
        
        elif shape.shape_type == 'rainbow':
            # 彩虹画笔特殊绘制
            import colorsys
            for i in range(len(shape.points) - 1):
                hue = (i * 0.01) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                self.canvas.create_line(
                    shape.points[i][0], shape.points[i][1],
                    shape.points[i+1][0], shape.points[i+1][1],
                    fill=color,
                    width=shape.width
                )
        
        else:
            # 其他曲线类型
            self.canvas.create_line(
                coords,
                fill=shape.color,
                width=shape.width,
                smooth=True
            )
        
        # 绘制选择框
        if shape.selected:
            self._draw_selection_box(shape)
    
    def _draw_selection_box(self, shape):
        """绘制选择框"""
        bounds = shape.get_bounds()
        if bounds:
            padding = 5
            self.canvas.create_rectangle(
                bounds[0] - padding,
                bounds[1] - padding,
                bounds[2] + padding,
                bounds[3] + padding,
                outline='blue',
                dash=(4, 4),
                width=2
            )
    
    def _update_shape_count(self):
        """更新图形数量"""
        self.statusbar.set_shape_count(self.shape_manager.count())
    
    # ============================================
    # 运行应用
    # ============================================
    
    def run(self):
        """运行应用程序"""
        self.statusbar.set_status("就绪 - 请选择工具开始绘图")
        self.root.mainloop()


# ============================================
# 主程序入口
# ============================================

def main():
    """主函数"""
    print("正在启动绘图软件...")
    print("模块结构:")
    print("  - shapes.py       (图形类)")
    print("  - transforms.py   (变换)")
    print("  - curves.py       (特殊曲线)")
    print("  - file_manager.py (文件管理)")
    print("  - ui_components.py (界面组件)")
    print("  - main.py         (主程序)")
    print()
    
    app = DrawingApplication()
    app.run()


if __name__ == "__main__":
    main()