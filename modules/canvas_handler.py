from shapes import ShapeFactory, Shape
from transforms import TransformManager
import math
import random
import tkinter as tk

# 导入 Pillow 的核心组件支持智能填充
from PIL import Image as PILImage, ImageDraw as PILImageDraw, ImageTk

class CanvasEventHandler:
    """处理画布上的所有鼠标事件和绘画逻辑"""
    
    def __init__(self, app):
        self.app = app
        self.is_drawing = False
        self.start_point = None
        self.temp_points = []
        self.temp_shape_ids = []
        self.temp_shape_id = None
        self.temp_spray_dots = []
        self.temp_rainbow_colors = []
        self.is_moving = False
        self.move_start = None
        
        # 文本直输状态控制
        self.active_entry = None
        self.text_frame = None
        self.text_window_id = None

    def bind_events(self):
        self.app.canvas.bind('<Button-1>', self.on_click)
        self.app.canvas.bind('<B1-Motion>', self.on_drag)
        self.app.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.app.canvas.bind('<Motion>', self.on_motion)

    def on_click(self, event):
        x, y = event.x, event.y
        
        # 无论用什么工具，只要点了画布，先提交未完成的文本框
        if self.active_entry:
            self._commit_text()
            return

        if self.app.current_tool == 'select':
            shape = self.app.shape_manager.get_shape_at(x, y)
            if shape:
                self.app.shape_manager.select_shape(shape)
                self.app.status_text.set(f"📖 已选中: {shape.shape_type}")
                self.is_moving = True
                self.move_start = (event.x_root, event.y_root)  # 记录鼠标起点（物理屏幕绝对坐标）
            else:
                self.app.cancel_selection()
                self.app.status_text.set("📖 未选中图形")
            self.app.redraw_all()
            
        elif self.app.current_tool == 'fill':
            # 上色工具：调用高精度浸染填充
            self._perform_flood_fill(x, y)
            
        elif self.app.current_tool == 'text':
            self.text_pos = (x, y)
            
            # 1. 🛠️ 升级：创建一个具有黄金色边框（bd=1, solid）的物理容器，美观且自适应极强
            self.text_frame = tk.Frame(
                self.app.canvas,
                bg='#c4a35a',       # 黄金色，契合书本封面主题
                bd=1, 
                relief='solid', 
                padx=6,             # 留出 6 像素的拖拽握把边缘
                pady=6,
                cursor='fleur'      # 悬停时显示十字拖拽手势
            )
            
            # 2. 挂载无缝扁平输入框到 Frame 内部
            self.active_entry = tk.Entry(
                self.text_frame,
                font=('微软雅黑', self.app.text_font_size),
                fg=self.app.current_color,
                bg=self.app.ui_builder.CANVAS_BG,
                bd=0, # 彻底去除输入框本身的白色框
                justify='center',
                insertbackground=self.app.current_color
            )
            self.active_entry.pack()
            
            # 3. 将整个 Frame 挂在画布的点击中心点
            self.text_window_id = self.app.canvas.create_window(x, y, window=self.text_frame, anchor='center')
            self.active_entry.focus_set()
            
            # 4. 🛠️ 拖拽引擎重构：使用完全物理静摩擦公式进行位移差值运算，100% 杜绝文本框消失
            def on_drag_start(e):
                self._drag_start_x = e.x_root
                self._drag_start_y = e.y_root
                # 记录文本框初始的物理画布位置
                coords = self.app.canvas.coords(self.text_window_id)
                self._orig_coords = (coords[0], coords[1])

            def on_drag_motion(e):
                # 严格计算鼠标滑行绝对像素差，绝不漂移
                dx = e.x_root - self._drag_start_x
                dy = e.y_root - self._drag_start_y
                new_x = self._orig_coords[0] + dx
                new_y = self._orig_coords[1] + dy
                self.app.canvas.coords(self.text_window_id, new_x, new_y)

            # 将拖动点击绑定在 Frame 的边框把手上
            self.text_frame.bind('<ButtonPress-1>', on_drag_start)
            self.text_frame.bind('<B1-Motion>', on_drag_motion)
            
            # 5. 绑定键盘输入和快捷键
            self.active_entry.bind('<KeyRelease>', self.adjust_border)
            self.active_entry.bind('<Return>', lambda e: self._commit_text())
            self.active_entry.bind('<Escape>', lambda e: self._cancel_text())
            
        else:
            self.is_drawing = True
            self.start_point = (x, y)
            self.temp_points = [(x, y)]
            self.temp_spray_dots.clear()
            self.temp_rainbow_colors.clear()
            if self.app.current_tool == 'rainbow':
                self.app.rainbow_brush.reset()

    def adjust_border(self, e=None):
        """物理布局管理器会自动包裹输入框，我们只需要让 Entry 随着字数变宽"""
        if not self.active_entry: return
        text_len = len(self.active_entry.get())
        # 根据字符个数，弹性伸缩 Entry 宽度（Frame 容器会自动跟着变大，边框永不缺失）
        self.active_entry.config(width=max(12, int(text_len * 1.2)))

    def _perform_flood_fill(self, click_x, click_y):
        """核心智能上色算法：种子漫延算法"""
        cw = self.app.canvas.winfo_width()
        ch = self.app.canvas.winfo_height()
        
        barrier_map = PILImage.new('L', (cw, ch), 0)
        draw = PILImageDraw.Draw(barrier_map)
        
        for s in self.app.shape_manager.shapes:
            if s.shape_type in ('image', 'text'): continue
            
            coords = []
            for p in s.points: coords.extend(p)
            if len(coords) < 4: continue
            
            w = max(2, s.width)
            if s.shape_type in ('rectangle', 'circle', 'ellipse'):
                draw.polygon(coords, outline=255, width=w)
            elif s.shape_type == 'spray' and hasattr(s, 'spray_dots'):
                for dx, dy in s.spray_dots:
                    draw.ellipse([dx-1, dy-1, dx+1, dy+1], fill=255)
            else:
                draw.line(coords, fill=255, width=w)
                
        try:
            if 0 <= click_x < cw and 0 <= click_y < ch:
                if barrier_map.getpixel((click_x, click_y)) < 200:
                    PILImageDraw.floodfill(barrier_map, (click_x, click_y), 128)
                    
                    rgb_tk = self.app.canvas.winfo_rgb(self.app.current_color)
                    r, g, b = rgb_tk[0] // 256, rgb_tk[1] // 256, rgb_tk[2] // 256
                    
                    color_layer = PILImage.new('RGBA', (cw, ch), (r, g, b, 255))
                    alpha_mask = barrier_map.point(lambda p: 255 if p == 128 else 0, mode='1')
                    
                    fill_layer = PILImage.new('RGBA', (cw, ch), (0, 0, 0, 0))
                    fill_layer.paste(color_layer, (0, 0), alpha_mask)
                    
                    photo = ImageTk.PhotoImage(fill_layer)
                    img_key = f"fill_{len(self.app.imported_images)}"
                    self.app.imported_images[img_key] = photo
                    
                    fill_shape = Shape('image', [(0, 0), (cw, ch)], self.app.current_color, 1)
                    fill_shape.image_key = img_key
                    
                    import base64
                    from io import BytesIO
                    buf = BytesIO()
                    fill_layer.save(buf, format="PNG")
                    fill_shape.image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
                    
                    self.app.shape_manager.shapes.insert(0, fill_shape)
                    self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
                    self.app._push_undo()
                    self.app.redraw_all()
        except Exception as err:
            print(f"种子漫延填充出错: {err}")

    def _commit_text(self):
        """将拖拽好的文本框确认并画在画布上"""
        if not self.active_entry: return
        
        text_content = self.active_entry.get().strip()
        coords = self.app.canvas.coords(self.text_window_id)
        final_x, final_y = coords[0], coords[1] if coords else (0,0)
        
        # 彻底清空临时 UI 组件
        self.app.canvas.delete(self.text_window_id)
        self.active_entry.destroy()
        self.text_frame.destroy()
        self.active_entry = None
        self.text_frame = None
        self.text_window_id = None
        
        if text_content:
            shape = Shape('text', [(final_x, final_y)], self.app.current_color, self.app.current_width)
            shape.text_content = text_content
            shape.text_font_size = self.app.text_font_size
            shape.angle = 0  
            self.app.shape_manager.add_shape(shape)
            self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
            self.app._push_undo()
            
        self.app.redraw_all()
        self.app._update_status()

    def _cancel_text(self):
        if self.active_entry:
            self.app.canvas.delete(self.text_window_id)
            self.active_entry.destroy()
            self.text_frame.destroy()
            self.active_entry = None
            self.text_frame = None
            self.text_window_id = None
        self.app.redraw_all()

    def on_drag(self, event):
        if self.is_drawing:
            x, y = event.x, event.y
            self._handle_drawing(x, y)
        elif self.is_moving and self.app.shape_manager.selected_shape:
            # 物理引擎拖动：使用 root 绝对坐标运算，彻底避免拖拽漂移
            dx = event.x_root - self.move_start[0]
            dy = event.y_root - self.move_start[1]
            TransformManager.move(self.app.shape_manager.selected_shape, dx, dy)
            self.move_start = (event.x_root, event.y_root)
            self.app.redraw_all()

    def _handle_drawing(self, x, y):
        c, w = self.app.current_color, self.app.current_width
        cvs = self.app.canvas
        if self.app.current_tool in ('line', 'rectangle', 'circle') and self.temp_shape_id:
            cvs.delete(self.temp_shape_id)

        if self.app.current_tool == 'line':
            self.temp_shape_id = cvs.create_line(self.start_point[0], self.start_point[1], x, y, fill=c, width=w, capstyle='round')
        elif self.app.current_tool == 'rectangle':
            self.temp_shape_id = cvs.create_rectangle(self.start_point[0], self.start_point[1], x, y, outline=c, width=w)
        elif self.app.current_tool == 'circle':
            cx, cy = (self.start_point[0] + x)/2, (self.start_point[1] + y)/2
            rx, ry = abs(x - self.start_point[0])/2, abs(y - self.start_point[1])/2
            self.temp_shape_id = cvs.create_oval(cx-rx, cy-ry, cx+rx, cy+ry, outline=c, width=w)
        elif self.app.current_tool in ('pencil', 'eraser', 'highlighter', 'rainbow'):
            self.temp_points.append((x, y))
            if len(self.temp_points) > 1:
                x1, y1 = self.temp_points[-2]
                if self.app.current_tool == 'eraser':
                    sid = cvs.create_line(x1, y1, x, y, fill=self.app.ui_builder.CANVAS_BG, width=w*5, capstyle='round')
                elif self.app.current_tool == 'highlighter':
                    sid = cvs.create_line(x1, y1, x, y, fill=c, width=w*4, capstyle='round', stipple='gray25')
                elif self.app.current_tool == 'rainbow':
                    color = self.app.rainbow_brush.get_next_color()
                    self.temp_rainbow_colors.append(color)
                    sid = cvs.create_line(x1, y1, x, y, fill=color, width=w, capstyle='round')
                else:
                    sid = cvs.create_line(x1, y1, x, y, fill=c, width=w, capstyle='round')
                self.temp_shape_ids.append(sid)
        elif self.app.current_tool == 'spray':
            self.temp_points.append((x, y))
            for _ in range(random.randint(3, 8)):
                ox, oy = random.randint(-w*3, w*3), random.randint(-w*3, w*3)
                sid = cvs.create_oval(x+ox, y+oy, x+ox+2, y+oy+2, fill=c, outline='')
                self.temp_shape_ids.append(sid)
                self.temp_spray_dots.append((x+ox, y+oy))

    def on_release(self, event):
        if not self.is_drawing:
            self.is_moving = False
            return
        x, y = event.x, event.y
        c, w = self.app.current_color, self.app.current_width
        
        if self.temp_shape_id: self.app.canvas.delete(self.temp_shape_id)
        for tid in self.temp_shape_ids: self.app.canvas.delete(tid)
        self.temp_shape_id = None
        self.temp_shape_ids.clear()

        shape = None
        if self.app.current_tool == 'line': shape = ShapeFactory.create_line(self.start_point, (x, y), c, w)
        elif self.app.current_tool == 'rectangle': shape = ShapeFactory.create_rectangle(self.start_point, (x, y), c, w)
        elif self.app.current_tool == 'circle':
            cx, cy = (self.start_point[0] + x)/2, (self.start_point[1] + y)/2
            rx, ry = abs(x - self.start_point[0])/2, abs(y - self.start_point[1])/2
            shape = ShapeFactory.create_ellipse((cx, cy), rx, ry, c, w)
        elif self.app.current_tool in ('pencil', 'highlighter') and len(self.temp_points) > 1:
            shape = Shape(self.app.current_tool, self.temp_points.copy(), c, w)
        elif self.app.current_tool == 'eraser' and len(self.temp_points) > 1:
            shape = Shape('pencil', self.temp_points.copy(), self.app.ui_builder.CANVAS_BG, w*5)
        elif self.app.current_tool == 'rainbow' and len(self.temp_points) > 1:
            shape = Shape('rainbow', self.temp_points.copy(), c, w)
            shape.rainbow_colors = self.temp_rainbow_colors.copy()
        elif self.app.current_tool == 'spray' and len(self.temp_points) > 0:
            shape = Shape('spray', self.temp_points.copy(), c, w)
            shape.spray_dots = self.temp_spray_dots.copy()

        if shape:
            self.app.shape_manager.add_shape(shape)
            self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
            self.app._push_undo()

        self.is_drawing = False
        self.app.redraw_all()
        self.app._update_status()

    def on_motion(self, event):
        self.app.coord_text.set(f"({event.x}, {event.y})")