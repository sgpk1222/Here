#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Shape:
    """图形基类"""
    def __init__(self, shape_type, points, color='black', width=2):
        self.shape_type = shape_type
        self.points = points
        self.color = color
        self.width = width
        self.selected = False
        self.fill_color = None
        self.angle = 0  # 新增：用于支持文本的旋转角度
    
    def get_bounds(self):
        if not self.points: return None
        
        # 针对文本的包围盒估算
        if self.shape_type == 'text' and hasattr(self, 'text_content'):
            x, y = self.points[0]
            fs = getattr(self, 'text_font_size', 20)
            w = len(self.text_content) * fs * 0.7
            h = fs * 1.2
            return (x - w/2, y - h/2, x + w/2, y + h/2)
        
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def contains_point(self, x, y, tolerance=5):
        bounds = self.get_bounds()
        if bounds is None: return False
        
        # 修复荧光笔和粗线难以选中的问题：根据线宽动态放大宽容度
        actual_tolerance = max(tolerance, self.width * 2)
        if self.shape_type == 'highlighter':
            actual_tolerance = max(actual_tolerance, self.width * 4)
            
        x1, y1, x2, y2 = bounds
        return (x1 - actual_tolerance <= x <= x2 + actual_tolerance and 
                y1 - actual_tolerance <= y <= y2 + actual_tolerance)
    
    def get_center(self):
        bounds = self.get_bounds()
        if bounds is None: return (0, 0)
        x1, y1, x2, y2 = bounds
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def to_dict(self):
        data = {
            'shape_type': self.shape_type,
            'points': self.points,
            'color': self.color,
            'width': self.width,
            'fill_color': self.fill_color,
            'selected': self.selected,
            'angle': getattr(self, 'angle', 0)
        }
        for attr in ['text_content', 'text_font_size', 'function_expr',
                      'image_path', 'image_key', 'image_size',
                      'rainbow_colors', 'spray_dots']:
            if hasattr(self, attr):
                data[attr] = getattr(self, attr)
        return data
    
    @staticmethod
    def from_dict(data):
        points = [tuple(p) for p in data['points']]
        shape = Shape(data['shape_type'], points, data.get('color', 'black'), data.get('width', 2))
        shape.fill_color = data.get('fill_color')
        shape.selected = data.get('selected', False)
        shape.angle = data.get('angle', 0)
        
        for attr in ['text_content', 'text_font_size', 'function_expr',
                      'image_path', 'image_key', 'image_size', 'rainbow_colors', 'spray_dots']:
            if attr in data: setattr(shape, attr, data[attr])
        return shape
    
    def copy(self):
        new_shape = Shape(self.shape_type, self.points.copy(), self.color, self.width)
        new_shape.fill_color = self.fill_color
        new_shape.angle = getattr(self, 'angle', 0)
        new_shape.selected = False
        return new_shape
    
    def __repr__(self):
        return f"Shape(type={self.shape_type}, points={len(self.points)}, color={self.color})"

class ShapeFactory:
    @staticmethod
    def create_line(start, end, color='black', width=2): return Shape('line', [start, end], color, width)
    @staticmethod
    def create_rectangle(start, end, color='black', width=2):
        x1, y1 = start
        x2, y2 = end
        return Shape('rectangle', [(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)], color, width)
    @staticmethod
    def create_ellipse(center, radius_x, radius_y, color='black', width=2):
        import math
        cx, cy = center
        points = [(cx + radius_x * math.cos(math.radians(i)), cy + radius_y * math.sin(math.radians(i))) for i in range(361)]
        return Shape('ellipse', points, color, width)
    @staticmethod
    def create_circle(center, radius, color='black', width=2):
        return ShapeFactory.create_ellipse(center, radius, radius, color, width)

class ShapeManager:
    def __init__(self):
        self.shapes = []
        self.selected_shape = None
    def add_shape(self, shape): self.shapes.append(shape)
    def remove_shape(self, shape):
        if shape in self.shapes: self.shapes.remove(shape)
    def clear_all(self):
        self.shapes.clear()
        self.selected_shape = None
    def get_shape_at(self, x, y, tolerance=5):
        for shape in reversed(self.shapes):
            if shape.contains_point(x, y, tolerance): return shape
        return None
    def select_shape(self, shape):
        self.deselect_all()
        if shape:
            shape.selected = True
            self.selected_shape = shape
    def deselect_all(self):
        for shape in self.shapes: shape.selected = False
        self.selected_shape = None
    def get_selected_shape(self): return self.selected_shape
    def count(self): return len(self.shapes)