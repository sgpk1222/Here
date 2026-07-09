import tkinter as tk
from tkinter import colorchooser

class UILayoutBuilder:
    BOOK_COVER = '#5d3a1a'
    BOOK_BINDING = '#8b6914'
    BOOK_ACCENT = '#c4a35a'
    PAGE_SHADOW = '#c8b896'
    SIDEBAR_BG = '#4a2c0f'
    SIDEBAR_TEXT = '#e8d5a3'
    BUTTON_BG = '#6b4423'
    BUTTON_HOVER = '#7d5229'
    BUTTON_ACTIVE = '#8b6914'
    BUTTON_TEXT = '#f5e6c8'
    CANVAS_BG = '#faf8f2'

    def __init__(self, app):
        self.app = app
        self.tool_buttons = {}

    def _bind_hover_effect(self, button, tool_id=None):
        button.bind("<Enter>", lambda e: button.config(bg=self.BUTTON_HOVER) if not (tool_id and self.app.current_tool == tool_id) else None)
        button.bind("<Leave>", lambda e: button.config(bg=self.BUTTON_BG) if not (tool_id and self.app.current_tool == tool_id) else None)

    def build_all(self):
        book_frame = tk.Frame(self.app.root, bg=self.BOOK_COVER, bd=0)
        book_frame.pack(fill='both', expand=True, padx=3, pady=3)
        self._create_quick_toolbar(book_frame)
        content = tk.Frame(book_frame, bg=self.BOOK_COVER)
        content.pack(fill='both', expand=True, side='top')
        self._create_sidebar(content)
        self._create_page(content)
        self._create_nav(book_frame)
        self._create_statusbar(book_frame)
        self._create_menu()

    def _create_quick_toolbar(self, parent):
        quick_bar = tk.Frame(parent, bg=self.BOOK_BINDING, height=36)
        quick_bar.pack(fill='x', side='top')
        quick_bar.pack_propagate(False)
        for text, cmd in [('📁 新建', self.app.on_new_notebook), ('💾 保存', self.app.on_save_file), ('↩ 撤销', self.app.undo), ('↪ 重做', self.app.redo)]:
            btn = tk.Button(quick_bar, text=text, font=('微软雅黑', 9, 'bold'), relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, activebackground=self.BUTTON_ACTIVE, activeforeground='white', cursor='hand2', padx=12, pady=2, command=cmd)
            btn.pack(side='left', padx=3, pady=3); self._bind_hover_effect(btn)

    def _create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.SIDEBAR_BG, width=180, bd=0)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        header = tk.Frame(sidebar, bg=self.BOOK_BINDING, height=40)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="📒 工具面板", font=('微软雅黑', 11, 'bold'), bg=self.BOOK_BINDING, fg=self.SIDEBAR_TEXT).pack(expand=True)

        tool_canvas = tk.Canvas(sidebar, bg=self.SIDEBAR_BG, highlightthickness=0, width=180)
        scrollbar = tk.Scrollbar(sidebar, orient='vertical', command=tool_canvas.yview)
        tool_frame = tk.Frame(tool_canvas, bg=self.SIDEBAR_BG)
        tool_frame.bind('<Configure>', lambda e: tool_canvas.configure(scrollregion=tool_canvas.bbox('all')))
        tool_canvas.create_window((0, 0), window=tool_frame, anchor='nw', width=180)
        tool_canvas.configure(yscrollcommand=scrollbar.set)

        self._build_tools(tool_frame)
        self._build_shapes(tool_frame)
        self._build_colors(tool_frame)
        self._build_width(tool_frame)
        self._build_font_size(tool_frame)
        self._build_bg_switcher(tool_frame)

        tool_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        tool_canvas.bind('<Enter>', lambda e: tool_canvas.bind_all('<MouseWheel>', lambda ev: tool_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
        tool_canvas.bind('<Leave>', lambda e: tool_canvas.unbind_all('<MouseWheel>'))

    def _build_tools(self, parent):
        tk.Label(parent, text="━ 绘图工具 ━", font=('微软雅黑', 9), bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))
        tools = [
            ('✏ 画笔', 'pencil'), ('🖊 荧光笔', 'highlighter'),
            ('🎨 喷枪', 'spray'), ('🌈 彩虹', 'rainbow'), ('🔤 文本', 'text'),
            ('🪣 填充', 'fill'), ('🧹 橡皮', 'eraser'), ('🖱 选择', 'select')
        ]
        for text, tid in tools:
            btn = tk.Button(parent, text=text, width=14, anchor='w', font=('微软雅黑', 9), relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, activebackground=self.BUTTON_ACTIVE, activeforeground='white', cursor='hand2', padx=8, command=lambda t=tid: self._select_tool(t))
            btn.pack(pady=1, padx=5); self.tool_buttons[tid] = btn; self._bind_hover_effect(btn, tid)
        self._select_tool('pencil')

    def _build_shapes(self, parent):
        tk.Label(parent, text="━ 常用形状 ━", font=('微软雅黑', 9), bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))
        shapes_frame = tk.Frame(parent, bg=self.SIDEBAR_BG)
        shapes_frame.pack(pady=2, fill='x', padx=6)
        for text, tid in [('📏 直线', 'line'), ('⬜ 矩形', 'rectangle'), ('⭕ 圆形', 'circle')]:
            btn = tk.Button(shapes_frame, text=text, font=('微软雅黑', 8), relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, activebackground=self.BUTTON_ACTIVE, activeforeground='white', cursor='hand2', padx=2, pady=4)
            btn.pack(side='left', expand=True, fill='x', padx=2); btn.config(command=lambda t=tid: self._select_tool(t))
            self.tool_buttons[tid] = btn; self._bind_hover_effect(btn, tid)

    def _select_tool(self, tool):
        self.app.current_tool = tool
        for tid, btn in self.tool_buttons.items():
            btn.config(bg=self.BUTTON_ACTIVE if tid == tool else self.BUTTON_BG, fg='white' if tid == tool else self.BUTTON_TEXT)
        if tool == 'rainbow': self.app.rainbow_brush.reset()
        if hasattr(self.app, 'canvas'):
            self.app.canvas.config(cursor='xterm' if tool == 'text' else 'hand2' if tool in ('select', 'fill') else 'cross')
        self.app.status_text.set(f"📖 当前工具: {tool}")

    def _build_colors(self, parent):
        tk.Label(parent, text="━ 颜色 ━", font=('微软雅黑', 9), bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))
        colors = ['#2c1810', '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#1abc9c', '#3498db', '#9b59b6', '#34495e', '#7f8c8d', '#ecf0f1', '#ffffff']
        color_frame = tk.Frame(parent, bg=self.SIDEBAR_BG)
        color_frame.pack(pady=2)
        for i, c in enumerate(colors):
            tk.Button(color_frame, bg=c, width=3, height=1, relief='flat', bd=1, cursor='hand2', command=lambda clr=c: self._pick_color(clr)).grid(row=i//4, column=i%4, padx=2, pady=2)
        custom_btn = tk.Button(parent, text="🎨 自定义颜色...", font=('微软雅黑', 8), bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, relief='flat', command=self._custom_color)
        custom_btn.pack(pady=4); self._bind_hover_effect(custom_btn)

    def _pick_color(self, color):
        self.app.current_color = color
        self.app.status_text.set(f"📖 当前颜色: {color}")

    def _custom_color(self):
        c = colorchooser.askcolor(title="选择颜色", initialcolor=self.app.current_color)
        if c[1]: self._pick_color(c[1])

    def _build_width(self, parent):
        tk.Label(parent, text="━ 笔触粗细 ━", font=('微软雅黑', 9), bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))
        wf = tk.Frame(parent, bg=self.SIDEBAR_BG)
        wf.pack(pady=2)
        for i, w in enumerate([1, 2, 3, 5, 8, 12, 16, 20]):
            btn = tk.Button(wf, text=str(w), width=3, font=('微软雅黑', 8), relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, command=lambda ww=w: self._set_width(ww))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2); self._bind_hover_effect(btn)
        self.width_preview = tk.Canvas(parent, width=120, height=24, bg=self.SIDEBAR_BG, highlightthickness=0)
        self.width_preview.pack(pady=4); self._set_width(3)

    def _set_width(self, w):
        self.app.current_width = w
        self.width_preview.delete('all')
        self.width_preview.create_line(10, 12, 110, 12, fill=self.BUTTON_TEXT, width=min(w, 10), capstyle='round')

    def _build_font_size(self, parent):
        tk.Label(parent, text="━ 文本字号 ━", font=('微软雅黑', 9), bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))
        ff = tk.Frame(parent, bg=self.SIDEBAR_BG)
        ff.pack(pady=2)
        self.font_scale = tk.Scale(ff, from_=10, to=72, orient='horizontal', font=('微软雅黑', 8), bg=self.SIDEBAR_BG, fg=self.BUTTON_TEXT, troughcolor=self.BUTTON_BG, highlightthickness=0, length=140, command=self._set_font_size)
        self.font_scale.set(self.app.text_font_size)
        self.font_scale.pack()

    def _set_font_size(self, val):
        self.app.text_font_size = int(val)
        if hasattr(self.app.canvas_handler, 'active_entry') and self.app.canvas_handler.active_entry:
            self.app.canvas_handler.active_entry.config(font=('微软雅黑', int(val)))
            self.app.canvas_handler.adjust_border()

    def _build_bg_switcher(self, parent):
        tk.Label(parent, text="━ 页面背景 ━", font=('微软雅黑', 9), bg=self.SIDEBAR_BG, fg=self.BOOK_ACCENT).pack(pady=(8, 4))
        bf = tk.Frame(parent, bg=self.SIDEBAR_BG); bf.pack(pady=2, fill='x', padx=8)
        bf.grid_columnconfigure(0, weight=1); bf.grid_columnconfigure(1, weight=1)
        for i, (text, mode) in enumerate([('空白', 'blank'), ('网格', 'grid'), ('横线', 'lined'), ('点阵', 'dot')]):
            btn = tk.Button(bf, text=text, font=('微软雅黑', 8), relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, activebackground=self.BUTTON_ACTIVE, activeforeground='white', command=lambda m=mode: self._change_bg(m))
            btn.grid(row=i//2, column=i%2, sticky='nsew', padx=2, pady=2); self._bind_hover_effect(btn)

    def _change_bg(self, mode):
        self.app.canvas_bg_mode = mode; self.app.redraw_all()

    def _create_page(self, parent):
        pc = tk.Frame(parent, bg=self.PAGE_SHADOW)
        pc.pack(side='left', fill='both', expand=True, padx=(20, 20), pady=(20, 10))
        pb = tk.Frame(pc, bg='white', bd=0)
        pb.pack(fill='both', expand=True, padx=1, pady=1)
        pi = tk.Frame(pb, bg=self.CANVAS_BG, bd=0)
        pi.pack(fill='both', expand=True, padx=3, pady=3)
        self.app.canvas = tk.Canvas(pi, bg=self.CANVAS_BG, cursor='cross', highlightthickness=0)
        self.app.canvas.pack(fill='both', expand=True)
        self.app.canvas.bind('<Configure>', lambda e: self.app.root.after(100, self.draw_page_background))

    def draw_page_background(self):
        cw, ch = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
        if cw < 50 or ch < 50: return
        self.app.canvas.delete('bg_decor')
        mode = self.app.canvas_bg_mode
        if mode == 'grid':
            for x in range(0, cw, 30): self.app.canvas.create_line(x, 0, x, ch, fill='#e8e0d0', tags='bg_decor')
            for y in range(0, ch, 30): self.app.canvas.create_line(0, y, cw, y, fill='#e8e0d0', tags='bg_decor')
        elif mode == 'lined':
            for y in range(30, ch, 30): self.app.canvas.create_line(0, y, cw, y, fill='#d8d0c0', tags='bg_decor')
            self.app.canvas.create_line(40, 0, 40, ch, fill='#f0c0c0', tags='bg_decor', width=1, dash=(2, 4))
        elif mode == 'dot':
            for x in range(0, cw, 20):
                for y in range(0, ch, 20): self.app.canvas.create_oval(x-1, y-1, x+1, y+1, fill='#d0c8b8', outline='', tags='bg_decor')

    def _create_nav(self, parent):
        nf = tk.Frame(parent, bg=self.BOOK_BINDING, height=36)
        nf.pack(fill='x', side='bottom')
        nf.pack_propagate(False)
        lf = tk.Frame(nf, bg=self.BOOK_BINDING); lf.pack(side='left', padx=20)
        pbtn = tk.Button(lf, text='◀ 上一页', font=('微软雅黑', 9), relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, command=self.app.prev_page)
        pbtn.pack(side='left', padx=2); self._bind_hover_effect(pbtn)
        self.page_label = tk.Label(lf, text='第 1 页', font=('微软雅黑', 10, 'bold'), bg=self.BOOK_BINDING, fg=self.SIDEBAR_TEXT, width=10)
        self.page_label.pack(side='left', padx=10)
        nbtn = tk.Button(lf, text='下一页 ▶', font=('微软雅黑', 9), relief='flat', bg=self.BUTTON_BG, fg=self.BUTTON_TEXT, command=self.app.next_page)
        nbtn.pack(side='left', padx=2); self._bind_hover_effect(nbtn)

    def _create_statusbar(self, parent):
        sf = tk.Frame(parent, bg='#3a1f0a', height=22)
        sf.pack(fill='x', side='bottom'); sf.pack_propagate(False)
        tk.Label(sf, textvariable=self.app.status_text, font=('微软雅黑', 8), bg='#3a1f0a', fg=self.BOOK_ACCENT, anchor='w', padx=10).pack(side='left', fill='x', expand=True)
        tk.Label(sf, textvariable=self.app.coord_text, font=('微软雅黑', 8), bg='#3a1f0a', fg=self.BOOK_ACCENT, padx=10).pack(side='right')
        tk.Label(sf, textvariable=self.app.count_text, font=('微软雅黑', 8), bg='#3a1f0a', fg=self.BOOK_ACCENT, padx=10).pack(side='right')

    def _create_menu(self):
        menubar = tk.Menu(self.app.root, bg=self.BOOK_COVER, fg=self.BUTTON_TEXT, activebackground=self.BUTTON_ACTIVE, font=('微软雅黑', 9))
        self.app.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='📁 文件', menu=file_menu)
        file_menu.add_command(label='新建笔记本', command=self.app.on_new_notebook, accelerator='Ctrl+N')
        file_menu.add_command(label='打开文件', command=self.app.on_open_file, accelerator='Ctrl+O')
        file_menu.add_command(label='保存文件', command=self.app.on_save_file, accelerator='Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label='导入图片', command=self.app.on_import_image)
        file_menu.add_command(label='导出为文本', command=self.app.on_export_text)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.app.root.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='✂ 编辑', menu=edit_menu)
        edit_menu.add_command(label='撤销', command=self.app.undo, accelerator='Ctrl+Z')
        edit_menu.add_command(label='重做', command=self.app.redo, accelerator='Ctrl+Y')
        edit_menu.add_separator()
        edit_menu.add_command(label='复制图形', command=self.app.copy_shape, accelerator='Ctrl+C')
        edit_menu.add_command(label='删除图形', command=self.app.delete_shape, accelerator='Delete')
        edit_menu.add_command(label='清空本页', command=self.app.on_clear_canvas)
        
        # 4. 📐 数学菜单 (🛠️ 完整恢复阿基米德螺线等几何命令！)
        math_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='📐 数学', menu=math_menu)
        math_menu.add_command(label='y=f(x) 函数图像', command=self.app.math_manager.on_math_function)
        math_menu.add_command(label='参数方程', command=self.app.math_manager.on_parametric_equation)
        math_menu.add_command(label='极坐标方程', command=self.app.math_manager.on_polar_equation)
        math_menu.add_separator()
        math_menu.add_command(label='正弦曲线', command=self.app.on_draw_sine_curve)
        math_menu.add_command(label='阿基米德螺线', command=self.app.on_draw_spiral)
        math_menu.add_command(label='心形曲线', command=self.app.on_draw_heart)
        math_menu.add_command(label='利萨如曲线', command=self.app.on_draw_lissajous)
        math_menu.add_command(label='花瓣曲线', command=self.app.on_draw_flower)

        transform_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='🔄 变换', menu=transform_menu)
        transform_menu.add_command(label='等比例缩放', command=self.app.on_scale_shape)
        transform_menu.add_command(label='中心点旋转', command=self.app.on_rotate_shape)
        transform_menu.add_command(label='水平翻转', command=lambda: self.app.on_flip_shape('horizontal'))
        transform_menu.add_command(label='垂直翻转', command=lambda: self.app.on_flip_shape('vertical'))

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='❓ 帮助', menu=help_menu)
        help_menu.add_command(label='使用说明', command=self.app._on_show_help)