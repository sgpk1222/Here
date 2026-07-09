import tkinter as tk
from tkinter import messagebox, filedialog
import copy
import json
import os
import math

try:
    from PIL import Image as PILImage, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# 基础数据模块导入
from shapes import Shape, ShapeManager, ShapeFactory
from transforms import TransformManager, TransformHelper
from curves import CurveGenerator
from file_manager import ExportManager
from ui_components import RainbowBrush, DialogHelper

# 核心拆分模块导入
from ui_builder import UILayoutBuilder
from canvas_handler import CanvasEventHandler
from math_dialogs import MathDialogManager

class NotebookAppCore:
    def __init__(self, root):
        self.root = root
        
        self.shape_manager = ShapeManager()
        self.rainbow_brush = RainbowBrush()
        self.pages = [[]]
        self.current_page = 0
        self.current_tool = 'pencil'
        self.current_color = '#2c1810'
        self.current_width = 3
        self.text_font_size = 20
        self.canvas_bg_mode = 'blank'
        self.imported_images = {}
        
        self.undo_stack = []
        self.redo_stack = []
        self.is_modified = False

        self.status_text = tk.StringVar(value="📖 就绪 - 请选择工具开始绘图")
        self.coord_text = tk.StringVar(value="")
        self.count_text = tk.StringVar(value="0个图形")
        self.width_var = tk.IntVar(value=3)

        self.ui_builder = UILayoutBuilder(self)
        self.canvas_handler = CanvasEventHandler(self)
        self.math_manager = MathDialogManager(self)

        self.root.configure(bg=self.ui_builder.BOOK_COVER)
        self.ui_builder.build_all()
        self.canvas_handler.bind_events()
        self._bind_shortcuts()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._push_undo()

    def run(self):
        self._update_status()
        self.root.mainloop()

    def on_closing(self):
        if self.is_modified:
            res = messagebox.askyesnocancel("保存提示", "您有未保存的更改，退出前要保存吗？")
            if res is True:
                if self.on_save_file(): self.root.destroy()
            elif res is False:
                self.root.destroy()
        else:
            self.root.destroy()

    def _bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.on_new_notebook())
        self.root.bind('<Control-s>', lambda e: self.on_save_file())
        self.root.bind('<Control-o>', lambda e: self.on_open_file())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-c>', lambda e: self.copy_shape())
        self.root.bind('<Delete>', lambda e: self.delete_shape())
        self.root.bind('<Escape>', lambda e: self.cancel_selection())
        self.root.bind('<Control-Prior>', lambda e: self.prev_page())
        self.root.bind('<Control-Next>', lambda e: self.next_page())

    def _push_undo(self):
        state = copy.deepcopy(self.shape_manager.shapes)
        self.undo_stack.append(state)
        self.redo_stack.clear()
        if len(self.undo_stack) > 50: self.undo_stack.pop(0)
        self.is_modified = True

    def undo(self):
        if len(self.undo_stack) <= 1: return
        current = self.undo_stack.pop()
        self.redo_stack.append(current)
        self.shape_manager.shapes = copy.deepcopy(self.undo_stack[-1])
        self.pages[self.current_page] = self.shape_manager.shapes
        self.shape_manager.deselect_all()
        self.redraw_all()
        self._update_status()
        self.is_modified = True

    def redo(self):
        if not self.redo_stack: return
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        self.shape_manager.shapes = copy.deepcopy(state)
        self.pages[self.current_page] = self.shape_manager.shapes
        self.shape_manager.deselect_all()
        self.redraw_all()
        self._update_status()
        self.is_modified = True

    def switch_to_page(self, page_idx):
        self.current_page = page_idx
        self.shape_manager.shapes = self.pages[self.current_page]
        self.shape_manager.deselect_all()
        self.redraw_all()
        self._update_status()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._push_undo()

    def on_new_page(self):
        self.pages[self.current_page] = self.shape_manager.shapes
        self.pages.insert(self.current_page + 1, [])
        self.current_page += 1
        self.switch_to_page(self.current_page)

    def on_delete_page(self):
        if len(self.pages) <= 1:
            self.pages[0] = []
            self.shape_manager.shapes = []
            self.switch_to_page(0)
            return
        del self.pages[self.current_page]
        if self.current_page >= len(self.pages): self.current_page = len(self.pages) - 1
        self.switch_to_page(self.current_page)

    def prev_page(self):
        if self.current_page > 0: self.switch_to_page(self.current_page - 1)

    def next_page(self):
        if self.current_page < len(self.pages) - 1: self.switch_to_page(self.current_page + 1)

    def redraw_all(self):
        self.canvas.delete('all')
        self.ui_builder.draw_page_background()
        for shape in self.shape_manager.shapes: self._draw_shape(shape)

    def _draw_shape(self, shape):
        if not shape.points: return
        coords = []
        for p in shape.points: coords.extend(p)

        if shape.shape_type == 'line':
            self.canvas.create_line(coords, fill=shape.color, width=shape.width, capstyle='round')
        elif shape.shape_type in ('rectangle', 'ellipse', 'circle'):
            self.canvas.create_polygon(coords, outline=shape.color, fill=shape.fill_color or '', width=shape.width)
        elif shape.shape_type == 'pencil':
            if getattr(shape, 'fill_color', None):
                self.canvas.create_polygon(coords, fill=shape.fill_color, outline='', smooth=True)
            self.canvas.create_line(coords, fill=shape.color, width=shape.width, smooth=True, capstyle='round', joinstyle='round')
        elif shape.shape_type == 'highlighter':
            if getattr(shape, 'fill_color', None):
                self.canvas.create_polygon(coords, fill=shape.fill_color, outline='', smooth=True)
            self.canvas.create_line(coords, fill=shape.color, width=shape.width * 4, smooth=True, capstyle='round', joinstyle='round', stipple='gray25')
        elif shape.shape_type == 'rainbow':
            if getattr(shape, 'fill_color', None):
                self.canvas.create_polygon(coords, fill=shape.fill_color, outline='', smooth=True)
            if hasattr(shape, 'rainbow_colors') and shape.rainbow_colors:
                for i in range(len(shape.points) - 1):
                    ci = min(i, len(shape.rainbow_colors) - 1)
                    self.canvas.create_line(shape.points[i][0], shape.points[i][1], shape.points[i+1][0], shape.points[i+1][1], fill=shape.rainbow_colors[ci], width=shape.width)
        elif shape.shape_type == 'spray':
            if getattr(shape, 'fill_color', None):
                self.canvas.create_polygon(coords, fill=shape.fill_color, outline='', smooth=True)
            if hasattr(shape, 'spray_dots') and shape.spray_dots:
                for dx, dy in shape.spray_dots:
                    self.canvas.create_oval(dx, dy, dx + 2, dy + 2, fill=shape.color, outline='')
        elif shape.shape_type == 'text':
            if hasattr(shape, 'text_content'):
                x, y = shape.points[0]
                fs = getattr(shape, 'text_font_size', 20)
                angle = getattr(shape, 'angle', 0)
                self.canvas.create_text(x, y, text=shape.text_content, fill=shape.color, font=('微软雅黑', fs), anchor='center', angle=angle)
        elif shape.shape_type == 'image':
            if hasattr(shape, 'image_key') and shape.image_key in self.imported_images:
                photo = self.imported_images[shape.image_key]
                self.canvas.create_image((shape.points[0][0] + shape.points[1][0]) / 2, (shape.points[0][1] + shape.points[1][1]) / 2, image=photo)
        else:
            self.canvas.create_line(coords, fill=shape.color, width=shape.width, smooth=True, capstyle='round')

        if shape.selected:
            bounds = shape.get_bounds()
            if bounds:
                self.canvas.create_rectangle(bounds[0] - 5, bounds[1] - 5, bounds[2] + 5, bounds[3] + 5, outline='#3498db', dash=(4, 4), width=2)

    def _update_status(self):
        self.count_text.set(f"{self.shape_manager.count()}个图形")
        if hasattr(self, 'ui_builder') and hasattr(self.ui_builder, 'page_label'):
            self.ui_builder.page_label.config(text=f'第 {self.current_page + 1} / {len(self.pages)} 页')

    def copy_shape(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected: return
        new_shape = TransformManager.copy_and_offset(selected, 20, 20)
        self.shape_manager.add_shape(new_shape)
        self.shape_manager.select_shape(new_shape)
        self.pages[self.current_page] = self.shape_manager.shapes
        self.redraw_all()
        self._push_undo()

    def delete_shape(self):
        selected = self.shape_manager.get_selected_shape()
        if not selected: return
        self.shape_manager.remove_shape(selected)
        self.pages[self.current_page] = self.shape_manager.shapes
        self.redraw_all()
        self._update_status()
        self._push_undo()

    def cancel_selection(self):
        self.shape_manager.deselect_all()
        self.redraw_all()

    def on_clear_canvas(self):
        if self.shape_manager.count() > 0 and messagebox.askyesno("确认", "确定要清空本页的所有图形吗？"):
            self.shape_manager.clear_all()
            self.pages[self.current_page] = []
            self.redraw_all()
            self._update_status()
            self._push_undo()

    # --- 📐 数学几何图形生成（全部映射为弹窗交互形式） ---
    def on_draw_sine_curve(self):
        """调出数学外脑弹窗配置正弦曲线"""
        self.math_manager.on_draw_sine_dialog()

    def on_draw_spiral(self):
        """调出数学外脑弹窗配置阿基米德螺线"""
        self.math_manager.on_draw_spiral_dialog()

    def on_draw_heart(self):
        """调出数学外脑弹窗配置心形曲线"""
        self.math_manager.on_draw_heart_dialog()

    def on_draw_lissajous(self):
        """调出数学外脑弹窗配置利萨如曲线"""
        self.math_manager.on_draw_lissajous_dialog()

    def on_draw_flower(self):
        """调出数学外脑弹窗配置花瓣曲线"""
        self.math_manager.on_draw_flower_dialog()

    # --- 变换核心逻辑 ---
    def on_scale_shape(self):
        if not self.shape_manager.get_selected_shape(): return
        DialogHelper.create_parameter_dialog(self.root, "缩放参数", [{'name': 'scale_x', 'label': '水平比例', 'type': 'float', 'default': 1.5, 'min': 0.1, 'max': 3.0}, {'name': 'scale_y', 'label': '垂直比例', 'type': 'float', 'default': 1.5, 'min': 0.1, 'max': 3.0}], self._apply_scale)
    def _apply_scale(self, params):
        s = self.shape_manager.get_selected_shape()
        if s: TransformManager.scale(s, *s.get_center(), params['scale_x'], params['scale_y']); self.redraw_all(); self._push_undo()

    def on_rotate_shape(self):
        if not self.shape_manager.get_selected_shape(): return
        DialogHelper.create_parameter_dialog(self.root, "旋转参数", [{'name': 'angle', 'label': '旋转角度', 'type': 'int', 'default': 45, 'min': -180, 'max': 180}], self._apply_rotate)
    def _apply_rotate(self, params):
        s = self.shape_manager.get_selected_shape()
        if s: TransformManager.rotate(s, *s.get_center(), params['angle']); self.redraw_all(); self._push_undo()

    def on_flip_shape(self, direction):
        s = self.shape_manager.get_selected_shape()
        if s: 
            TransformManager.flip_horizontal(s) if direction == 'horizontal' else TransformManager.flip_vertical(s)
            self.redraw_all(); self._push_undo()

    def on_add_shadow(self):
        s = self.shape_manager.get_selected_shape()
        if s:
            self.shape_manager.shapes.insert(self.shape_manager.shapes.index(s), TransformHelper.create_shadow_shape(s))
            self.redraw_all(); self._push_undo()

    def on_generate_pattern(self):
        DialogHelper.create_parameter_dialog(self.root, "生成图案", [{'name': 'pattern_type', 'label': '图案类型', 'type': 'choice', 'default': 'circle', 'choices': [('circle', '同心圆'), ('star', '星形'), ('flower', '花瓣')]}], self._apply_generate_pattern)
    def _apply_generate_pattern(self, params):
        cx, cy = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
        if params['pattern_type'] == 'circle':
            for r in range(20, 150, 20): self.shape_manager.add_shape(ShapeFactory.create_circle((cx, cy), r, self.current_color, self.current_width))
        elif params['pattern_type'] == 'star':
            for r_a in range(0, 360, 30):
                pts = [(cx + (100 if i%2==0 else 50)*math.cos(math.radians(i*36+r_a)-math.pi/2), cy + (100 if i%2==0 else 50)*math.sin(math.radians(i*36+r_a)-math.pi/2)) for i in range(11)]
                self.shape_manager.add_shape(Shape('star', pts, self.current_color, self.current_width))
        self.redraw_all(); self._push_undo()

    def on_import_image(self):
        if not HAS_PIL: return messagebox.showerror("错误", "需运行 `pip install Pillow` 导入外部图片")
        filepath = filedialog.askopenfilename(title="导入图片", filetypes=[("图片", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if filepath:
            try:
                img = PILImage.open(filepath)
                cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
                ratio = min(cw*0.8/img.width, ch*0.8/img.height, 1.0)
                new_w, new_h = int(img.width * ratio), int(img.height * ratio)
                img = img.resize((new_w, new_h), PILImage.Resampling.LANCZOS if hasattr(PILImage, 'Resampling') else PILImage.LANCZOS)
                self.imported_images[f"img_{len(self.imported_images)}"] = ImageTk.PhotoImage(img)
                s = Shape('image', [(cw//2 - new_w//2, ch//2 - new_h//2), (cw//2 + new_w//2, ch//2 + new_h//2)], 'black', 1)
                s.image_path, s.image_key, s.image_size = filepath, f"img_{len(self.imported_images)-1}", (new_w, new_h)
                self.shape_manager.add_shape(s); self.redraw_all(); self._push_undo()
            except Exception as e: messagebox.showerror("错误", str(e))

    def on_export_text(self):
        if self.shape_manager.count() > 0:
            filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本", "*.txt")])
            if filepath: ExportManager.export_to_text(self.shape_manager.shapes, filepath)

    def on_export_summary(self):
        if self.shape_manager.count() > 0:
            filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本", "*.txt")])
            if filepath: ExportManager.export_summary(self.shape_manager.shapes, filepath)

    def on_new_notebook(self):
        if self.is_modified and not messagebox.askyesno("确认", "有未保存更改，确定新建？"): return
        self.pages, self.current_page, self.shape_manager.shapes = [[]], 0, []
        self.imported_images.clear(); self.undo_stack.clear(); self.redo_stack.clear()
        self.is_modified = False
        self._push_undo(); self.redraw_all(); self._update_status()

    def on_save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".nb.json", filetypes=[("笔记本", "*.nb.json")])
        if filepath:
            data = {'version': '3.0', 'pages': [[s.to_dict() for s in p] for p in self.pages], 'current_page': self.current_page, 'bg_mode': self.canvas_bg_mode}
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
            self.is_modified = False
            self.status_text.set("📖 保存成功")
            return True
        return False

    def on_open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("笔记本文件", "*.nb.json"), ("JSON", "*.json")])
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
            self.pages = []
            self.imported_images.clear()
            for pd in data.get('pages', []):
                page_shapes = []
                for sd in pd:
                    shape = Shape.from_dict(sd)
                    page_shapes.append(shape)
                    if shape.shape_type == 'image':
                        self._reload_image_for_shape(shape)
                self.pages.append(page_shapes)
            self.current_page, self.canvas_bg_mode = data.get('current_page', 0), data.get('bg_mode', 'blank')
            self.is_modified = False
            self.switch_to_page(self.current_page)

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
- 喷枪：模拟喷漆效果
- 彩虹画笔：彩虹渐变描边
- 文本工具：点击画布直接生成输入框，按回车或点击空白处保存
- 填充工具：点击画笔绘制或几何图形进行上色
- 橡皮：擦除画错的内容（背景色绘制）

📐 【数学函数】
- y=f(x) 函数图像
- 参数方程 x(t), y(t)
- 极坐标方程 r=f(θ)

🖼 【图片导入】
- 支持 PNG/JPG/GIF/BMP

⌨ 【快捷键】
Ctrl+Z 撤销  Ctrl+Y 重做
Ctrl+N 新建  Ctrl+S 保存  Ctrl+O 打开
Ctrl+PageUp 上一页  Ctrl+PageDown 下一页
Delete 删除选中图形/文本  Esc 取消选择
        """
        win = tk.Toplevel(self.root)
        win.title("使用说明")
        win.geometry("550x550")
        text = tk.Text(win, wrap='word', padx=15, pady=15, font=('微软雅黑', 10), bg='#faf8f2')
        text.pack(fill='both', expand=True)
        text.insert('1.0', help_text)
        text.config(state='disabled')