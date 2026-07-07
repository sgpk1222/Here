#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模块五：UI组件模块
功能：定义所有界面组件（工具栏、颜色面板、菜单栏等）
作者：课程设计团队
"""

import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys


# ============================================
# 子模块一：工具栏组件
# ============================================

class ToolbarPanel:
    """
    工具栏面板
    包含所有绘图工具的选择按钮
    """
    
    def __init__(self, parent_frame, on_tool_change_callback):
        """
        初始化工具栏
        
        参数:
            parent_frame: 父容器
            on_tool_change_callback: 工具切换回调函数
        """
        self.parent = parent_frame
        self.on_tool_change = on_tool_change_callback
        
        # 工具按钮字典
        self.tool_buttons = {}
        
        # 创建工具栏
        self._create_toolbar()
    
    def _create_toolbar(self):
        """创建工具栏界面"""
        # 标题
        title_label = tk.Label(
            self.parent,
            text="绘图工具",
            font=('微软雅黑', 10, 'bold')
        )
        title_label.pack(pady=5)
        
        # 工具定义列表
        tools = [
            ('选择', 'select', '选择和移动图形'),
            ('直线', 'line', '绘制直线'),
            ('矩形', 'rectangle', '绘制矩形'),
            ('圆形', 'circle', '绘制圆形/椭圆'),
            ('画笔', 'pencil', '自由绘制曲线'),
            ('彩虹', 'rainbow', '彩虹渐变画笔'),
            ('橡皮', 'eraser', '擦除内容')
        ]
        
        # 创建按钮
        for text, tool_id, tooltip in tools:
            btn = tk.Button(
                self.parent,
                text=text,
                width=8,
                height=1,
                relief='raised',
                command=lambda t=tool_id: self._on_button_click(t)
            )
            btn.pack(pady=2, padx=5)
            
            # 创建工具提示
            ToolTip(btn, tooltip)
            
            # 存储按钮引用
            self.tool_buttons[tool_id] = btn
        
        # 默认选中直线工具
        self.set_active_tool('line')
    
    def _on_button_click(self, tool_id):
        """工具按钮点击事件"""
        self.set_active_tool(tool_id)
        if self.on_tool_change:
            self.on_tool_change(tool_id)
    
    def set_active_tool(self, tool_id):
        """设置当前激活的工具"""
        # 更新所有按钮状态
        for tid, btn in self.tool_buttons.items():
            if tid == tool_id:
                btn.config(relief='sunken', bg='lightblue')
            else:
                btn.config(relief='raised', bg='SystemButtonFace')


# ============================================
# 子模块二：颜色面板组件
# ============================================

class ColorPanel:
    """
    颜色选择面板
    包含颜色选择器和预设颜色按钮
    """
    
    def __init__(self, parent_frame, on_color_change_callback):
        """
        初始化颜色面板
        
        参数:
            parent_frame: 父容器
            on_color_change_callback: 颜色切换回调函数
        """
        self.parent = parent_frame
        self.on_color_change = on_color_change_callback
        
        # 当前颜色
        self.current_color = 'black'
        
        # 预设颜色列表
        self.presets = [
            'black', 'white', 'red', 'blue', 'green',
            'yellow', 'orange', 'purple', 'pink', 'cyan',
            'brown', 'gray', 'magenta', 'lime', 'navy'
        ]
        
        # 创建颜色面板
        self._create_panel()
    
    def _create_panel(self):
        """创建颜色面板界面"""
        # 标题
        title_label = tk.Label(
            self.parent,
            text="颜色选择",
            font=('微软雅黑', 10, 'bold')
        )
        title_label.pack(pady=5)
        
        # 当前颜色显示框
        self.color_display_frame = tk.Frame(
            self.parent,
            width=40,
            height=40,
            relief='sunken',
            bd=2
        )
        self.color_display_frame.pack(pady=5)
        self.color_display_frame.pack_propagate(False)
        
        # 当前颜色按钮（点击打开选择器）
        self.color_button = tk.Button(
            self.color_display_frame,
            bg=self.current_color,
            command=self._open_color_dialog
        )
        self.color_button.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 预设颜色网格
        self._create_preset_grid()
    
    def _create_preset_grid(self):
        """创建预设颜色网格"""
        preset_frame = tk.Frame(self.parent)
        preset_frame.pack(pady=5)
        
        # 创建预设颜色按钮（3行5列）
        for i, color in enumerate(self.presets):
            row = i // 5
            col = i % 5
            
            btn = tk.Button(
                preset_frame,
                bg=color,
                width=2,
                height=1,
                relief='raised',
                command=lambda c=color: self._on_preset_click(c)
            )
            btn.grid(row=row, column=col, padx=1, pady=1)
            
            # 添加工具提示
            ToolTip(btn, color)
    
    def _open_color_dialog(self):
        """打开颜色选择对话框"""
        color = colorchooser.askcolor(
            title="选择颜色",
            initialcolor=self.current_color
        )
        
        if color[1]:
            self.set_color(color[1])
    
    def _on_preset_click(self, color):
        """预设颜色点击事件"""
        self.set_color(color)
    
    def set_color(self, color):
        """设置当前颜色"""
        self.current_color = color
        self.color_button.config(bg=color)
        
        if self.on_color_change:
            self.on_color_change(color)
    
    def get_color(self):
        """获取当前颜色"""
        return self.current_color


# ============================================
# 子模块三：线宽调节组件
# ============================================

class WidthPanel:
    """
    线宽调节面板
    使用滑块调节线条宽度
    """
    
    def __init__(self, parent_frame, on_width_change_callback):
        """
        初始化线宽面板
        
        参数:
            parent_frame: 父容器
            on_width_change_callback: 线宽切换回调函数
        """
        self.parent = parent_frame
        self.on_width_change = on_width_change_callback
        
        # 当前线宽
        self.current_width = 2
        
        # 创建线宽面板
        self._create_panel()
    
    def _create_panel(self):
        """创建线宽面板界面"""
        # 标题
        title_label = tk.Label(
            self.parent,
            text="线条宽度",
            font=('微软雅黑', 10, 'bold')
        )
        title_label.pack(pady=5)
        
        # 线宽滑块
        self.width_var = tk.IntVar(value=self.current_width)
        
        self.width_scale = tk.Scale(
            self.parent,
            from_=1,
            to=20,
            orient='horizontal',
            variable=self.width_var,
            command=self._on_scale_change,
            length=60,
            showvalue=True
        )
        self.width_scale.pack(pady=5)
        
        # 线宽预览
        self._create_width_preview()
    
    def _create_width_preview(self):
        """创建线宽预览"""
        preview_frame = tk.Frame(self.parent)
        preview_frame.pack(pady=5)
        
        # 预览标签
        tk.Label(preview_frame, text="预览:").pack(side='left')
        
        # 预览画布
        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=60,
            height=20,
            bg='white'
        )
        self.preview_canvas.pack(side='left', padx=5)
        
        # 绘制预览线
        self._update_preview()
    
    def _on_scale_change(self, value):
        """滑块值改变事件"""
        self.current_width = int(value)
        self._update_preview()
        
        if self.on_width_change:
            self.on_width_change(self.current_width)
    
    def _update_preview(self):
        """更新预览线"""
        self.preview_canvas.delete('all')
        
        # 绘制预览线
        self.preview_canvas.create_line(
            5, 10, 55, 10,
            width=self.current_width,
            fill='black'
        )
    
    def set_width(self, width):
        """设置线宽"""
        self.current_width = width
        self.width_var.set(width)
        self._update_preview()
    
    def get_width(self):
        """获取当前线宽"""
        return self.current_width


# ============================================
# 子模块四：状态栏组件
# ============================================

class StatusBar:
    """
    状态栏组件
    显示程序运行状态、坐标、图形数量等信息
    """
    
    def __init__(self, parent_window):
        """
        初始化状态栏
        
        参数:
            parent_window: 父窗口
        """
        self.parent = parent_window
        
        # 创建状态栏
        self._create_statusbar()
    
    def _create_statusbar(self):
        """创建状态栏界面"""
        # 状态栏框架
        self.status_frame = tk.Frame(
            self.parent,
            relief='sunken',
            bd=1
        )
        self.status_frame.pack(side='bottom', fill='x')
        
        # 工具状态显示
        self.status_label = tk.Label(
            self.status_frame,
            text="就绪",
            anchor='w',
            font=('微软雅黑', 9),
            padx=10
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        # 分隔符
        ttk.Separator(self.status_frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # 图形数量显示
        self.count_label = tk.Label(
            self.status_frame,
            text="图形: 0",
            anchor='e',
            font=('微软雅黑', 9),
            padx=10
        )
        self.count_label.pack(side='right')
        
        # 分隔符
        ttk.Separator(self.status_frame, orient='vertical').pack(side='right', fill='y', padx=5)
        
        # 坐标显示
        self.coord_label = tk.Label(
            self.status_frame,
            text="坐标: (0, 0)",
            anchor='e',
            font=('微软雅黑', 9),
            padx=10
        )
        self.coord_label.pack(side='right')
    
    def set_status(self, text):
        """设置状态文本"""
        self.status_label.config(text=text)
    
    def set_coordinates(self, x, y):
        """设置坐标显示"""
        self.coord_label.config(text=f"坐标: ({x}, {y})")
    
    def set_shape_count(self, count):
        """设置图形数量"""
        self.count_label.config(text=f"图形: {count}")


# ============================================
# 子模块五：菜单栏组件
# ============================================

class MenuBar:
    """
    菜单栏组件
    包含所有菜单项和菜单命令
    """
    
    def __init__(self, parent_window, callbacks):
        """
        初始化菜单栏
        
        参数:
            parent_window: 父窗口
            callbacks: 菜单命令回调函数字典
        """
        self.parent = parent_window
        self.callbacks = callbacks
        
        # 创建菜单栏
        self._create_menubar()
    
    def _create_menubar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        
        # 文件菜单
        self._create_file_menu(menubar)
        
        # 编辑菜单
        self._create_edit_menu(menubar)
        
        # 绘图菜单
        self._create_draw_menu(menubar)
        
        # 特殊曲线菜单
        self._create_curve_menu(menubar)
        
        # 变换菜单
        self._create_transform_menu(menubar)
        
        # 创意工具菜单
        self._create_creative_menu(menubar)
        
        # 帮助菜单
        self._create_help_menu(menubar)
    
    def _create_file_menu(self, menubar):
        """创建文件菜单"""
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        file_menu.add_command(
            label="新建画布",
            command=self._get_callback('new_canvas'),
            accelerator="Ctrl+N"
        )
        
        file_menu.add_command(
            label="打开文件",
            command=self._get_callback('open_file'),
            accelerator="Ctrl+O"
        )
        
        file_menu.add_command(
            label="保存文件",
            command=self._get_callback('save_file'),
            accelerator="Ctrl+S"
        )
        
        file_menu.add_separator()
        
        file_menu.add_command(
            label="退出程序",
            command=self.parent.quit
        )
    
    def _create_edit_menu(self, menubar):
        """创建编辑菜单"""
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        edit_menu.add_command(
            label="复制图形",
            command=self._get_callback('copy_shape'),
            accelerator="Ctrl+C"
        )
        
        edit_menu.add_command(
            label="删除图形",
            command=self._get_callback('delete_shape'),
            accelerator="Delete"
        )
        
        edit_menu.add_separator()
        
        edit_menu.add_command(
            label="清空画布",
            command=self._get_callback('clear_canvas')
        )
    
    def _create_draw_menu(self, menubar):
        """创建绘图菜单"""
        draw_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="绘图", menu=draw_menu)
        
        draw_menu.add_command(
            label="直线",
            command=lambda: self._get_callback('set_tool')('line')
        )
        
        draw_menu.add_command(
            label="矩形",
            command=lambda: self._get_callback('set_tool')('rectangle')
        )
        
        draw_menu.add_command(
            label="圆形",
            command=lambda: self._get_callback('set_tool')('circle')
        )
        
        draw_menu.add_separator()
        
        draw_menu.add_command(
            label="自由画笔",
            command=lambda: self._get_callback('set_tool')('pencil')
        )
        
        draw_menu.add_command(
            label="彩虹画笔",
            command=lambda: self._get_callback('set_tool')('rainbow')
        )
    
    def _create_curve_menu(self, menubar):
        """创建特殊曲线菜单"""
        curve_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="特殊曲线", menu=curve_menu)
        
        curve_menu.add_command(
            label="正弦曲线",
            command=self._get_callback('draw_sine')
        )
        
        curve_menu.add_command(
            label="阿基米德螺线",
            command=self._get_callback('draw_spiral')
        )
        
        curve_menu.add_separator()
        
        curve_menu.add_command(
            label="心形曲线",
            command=self._get_callback('draw_heart')
        )
        
        curve_menu.add_command(
            label="利萨如曲线",
            command=self._get_callback('draw_lissajous')
        )
        
        curve_menu.add_command(
            label="花瓣曲线",
            command=self._get_callback('draw_flower')
        )
    
    def _create_transform_menu(self, menubar):
        """创建变换菜单"""
        transform_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="变换", menu=transform_menu)
        
        transform_menu.add_command(
            label="缩放图形",
            command=self._get_callback('scale_shape')
        )
        
        transform_menu.add_command(
            label="旋转图形",
            command=self._get_callback('rotate_shape')
        )
        
        transform_menu.add_separator()
        
        transform_menu.add_command(
            label="水平翻转",
            command=lambda: self._get_callback('flip_shape')('horizontal')
        )
        
        transform_menu.add_command(
            label="垂直翻转",
            command=lambda: self._get_callback('flip_shape')('vertical')
        )
    
    def _create_creative_menu(self, menubar):
        """创建创意工具菜单"""
        creative_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="创意工具", menu=creative_menu)
        
        creative_menu.add_command(
            label="图形填充",
            command=self._get_callback('fill_shape')
        )
        
        creative_menu.add_command(
            label="添加阴影",
            command=self._get_callback('add_shadow')
        )
        
        creative_menu.add_separator()
        
        creative_menu.add_command(
            label="生成图案",
            command=self._get_callback('generate_pattern')
        )
    
    def _create_help_menu(self, menubar):
        """创建帮助菜单"""
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        help_menu.add_command(
            label="使用说明",
            command=self._get_callback('show_help')
        )
        
        help_menu.add_separator()
        
        help_menu.add_command(
            label="关于软件",
            command=self._get_callback('show_about')
        )
    
    def _get_callback(self, callback_name):
        """获取回调函数"""
        return self.callbacks.get(callback_name, lambda: None)


# ============================================
# 工具提示辅助类
# ============================================

class ToolTip:
    """
    工具提示类
    为控件添加鼠标悬停提示
    """
    
    def __init__(self, widget, text):
        """
        初始化工具提示
        
        参数:
            widget: 要添加提示的控件
            text: 提示文本
        """
        self.widget = widget
        self.text = text
        self.tip_window = None
        
        # 绑定事件
        widget.bind('<Enter>', self.show_tip)
        widget.bind('<Leave>', self.hide_tip)
    
    def show_tip(self, event=None):
        """显示提示"""
        if self.tip_window:
            return
        
        # 创建提示窗口
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        # 创建提示标签
        label = tk.Label(
            self.tip_window,
            text=self.text,
            justify='left',
            background='#ffffe0',
            relief='solid',
            borderwidth=1,
            font=('微软雅黑', 9)
        )
        label.pack()
    
    def hide_tip(self, event=None):
        """隐藏提示"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ============================================
