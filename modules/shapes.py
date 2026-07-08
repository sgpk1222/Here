#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模块一：图形类定义模块
功能：定义所有图形的数据结构、属性和基本方法
作者：课程设计团队
"""

class Shape:
    """
    图形基类
    所有图形（直线、矩形、圆形等）都继承自此类
    """
    
    def __init__(self, shape_type, points, color='black', width=2):
        """
        初始化图形对象
        
        参数:
            shape_type: 图形类型 (line/rectangle/circle/pencil/sine/spiral等)
            points: 图形的坐标点列表 [(x1,y1), (x2,y2), ...]
            color: 线条颜色 (默认黑色)
            width: 线条宽度 (默认2像素)
        """
        self.shape_type = shape_type          # 图形类型标识
        self.points = points                  # 图形坐标点列表
        self.color = color                    # 线条颜色
        self.width = width                    # 线条宽度
        self.selected = False                 # 是否被选中状态
        self.fill_color = None               # 填充颜色（可选）
    
    def get_bounds(self):
        """
        获取图形的边界框
        
        返回:
            (x1, y1, x2, y2): 边界框的左上角和右下角坐标
            None: 如果图形没有点则返回None
        """
        if not self.points:
            return None
        
        # 提取所有x坐标和y坐标
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]
        
        # 返回最小最大边界
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def contains_point(self, x, y, tolerance=5):
        """
        判断指定点是否在图形附近（用于选择检测）
        
        参数:
            x, y: 要检测的点坐标
            tolerance: 容差范围（像素），默认5像素
        
        返回:
            True: 点在图形附近
            False: 点不在图形附近
        """
        bounds = self.get_bounds()
        if bounds is None:
            return False
        
        x1, y1, x2, y2 = bounds
        
        # 判断点是否在边界框内（加上容差）
        return (x1 - tolerance <= x <= x2 + tolerance and 
                y1 - tolerance <= y <= y2 + tolerance)
    
    def get_center(self):
        """
        获取图形的中心点坐标
        
        返回:
            (cx, cy): 中心点坐标
        """
        bounds = self.get_bounds()
        if bounds is None:
            return (0, 0)
        
        x1, y1, x2, y2 = bounds
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def to_dict(self):
        """
        将图形对象转换为字典（用于JSON序列化）
        
        返回:
            dict: 包含图形所有属性的字典
        """
        data = {
            'shape_type': self.shape_type,
            'points': self.points,
            'color': self.color,
            'width': self.width,
            'fill_color': self.fill_color,
            'selected': self.selected
        }
        for attr in ['text_content', 'text_font_size', 'function_expr',
                      'image_path', 'image_key', 'image_size',
                      'rainbow_colors', 'spray_dots']:
            if hasattr(self, attr):
                data[attr] = getattr(self, attr)
        return data
    
    @staticmethod
    def from_dict(data):
        """
        从字典创建图形对象（用于JSON反序列化）
        
        参数:
            data: 包含图形属性的字典
        
        返回:
            Shape: 新创建的图形对象
        """
        # 确保点是元组形式
        points = [tuple(p) for p in data['points']]
        
        shape = Shape(
            data['shape_type'],
            points,
            data.get('color', 'black'),
            data.get('width', 2)
        )
        shape.fill_color = data.get('fill_color')
        shape.selected = data.get('selected', False)
        
        # 恢复扩展属性
        for attr in ['text_content', 'text_font_size', 'function_expr',
                      'image_path', 'image_key', 'image_size',
                      'rainbow_colors', 'spray_dots']:
            if attr in data:
                setattr(shape, attr, data[attr])
        
        return shape
    
    def copy(self):
        """
        创建图形的深拷贝副本
        
        返回:
            Shape: 新的图形对象（与原图形独立）
        """
        new_shape = Shape(
            self.shape_type,
            self.points.copy(),      # 复制点列表
            self.color,
            self.width
        )
        new_shape.fill_color = self.fill_color
        new_shape.selected = False    # 副本默认不选中
        return new_shape
    
    def __repr__(self):
        """字符串表示，便于调试"""
        return f"Shape(type={self.shape_type}, points={len(self.points)}, color={self.color})"


# ============================================
# 图形工厂类 - 简化图形创建
# ============================================

class ShapeFactory:
    """
    图形工厂类
    提供创建各种图形的静态方法
    """
    
    @staticmethod
    def create_line(start, end, color='black', width=2):
        """
        创建直线图形
        
        参数:
            start: 起点坐标 (x1, y1)
            end: 终点坐标 (x2, y2)
            color: 线条颜色
            width: 线条宽度
        """
        points = [start, end]
        return Shape('line', points, color, width)
    
    @staticmethod
    def create_rectangle(start, end, color='black', width=2):
        """
        创建矩形图形
        
        参数:
            start: 起点坐标（左上角）
            end: 终点坐标（右下角）
            color: 线条颜色
            width: 线条宽度
        """
        x1, y1 = start
        x2, y2 = end
        
        # 矩形的四个顶点 + 闭合点
        points = [
            (x1, y1),    # 左上
            (x1, y2),    # 左下
            (x2, y2),    # 右下
            (x2, y1),    # 右上
            (x1, y1)     # 闭合到起点
        ]
        return Shape('rectangle', points, color, width)
    
    @staticmethod
    def create_ellipse(center, radius_x, radius_y, color='black', width=2):
        """
        创建椭圆/圆形图形
        
        参数:
            center: 圆心坐标 (cx, cy)
            radius_x: 水平半径
            radius_y: 垂直半径
            color: 线条颜色
            width: 线条宽度
        """
        import math
        cx, cy = center
        points = []
        
        # 生成361个点（圆形的离散化）
        for i in range(361):
            angle = math.radians(i)
            x = cx + radius_x * math.cos(angle)
            y = cy + radius_y * math.sin(angle)
            points.append((x, y))
        
        return Shape('ellipse', points, color, width)
    
    @staticmethod
    def create_circle(center, radius, color='black', width=2):
        """
        创建圆形图形
        
        参数:
            center: 圆心坐标 (cx, cy)
            radius: 半径
            color: 线条颜色
            width: 线条宽度
        """
        return ShapeFactory.create_ellipse(center, radius, radius, color, width)
    
    @staticmethod
    def create_pencil_path(points, color='black', width=2):
        """
        创建自由画笔路径
        
        参数:
            points: 路径点列表
            color: 线条颜色
            width: 线条宽度
        """
        return Shape('pencil', points, color, width)


# ============================================
# 图形管理器类 - 管理所有图形
# ============================================

class ShapeManager:
    """
    图形管理器类
    管理画布上的所有图形对象
    """
    
    def __init__(self):
        """初始化图形管理器"""
        self.shapes = []           # 所有图形列表
        self.selected_shape = None # 当前选中的图形
    
    def add_shape(self, shape):
        """
        添加图形到管理器
        
        参数:
            shape: 要添加的图形对象
        """
        self.shapes.append(shape)
    
    def remove_shape(self, shape):
        """
        从管理器移除图形
        
        参数:
            shape: 要移除的图形对象
        """
        if shape in self.shapes:
            self.shapes.remove(shape)
    
    def clear_all(self):
        """清空所有图形"""
        self.shapes.clear()
        self.selected_shape = None
    
    def get_shape_at(self, x, y, tolerance=5):
        """
        获取指定位置的图形（从上到下查找）
        
        参数:
            x, y: 坐标点
            tolerance: 容差范围
        
        返回:
            Shape: 找到的图形，如果没找到返回None
        """
        # 从后往前查找（后绘制的在上面）
        for shape in reversed(self.shapes):
            if shape.contains_point(x, y, tolerance):
                return shape
        return None
    
    def select_shape(self, shape):
        """
        选指定图形
        
        参数:
            shape: 要选中的图形
        """
        # 取消之前的选择
        self.deselect_all()
        
        # 选中新图形
        if shape:
            shape.selected = True
            self.selected_shape = shape
    
    def deselect_all(self):
        """取消所有图形的选择"""
        for shape in self.shapes:
            shape.selected = False
        self.selected_shape = None
    
    def get_selected_shape(self):
        """获取当前选中的图形"""
        return self.selected_shape
    
    def count(self):
        """获取图形数量"""
        return len(self.shapes)
    
    def get_all_shapes(self):
        """获取所有图形"""
        return self.shapes.copy()
    
    def move_shape_to_front(self, shape):
        """将图形移到最上层"""
        if shape in self.shapes:
            self.shapes.remove(shape)
            self.shapes.append(shape)
    
    def move_shape_to_back(self, shape):
        """将图形移到最下层"""
        if shape in self.shapes:
            self.shapes.remove(shape)
            self.shapes.insert(0, shape)


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    # 测试图形类
    print("=== 测试图形类 ===")
    
    # 创建直线
    line = ShapeFactory.create_line((0, 0), (100, 100), 'red', 3)
    print(f"直线: {line}")
    print(f"边界框: {line.get_bounds()}")
    
    # 创建矩形
    rect = ShapeFactory.create_rectangle((50, 50), (150, 150), 'blue', 2)
    print(f"矩形: {rect}")
    print(f"中心点: {rect.get_center()}")
    
    # 创建圆形
    circle = ShapeFactory.create_circle((200, 200), 50, 'green', 2)
    print(f"圆形: {circle}")
    print(f"点数: {len(circle.points)}")
    
    # 测试序列化
    print("\n=== 测试序列化 ===")
    data = line.to_dict()
    print(f"序列化数据: {data}")
    
    new_line = Shape.from_dict(data)
    print(f"反序列化图形: {new_line}")
    
    # 测试图形管理器
    print("\n=== 测试图形管理器 ===")
    manager = ShapeManager()
    manager.add_shape(line)
    manager.add_shape(rect)
    manager.add_shape(circle)
    print(f"图形数量: {manager.count()}")
    
    # 测试选择
    found = manager.get_shape_at(100, 100)
    if found:
        manager.select_shape(found)
        print(f"选中图形: {found}")
    
    print("\n所有测试通过!")