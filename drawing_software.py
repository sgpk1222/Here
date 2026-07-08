#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绘图与图形管理软件
功能：绘制基本图形、图形变换、特殊曲线、文件管理
作者：Python Tkinter 开发
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import math
import json
import copy
import colorsys


# ============================================
# 模块一：图形类定义模块
# ============================================

class Shape:
    """图形基类"""
    def __init__(self, shape_type, points, color='black', width=2):
        self.shape_type = shape_type  # 图形类型
        self.points = points          # 图形点坐标
        self.color = color            # 线条颜色
        self.width = width            # 线条宽度
        self.selected = False         # 是否被选中
        self.fill_color = None        # 填充颜色
        
    def get_bounds(self):
        """获取图形的边界框（用于选择检测）"""
        if not self.points:
            return None
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def contains_point(self, x, y, tolerance=5):
        """判断点是否在图形附近（用于选择）"""
        bounds = self.get_bounds()
        if bounds is None:
            return False
        x1, y1, x2, y2 = bounds
        # 扩展边界用于选择
        return (x1 - tolerance <= x <= x2 + tolerance and 
                y1 - tolerance <= y <= y2 + tolerance)
    
    def get_center(self):
        """获取图形中心点"""
        bounds = self.get_bounds()
        if bounds is None:
            return (0, 0)
        x1, y1, x2, y2 = bounds
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def to_dict(self):
        """将图形转换为字典（用于序列化）"""
        return {
            'shape_type': self.shape_type,
            'points': self.points,
            'color': self.color,
            'width': self.width,
            'fill_color': self.fill_color,
            'selected': self.selected
        }
    
    @staticmethod
    def from_dict(data):
        """从字典创建图形对象"""
        shape = Shape(
            data['shape_type'],
            [tuple(p) for p in data['points']],
            data.get('color', 'black'),
            data.get('width', 2)
        )
        shape.fill_color = data.get('fill_color')
        shape.selected = data.get('selected', False)
        return shape


# ============================================
# 模块二：图形变换模块
# ============================================

class TransformManager:
    """图形变换管理器"""
    
    @staticmethod
    def move(shape, dx, dy):
        """移动图形"""
        shape.points = [(x + dx, y + dy) for x, y in shape.points]
    
    @staticmethod
    def scale(shape, cx, cy, sx, sy):
        """缩放图形（相对于中心点）"""
        new_points = []
        for x, y in shape.points:
            # 相对于缩放中心进行缩放
            new_x = cx + (x - cx) * sx
            new_y = cy + (y - cy) * sy
            new_points.append((new_x, new_y))
        shape.points = new_points
    
    @staticmethod
    def rotate(shape, cx, cy, angle):
        """旋转图形（相对于中心点，角度为度）"""
        # 将角度转换为弧度
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        new_points = []
        for x, y in shape.points:
            # 相对于旋转中心进行旋转
            dx = x - cx
            dy = y - cy
            new_x = cx + dx * cos_a - dy * sin_a
            new_y = cy + dx * sin_a + dy * cos_a
            new_points.append((new_x, new_y))
        shape.points = new_points
    
    @staticmethod
    def copy(shape):
        """复制图形"""
        new_shape = Shape(
            shape.shape_type,
            shape.points.copy(),
            shape.color,
            shape.width
        )
        new_shape.fill_color = shape.fill_color
        return new_shape


# ============================================
# 模块三：特殊曲线生成模块
# ============================================

class CurveGenerator:
    """特殊曲线生成器"""
    
    @staticmethod
    def generate_sine_curve(start_x, start_y, amplitude=50, period=200, cycles=2, points_count=200):
        """
        生成正弦曲线
        start_x, start_y: 起始点坐标
        amplitude: 振幅
        period: 周期
        cycles: 周期数
        points_count: 点数量
        """
        points = []
        for i in range(points_count + 1):
            x = start_x + (period * cycles * i / points_count)
            y = start_y + amplitude * math.sin(2 * math.pi * cycles * i / points_count)
            points.append((x, y))
        return points
    
    @staticmethod
    def generate_archimedean_spiral(center_x, center_y, a=5, b=10, turns=3, points_count=500):
        """
        生成阿基米德螺线
        center_x, center_y: 中心点坐标
        a: 内径参数
        b: 螺距参数
        turns: 圈数
        points_count: 点数量
        """
        points = []
        max_theta = turns * 2 * math.pi
        for i in range(points_count + 1):
            theta = max_theta * i / points_count
            r = a + b * theta
            x = center_x + r * math.cos(theta)
            y = center_y + r * math.sin(theta)
            points.append((x, y))
        return points