# 对话框辅助类
# ============================================

class DialogHelper:
    """
    对话框辅助类
    提供常用对话框的创建方法
    """
    
    @staticmethod
    def create_parameter_dialog(parent, title, parameters, on_confirm_callback):
        """
        创建参数设置对话框
        
        参数:
            parent: 父窗口
            title: 对话框标题
            parameters: 参数列表，每个参数是字典:
                {
                    'name': '参数名称',
                    'label': '显示标签',
                    'type': 'int/float/color',
                    'default': 默认值,
                    'min': 最小值,
                    'max': 最大值
                }
            on_confirm_callback: 确认回调函数
        
        示例:
            parameters = [
                {
                    'name': 'amplitude',
                    'label': '振幅',
                    'type': 'int',
                    'default': 50,
                    'min': 10,
                    'max': 200
                }
            ]
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.grab_set()
        
        # 参数控件字典
        param_vars = {}
        
        # 创建参数控件
        for param in parameters:
            frame = tk.Frame(dialog)
            frame.pack(pady=5, padx=10, fill='x')
            
            # 标签
            label = tk.Label(frame, text=param['label'], width=10)
            label.pack(side='left')
            
            # 根据类型创建控件
            if param['type'] == 'int':
                var = tk.IntVar(value=param['default'])
                scale = tk.Scale(
                    frame,
                    from_=param['min'],
                    to=param['max'],
                    orient='horizontal',
                    variable=var,
                    length=200
                )
                scale.pack(side='left', fill='x', expand=True)
                param_vars[param['name']] = var
            
            elif param['type'] == 'float':
                var = tk.DoubleVar(value=param['default'])
                scale = tk.Scale(
                    frame,
                    from_=param['min'],
                    to=param['max'],
                    resolution=0.1,
                    orient='horizontal',
                    variable=var,
                    length=200
                )
                scale.pack(side='left', fill='x', expand=True)
                param_vars[param['name']] = var
            
            elif param['type'] == 'color':
                var = tk.StringVar(value=param['default'])
                btn = tk.Button(
                    frame,
                    bg=param['default'],
                    text="选择颜色",
                    command=lambda v=var, f=frame: DialogHelper._choose_color_in_dialog(v, f)
                )
                btn.pack(side='left')
                param_vars[param['name']] = var
        
        # 确认按钮
        def on_confirm():
            values = {}
            for name, var in param_vars.items():
                values[name] = var.get()
            
            on_confirm_callback(values)
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="确定", command=on_confirm, width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="取消", command=dialog.destroy, width=10).pack(side='left', padx=5)
        
        return dialog
    
    @staticmethod
    def _choose_color_in_dialog(var, frame):
        """在对话框中选择颜色"""
        color = colorchooser.askcolor(initialcolor=var.get())
        if color[1]:
            var.set(color[1])
            # 更新按钮颜色（需要找到按钮）
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(bg=color[1])


# ============================================
# 彩虹画笔辅助类
# ============================================

class RainbowBrush:
    """
    彩虹画笔辅助类
    提供彩虹色渐变计算
    """
    
    def __init__(self):
        """初始化彩虹画笔"""
        self.hue_offset = 0
    
    def get_next_color(self):
        """
        获取下一个彩虹色
        
        返回:
            str: RGB颜色字符串 (#RRGGBB)
        """
        # 计算HSV颜色
        hue = (self.hue_offset * 0.05) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        
        # 转换为RGB字符串
        color = '#%02x%02x%02x' % (
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
        
        # 增加偏移
        self.hue_offset += 1
        
        return color
    
    def reset(self):
        """重置偏移"""
        self.hue_offset = 0


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("=== 测试UI组件模块 ===")
    
    # 创建测试窗口
    test_window = tk.Tk()
    test_window.title("UI组件测试")
    test_window.geometry("400x600")
    
    # 左侧工具栏
    toolbar_frame = tk.Frame(test_window, relief='raised', bd=2)
    toolbar_frame.pack(side='left', fill='y', padx=5, pady=5)
    
    def on_tool_change(tool):
        print(f"工具切换: {tool}")
    
    toolbar = ToolbarPanel(toolbar_frame, on_tool_change)
    
    # 颜色面板
    color_frame = tk.Frame(test_window, relief='raised', bd=2)
    color_frame.pack(side='left', fill='y', padx=5, pady=5)
    
    def on_color_change(color):
        print(f"颜色切换: {color}")
    
    color_panel = ColorPanel(color_frame, on_color_change)
    
    # 状态栏
    statusbar = StatusBar(test_window)
    statusbar.set_status("测试模式")
    statusbar.set_coordinates(100, 200)
    statusbar.set_shape_count(5)
    
    # 测试彩虹画笔
    print("\n测试彩虹画笔:")
    rainbow = RainbowBrush()
    for i in range(5):
        color = rainbow.get_next_color()
        print(f"彩虹色{i+1}: {color}")
    
    print("\nUI组件测试窗口已打开，请手动测试...")
    
    test_window.mainloop()