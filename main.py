#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绘图笔记本 - 书本风格绘图软件 v3.0
功能：书本风格界面、多页翻页、数学函数绘制、图片导入、OneNote风格工具
作者：课程设计团队
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import sys
import os
import math
import random
import colorsys
import copy
import json
try:
    from PIL import Image as PILImage, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from shapes import Shape, ShapeFactory, ShapeManager
from transforms import TransformManager, TransformHelper
from curves import CurveGenerator, CurvePresets
from file_manager import FileManager, BackupManager, ExportManager
from ui_components import (
    ToolbarPanel, ColorPanel, WidthPanel,
    StatusBar, MenuBar, DialogHelper, RainbowBrush
)

# ============================================
# 书本风格笔记本应用
# ============================================

class NotebookApp:
    """书本风格绘图笔记本"""

    # 书本配色方案
    BOOK_BG = '#f5f0e8'           # 书页背景(米白)
    BOOK_COVER = '#5d3a1a'        # 封面深棕
    BOOK_BINDING = '#8b6914'      # 书脊金色
    BOOK_ACCENT = '#c4a35a'       # 装饰金色
    BOOK_LINE = '#d4c5a9'         # 横线颜色
    PAGE_SHADOW = '#c8b896'       # 书页阴影
    SIDEBAR_BG = '#4a2c0f'        # 侧边栏深棕
    SIDEBAR_TEXT = '#e8d5a3'      # 侧边栏文字金色
    BUTTON_BG = '#6b4423'         # 按钮棕色
    BUTTON_ACTIVE = '#8b6914'     # 按钮激活金色
    BUTTON_TEXT = '#f5e6c8'       # 按钮文字
    CANVAS_BG = '#faf8f2'         # 画布背景

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("绘图笔记本 v3.0")
        self.root.geometry("1300x850")
        self.root.configure(bg=self.BOOK_COVER)

        # 核心组件
        self.shape_manager = ShapeManager()
        self.rainbow_brush = RainbowBrush()

        # 翻页系统
        self.pages = [[]]          # 每页的图形列表
        self.current_page = 0

        # 状态变量
        self.current_tool = 'pencil'
        self.current_color = '#2c1810'
        self.current_width = 3
        self.text_font_size = 20
        self.canvas_bg_mode = 'blank'  # blank / grid / lined / dot

        # 绘图状态
        self.is_drawing = False
        self.start_point = None
        self.temp_points = []
        self.temp_shape_ids = []
        self.temp_shape_id = None
        self.temp_spray_dots = []
        self.temp_rainbow_colors = []

        # 移动状态
        self.is_moving = False
        self.move_start = None

        # 撤销/重做
        self.undo_stack = []
        self.redo_stack = []
        self._push_undo()

        # 导入的图片
        self.imported_images = {}

        # 创建界面
        self._create_book_ui()
        self._bind_shortcuts()

    # ============================================
    # 书本风格UI
    # ============================================

    def _create_book_ui(self):
        """创建书本风格界面"""
        # 主容器 - 书本封面
        self.book_frame = tk.Frame(self.root, bg=self.BOOK_COVER, bd=0)
        self.book_frame.pack(fill='both', expand=True, padx=3, pady=3)

        # 顶部书脊装饰条
        top_bar = tk.Frame(self.book_frame, bg=self.BOOK_BINDING, height=4)
        top_bar.pack(fill='x', side='top')

        # 中间内容区
        content = tk.Frame(self.book_frame, bg=self.BOOK_COVER)
        content.pack(fill='both', expand=True, side='top')

        # 左侧书签侧边栏
        self._create_book_sidebar(content)

        # 右侧书页区域
        self._create_book_page(content)

        # 底部导航栏
        self._create_page_nav()

        # 底部状态栏
        self._create_book_statusbar()

        # 菜单栏
        self._create_book_menu()

    def _create_book_sidebar(self, parent):
        """创建书本风格侧边栏"""
        sidebar = tk.Frame(parent, bg=self.SIDEBAR_BG, width=180, bd=0)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # 书签标题装饰
        header_frame = tk.Frame(sidebar, bg=self.BOOK_BINDING, height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="📒 工具面板", font=('微软雅黑', 11, 'bold'),
                 bg=self.BOOK_BINDING, fg=self.SIDEBAR_TEXT).pack(expand=True)

        # 工具区域 - 可滚动
        tool_canvas = tk.Canvas(sidebar, bg=self.SIDEBAR_BG, highlightthickness=0, width=180)
        scrollbar = tk.Scrollbar(sidebar, orient='vertical', command=tool_canvas.yview)
        tool_frame = tk.Frame(tool_canvas, bg=self.SIDEBAR_BG)

        tool_frame.bind('<Configure>', lambda e: tool_canvas.configure(scrollregion=tool_canvas.bbox('all')))
        tool_canvas.create_window((0, 0), window=tool_frame, anchor='nw', width=180)
        tool_canvas.configure(yscrollcommand=scrollbar.set)

        # 绘图工具
        self._create_book_tools(tool_frame)

        # 颜色选择
        self._create_book_colors(tool_frame)

        # 线宽
        self._create_book_width(tool_frame)

        # 背景切换
        self._create_bg_switcher(tool_frame)

        tool_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        def _on_mousewheel(event):
            tool_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        tool_canvas.bind('<Enter>', lambda e: tool_canvas.bind_all('<MouseWheel>', _on_mousewheel))
        tool_canvas.bind('<Leave>', lambda e: tool_canvas.unbind_all('<MouseWheel>'))

    def _create_book_tools(self, parent):
        """创建书本工具按钮"""
        tk.Label(parent, text="━ 绘图工具 ━", font=('微软雅黑', 9),
                 bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))

        tools = [
            ('✏ 画笔', 'pencil', '自由绘制'),
            ('🖊 荧光笔', 'highlighter', '半透明标记'),
            ('✒ 书法笔', 'calligraphy', '书法效果'),
            ('📏 直线', 'line', '直线'),
            ('⬜ 矩形', 'rectangle', '矩形'),
            ('⭕ 椭圆', 'circle', '椭圆'),
            ('🎨 喷枪', 'spray', '喷漆'),
            ('🌈 彩虹', 'rainbow', '彩虹'),
            ('🔤 文字', 'text', '文字'),
            ('🧹 橡皮', 'eraser', '橡皮'),
            ('🖱 选择', 'select', '选择移动'),
        ]

        self.tool_buttons = {}
        for text, tool_id, tip in tools:
            btn = tk.Button(parent, text=text, width=14, anchor='w',
                          font=('微软雅黑', 9), relief='flat',
                          bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                          activebackground=self.BUTTON_ACTIVE, activeforeground='white',
                          cursor='hand2', padx=8,
                          command=lambda t=tool_id: self._on_tool_select(t))
            btn.pack(pady=1, padx=5)
            self.tool_buttons[tool_id] = btn

        self._update_tool_highlight('pencil')

    def _create_book_colors(self, parent):
        """创建书本颜色选择"""
        tk.Label(parent, text="━ 颜色 ━", font=('微软雅黑', 9),
                 bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))

        colors = [
            '#2c1810', '#e74c3c', '#e67e22', '#f1c40f',
            '#2ecc71', '#1abc9c', '#3498db', '#9b59b6',
            '#34495e', '#7f8c8d', '#ecf0f1', '#ffffff'
        ]

        color_frame = tk.Frame(parent, bg=self.SIDEBAR_BG)
        color_frame.pack(pady=2)

        for i, c in enumerate(colors):
            row, col = i // 4, i % 4
            btn = tk.Button(color_frame, bg=c, width=3, height=1,
                          relief='flat', bd=1, cursor='hand2',
                          command=lambda clr=c: self._on_color_pick(clr))
            btn.grid(row=row, column=col, padx=2, pady=2)

        # 自定义颜色按钮
        tk.Button(parent, text="🎨 自定义颜色...", font=('微软雅黑', 8),
                 bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, relief='flat',
                 activebackground=self.BUTTON_ACTIVE,
                 command=self._on_custom_color).pack(pady=4)

    def _create_book_width(self, parent):
        """创建线宽选择"""
        tk.Label(parent, text="━ 笔触粗细 ━", font=('微软雅黑', 9),
                 bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))

        width_frame = tk.Frame(parent, bg=self.SIDEBAR_BG)
        width_frame.pack(pady=2)

        self.width_var = tk.IntVar(value=3)
        widths = [1, 2, 3, 5, 8, 12, 16, 20]
        for i, w in enumerate(widths):
            row, col = i // 4, i % 4
            btn = tk.Button(width_frame, text=str(w), width=3, font=('微软雅黑', 8),
                          relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                          activebackground=self.BUTTON_ACTIVE,
                          command=lambda ww=w: self._on_width_set(ww))
            btn.grid(row=row, column=col, padx=2, pady=2)

        # 预览指示
        self.width_preview = tk.Canvas(parent, width=120, height=24,
                                       bg=self.SIDEBAR_BG, highlightthickness=0)
        self.width_preview.pack(pady=4)
        self._update_width_preview()

    def _create_bg_switcher(self, parent):
        """创建背景切换"""
        tk.Label(parent, text="━ 页面背景 ━", font=('微软雅黑', 9),
                 bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))

        bg_frame = tk.Frame(parent, bg=self.SIDEBAR_BG)
        bg_frame.pack(pady=2)

        modes = [('空白', 'blank'), ('网格', 'grid'), ('横线', 'lined'), ('点阵', 'dot')]
        for text, mode in modes:
            tk.Button(bg_frame, text=text, width=6, font=('微软雅黑', 8),
                     relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                     activebackground=self.BUTTON_ACTIVE,
                     command=lambda m=mode: self._on_bg_change(m)).pack(side='left', padx=1)

    def _create_book_page(self, parent):
        """创建书页区域"""
        # 页面容器
        page_container = tk.Frame(parent, bg=self.PAGE_SHADOW)
        page_container.pack(side='left', fill='both', expand=True, padx=(20, 20), pady=(20, 10))

        # 书页白边
        page_border = tk.Frame(page_container, bg='white', bd=0)
        page_border.pack(fill='both', expand=True, padx=1, pady=1)

        # 书页内边距
        page_inner = tk.Frame(page_border, bg=self.CANVAS_BG, bd=0)
        page_inner.pack(fill='both', expand=True, padx=3, pady=3)

        # 画布
        self.canvas = tk.Canvas(page_inner, bg=self.CANVAS_BG, cursor='cross',
                                highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # 鼠标事件
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<B1-Motion>', self._on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_canvas_release)
        self.canvas.bind('<Motion>', self._on_canvas_motion)
        self.canvas.bind('<Configure>', self._on_canvas_resize)

        # 绘制默认背景
        self._draw_page_background()

    def _create_page_nav(self):
        """创建页脚导航栏"""
        nav_frame = tk.Frame(self.book_frame, bg=self.BOOK_BINDING, height=36)
        nav_frame.pack(fill='x', side='bottom')
        nav_frame.pack_propagate(False)

        # 左区域 - 翻页按钮
        left_frame = tk.Frame(nav_frame, bg=self.BOOK_BINDING)
        left_frame.pack(side='left', padx=20)

        self.prev_btn = tk.Button(left_frame, text='◀ 上一页', font=('微软雅黑', 9),
                                  relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                                  activebackground=self.BUTTON_ACTIVE,
                                  command=self._on_prev_page)
        self.prev_btn.pack(side='left', padx=2)

        self.page_label = tk.Label(left_frame, text='第 1 页', font=('微软雅黑', 10, 'bold'),
                                   bg=self.BOOK_BINDING, fg=self.SIDEBAR_TEXT, width=10)
        self.page_label.pack(side='left', padx=10)

        self.next_btn = tk.Button(left_frame, text='下一页 ▶', font=('微软雅黑', 9),
                                  relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                                  activebackground=self.BUTTON_ACTIVE,
                                  command=self._on_next_page)
        self.next_btn.pack(side='left', padx=2)

        # 右区域 - 快速操作
        right_frame = tk.Frame(nav_frame, bg=self.BOOK_BINDING)
        right_frame.pack(side='right', padx=20)

        quick_actions = [
            ('📐 数学函数', self._on_math_function),
            ('🖼 导入图片', self._on_import_image),
            ('➕ 新建页', self._on_new_page),
            ('🗑 删除本页', self._on_delete_page),
        ]

        for text, cmd in quick_actions:
            tk.Button(right_frame, text=text, font=('微软雅黑', 9),
                     relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                     activebackground=self.BUTTON_ACTIVE,
                     command=cmd).pack(side='left', padx=2)

    def _create_book_statusbar(self):
        """创建状态栏"""
        status_frame = tk.Frame(self.book_frame, bg='#3a1f0a', height=22)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)

        self.status_text = tk.StringVar(value="📖 就绪 - 请选择工具开始绘图")
        tk.Label(status_frame, textvariable=self.status_text, font=('微软雅黑', 8),
                bg='#3a1f0a', fg=self.BOOK_ACCENT, anchor='w', padx=10).pack(side='left', fill='x', expand=True)

        self.coord_text = tk.StringVar(value="")
        tk.Label(status_frame, textvariable=self.coord_text, font=('微软雅黑', 8),
                bg='#3a1f0a', fg=self.BOOK_ACCENT, padx=10).pack(side='right')

        self.count_text = tk.StringVar(value="0个图形")
        tk.Label(status_frame, textvariable=self.count_text, font=('微软雅黑', 8),
                bg='#3a1f0a', fg=self.BOOK_ACCENT, padx=10).pack(side='right')

    def _create_book_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root, bg=self.BOOK_COVER, fg=self.BUTTON_TEXT,
                         activebackground=self.BUTTON_ACTIVE, activeforeground='white',
                         font=('微软雅黑', 9))

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0, font=('微软雅黑', 9))
        menubar.add_cascade(label='📁 文件', menu=file_menu)
        file_menu.add_command(label='新建笔记本', command=self._on_new_notebook, accelerator='Ctrl+N')
        file_menu.add_command(label='打开文件', command=self._on_open_file, accelerator='Ctrl+O')
        file_menu.add_command(label='保存文件', command=self._on_save_file, accelerator='Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label='导入图片', command=self._on_import_image)
        file_menu.add_command(label='导出为文本', command=self._on_export_text)
        file_menu.add_command(label='导出统计摘要', command=self._on_export_summary)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.root.quit)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0, font=('微软雅黑', 9))
        menubar.add_cascade(label='✂ 编辑', menu=edit_menu)
        edit_menu.add_command(label='撤销', command=self._on_undo, accelerator='Ctrl+Z')
        edit_menu.add_command(label='重做', command=self._on_redo, accelerator='Ctrl+Y')
        edit_menu.add_separator()
        edit_menu.add_command(label='复制图形', command=self._on_copy_shape, accelerator='Ctrl+C')
        edit_menu.add_command(label='删除图形', command=self._on_delete_shape, accelerator='Delete')
        edit_menu.add_command(label='清空本页', command=self._on_clear_canvas)

        # 页面菜单
        page_menu = tk.Menu(menubar, tearoff=0, font=('微软雅黑', 9))
        menubar.add_cascade(label='📄 页面', menu=page_menu)
        page_menu.add_command(label='新建页面', command=self._on_new_page)
        page_menu.add_command(label='删除本页', command=self._on_delete_page)
        page_menu.add_command(label='上一页', command=self._on_prev_page)
        page_menu.add_command(label='下一页', command=self._on_next_page)
        page_menu.add_separator()
        page_menu.add_command(label='空白背景', command=lambda: self._on_bg_change('blank'))
        page_menu.add_command(label='网格背景', command=lambda: self._on_bg_change('grid'))
        page_menu.add_command(label='横线背景', command=lambda: self._on_bg_change('lined'))
        page_menu.add_command(label='点阵背景', command=lambda: self._on_bg_change('dot'))

        # 数学菜单
        math_menu = tk.Menu(menubar, tearoff=0, font=('微软雅黑', 9))
        menubar.add_cascade(label='📐 数学', menu=math_menu)
        math_menu.add_command(label='y=f(x) 函数图像', command=lambda: self._on_math_function())
        math_menu.add_command(label='参数方程', command=lambda: self._on_parametric_equation())
        math_menu.add_command(label='极坐标方程', command=lambda: self._on_polar_equation())
        math_menu.add_separator()
        math_menu.add_command(label='正弦曲线', command=self._on_draw_sine_curve)
        math_menu.add_command(label='阿基米德螺线', command=self._on_draw_spiral)
        math_menu.add_command(label='心形曲线', command=self._on_draw_heart)
        math_menu.add_command(label='利萨如曲线', command=self._on_draw_lissajous)
        math_menu.add_command(label='花瓣曲线', command=self._on_draw_flower)

        # 变换菜单
        transform_menu = tk.Menu(menubar, tearoff=0, font=('微软雅黑', 9))
        menubar.add_cascade(label='🔄 变换', menu=transform_menu)
        transform_menu.add_command(label='缩放', command=self._on_scale_shape)
        transform_menu.add_command(label='旋转', command=self._on_rotate_shape)
        transform_menu.add_command(label='水平翻转', command=lambda: self._on_flip_shape('horizontal'))
        transform_menu.add_command(label='垂直翻转', command=lambda: self._on_flip_shape('vertical'))
        transform_menu.add_separator()
        transform_menu.add_command(label='填充颜色', command=self._on_fill_shape)
        transform_menu.add_command(label='添加阴影', command=self._on_add_shadow)
        transform_menu.add_command(label='生成图案', command=self._on_generate_pattern)

        # 帮助
        help_menu = tk.Menu(menubar, tearoff=0, font=('微软雅黑', 9))
        menubar.add_cascade(label='❓ 帮助', menu=help_menu)
        help_menu.add_command(label='使用说明', command=self._on_show_help)
        help_menu.add_command(label='关于', command=self._on_show_about)

        self.root.config(menu=menubar)

    # ============================================
    # 页面管理
    # ============================================

    def _on_new_page(self):
        """新建页面"""
        self.pages[self.current_page] = self.shape_manager.shapes
        self.pages.insert(self.current_page + 1, [])
        self.current_page += 1
        self._switch_to_page(self.current_page)

    def _on_delete_page(self):
        """删除当前页"""
        if len(self.pages) <= 1:
            self.pages[0] = []
            self.shape_manager.shapes = []
            self.shape_manager.deselect_all()
            self._redraw_all()
            self._update_status()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self._push_undo()
            return
        del self.pages[self.current_page]
        if self.current_page >= len(self.pages):
            self.current_page = len(self.pages) - 1
        self._switch_to_page(self.current_page)

    def _on_prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.pages[self.current_page] = self.shape_manager.shapes
            self._switch_to_page(self.current_page - 1)

    def _on_next_page(self):
        """下一页"""
        if self.current_page < len(self.pages) - 1:
            self.pages[self.current_page] = self.shape_manager.shapes
            self._switch_to_page(self.current_page + 1)

    def _switch_to_page(self, page_idx):
        """切换到指定页面"""
        self.current_page = page_idx
        self.shape_manager.shapes = self.pages[self.current_page]
        self.shape_manager.deselect_all()
        self._redraw_all()
        self._update_status()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._push_undo()

    # ============================================
    # 工具和属性
    # ============================================

    def _on_tool_select(self, tool):
        """选择工具"""
        self.current_tool = tool
        self._update_tool_highlight(tool)

        tool_names = {
            'pencil': '画笔', 'highlighter': '荧光笔', 'calligraphy': '书法笔',
            'line': '直线', 'rectangle': '矩形', 'circle': '椭圆',
            'spray': '喷枪', 'rainbow': '彩虹', 'text': '文字',
            'eraser': '橡皮', 'select': '选择'
        }

        if tool == 'rainbow':
            self.rainbow_brush.reset()

        if tool == 'text':
            self.canvas.config(cursor='xterm')
        elif tool == 'select':
            self.canvas.config(cursor='hand2')
        else:
            self.canvas.config(cursor='cross')

        self.status_text.set(f"📖 当前工具: {tool_names.get(tool, tool)}")

    def _update_tool_highlight(self, active_tool):
        """更新工具按钮高亮"""
        for tid, btn in self.tool_buttons.items():
            if tid == active_tool:
                btn.config(bg=self.BUTTON_ACTIVE, fg='white')
            else:
                btn.config(bg=self.BUTTON_BG, fg=self.BUTTON_TEXT)

    def _on_color_pick(self, color):
        """选择颜色"""
        self.current_color = color
        self.status_text.set(f"📖 当前颜色: {color}")

    def _on_custom_color(self):
        """自定义颜色"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="选择颜色", initialcolor=self.current_color)
        if color[1]:
            self.current_color = color[1]
            self.status_text.set(f"📖 当前颜色: {color[1]}")

    def _on_width_set(self, width):
        """设置线宽"""
        self.current_width = width
        self.width_var.set(width)
        self._update_width_preview()
        self.status_text.set(f"📖 笔触粗细: {width}px")

    def _update_width_preview(self):
        """更新线宽预览"""
        self.width_preview.delete('all')
        w = self.current_width
        self.width_preview.create_line(10, 12, 110, 12, fill=self.BUTTON_TEXT,
                                       width=min(w, 10), capstyle='round')

    def _on_bg_change(self, mode):
        """切换背景"""
        self.canvas_bg_mode = mode
        self._draw_page_background()
        self._redraw_all()

    def _draw_page_background(self):
        """绘制页面背景"""
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 50 or ch < 50:
            return

        self.canvas.delete('bg_decor')

        if self.canvas_bg_mode == 'grid':
            for x in range(0, cw, 30):
                self.canvas.create_line(x, 0, x, ch, fill='#e8e0d0',
                                        tags='bg_decor')
            for y in range(0, ch, 30):
                self.canvas.create_line(0, y, cw, y, fill='#e8e0d0',
                                        tags='bg_decor')

        elif self.canvas_bg_mode == 'lined':
            for y in range(30, ch, 30):
                self.canvas.create_line(0, y, cw, y, fill='#d8d0c0',
                                        tags='bg_decor', width=1)
            self.canvas.create_line(40, 0, 40, ch, fill='#f0c0c0',
                                    tags='bg_decor', width=1, dash=(2, 4))

        elif self.canvas_bg_mode == 'dot':
            for x in range(0, cw, 20):
                for y in range(0, ch, 20):
                    self.canvas.create_oval(x-1, y-1, x+1, y+1,
                                            fill='#d0c8b8', outline='',
                                            tags='bg_decor')

    def _on_canvas_resize(self, event):
        """画布大小改变"""
        if hasattr(self, '_resize_after_id'):
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(100, self._delayed_resize)

    def _delayed_resize(self):
        """延迟重绘(防抖)"""
        self._draw_page_background()
        self._redraw_all()

    # ============================================
    # 快捷键
    # ============================================

    def _bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self._on_new_notebook())
        self.root.bind('<Control-s>', lambda e: self._on_save_file())
        self.root.bind('<Control-o>', lambda e: self._on_open_file())
        self.root.bind('<Control-z>', lambda e: self._on_undo())
        self.root.bind('<Control-y>', lambda e: self._on_redo())
        self.root.bind('<Control-c>', lambda e: self._on_copy_shape())
        self.root.bind('<Delete>', lambda e: self._on_delete_shape())
        self.root.bind('<Escape>', lambda e: self._cancel_selection())
        self.root.bind('<Control-Prior>', lambda e: self._on_prev_page())
        self.root.bind('<Control-Next>', lambda e: self._on_next_page())

    # ============================================
    # 鼠标事件
    # ============================================

    def _on_canvas_click(self, event):
        x, y = event.x, event.y

        if self.current_tool == 'select':
            self._select_shape_at(x, y)
            if self.shape_manager.selected_shape:
                self.is_moving = True
                self.move_start = (x, y)
        elif self.current_tool == 'text':
            self._place_text(x, y)
        else:
            self.is_drawing = True
            self.start_point = (x, y)
            self.temp_points = [(x, y)]
            self.temp_spray_dots.clear()
            self.temp_rainbow_colors.clear()
            if self.current_tool == 'rainbow':
                self.rainbow_brush.reset()

    def _on_canvas_drag(self, event):
        x, y = event.x, event.y

        if self.is_drawing:
            self._handle_drawing_drag(x, y)
        elif self.is_moving and self.shape_manager.selected_shape:
            dx = x - self.move_start[0]
            dy = y - self.move_start[1]
            TransformManager.move(self.shape_manager.selected_shape, dx, dy)
            self.move_start = (x, y)
            self._redraw_all()

    def _on_canvas_release(self, event):
        x, y = event.x, event.y

        if self.is_drawing:
            self._finalize_drawing(x, y)
            self.is_drawing = False

        self.is_moving = False
        self.move_start = None
        self._update_status()

    def _on_canvas_motion(self, event):
        self.coord_text.set(f"({event.x}, {event.y})")

    def _handle_drawing_drag(self, x, y):
        """处理绘图拖拽"""
        if self.current_tool in ('line', 'rectangle', 'circle'):
            if self.temp_shape_id:
                self.canvas.delete(self.temp_shape_id)

        if self.current_tool == 'line':
            self.temp_shape_id = self.canvas.create_line(
                self.start_point[0], self.start_point[1], x, y,
                fill=self.current_color, width=self.current_width,
                capstyle='round')

        elif self.current_tool == 'rectangle':
            self.temp_shape_id = self.canvas.create_rectangle(
                self.start_point[0], self.start_point[1], x, y,
                outline=self.current_color, width=self.current_width)

        elif self.current_tool == 'circle':
            cx = (self.start_point[0] + x) / 2
            cy = (self.start_point[1] + y) / 2
            rx = abs(x - self.start_point[0]) / 2
            ry = abs(y - self.start_point[1]) / 2
            self.temp_shape_id = self.canvas.create_oval(
                cx - rx, cy - ry, cx + rx, cy + ry,
                outline=self.current_color, width=self.current_width)

        elif self.current_tool == 'pencil':
            self.temp_points.append((x, y))
            if len(self.temp_points) > 1:
                seg_id = self.canvas.create_line(
                    self.temp_points[-2][0], self.temp_points[-2][1],
                    self.temp_points[-1][0], self.temp_points[-1][1],
                    fill=self.current_color, width=self.current_width,
                    capstyle='round', joinstyle='round')
                self.temp_shape_ids.append(seg_id)

        elif self.current_tool == 'highlighter':
            self.temp_points.append((x, y))
            if len(self.temp_points) > 1:
                seg_id = self.canvas.create_line(
                    self.temp_points[-2][0], self.temp_points[-2][1],
                    self.temp_points[-1][0], self.temp_points[-1][1],
                    fill=self.current_color, width=self.current_width * 4,
                    capstyle='round', joinstyle='round', stipple='gray25')
                self.temp_shape_ids.append(seg_id)

        elif self.current_tool == 'calligraphy':
            self.temp_points.append((x, y))
            if len(self.temp_points) > 1:
                x1, y1 = self.temp_points[-2]
                x2, y2 = self.temp_points[-1]
                seg_id = self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=self.current_color,
                    width=self.current_width,
                    capstyle='round', joinstyle='round')
                self.temp_shape_ids.append(seg_id)
                if len(self.temp_points) > 3:
                    px, py = self.temp_points[-3]
                    angle = math.atan2(y2 - y1, x2 - x1)
                    ox = math.cos(angle + math.pi / 2) * self.current_width * 0.5
                    oy = math.sin(angle + math.pi / 2) * self.current_width * 0.5
                    poly_id = self.canvas.create_polygon(
                        x1 + ox, y1 + oy, x2 + ox, y2 + oy,
                        x2 - ox, y2 - oy, x1 - ox, y1 - oy,
                        fill=self.current_color, outline='')
                    self.temp_shape_ids.append(poly_id)

        elif self.current_tool == 'rainbow':
            self.temp_points.append((x, y))
            if len(self.temp_points) > 1:
                color = self.rainbow_brush.get_next_color()
                self.temp_rainbow_colors.append(color)
                seg_id = self.canvas.create_line(
                    self.temp_points[-2][0], self.temp_points[-2][1],
                    self.temp_points[-1][0], self.temp_points[-1][1],
                    fill=color, width=self.current_width,
                    capstyle='round', joinstyle='round')
                self.temp_shape_ids.append(seg_id)

        elif self.current_tool == 'spray':
            self.temp_points.append((x, y))
            for _ in range(random.randint(3, 8)):
                ox = random.randint(-self.current_width * 3, self.current_width * 3)
                oy = random.randint(-self.current_width * 3, self.current_width * 3)
                dot_id = self.canvas.create_oval(
                    x + ox, y + oy, x + ox + 2, y + oy + 2,
                    fill=self.current_color, outline='')
                self.temp_shape_ids.append(dot_id)
                self.temp_spray_dots.append((x + ox, y + oy))

        elif self.current_tool == 'eraser':
            es = self.current_width * 5
            eraser_id = self.canvas.create_rectangle(
                x - es, y - es, x + es, y + es,
                fill=self.CANVAS_BG, outline=self.CANVAS_BG)
            self.temp_shape_ids.append(eraser_id)

    def _finalize_drawing(self, x, y):
        """完成绘图"""
        if self.temp_shape_id:
            self.canvas.delete(self.temp_shape_id)
            self.temp_shape_id = None
        for tid in self.temp_shape_ids:
            self.canvas.delete(tid)
        self.temp_shape_ids.clear()
        self.temp_spray_dots.clear()
        self.temp_rainbow_colors.clear()

        if self.current_tool == 'line':
            shape = ShapeFactory.create_line(self.start_point, (x, y),
                                             self.current_color, self.current_width)
        elif self.current_tool == 'rectangle':
            shape = ShapeFactory.create_rectangle(self.start_point, (x, y),
                                                   self.current_color, self.current_width)
        elif self.current_tool == 'circle':
            cx = (self.start_point[0] + x) / 2
            cy = (self.start_point[1] + y) / 2
            rx = abs(x - self.start_point[0]) / 2
            ry = abs(y - self.start_point[1]) / 2
            shape = ShapeFactory.create_ellipse((cx, cy), rx, ry,
                                                 self.current_color, self.current_width)
        elif self.current_tool in ('pencil', 'highlighter', 'calligraphy') and len(self.temp_points) > 1:
            shape = Shape(self.current_tool, self.temp_points.copy(),
                         self.current_color, self.current_width)
        elif self.current_tool == 'rainbow' and len(self.temp_points) > 1:
            shape = Shape('rainbow', self.temp_points.copy(),
                         self.current_color, self.current_width)
            shape.rainbow_colors = self.temp_rainbow_colors.copy()
        elif self.current_tool == 'spray' and len(self.temp_points) > 0:
            shape = Shape('spray', self.temp_points.copy(),
                         self.current_color, self.current_width)
            shape.spray_dots = self.temp_spray_dots.copy()
        else:
            return

        self.shape_manager.add_shape(shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._push_undo()

    def _place_text(self, x, y):
        """放置文字"""
        text = simpledialog.askstring("输入文字", "请输入文字内容:", parent=self.root)
        if text:
            shape = Shape('text', [(x, y)], self.current_color, self.current_width)
            shape.text_content = text
            shape.text_font_size = self.text_font_size
            self.shape_manager.add_shape(shape)
            self.pages[self.current_page] = self.shape_manager.shapes
            self._redraw_all()
            self._update_status()
            self._push_undo()

    # ============================================
    # 图形选择和管理
    # ============================================

    def _select_shape_at(self, x, y):
        shape = self.shape_manager.get_shape_at(x, y)
        if shape:
            self.shape_manager.select_shape(shape)
            self.status_text.set(f"📖 已选中: {shape.shape_type}")
        else:
            self.shape_manager.deselect_all()
            self.status_text.set("📖 未选中图形")
        self._redraw_all()

    def _cancel_selection(self):
        self.shape_manager.deselect_all()
        self._redraw_all()

    # ============================================
    # 撤销/重做
    # ============================================

    def _push_undo(self):
        state = copy.deepcopy(self.shape_manager.shapes)
        self.undo_stack.append(state)
        self.redo_stack.clear()
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def _on_undo(self):
        if len(self.undo_stack) <= 1:
            self.status_text.set("📖 没有可撤销的操作")
            return
        current = self.undo_stack.pop()
        self.redo_stack.append(current)
        self.shape_manager.shapes = copy.deepcopy(self.undo_stack[-1])
        self.pages[self.current_page] = self.shape_manager.shapes
        self.shape_manager.deselect_all()
        self._redraw_all()
        self._update_status()
        self.status_text.set("📖 已撤销")

    def _on_redo(self):
        if not self.redo_stack:
            self.status_text.set("📖 没有可重做的操作")
            return
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        self.shape_manager.shapes = copy.deepcopy(state)
        self.pages[self.current_page] = self.shape_manager.shapes
        self.shape_manager.deselect_all()
        self._redraw_all()
        self._update_status()
        self.status_text.set("📖 已重做")

    # ============================================
    # 文件操作
    # ============================================

    def _on_new_notebook(self):
        if any(len(p) > 0 for p in self.pages):
            if not messagebox.askyesno("确认", "确定要新建笔记本吗？"):
                return
        self.pages = [[]]
        self.current_page = 0
        self.shape_manager.shapes = []
        self.imported_images.clear()
        self.undo_stack = []
        self.redo_stack = []
        self._push_undo()
        self._redraw_all()
        self._update_status()

    def _on_save_file(self):
        filepath = filedialog.asksaveasfilename(
            title="保存笔记本",
            defaultextension=".nb.json",
            filetypes=[("笔记本文件", "*.nb.json"), ("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filepath:
            serializable_pages = []
            for page in self.pages:
                serializable_pages.append([s.to_dict() for s in page])
            data = {
                'version': '3.0',
                'pages': serializable_pages,
                'current_page': self.current_page,
                'bg_mode': self.canvas_bg_mode
            }
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.status_text.set(f"📖 已保存: {filepath}")
                messagebox.showinfo("成功", "笔记本保存成功！")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

    def _on_open_file(self):
        filepath = filedialog.askopenfilename(
            title="打开笔记本",
            filetypes=[("笔记本文件", "*.nb.json"), ("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'pages' in data:
                    self.pages = []
                    self.imported_images.clear()
                    for page_data in data['pages']:
                        page_shapes = []
                        for sd in page_data:
                            shape = Shape.from_dict(sd)
                            page_shapes.append(shape)
                            if shape.shape_type == 'image' and hasattr(shape, 'image_path'):
                                self._reload_image_for_shape(shape)
                        self.pages.append(page_shapes)
                    self.current_page = data.get('current_page', 0)
                    self.canvas_bg_mode = data.get('bg_mode', 'blank')
                    self._switch_to_page(self.current_page)
                    self._draw_page_background()
                    self.status_text.set(f"📖 已打开: {filepath}")
                else:
                    shapes = [Shape.from_dict(s) for s in data.get('shapes', [])]
                    self.pages = [shapes]
                    self.current_page = 0
                    self._switch_to_page(0)
                    self.status_text.set(f"📖 已导入: {filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {str(e)}")

    def _on_export_text(self):
        if self.shape_manager.count() == 0:
            messagebox.showinfo("提示", "画布为空")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")]
        )
        if filepath:
            ExportManager.export_to_text(self.shape_manager.shapes, filepath)
            self.status_text.set(f"📖 已导出: {filepath}")

    def _on_export_summary(self):
        if self.shape_manager.count() == 0:
            messagebox.showinfo("提示", "画布为空")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")]
        )
        if filepath:
            ExportManager.export_summary(self.shape_manager.shapes, filepath)
            self.status_text.set(f"📖 摘要已导出: {filepath}")

    # ============================================
    # 编辑操作
    # ============================================

    def _on_copy_shape(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected:
            messagebox.showinfo("提示", "请先选择图形")
            return
        new_shape = TransformManager.copy_and_offset(selected, 20, 20)
        self.shape_manager.add_shape(new_shape)
        self.shape_manager.select_shape(new_shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    def _on_delete_shape(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected:
            messagebox.showinfo("提示", "请先选择图形")
            return
        self.shape_manager.remove_shape(selected)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    def _on_clear_canvas(self):
        if self.shape_manager.count() > 0:
            if messagebox.askyesno("确认", "确定要清空本页吗？"):
                self.shape_manager.clear_all()
                self.pages[self.current_page] = []
                self._redraw_all()
                self._update_status()
                self._push_undo()

    # ============================================
    # 数学函数绘制
    # ============================================

    def _on_math_function(self):
        """y=f(x) 函数图像绘制"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📐 绘制 y=f(x) 函数图像")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.CANVAS_BG)

        tk.Label(dialog, text="y = f(x) 函数图像绘制", font=('微软雅黑', 14, 'bold'),
                 bg=self.CANVAS_BG).pack(pady=10)

        # 函数表达式
        tk.Label(dialog, text="函数表达式 (使用x作为变量):", font=('微软雅黑', 10),
                 bg=self.CANVAS_BG).pack(pady=(10, 2))
        tk.Label(dialog, text="示例: sin(x), x**2, 2*x+1, cos(x)*10, abs(x)", font=('微软雅黑', 8),
                 fg='gray', bg=self.CANVAS_BG).pack()

        expr_var = tk.StringVar(value='sin(x)')
        tk.Entry(dialog, textvariable=expr_var, font=('Consolas', 14), width=30,
                justify='center').pack(pady=5, ipady=3)

        # 预设函数
        presets_frame = tk.Frame(dialog, bg=self.CANVAS_BG)
        presets_frame.pack(pady=5)
        presets = [
            ('sin(x)', 'sin'), ('cos(x)', 'cos'), ('tan(x)', 'tan'),
            ('x**2', 'x²'), ('x**3', 'x³'), ('sqrt(abs(x))', '√|x|'),
            ('1/x', '1/x'), ('exp(x)', 'eˣ'), ('log(abs(x))', 'ln|x|'),
        ]
        for label, expr_name in presets:
            tk.Button(presets_frame, text=expr_name, font=('微软雅黑', 8),
                     relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                     command=lambda e=label: expr_var.set(e)).pack(side='left', padx=2)

        # 参数
        params_frame = tk.Frame(dialog, bg=self.CANVAS_BG)
        params_frame.pack(pady=10)

        tk.Label(params_frame, text="x范围:", bg=self.CANVAS_BG).grid(row=0, column=0)
        xmin_var = tk.DoubleVar(value=-10)
        xmax_var = tk.DoubleVar(value=10)
        tk.Scale(params_frame, from_=-20, to=0, variable=xmin_var, orient='horizontal',
                length=150, bg=self.CANVAS_BG).grid(row=0, column=1)
        tk.Scale(params_frame, from_=0, to=20, variable=xmax_var, orient='horizontal',
                length=150, bg=self.CANVAS_BG).grid(row=0, column=2)
        tk.Label(params_frame, textvariable=xmin_var, bg=self.CANVAS_BG, width=4).grid(row=0, column=3)
        tk.Label(params_frame, text="~", bg=self.CANVAS_BG).grid(row=0, column=4)
        tk.Label(params_frame, textvariable=xmax_var, bg=self.CANVAS_BG, width=4).grid(row=0, column=5)

        tk.Label(params_frame, text="步长:", bg=self.CANVAS_BG).grid(row=1, column=0, pady=5)
        step_var = tk.DoubleVar(value=0.1)
        step_scale = tk.Scale(params_frame, from_=0.01, to=1.0, resolution=0.01,
                              variable=step_var, orient='horizontal', length=300,
                              bg=self.CANVAS_BG)
        step_scale.grid(row=1, column=1, columnspan=5)

        def draw_function():
            try:
                expr = expr_var.get()
                xmin = xmin_var.get()
                xmax = xmax_var.get()
                step = step_var.get()

                cw = self.canvas.winfo_width()
                ch = self.canvas.winfo_height()
                cx = cw // 2
                cy = ch // 2

                scale_x = (cw - 100) / (xmax - xmin)
                scale_y = 30

                safe_globals = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                    'sqrt': math.sqrt, 'abs': abs, 'exp': math.exp,
                    'log': math.log, 'log10': math.log10,
                    'pi': math.pi, 'e': math.e,
                    'ceil': math.ceil, 'floor': math.floor,
                    'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
                }

                points = []
                x = xmin
                while x <= xmax:
                    try:
                        y = eval(expr, {"__builtins__": {}}, {**safe_globals, 'x': x})
                        if isinstance(y, (int, float)) and abs(y) < 1e6:
                            px = cx + x * scale_x
                            py = cy - y * scale_y
                            if 0 <= px <= cw and 0 <= py <= ch:
                                points.append((px, py))
                    except:
                        pass
                    x += step

                if points:
                    shape = Shape('function', points, self.current_color, self.current_width)
                    shape.function_expr = expr
                    self.shape_manager.add_shape(shape)
                    self.pages[self.current_page] = self.shape_manager.shapes
                    self._redraw_all()
                    self._update_status()
                    self._push_undo()
                    self.status_text.set(f"📖 已绘制: y = {expr}")
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "无法计算函数，请检查表达式", parent=dialog)
            except Exception as e:
                messagebox.showerror("错误", f"表达式错误: {str(e)}", parent=dialog)

        tk.Button(dialog, text="📐 绘制函数图像", font=('微软雅黑', 12, 'bold'),
                 bg=self.BUTTON_ACTIVE, fg='white', relief='flat',
                 padx=30, pady=8, cursor='hand2',
                 command=draw_function).pack(pady=15)

        tk.Button(dialog, text="取消", font=('微软雅黑', 9),
                 command=dialog.destroy).pack()

    def _on_parametric_equation(self):
        """参数方程绘制"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📐 参数方程绘制")
        dialog.geometry("500x380")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.CANVAS_BG)

        tk.Label(dialog, text="参数方程: x(t), y(t)", font=('微软雅黑', 14, 'bold'),
                 bg=self.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="x(t) =", font=('微软雅黑', 10), bg=self.CANVAS_BG).pack()
        x_var = tk.StringVar(value='16*sin(t)**3')
        tk.Entry(dialog, textvariable=x_var, font=('Consolas', 12), width=30,
                justify='center').pack(pady=3, ipady=2)

        tk.Label(dialog, text="y(t) =", font=('微软雅黑', 10), bg=self.CANVAS_BG).pack()
        y_var = tk.StringVar(value='13*cos(t)-5*cos(2*t)-2*cos(3*t)-cos(4*t)')
        tk.Entry(dialog, textvariable=y_var, font=('Consolas', 12), width=30,
                justify='center').pack(pady=3, ipady=2)

        tk.Label(dialog, text="t范围: 0 ~", font=('微软雅黑', 10), bg=self.CANVAS_BG).pack(pady=5)
        tmax_var = tk.DoubleVar(value=2 * math.pi)
        tk.Scale(dialog, from_=math.pi, to=10 * math.pi, resolution=0.1,
                variable=tmax_var, orient='horizontal', length=300,
                bg=self.CANVAS_BG).pack()

        def draw_parametric():
            try:
                safe_globals = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'sqrt': math.sqrt, 'abs': abs, 'exp': math.exp,
                    'log': math.log, 'pi': math.pi, 'e': math.e,
                }
                cw = self.canvas.winfo_width()
                ch = self.canvas.winfo_height()
                points = []
                t = 0
                while t <= tmax_var.get():
                    try:
                        xt = eval(x_var.get(), {"__builtins__": {}}, {**safe_globals, 't': t})
                        yt = eval(y_var.get(), {"__builtins__": {}}, {**safe_globals, 't': t})
                        px = cw // 2 + xt * 2
                        py = ch // 2 - yt * 2
                        if 0 <= px <= cw and 0 <= py <= ch:
                            points.append((px, py))
                    except:
                        pass
                    t += 0.02

                if points:
                    shape = Shape('parametric', points, self.current_color, self.current_width)
                    self.shape_manager.add_shape(shape)
                    self.pages[self.current_page] = self.shape_manager.shapes
                    self._redraw_all()
                    self._update_status()
                    self._push_undo()
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"表达式错误: {str(e)}", parent=dialog)

        tk.Button(dialog, text="📐 绘制参数方程", font=('微软雅黑', 12, 'bold'),
                 bg=self.BUTTON_ACTIVE, fg='white', relief='flat',
                 padx=30, pady=8, command=draw_parametric).pack(pady=15)

    def _on_polar_equation(self):
        """极坐标方程绘制"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📐 极坐标方程绘制")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.CANVAS_BG)

        tk.Label(dialog, text="极坐标: r = f(θ)", font=('微软雅黑', 14, 'bold'),
                 bg=self.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="r(θ) =", font=('微软雅黑', 10), bg=self.CANVAS_BG).pack()
        tk.Label(dialog, text="示例: 2*(1+cos(theta)), 3*sin(2*theta), 2*theta", font=('微软雅黑', 8),
                 fg='gray', bg=self.CANVAS_BG).pack()

        r_var = tk.StringVar(value='2*(1+cos(theta))')
        tk.Entry(dialog, textvariable=r_var, font=('Consolas', 12), width=30,
                justify='center').pack(pady=5, ipady=2)

        presets_frame = tk.Frame(dialog, bg=self.CANVAS_BG)
        presets_frame.pack(pady=5)
        for label, expr in [
            ('心形线', '2*(1+cos(theta))'),
            ('三叶草', '3*sin(2*theta)'),
            ('阿基米德', 'theta/3'),
            ('玫瑰线', '4*sin(3*theta)'),
        ]:
            tk.Button(presets_frame, text=label, font=('微软雅黑', 8),
                     relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT,
                     command=lambda e=expr: r_var.set(e)).pack(side='left', padx=2)

        def draw_polar():
            try:
                safe_globals = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'theta': 0, 'pi': math.pi,
                }
                cw = self.canvas.winfo_width()
                ch = self.canvas.winfo_height()
                cx, cy = cw // 2, ch // 2
                points = []

                theta = 0
                while theta <= 2 * math.pi:
                    try:
                        r = eval(r_var.get(), {"__builtins__": {}}, {**safe_globals, 'theta': theta})
                        if isinstance(r, (int, float)) and abs(r) < 1000:
                            px = cx + r * 20 * math.cos(theta)
                            py = cy - r * 20 * math.sin(theta)
                            if -1000 <= px <= cw + 1000 and -1000 <= py <= ch + 1000:
                                points.append((px, py))
                    except:
                        pass
                    theta += 0.02

                if points:
                    shape = Shape('polar', points, self.current_color, self.current_width)
                    self.shape_manager.add_shape(shape)
                    self.pages[self.current_page] = self.shape_manager.shapes
                    self._redraw_all()
                    self._update_status()
                    self._push_undo()
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"表达式错误: {str(e)}", parent=dialog)

        tk.Button(dialog, text="📐 绘制极坐标方程", font=('微软雅黑', 12, 'bold'),
                 bg=self.BUTTON_ACTIVE, fg='white', relief='flat',
                 padx=30, pady=8, command=draw_polar).pack(pady=15)

    # ============================================
    # 图片导入
    # ============================================

    def _reload_image_for_shape(self, shape):
        """重新加载shape中的图片"""
        if not HAS_PIL or not hasattr(shape, 'image_path'):
            return
        try:
            if not os.path.exists(shape.image_path):
                return
            img = PILImage.open(shape.image_path)
            w, h = getattr(shape, 'image_size', (img.width, img.height))
            try:
                resize_filter = PILImage.LANCZOS
            except AttributeError:
                resize_filter = PILImage.Resampling.LANCZOS
            img = img.resize((w, h), resize_filter)
            photo = ImageTk.PhotoImage(img)
            img_key = f"img_{len(self.imported_images)}"
            self.imported_images[img_key] = photo
            shape.image_key = img_key
        except Exception:
            pass

    def _on_import_image(self):
        """导入图片"""
        if not HAS_PIL:
            messagebox.showerror("错误", "需要安装 Pillow 库才能导入图片\n请运行: pip install Pillow")
            return

        filepath = filedialog.askopenfilename(
            title="导入图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("所有文件", "*.*")
            ]
        )
        if not filepath:
            return

        try:
            img = PILImage.open(filepath)

            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            max_w = cw * 0.8
            max_h = ch * 0.8
            ratio = min(max_w / img.width, max_h / img.height, 1.0)
            new_w = int(img.width * ratio)
            new_h = int(img.height * ratio)
            try:
                resize_filter = PILImage.LANCZOS
            except AttributeError:
                resize_filter = PILImage.Resampling.LANCZOS
            img = img.resize((new_w, new_h), resize_filter)

            photo = ImageTk.PhotoImage(img)
            img_id = self.canvas.create_image(cw // 2, ch // 2, image=photo, anchor='center')

            img_key = f"img_{len(self.imported_images)}"
            self.imported_images[img_key] = photo

            shape = Shape('image', [(cw // 2 - new_w // 2, ch // 2 - new_h // 2),
                                     (cw // 2 + new_w // 2, ch // 2 + new_h // 2)],
                         'black', 1)
            shape.image_path = filepath
            shape.image_key = img_key
            shape.image_size = (new_w, new_h)
            self.shape_manager.add_shape(shape)
            self.pages[self.current_page] = self.shape_manager.shapes
            self._update_status()
            self._push_undo()
            self.status_text.set(f"📖 已导入图片: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("错误", f"导入图片失败: {str(e)}")

    # ============================================
    # 特殊曲线
    # ============================================

    def _on_draw_sine_curve(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        points = CurveGenerator.generate_sine_curve(50, ch // 2, 50, 200, 2)
        shape = Shape('sine', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    def _on_draw_spiral(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        points = CurveGenerator.generate_archimedean_spiral(cw // 2, ch // 2, 5, 10, 3)
        shape = Shape('spiral', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    def _on_draw_heart(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        points = CurveGenerator.generate_heart_curve(cw // 2, ch // 2, size=50)
        shape = Shape('heart', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    def _on_draw_lissajous(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        points = CurveGenerator.generate_lissajous_curve(cw // 2, ch // 2, a=80, b=80, frequency_x=3, frequency_y=2)
        shape = Shape('lissajous', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    def _on_draw_flower(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        points = CurveGenerator.generate_flower_curve(cw // 2, ch // 2, radius=80, petals=5)
        shape = Shape('flower', points, self.current_color, self.current_width)
        self.shape_manager.add_shape(shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    # ============================================
    # 变换
    # ============================================

    def _on_scale_shape(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected:
            messagebox.showinfo("提示", "请先选择图形")
            return
        DialogHelper.create_parameter_dialog(
            self.root, "缩放参数",
            [{'name': 'scale_x', 'label': '水平比例', 'type': 'float', 'default': 1.5, 'min': 0.1, 'max': 3.0},
             {'name': 'scale_y', 'label': '垂直比例', 'type': 'float', 'default': 1.5, 'min': 0.1, 'max': 3.0}],
            self._apply_scale
        )

    def _apply_scale(self, params):
        selected = self.shape_manager.get_selected_shape()
        if selected:
            cx, cy = selected.get_center()
            TransformManager.scale(selected, cx, cy, params['scale_x'], params['scale_y'])
            self.pages[self.current_page] = self.shape_manager.shapes
            self._redraw_all()
            self._push_undo()

    def _on_rotate_shape(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected:
            messagebox.showinfo("提示", "请先选择图形")
            return
        DialogHelper.create_parameter_dialog(
            self.root, "旋转参数",
            [{'name': 'angle', 'label': '旋转角度', 'type': 'int', 'default': 45, 'min': -180, 'max': 180}],
            self._apply_rotate
        )

    def _apply_rotate(self, params):
        selected = self.shape_manager.get_selected_shape()
        if selected:
            cx, cy = selected.get_center()
            TransformManager.rotate(selected, cx, cy, params['angle'])
            self.pages[self.current_page] = self.shape_manager.shapes
            self._redraw_all()
            self._push_undo()

    def _on_flip_shape(self, direction):
        selected = self.shape_manager.get_selected_shape()
        if not selected:
            messagebox.showinfo("提示", "请先选择图形")
            return
        if direction == 'horizontal':
            TransformManager.flip_horizontal(selected)
        else:
            TransformManager.flip_vertical(selected)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._push_undo()

    def _on_fill_shape(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected:
            messagebox.showinfo("提示", "请先选择图形")
            return
        DialogHelper.create_parameter_dialog(
            self.root, "填充颜色",
            [{'name': 'fill_color', 'label': '填充颜色', 'type': 'color', 'default': 'lightblue'}],
            self._apply_fill
        )

    def _apply_fill(self, params):
        selected = self.shape_manager.get_selected_shape()
        if selected:
            selected.fill_color = params['fill_color']
            self.pages[self.current_page] = self.shape_manager.shapes
            self._redraw_all()
            self._push_undo()

    def _on_add_shadow(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected:
            messagebox.showinfo("提示", "请先选择图形")
            return
        shadow = TransformHelper.create_shadow_shape(selected)
        shapes = self.shape_manager.shapes
        index = shapes.index(selected)
        shapes.insert(index, shadow)
        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    def _on_generate_pattern(self):
        DialogHelper.create_parameter_dialog(
            self.root, "生成图案",
            [{'name': 'pattern_type', 'label': '图案类型', 'type': 'choice',
              'default': 'circle', 'choices': [
                  ('circle', '同心圆'), ('star', '星形'), ('flower', '花瓣')
              ]}],
            self._apply_generate_pattern
        )

    def _apply_generate_pattern(self, params):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        cx, cy = cw // 2, ch // 2

        if params['pattern_type'] == 'circle':
            for r in range(20, 150, 20):
                shape = ShapeFactory.create_circle((cx, cy), r, self.current_color, self.current_width)
                self.shape_manager.add_shape(shape)
        elif params['pattern_type'] == 'star':
            for rotation in range(0, 360, 30):
                points = []
                for i in range(11):
                    angle = math.radians(i * 36 + rotation)
                    r = 100 if i % 2 == 0 else 50
                    points.append((cx + r * math.cos(angle - math.pi / 2),
                                   cy + r * math.sin(angle - math.pi / 2)))
                self.shape_manager.add_shape(Shape('star', points, self.current_color, self.current_width))
        elif params['pattern_type'] == 'flower':
            points = [(cx + 80 * abs(math.sin(3 * math.radians(i))) * math.cos(math.radians(i)),
                       cy + 80 * abs(math.sin(3 * math.radians(i))) * math.sin(math.radians(i)))
                      for i in range(361)]
            self.shape_manager.add_shape(Shape('flower', points, self.current_color, self.current_width))

        self.pages[self.current_page] = self.shape_manager.shapes
        self._redraw_all()
        self._update_status()
        self._push_undo()

    # ============================================
    # 绘制和更新
    # ============================================

    def _redraw_all(self):
        """重绘所有图形"""
        self.canvas.delete('all')
        self._draw_page_background()

        for shape in self.shape_manager.shapes:
            self._draw_shape(shape)

    def _draw_shape(self, shape):
        """绘制单个图形"""
        if not shape.points:
            return

        coords = []
        for p in shape.points:
            coords.extend(p)

        if shape.shape_type == 'line':
            self.canvas.create_line(coords, fill=shape.color, width=shape.width, capstyle='round')

        elif shape.shape_type == 'rectangle':
            self.canvas.create_polygon(coords, outline=shape.color,
                                       fill=shape.fill_color or '', width=shape.width)

        elif shape.shape_type in ('ellipse', 'circle'):
            self.canvas.create_polygon(coords, outline=shape.color,
                                       fill=shape.fill_color or '', width=shape.width)

        elif shape.shape_type in ('pencil', 'calligraphy'):
            self.canvas.create_line(coords, fill=shape.color, width=shape.width,
                                    smooth=True, capstyle='round', joinstyle='round')

        elif shape.shape_type == 'highlighter':
            self.canvas.create_line(coords, fill=shape.color, width=shape.width * 4,
                                    smooth=True, capstyle='round', joinstyle='round',
                                    stipple='gray25')

        elif shape.shape_type == 'rainbow':
            if hasattr(shape, 'rainbow_colors') and shape.rainbow_colors:
                for i in range(len(shape.points) - 1):
                    ci = min(i, len(shape.rainbow_colors) - 1)
                    self.canvas.create_line(
                        shape.points[i][0], shape.points[i][1],
                        shape.points[i+1][0], shape.points[i+1][1],
                        fill=shape.rainbow_colors[ci], width=shape.width)
            else:
                for i in range(len(shape.points) - 1):
                    hue = (i * 0.01) % 1.0
                    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                    self.canvas.create_line(
                        shape.points[i][0], shape.points[i][1],
                        shape.points[i+1][0], shape.points[i+1][1],
                        fill=color, width=shape.width)

        elif shape.shape_type == 'spray':
            if hasattr(shape, 'spray_dots') and shape.spray_dots:
                for dx, dy in shape.spray_dots:
                    self.canvas.create_oval(dx, dy, dx + 2, dy + 2,
                                            fill=shape.color, outline='')
            else:
                for px, py in shape.points:
                    for _ in range(random.randint(2, 5)):
                        ox = random.randint(-shape.width * 3, shape.width * 3)
                        oy = random.randint(-shape.width * 3, shape.width * 3)
                        self.canvas.create_oval(px + ox, py + oy, px + ox + 2, py + oy + 2,
                                                fill=shape.color, outline='')

        elif shape.shape_type == 'text':
            if hasattr(shape, 'text_content'):
                x, y = shape.points[0]
                fs = getattr(shape, 'text_font_size', 20)
                self.canvas.create_text(x, y, text=shape.text_content,
                                        fill=shape.color, font=('微软雅黑', fs), anchor='w')

        elif shape.shape_type == 'image':
            if hasattr(shape, 'image_key') and shape.image_key in self.imported_images:
                x1, y1 = shape.points[0]
                x2, y2 = shape.points[1]
                photo = self.imported_images[shape.image_key]
                self.canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=photo)

        else:
            self.canvas.create_line(coords, fill=shape.color, width=shape.width,
                                    smooth=True, capstyle='round')

        if shape.selected:
            bounds = shape.get_bounds()
            if bounds:
                self.canvas.create_rectangle(
                    bounds[0] - 5, bounds[1] - 5,
                    bounds[2] + 5, bounds[3] + 5,
                    outline='#3498db', dash=(4, 4), width=2)

    def _update_status(self):
        """更新状态栏"""
        self.count_text.set(f"{self.shape_manager.count()}个图形")
        self.page_label.config(text=f'第 {self.current_page + 1} / {len(self.pages)} 页')

    # ============================================
    # 帮助
    # ============================================

    def _on_show_help(self):
        help_text = """
绘图笔记本 v3.0 - 使用说明

📖 【书本界面】
- 左侧工具栏选择绘图工具
- 底部导航栏翻页（Ctrl+PageUp/PageDown）
- 切换页面背景：空白/网格/横线/点阵

✏ 【绘图工具】
- 画笔：自由绘制，实时显示轨迹
- 荧光笔：半透明标记，适合做笔记
- 书法笔：模拟毛笔/钢笔效果
- 喷枪：模拟喷漆效果
- 彩虹画笔：彩虹渐变描边
- 文字工具：点击画布添加文字

📐 【数学函数】
- y=f(x) 函数图像
- 参数方程 x(t), y(t)
- 极坐标方程 r=f(θ)
- 支持 sin, cos, tan, sqrt, exp, log 等

🖼 【图片导入】
- 支持 PNG/JPG/GIF/BMP/WebP
- 自动缩放适应画布

⌨ 【快捷键】
Ctrl+Z 撤销  Ctrl+Y 重做
Ctrl+N 新建  Ctrl+S 保存  Ctrl+O 打开
Ctrl+PageUp 上一页  Ctrl+PageDown 下一页
Delete 删除  Esc 取消选择
        """
        win = tk.Toplevel(self.root)
        win.title("使用说明")
        win.geometry("550x550")
        win.configure(bg=self.CANVAS_BG)
        text = tk.Text(win, wrap='word', padx=15, pady=15,
                       font=('微软雅黑', 10), bg=self.CANVAS_BG)
        text.pack(fill='both', expand=True)
        text.insert('1.0', help_text)
        text.config(state='disabled')

    def _on_show_about(self):
        messagebox.showinfo("关于",
            "📒 绘图笔记本 v3.0\n\n"
            "书本风格 | 多页翻页 | 数学函数\n"
            "图片导入 | 荧光笔 | 书法笔\n\n"
            "© 2024 课程设计作品")

    def run(self):
        self.status_text.set("📖 就绪 - 选择工具开始绘图")
        self._update_status()
        self.root.mainloop()


def main():
    print("正在启动绘图笔记本 v3.0...")
    app = NotebookApp()
    app.run()


if __name__ == "__main__":
    main()