import tkinter as tk
from tkinter import messagebox
import math
from shapes import Shape

class MathDialogManager:
    """管理并处理所有复杂的数学弹窗及计算逻辑"""
    def __init__(self, app):
        self.app = app

    def on_math_function(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("📐 绘制 y=f(x) 函数图像")
        dialog.geometry("500x400")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)
        
        tk.Label(dialog, text="函数表达式 (使用x作为变量):", font=('微软雅黑', 10), bg=self.app.ui_builder.CANVAS_BG).pack(pady=(10, 2))
        expr_var = tk.StringVar(value='sin(x)')
        tk.Entry(dialog, textvariable=expr_var, font=('Consolas', 14), width=30, justify='center').pack(pady=5)

        tk.Label(dialog, text="x 范围:").pack()
        xmin_var = tk.DoubleVar(value=-10)
        xmax_var = tk.DoubleVar(value=10)
        
        f = tk.Frame(dialog, bg=self.app.ui_builder.CANVAS_BG)
        f.pack()
        tk.Entry(f, textvariable=xmin_var, width=5).pack(side='left')
        tk.Label(f, text=" 到 ", bg=self.app.ui_builder.CANVAS_BG).pack(side='left')
        tk.Entry(f, textvariable=xmax_var, width=5).pack(side='left')

        def draw():
            try:
                expr, xmin, xmax = expr_var.get(), xmin_var.get(), xmax_var.get()
                cw, ch = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
                scale_x, scale_y = (cw - 100) / (xmax - xmin), 30
                safe_globals = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'sqrt': math.sqrt, 'abs': abs, 'exp': math.exp,
                    'log': math.log, 'pi': math.pi
                }
                
                points = []
                x = xmin
                while x <= xmax:
                    try:
                        y = eval(expr, {"__builtins__": {}}, {**safe_globals, 'x': x})
                        px, py = cw//2 + x * scale_x, ch//2 - y * scale_y
                        if 0 <= px <= cw and 0 <= py <= ch:
                            points.append((px, py))
                    except: pass
                    x += 0.1
                    
                if points:
                    shape = Shape('function', points, self.app.current_color, self.app.current_width)
                    self.app.shape_manager.add_shape(shape)
                    self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
                    self.app.redraw_all()
                    self.app._push_undo()
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"表达式错误: {str(e)}", parent=dialog)
                
        tk.Button(dialog, text="绘制图像", command=draw, bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=20, pady=5).pack(pady=20)

    def on_parametric_equation(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("📐 参数方程绘制")
        dialog.geometry("500x380")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)

        tk.Label(dialog, text="参数方程: x(t), y(t)", font=('微软雅黑', 14, 'bold'), bg=self.app.ui_builder.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="x(t) =", font=('微软雅黑', 10), bg=self.app.ui_builder.CANVAS_BG).pack()
        x_var = tk.StringVar(value='16*sin(t)**3')
        tk.Entry(dialog, textvariable=x_var, font=('Consolas', 12), width=30, justify='center').pack(pady=3, ipady=2)

        tk.Label(dialog, text="y(t) =", font=('微软雅黑', 10), bg=self.app.ui_builder.CANVAS_BG).pack()
        y_var = tk.StringVar(value='13*cos(t)-5*cos(2*t)-2*cos(3*t)-cos(4*t)')
        tk.Entry(dialog, textvariable=y_var, font=('Consolas', 12), width=30, justify='center').pack(pady=3, ipady=2)

        tk.Label(dialog, text="t范围: 0 ~", font=('微软雅黑', 10), bg=self.app.ui_builder.CANVAS_BG).pack(pady=5)
        tmax_var = tk.DoubleVar(value=2 * math.pi)
        tk.Scale(dialog, from_=math.pi, to=10 * math.pi, resolution=0.1, variable=tmax_var, orient='horizontal', length=300, bg=self.app.ui_builder.CANVAS_BG).pack()

        def draw_parametric():
            try:
                safe_globals = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'sqrt': math.sqrt, 'abs': abs, 'exp': math.exp,
                    'log': math.log, 'pi': math.pi, 'e': math.e,
                }
                cw = self.app.canvas.winfo_width()
                ch = self.app.canvas.winfo_height()
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
                    except: pass
                    t += 0.02

                if points:
                    shape = Shape('parametric', points, self.app.current_color, self.app.current_width)
                    self.app.shape_manager.add_shape(shape)
                    self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
                    self.app.redraw_all()
                    self.app._update_status()
                    self.app._push_undo()
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"表达式错误: {str(e)}", parent=dialog)

        tk.Button(dialog, text="📐 绘制参数方程", font=('微软雅黑', 12, 'bold'), bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=30, pady=8, command=draw_parametric).pack(pady=15)

    def on_polar_equation(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("📐 极坐标方程绘制")
        dialog.geometry("500x350")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)

        tk.Label(dialog, text="极坐标: r = f(θ)", font=('微软雅黑', 14, 'bold'), bg=self.app.ui_builder.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="r(θ) =", font=('微软雅黑', 10), bg=self.app.ui_builder.CANVAS_BG).pack()
        r_var = tk.StringVar(value='2*(1+cos(theta))')
        tk.Entry(dialog, textvariable=r_var, font=('Consolas', 12), width=30, justify='center').pack(pady=5, ipady=2)

        presets_frame = tk.Frame(dialog, bg=self.app.ui_builder.CANVAS_BG)
        presets_frame.pack(pady=5)
        for label, expr in [
            ('心形线', '2*(1+cos(theta))'),
            ('三叶草', '3*sin(2*theta)'),
            ('阿基米德', 'theta/3'),
            ('玫瑰线', '4*sin(3*theta)'),
        ]:
            tk.Button(presets_frame, text=label, font=('微软雅黑', 8), relief='flat', bg=self.app.ui_builder.BUTTON_BG, fg=self.app.ui_builder.BUTTON_TEXT, command=lambda e=expr: r_var.set(e)).pack(side='left', padx=2)

        def draw_polar():
            try:
                safe_globals = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'theta': 0, 'pi': math.pi,
                }
                cw = self.app.canvas.winfo_width()
                ch = self.app.canvas.winfo_height()
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
                    except: pass
                    theta += 0.02

                if points:
                    shape = Shape('polar', points, self.app.current_color, self.app.current_width)
                    self.app.shape_manager.add_shape(shape)
                    self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
                    self.app.redraw_all()
                    self.app._update_status()
                    self.app._push_undo()
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"表达式错误: {str(e)}", parent=dialog)

        tk.Button(dialog, text="📐 绘制极坐标方程", font=('微软雅黑', 12, 'bold'), bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=30, pady=8, command=draw_polar).pack(pady=15)

    def on_draw_spiral_dialog(self):
        """阿基米德螺线参数交互设定器"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("🌀 阿基米德螺线设置")
        dialog.geometry("380x320")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)

        tk.Label(dialog, text="阿基米德螺线 (r = a + b * θ)", font=('微软雅黑', 12, 'bold'), bg=self.app.ui_builder.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="起始半径 a (内径):", bg=self.app.ui_builder.CANVAS_BG).pack()
        a_var = tk.IntVar(value=5)
        tk.Scale(dialog, from_=0, to=50, orient='horizontal', variable=a_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="螺距参数 b (螺旋宽度):", bg=self.app.ui_builder.CANVAS_BG).pack()
        b_var = tk.IntVar(value=10)
        tk.Scale(dialog, from_=1, to=30, orient='horizontal', variable=b_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="旋转圈数 (Turns):", bg=self.app.ui_builder.CANVAS_BG).pack()
        turns_var = tk.IntVar(value=3)
        tk.Scale(dialog, from_=1, to=15, orient='horizontal', variable=turns_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        def draw():
            cw, ch = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
            from curves import CurveGenerator
            points = CurveGenerator.generate_archimedean_spiral(cw // 2, ch // 2, a_var.get(), b_var.get(), turns_var.get())
            shape = Shape('spiral', points, self.app.current_color, self.app.current_width)
            self.app.shape_manager.add_shape(shape)
            self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
            self.app.redraw_all()
            self.app._push_undo()
            dialog.destroy()

        tk.Button(dialog, text="绘制螺线", command=draw, bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=20, pady=5).pack(pady=15)

    def on_draw_sine_dialog(self):
        """🛠️ 新增：正弦曲线参数设置弹窗"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("📈 正弦曲线设置")
        dialog.geometry("380x320")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)

        tk.Label(dialog, text="正弦曲线参数 (y = A * sin(2π * x / T))", font=('微软雅黑', 11, 'bold'), bg=self.app.ui_builder.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="波形振幅 A (高度):", bg=self.app.ui_builder.CANVAS_BG).pack()
        amp_var = tk.IntVar(value=50)
        tk.Scale(dialog, from_=10, to=150, orient='horizontal', variable=amp_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="基本周期 T (波长):", bg=self.app.ui_builder.CANVAS_BG).pack()
        period_var = tk.IntVar(value=200)
        tk.Scale(dialog, from_=50, to=400, orient='horizontal', variable=period_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="周期数 (波形个数):", bg=self.app.ui_builder.CANVAS_BG).pack()
        cycles_var = tk.IntVar(value=2)
        tk.Scale(dialog, from_=1, to=8, orient='horizontal', variable=cycles_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        def draw():
            cw, ch = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
            from curves import CurveGenerator
            points = CurveGenerator.generate_sine_curve(50, ch // 2, amp_var.get(), period_var.get(), cycles_var.get())
            shape = Shape('sine', points, self.app.current_color, self.app.current_width)
            self.app.shape_manager.add_shape(shape)
            self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
            self.app.redraw_all()
            self.app._push_undo()
            dialog.destroy()

        tk.Button(dialog, text="绘制正弦线", command=draw, bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=20, pady=5).pack(pady=15)

    def on_draw_heart_dialog(self):
        """🛠️ 新增：心形曲线尺寸参数设置弹窗"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("💖 心形曲线设置")
        dialog.geometry("380x220")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)

        tk.Label(dialog, text="经典心形曲线", font=('微软雅黑', 12, 'bold'), bg=self.app.ui_builder.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="心形尺寸大小 (Size Scale):", bg=self.app.ui_builder.CANVAS_BG).pack()
        size_var = tk.IntVar(value=50)
        tk.Scale(dialog, from_=10, to=150, orient='horizontal', variable=size_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        def draw():
            cw, ch = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
            from curves import CurveGenerator
            points = CurveGenerator.generate_heart_curve(cw // 2, ch // 2, size=size_var.get())
            shape = Shape('heart', points, self.app.current_color, self.app.current_width)
            self.app.shape_manager.add_shape(shape)
            self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
            self.app.redraw_all()
            self.app._push_undo()
            dialog.destroy()

        tk.Button(dialog, text="绘制心形", command=draw, bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=20, pady=5).pack(pady=15)

    def on_draw_lissajous_dialog(self):
        """🛠️ 新增：利萨如曲线高级参数弹窗"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("🎨 利萨如曲线设置")
        dialog.geometry("380x380")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)

        tk.Label(dialog, text="利萨如声学谐振曲线", font=('微软雅黑', 12, 'bold'), bg=self.app.ui_builder.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="水平展宽 a:", bg=self.app.ui_builder.CANVAS_BG).pack()
        a_var = tk.IntVar(value=80)
        tk.Scale(dialog, from_=20, to=200, orient='horizontal', variable=a_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="垂直展宽 b:", bg=self.app.ui_builder.CANVAS_BG).pack()
        b_var = tk.IntVar(value=80)
        tk.Scale(dialog, from_=20, to=200, orient='horizontal', variable=b_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="水平振动频率 nx:", bg=self.app.ui_builder.CANVAS_BG).pack()
        fx_var = tk.IntVar(value=3)
        tk.Scale(dialog, from_=1, to=10, orient='horizontal', variable=fx_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="垂直振动频率 ny:", bg=self.app.ui_builder.CANVAS_BG).pack()
        fy_var = tk.IntVar(value=2)
        tk.Scale(dialog, from_=1, to=10, orient='horizontal', variable=fy_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        def draw():
            cw, ch = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
            from curves import CurveGenerator
            points = CurveGenerator.generate_lissajous_curve(cw // 2, ch // 2, a=a_var.get(), b=b_var.get(), frequency_x=fx_var.get(), frequency_y=fy_var.get())
            shape = Shape('lissajous', points, self.app.current_color, self.app.current_width)
            self.app.shape_manager.add_shape(shape)
            self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
            self.app.redraw_all()
            self.app._push_undo()
            dialog.destroy()

        tk.Button(dialog, text="绘制曲线", command=draw, bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=20, pady=5).pack(pady=15)

    def on_draw_flower_dialog(self):
        """🛠️ 新增：玫瑰花瓣曲线瓣数设置弹窗"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("🌸 花瓣曲线设置")
        dialog.geometry("380x280")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=self.app.ui_builder.CANVAS_BG)

        tk.Label(dialog, text="花瓣线 (r = radius * |sin(petals * θ)|)", font=('微软雅黑', 12, 'bold'), bg=self.app.ui_builder.CANVAS_BG).pack(pady=10)

        tk.Label(dialog, text="花瓣整体半径 R:", bg=self.app.ui_builder.CANVAS_BG).pack()
        r_var = tk.IntVar(value=80)
        tk.Scale(dialog, from_=20, to=200, orient='horizontal', variable=r_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        tk.Label(dialog, text="花瓣瓣数:", bg=self.app.ui_builder.CANVAS_BG).pack()
        petals_var = tk.IntVar(value=5)
        tk.Scale(dialog, from_=3, to=15, orient='horizontal', variable=petals_var, length=250, bg=self.app.ui_builder.CANVAS_BG, highlightthickness=0).pack()

        def draw():
            cw, ch = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
            from curves import CurveGenerator
            points = CurveGenerator.generate_flower_curve(cw // 2, ch // 2, radius=r_var.get(), petals=petals_var.get())
            shape = Shape('flower', points, self.app.current_color, self.app.current_width)
            self.app.shape_manager.add_shape(shape)
            self.app.pages[self.app.current_page] = self.app.shape_manager.shapes
            self.app.redraw_all()
            self.app._push_undo()
            dialog.destroy()

        tk.Button(dialog, text="绘制花瓣", command=draw, bg=self.app.ui_builder.BUTTON_ACTIVE, fg='white', relief='flat', padx=20, pady=5).pack(pady=15)