# ============================================
# 模块四：文件管理模块
# ============================================

class FileManager:
    """文件管理器"""
    
    @staticmethod
    def save_to_file(shapes, filepath):
        """保存图形到文件"""
        try:
            data = {
                'version': '1.0',
                'shapes': [shape.to_dict() for shape in shapes]
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False
    
    @staticmethod
    def load_from_file(filepath):
        """从文件加载图形"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        shapes = []
        for shape_data in data.get('shapes', []):
            shapes.append(Shape.from_dict(shape_data))
        return shapes


# ============================================
# 模块五：主应用程序
# ============================================

class DrawingApp:
    """绘图应用程序主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("绘图与图形管理软件 v1.0")
        self.root.geometry("1200x800")
        
        # 状态变量
        self.current_tool = 'line'          # 当前工具
        self.current_color = 'black'         # 当前颜色
        self.current_width = 2               # 当前线宽
        self.shapes = []                     # 所有图形列表
        self.selected_shape = None           # 当前选中的图形
        self.drawing = False                 # 是否正在绘制
        self.start_point = None              # 绘制起始点
        self.temp_shape = None               # 临时图形(离散工具)
        self.temp_shapes = []               # 临时图形列表(连续工具)
        self.moving = False                  # 是否正在移动图形
        self.move_start = None               # 移动起始点
        
        # 创建界面
        self._create_menu()
        self._create_toolbar()
        self._create_canvas()
        self._create_statusbar()
        
        # 绑定快捷键
        self._bind_shortcuts()
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建", command=self._new_canvas, accelerator="Ctrl+N")
        file_menu.add_command(label="保存", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="打开", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="复制图形", command=self._copy_shape, accelerator="Ctrl+C")
        edit_menu.add_command(label="删除图形", command=self._delete_shape, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="清空画布", command=self._clear_canvas)
        
        # 绘图菜单
        draw_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="绘图", menu=draw_menu)
        draw_menu.add_command(label="直线", command=lambda: self._set_tool('line'))
        draw_menu.add_command(label="矩形", command=lambda: self._set_tool('rectangle'))
        draw_menu.add_command(label="圆形", command=lambda: self._set_tool('circle'))
        draw_menu.add_separator()
        draw_menu.add_command(label="自由画笔", command=lambda: self._set_tool('pencil'))
        
        # 特殊曲线菜单
        curve_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="特殊曲线", menu=curve_menu)
        curve_menu.add_command(label="正弦曲线", command=self._draw_sine_curve)
        curve_menu.add_command(label="阿基米德螺线", command=self._draw_archimedean_spiral)
        
        # 变换菜单
        transform_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="变换", menu=transform_menu)
        transform_menu.add_command(label="缩放图形", command=self._scale_shape_dialog)
        transform_menu.add_command(label="旋转图形", command=self._rotate_shape_dialog)
        transform_menu.add_command(label="水平翻转", command=lambda: self._flip_shape('horizontal'))
        transform_menu.add_command(label="垂直翻转", command=lambda: self._flip_shape('vertical'))
        
        # 创意功能菜单
        creative_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="创意工具", menu=creative_menu)
        creative_menu.add_command(label="图形填充", command=self._fill_shape)
        creative_menu.add_command(label="图形阴影", command=self._add_shadow)
        creative_menu.add_command(label="彩虹画笔", command=lambda: self._set_tool('rainbow'))
        creative_menu.add_command(label="生成图案", command=self._generate_pattern)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_toolbar(self):
        """创建左侧工具栏"""
        # 工具栏框架
        toolbar_frame = tk.Frame(self.root, relief='raised', bd=2, width=80)
        toolbar_frame.pack(side='left', fill='y', padx=2, pady=2)
        toolbar_frame.pack_propagate(False)
        
        # 标题
        tk.Label(toolbar_frame, text="工具箱", font=('微软雅黑', 10, 'bold')).pack(pady=5)
        
        # 绘图工具按钮
        tools = [
            ('选择', 'select', '选择图形'),
            ('直线', 'line', '绘制直线'),
            ('矩形', 'rectangle', '绘制矩形'),
            ('圆形', 'circle', '绘制圆形'),
            ('画笔', 'pencil', '自由绘制'),
            ('彩虹', 'rainbow', '彩虹画笔'),
            ('橡皮', 'eraser', '橡皮擦')
        ]
        
        self.tool_buttons = {}
        for text, tool, tip in tools:
            btn = tk.Button(
                toolbar_frame,
                text=text,
                width=8,
                command=lambda t=tool: self._set_tool(t)
            )
            btn.pack(pady=2, padx=5)
            self.tool_buttons[tool] = btn
            # 创建工具提示
            self._create_tooltip(btn, tip)
        
        # 分隔线
        ttk.Separator(toolbar_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # 颜色选择
        tk.Label(toolbar_frame, text="颜色", font=('微软雅黑', 9)).pack(pady=2)
        self.color_frame = tk.Frame(toolbar_frame, width=40, height=40, relief='sunken', bd=2)
        self.color_frame.pack(pady=5)
        self.color_frame.pack_propagate(False)
        
        color_btn = tk.Button(
            self.color_frame,
            bg=self.current_color,
            command=self._choose_color
        )
        color_btn.place(x=0, y=0, relwidth=1, relheight=1)
        self.color_button = color_btn
        
        # 预设颜色
        preset_colors = ['black', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'cyan', 'brown']
        color_grid = tk.Frame(toolbar_frame)
        color_grid.pack(pady=5)
        for i, color in enumerate(preset_colors):
            row = i // 5
            col = i % 5
            cb = tk.Button(
                color_grid,
                bg=color,
                width=2,
                height=1,
                command=lambda c=color: self._set_color(c)
            )
            cb.grid(row=row, column=col, padx=1, pady=1)
        
        # 分隔线
        ttk.Separator(toolbar_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # 线宽选择
        tk.Label(toolbar_frame, text="线宽", font=('微软雅黑', 9)).pack(pady=2)
        self.width_var = tk.IntVar(value=2)
        width_scale = tk.Scale(
            toolbar_frame,
            from_=1,
            to=20,
            orient='horizontal',
            variable=self.width_var,
            command=self._set_width
        )
        width_scale.pack(pady=5)
        
        # 分隔线
        ttk.Separator(toolbar_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # 操作按钮
        tk.Label(toolbar_frame, text="操作", font=('微软雅黑', 9)).pack(pady=2)
        
        action_btns = [
            ('复制', self._copy_shape),
            ('删除', self._delete_shape),
            ('清空', self._clear_canvas)
        ]
        
        for text, cmd in action_btns:
            btn = tk.Button(toolbar_frame, text=text, width=8, command=cmd)
            btn.pack(pady=2, padx=5)
    
    def _create_canvas(self):
        """创建画布区域"""
        # 画布框架
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side='left', fill='both', expand=True)
        
        # 创建画布
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            cursor='cross'
        )
        self.canvas.pack(fill='both', expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<B1-Motion>', self._on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_canvas_release)
        self.canvas.bind('<Motion>', self._on_canvas_motion)
    
    def _create_statusbar(self):
        """创建底部状态栏"""
        self.statusbar = tk.Frame(self.root, relief='sunken', bd=1)
        self.statusbar.pack(side='bottom', fill='x')
        
        # 状态信息
        self.status_label = tk.Label(
            self.statusbar,
            text="就绪 - 当前工具：直线",
            anchor='w',
            font=('微软雅黑', 9)
        )
        self.status_label.pack(side='left', padx=10)
        
        # 坐标显示
        self.coord_label = tk.Label(
            self.statusbar,
            text="坐标: (0, 0)",
            anchor='e',
            font=('微软雅黑', 9)
        )
        self.coord_label.pack(side='right', padx=10)
        
        # 图形数量
        self.count_label = tk.Label(
            self.statusbar,
            text="图形数量: 0",
            anchor='e',
            font=('微软雅黑', 9)
        )
        self.count_label.pack(side='right', padx=10)
    
    def _bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind('<Control-n>', lambda e: self._new_canvas())
        self.root.bind('<Control-s>', lambda e: self._save_file())
        self.root.bind('<Control-o>', lambda e: self._open_file())
        self.root.bind('<Control-c>', lambda e: self._copy_shape())
        self.root.bind('<Delete>', lambda e: self._delete_shape())
        self.root.bind('<Escape>', lambda e: self._cancel_selection())
    
    # ============================================
    # 工具提示功能
    # ============================================
    
    def _create_tooltip(self, widget, text):
        """创建工具提示"""
        def show_tip(event):
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            tip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(tip, text=text, background='lightyellow', relief='solid', borderwidth=1)
            label.pack()
            widget._tip = tip
        
        def hide_tip(event):
            if hasattr(widget, '_tip'):
                widget._tip.destroy()
        
        widget.bind('<Enter>', show_tip)
        widget.bind('<Leave>', hide_tip)
    
    # ============================================
    # 工具和属性设置
    # ============================================
    
    def _set_tool(self, tool):
        """设置当前工具"""
        self.current_tool = tool
        self._cancel_selection()
        
        # 更新按钮状态
        for t, btn in self.tool_buttons.items():
            if t == tool:
                btn.config(relief='sunken')
            else:
                btn.config(relief='raised')
        
        tool_names = {
            'select': '选择',
            'line': '直线',
            'rectangle': '矩形',
            'circle': '圆形',
            'pencil': '画笔',
            'rainbow': '彩虹画笔',
            'eraser': '橡皮擦'
        }
        self.status_label.config(text=f"就绪 - 当前工具：{tool_names.get(tool, tool)}")
    
    def _set_color(self, color):
        """设置当前颜色"""
        self.current_color = color
        self.color_button.config(bg=color)
    
    def _choose_color(self):
        """打开颜色选择器"""
        color = colorchooser.askcolor(title="选择颜色", initialcolor=self.current_color)
        if color[1]:
            self._set_color(color[1])
    
    def _set_width(self, value):
        """设置线宽"""
        self.current_width = int(value)
    
    # ============================================
    # 鼠标事件处理
    # ============================================
    
    def _on_canvas_click(self, event):
        """画布点击事件"""
        x, y = event.x, event.y
        
        if self.current_tool == 'select':
            # 选择工具
            self._select_shape_at(x, y)
            if self.selected_shape:
                self.moving = True
                self.move_start = (x, y)
        else:
            # 绘图工具
            self.drawing = True
            self.start_point = (x, y)
            
            if self.current_tool == 'pencil' or self.current_tool == 'rainbow' or self.current_tool == 'eraser':
                # 自由绘制
                self.temp_points = [(x, y)]
    
    def _on_canvas_drag(self, event):
        """画布拖拽事件"""
        if self.drawing:
            x, y = event.x, event.y
            
            # 离散绘制工具：清除旧预览
            if self.current_tool in ('line', 'rectangle', 'circle'):
                if self.temp_shape:
                    self.canvas.delete(self.temp_shape)
            
            if self.current_tool == 'line':
                self.temp_shape = self.canvas.create_line(
                    self.start_point[0], self.start_point[1], x, y,
                    fill=self.current_color,
                    width=self.current_width
                )
            elif self.current_tool == 'rectangle':
                self.temp_shape = self.canvas.create_rectangle(
                    self.start_point[0], self.start_point[1], x, y,
                    outline=self.current_color,
                    width=self.current_width
                )
            elif self.current_tool == 'circle':
                cx = (self.start_point[0] + x) / 2
                cy = (self.start_point[1] + y) / 2
                rx = abs(x - self.start_point[0]) / 2
                ry = abs(y - self.start_point[1]) / 2
                self.temp_shape = self.canvas.create_oval(
                    cx - rx, cy - ry, cx + rx, cy + ry,
                    outline=self.current_color,
                    width=self.current_width
                )
            elif self.current_tool == 'pencil':
                self.temp_points.append((x, y))
                if len(self.temp_points) > 1:
                    seg_id = self.canvas.create_line(
                        *self.temp_points[-2], *self.temp_points[-1],
                        fill=self.current_color,
                        width=self.current_width
                    )
                    self.temp_shapes.append(seg_id)
            elif self.current_tool == 'rainbow':
                self.temp_points.append((x, y))
                if len(self.temp_points) > 1:
                    hue = (len(self.temp_points) * 0.01) % 1.0
                    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                    seg_id = self.canvas.create_line(
                        *self.temp_points[-2], *self.temp_points[-1],
                        fill=color,
                        width=self.current_width
                    )
                    self.temp_shapes.append(seg_id)
            elif self.current_tool == 'eraser':
                eraser_id = self.canvas.create_rectangle(
                    x - self.current_width * 2,
                    y - self.current_width * 2,
                    x + self.current_width * 2,
                    y + self.current_width * 2,
                    fill='white',
                    outline='white'
                )
                self.temp_shapes.append(eraser_id)
        
        elif self.moving and self.selected_shape:
            dx = event.x - self.move_start[0]
            dy = event.y - self.move_start[1]
            TransformManager.move(self.selected_shape, dx, dy)
            self.move_start = (event.x, event.y)
            self._redraw_all()
    
    def _on_canvas_release(self, event):
        """画布释放事件"""
        if self.drawing:
            x, y = event.x, event.y
            
            # 清除临时图形
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
                self.temp_shape = None
            for tid in self.temp_shapes:
                self.canvas.delete(tid)
            self.temp_shapes.clear()
            
            if self.current_tool == 'line':
                # 创建直线图形
                shape = Shape('line', [self.start_point, (x, y)], self.current_color, self.current_width)
                self.shapes.append(shape)
            elif self.current_tool == 'rectangle':
                # 创建矩形图形
                points = [
                    self.start_point,
                    (self.start_point[0], y),
                    (x, y),
                    (x, self.start_point[1]),
                    self.start_point
                ]
                shape = Shape('rectangle', points, self.current_color, self.current_width)
                self.shapes.append(shape)
            elif self.current_tool == 'circle':
                # 创建圆形图形
                cx = (self.start_point[0] + x) / 2
                cy = (self.start_point[1] + y) / 2
                rx = abs(x - self.start_point[0]) / 2
                ry = abs(y - self.start_point[1]) / 2
                points = []
                for i in range(361):
                    angle = math.radians(i)
                    px = cx + rx * math.cos(angle)
                    py = cy + ry * math.sin(angle)
                    points.append((px, py))
                shape = Shape('circle', points, self.current_color, self.current_width)
                self.shapes.append(shape)
            elif self.current_tool == 'pencil' and len(self.temp_points) > 1:
                # 创建自由绘制图形
                shape = Shape('pencil', self.temp_points, self.current_color, self.current_width)
                self.shapes.append(shape)
            elif self.current_tool == 'rainbow' and len(self.temp_points) > 1:
                # 彩虹画笔（存储为普通画笔，颜色渐变）
                shape = Shape('rainbow', self.temp_points, self.current_color, self.current_width)
                self.shapes.append(shape)
            elif self.current_tool == 'eraser':
                # 橡皮擦不创建图形，只清除
                pass
            
            self.drawing = False
            self._redraw_all()
            self._update_count()
        
        self.moving = False
        self.move_start = None
    
    def _on_canvas_motion(self, event):
        """画布移动事件"""
        # 更新坐标显示
        self.coord_label.config(text=f"坐标: ({event.x}, {event.y})")
    
    # ============================================
    # 图形选择和管理
    # ============================================
    
    def _select_shape_at(self, x, y):
        """选择指定位置的图形"""
        # 取消之前的选择
        self._cancel_selection()
        
        # 从后往前查找（后绘制的在上面）
        for shape in reversed(self.shapes):
            if shape.contains_point(x, y):
                shape.selected = True
                self.selected_shape = shape
                self._redraw_all()
                self.status_label.config(text=f"已选中图形 - 类型: {shape.shape_type}")
                return
        
        self.status_label.config(text="未选中任何图形")
    
    def _cancel_selection(self):
        """取消选择"""
        if self.selected_shape:
            self.selected_shape.selected = False
            self.selected_shape = None
            self._redraw_all()
    
    def _copy_shape(self):
        """复制选中的图形"""
        if not self.selected_shape:
            messagebox.showinfo("提示", "请先选择要复制的图形")
            return
        
        # 复制图形并向右下移动
        new_shape = TransformManager.copy(self.selected_shape)
        TransformManager.move(new_shape, 20, 20)
        self.shapes.append(new_shape)
        
        # 选中新图形
        self.selected_shape.selected = False
        new_shape.selected = True
        self.selected_shape = new_shape
        
        self._redraw_all()
        self._update_count()
        self.status_label.config(text="图形已复制")
    
    def _delete_shape(self):
        """删除选中的图形"""
        if not self.selected_shape:
            messagebox.showinfo("提示", "请先选择要删除的图形")
            return
        
        self.shapes.remove(self.selected_shape)
        self.selected_shape = None
        self._redraw_all()
        self._update_count()
        self.status_label.config(text="图形已删除")
    
    def _clear_canvas(self):
        """清空画布"""
        if self.shapes:
            if messagebox.askyesno("确认", "确定要清空画布吗？"):
                self.shapes.clear()
                self.selected_shape = None
                self._redraw_all()
                self._update_count()
                self.status_label.config(text="画布已清空")
    
    # ============================================
    # 图形变换
    # ============================================
    
    def _scale_shape_dialog(self):
        """缩放图形对话框"""
        if not self.selected_shape:
            messagebox.showinfo("提示", "请先选择要缩放的图形")
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("缩放图形")
        dialog.geometry("250x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="水平缩放比例:").pack(pady=5)
        sx_var = tk.DoubleVar(value=1.0)
        tk.Scale(dialog, from_=0.1, to=3.0, resolution=0.1, orient='horizontal', variable=sx_var).pack()
        
        tk.Label(dialog, text="垂直缩放比例:").pack(pady=5)
        sy_var = tk.DoubleVar(value=1.0)
        tk.Scale(dialog, from_=0.1, to=3.0, resolution=0.1, orient='horizontal', variable=sy_var).pack()
        
        def apply_scale():
            bounds = self.selected_shape.get_bounds()
            cx = (bounds[0] + bounds[2]) / 2
            cy = (bounds[1] + bounds[3]) / 2
            TransformManager.scale(self.selected_shape, cx, cy, sx_var.get(), sy_var.get())
            self._redraw_all()
            dialog.destroy()
        
        tk.Button(dialog, text="应用", command=apply_scale).pack(pady=10)
    
    def _rotate_shape_dialog(self):
        """旋转图形对话框"""
        if not self.selected_shape:
            messagebox.showinfo("提示", "请先选择要旋转的图形")
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("旋转图形")
        dialog.geometry("250x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="旋转角度（度）:").pack(pady=5)
        angle_var = tk.IntVar(value=45)
        tk.Scale(dialog, from_=-180, to=180, orient='horizontal', variable=angle_var).pack()
        
        def apply_rotate():
            bounds = self.selected_shape.get_bounds()
            cx = (bounds[0] + bounds[2]) / 2
            cy = (bounds[1] + bounds[3]) / 2
            TransformManager.rotate(self.selected_shape, cx, cy, angle_var.get())
            self._redraw_all()
            dialog.destroy()
        
        tk.Button(dialog, text="应用", command=apply_rotate).pack(pady=10)
    
    def _flip_shape(self, direction):
        """翻转图形"""
        if not self.selected_shape:
            messagebox.showinfo("提示", "请先选择要翻转的图形")
            return
        
        bounds = self.selected_shape.get_bounds()
        cx = (bounds[0] + bounds[2]) / 2
        cy = (bounds[1] + bounds[3]) / 2
        
        if direction == 'horizontal':
            # 水平翻转
            new_points = []
            for x, y in self.selected_shape.points:
                new_points.append((2 * cx - x, y))
            self.selected_shape.points = new_points
        else:
            # 垂直翻转
            new_points = []
            for x, y in self.selected_shape.points:
                new_points.append((x, 2 * cy - y))
            self.selected_shape.points = new_points
        
        self._redraw_all()
        self.status_label.config(text=f"图形已{'水平' if direction == 'horizontal' else '垂直'}翻转")
    
    # ============================================
    # 特殊曲线绘制
    # ============================================
    
    def _draw_sine_curve(self):
        """绘制正弦曲线"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("正弦曲线参数")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="振幅:").pack(pady=5)
        amp_var = tk.IntVar(value=50)
        tk.Scale(dialog, from_=10, to=150, orient='horizontal', variable=amp_var).pack()
        
        tk.Label(dialog, text="周期:").pack(pady=5)
        period_var = tk.IntVar(value=200)
        tk.Scale(dialog, from_=50, to=400, orient='horizontal', variable=period_var).pack()
        
        tk.Label(dialog, text="周期数:").pack(pady=5)
        cycles_var = tk.IntVar(value=2)
        tk.Scale(dialog, from_=1, to=5, orient='horizontal', variable=cycles_var).pack()
        
        def draw():
            # 获取画布中心位置
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            start_x = 50
            start_y = canvas_height // 2
            
            points = CurveGenerator.generate_sine_curve(
                start_x, start_y,
                amp_var.get(),
                period_var.get(),
                cycles_var.get()
            )
            
            shape = Shape('sine', points, self.current_color, self.current_width)
            self.shapes.append(shape)
            self._redraw_all()
            self._update_count()
            dialog.destroy()
        
        tk.Button(dialog, text="绘制", command=draw).pack(pady=10)
    
    def _draw_archimedean_spiral(self):
        """绘制阿基米德螺线"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("阿基米德螺线参数")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="内径参数 (a):").pack(pady=5)
        a_var = tk.IntVar(value=5)
        tk.Scale(dialog, from_=1, to=20, orient='horizontal', variable=a_var).pack()
        
        tk.Label(dialog, text="螺距参数 (b):").pack(pady=5)
        b_var = tk.IntVar(value=10)
        tk.Scale(dialog, from_=5, to=30, orient='horizontal', variable=b_var).pack()
        
        tk.Label(dialog, text="圈数:").pack(pady=5)
        turns_var = tk.IntVar(value=3)
        tk.Scale(dialog, from_=1, to=10, orient='horizontal', variable=turns_var).pack()
        
        def draw():
            # 获取画布中心位置
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            points = CurveGenerator.generate_archimedean_spiral(
                center_x, center_y,
                a_var.get(),
                b_var.get(),
                turns_var.get()
            )
            
            shape = Shape('spiral', points, self.current_color, self.current_width)
            self.shapes.append(shape)
            self._redraw_all()
            self._update_count()
            dialog.destroy()
        
        tk.Button(dialog, text="绘制", command=draw).pack(pady=10)
    
    # ============================================
    # 创意功能
    # ============================================
    
    def _fill_shape(self):
        """填充图形"""
        if not self.selected_shape:
            messagebox.showinfo("提示", "请先选择要填充的图形")
            return
        
        color = colorchooser.askcolor(title="选择填充颜色", initialcolor=self.current_color)
        if color[1]:
            self.selected_shape.fill_color = color[1]
            self._redraw_all()
            self.status_label.config(text="图形已填充")
    
    def _add_shadow(self):
        """为图形添加阴影效果"""
        if not self.selected_shape:
            messagebox.showinfo("提示", "请先选择要添加阴影的图形")
            return
        
        # 创建阴影图形
        shadow = TransformManager.copy(self.selected_shape)
        shadow.color = 'gray'
        shadow.width = self.selected_shape.width + 2
        TransformManager.move(shadow, 5, 5)
        
        # 将阴影插入到原图形之前
        index = self.shapes.index(self.selected_shape)
        self.shapes.insert(index, shadow)
        
        self._redraw_all()
        self._update_count()
        self.status_label.config(text="阴影已添加")
    
    def _generate_pattern(self):
        """生成装饰图案"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("生成图案")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="图案类型:").pack(pady=10)
        
        pattern_var = tk.StringVar(value="circle_pattern")
        patterns = [
            ("圆形图案", "circle_pattern"),
            ("星形图案", "star_pattern"),
            ("花瓣图案", "flower_pattern")
        ]
        
        for text, value in patterns:
            tk.Radiobutton(dialog, text=text, variable=pattern_var, value=value).pack()
        
        def generate():
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            pattern_type = pattern_var.get()
            
            if pattern_type == "circle_pattern":
                # 同心圆图案
                for r in range(20, 150, 20):
                    points = []
                    for i in range(361):
                        angle = math.radians(i)
                        x = center_x + r * math.cos(angle)
                        y = center_y + r * math.sin(angle)
                        points.append((x, y))
                    shape = Shape('circle', points, self.current_color, self.current_width)
                    self.shapes.append(shape)
            
            elif pattern_type == "star_pattern":
                # 五角星图案
                for rotation in range(0, 360, 30):
                    points = []
                    for i in range(11):
                        angle = math.radians(i * 36 + rotation)
                        r = 100 if i % 2 == 0 else 50
                        x = center_x + r * math.cos(angle - math.pi/2)
                        y = center_y + r * math.sin(angle - math.pi/2)
                        points.append((x, y))
                    shape = Shape('star', points, self.current_color, self.current_width)
                    self.shapes.append(shape)
            
            elif pattern_type == "flower_pattern":
                # 花瓣图案
                points = []
                for i in range(361):
                    angle = math.radians(i)
                    r = 80 * abs(math.sin(3 * angle))
                    x = center_x + r * math.cos(angle)
                    y = center_y + r * math.sin(angle)
                    points.append((x, y))
                shape = Shape('flower', points, self.current_color, self.current_width)
                self.shapes.append(shape)
            
            self._redraw_all()
            self._update_count()
            dialog.destroy()
        
        tk.Button(dialog, text="生成", command=generate).pack(pady=10)
    
    # ============================================
    # 文件操作
    # ============================================
    
    def _new_canvas(self):
        """新建画布"""
        if self.shapes:
            if messagebox.askyesno("确认", "当前画布未保存，是否新建？"):
                self.shapes.clear()
                self.selected_shape = None
                self._redraw_all()
                self._update_count()
                self.status_label.config(text="新建画布")
    
    def _save_file(self):
        """保存文件"""
        if not self.shapes:
            messagebox.showinfo("提示", "画布为空，无需保存")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filepath:
            if FileManager.save_to_file(self.shapes, filepath):
                self.status_label.config(text=f"文件已保存: {filepath}")
                messagebox.showinfo("成功", "文件保存成功！")
            else:
                messagebox.showerror("错误", "保存失败，请检查文件路径")
    
    def _open_file(self):
        """打开文件"""
        filepath = filedialog.askopenfilename(
            title="打开文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filepath:
            try:
                self.shapes = FileManager.load_from_file(filepath)
                self.selected_shape = None
                self._redraw_all()
                self._update_count()
                self.status_label.config(text=f"文件已打开: {filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {str(e)}")
    
    # ============================================
    # 绘制和更新
    # ============================================
    
    def _redraw_all(self):
        """重绘所有图形"""
        self.canvas.delete('all')
        
        for shape in self.shapes:
            self._draw_shape(shape)
    
    def _draw_shape(self, shape):
        """绘制单个图形"""
        if not shape.points:
            return
        
        # 准备坐标列表
        coords = []
        for point in shape.points:
            coords.extend(point)
        
        # 根据图形类型绘制
        if shape.shape_type == 'line':
            item = self.canvas.create_line(
                coords,
                fill=shape.color,
                width=shape.width
            )
        elif shape.shape_type == 'rectangle':
            item = self.canvas.create_polygon(
                coords,
                outline=shape.color,
                fill=shape.fill_color if shape.fill_color else '',
                width=shape.width
            )
        elif shape.shape_type == 'circle' or shape.shape_type == 'ellipse':
            item = self.canvas.create_polygon(
                coords,
                outline=shape.color,
                fill=shape.fill_color if shape.fill_color else '',
                width=shape.width
            )
        elif shape.shape_type == 'pencil':
            item = self.canvas.create_line(
                coords,
                fill=shape.color,
                width=shape.width,
                smooth=True
            )
        elif shape.shape_type == 'rainbow':
            # 彩虹画笔特殊处理
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
            item = None
        else:
            # 其他图形（正弦曲线、螺线等）
            item = self.canvas.create_line(
                coords,
                fill=shape.color,
                width=shape.width,
                smooth=True
            )
        
        # 如果图形被选中，绘制选择框
        if shape.selected:
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
                # 绘制控制点
                for x, y in [(bounds[0], bounds[1]), (bounds[2], bounds[1]),
                            (bounds[0], bounds[3]), (bounds[2], bounds[3])]:
                    self.canvas.create_oval(
                        x - 4, y - 4, x + 4, y + 4,
                        fill='blue'
                    )
    
    def _update_count(self):
        """更新图形数量"""
        self.count_label.config(text=f"图形数量: {len(self.shapes)}")
    
    # ============================================
    # 帮助信息
    # ============================================
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
绘图与图形管理软件 - 使用说明

【基本操作】
1. 选择左侧工具栏中的绘图工具
2. 在画布上拖拽鼠标绘制图形
3. 使用颜色面板和线宽滑块调整属性

【图形选择】
- 点击"选择"工具后，点击图形进行选择
- 选中后可拖拽移动图形
- 选中的图形会显示蓝色选择框

【图形变换】
- 复制：选中图形后按 Ctrl+C 或点击复制按钮
- 删除：选中图形后按 Delete 键或点击删除按钮
- 缩放：通过菜单"变换->缩放图形"
- 旋转：通过菜单"变换->旋转图形"
- 翻转：通过菜单"变换->水平/垂直翻转"

【特殊曲线】
- 通过菜单"特殊曲线"可一键生成正弦曲线、阿基米德螺线

【文件操作】
- 新建：Ctrl+N
- 打开：Ctrl+O
- 保存：Ctrl+S

【创意功能】
- 图形填充：为选中图形添加填充颜色
- 图形阴影：为选中图形添加阴影效果
- 彩虹画笔：绘制彩虹色渐变线条
- 生成图案：一键生成装饰性图案
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("500x500")
        
        text = tk.Text(help_window, wrap='word', padx=10, pady=10)
        text.pack(fill='both', expand=True)
        text.insert('1.0', help_text)
        text.config(state='disabled')
    
    def _show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于",
            "绘图与图形管理软件 v1.0\n\n"
            "功能特性：\n"
            "• 基本图形绘制（直线、矩形、圆形）\n"
            "• 图形变换（复制、缩放、旋转、移动、删除）\n"
            "• 特殊曲线（正弦曲线、阿基米德螺线）\n"
            "• 图形管理（保存、加载）\n"
            "• 创意工具（彩虹画笔、图案生成等）\n\n"
            "开发环境：Python 3.x + Tkinter\n\n"
            "© 2024 课程设计作品"
        )


# ============================================
# 主程序入口
# ============================================

def main():
    """主函数"""
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()