#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math

class TransformManager:
    @staticmethod
    def move(shape, dx, dy):
        # 1. 移动主控制点
        shape.points = [(x + dx, y + dy) for x, y in shape.points]
        # 🛠️ 关键修复：同步平移喷枪的所有墨点
        if hasattr(shape, 'spray_dots') and shape.spray_dots:
            shape.spray_dots = [(x + dx, y + dy) for x, y in shape.spray_dots]
    
    @staticmethod
    def scale(shape, center_x, center_y, scale_x, scale_y):
        # 1. 缩放主控制点
        new_points = []
        for x, y in shape.points:
            new_x = center_x + (x - center_x) * scale_x
            new_y = center_y + (y - center_y) * scale_y
            new_points.append((new_x, new_y))
        shape.points = new_points
        
        # 🛠️ 关键修复：同步缩放喷枪的所有墨点
        if hasattr(shape, 'spray_dots') and shape.spray_dots:
            shape.spray_dots = [(center_x + (x - center_x) * scale_x, center_y + (y - center_y) * scale_y) for x, y in shape.spray_dots]
            
        # 🛠️ 关键修复：同步缩放文本的字号大小
        if shape.shape_type == 'text' and hasattr(shape, 'text_font_size'):
            avg_scale = (scale_x + scale_y) / 2
            shape.text_font_size = max(10, int(shape.text_font_size * avg_scale))
    
    @staticmethod
    def rotate(shape, center_x, center_y, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        def rotate_pt(pt):
            dx = pt[0] - center_x
            dy = pt[1] - center_y
            # 旋转标准方程
            return (center_x + dx * cos_angle - dy * sin_angle, center_y + dx * sin_angle + dy * cos_angle)
            
        # 1. 旋转主点
        shape.points = [rotate_pt(p) for p in shape.points]
        
        # 🛠️ 关键修复：同步旋转喷枪的所有墨点
        if hasattr(shape, 'spray_dots') and shape.spray_dots:
            shape.spray_dots = [rotate_pt(p) for p in shape.spray_dots]
            
        # 2. 旋转文本角度
        if shape.shape_type == 'text':
            shape.angle = (getattr(shape, 'angle', 0) - angle_degrees) % 360
    
    @staticmethod
    def flip_horizontal(shape, center_x=None):
        if center_x is None:
            bounds = shape.get_bounds()
            if bounds: center_x = (bounds[0] + bounds[2]) / 2
            else: return
        shape.points = [(2 * center_x - x, y) for x, y in shape.points]
        # 🛠️ 关键修复：同步翻转喷枪
        if hasattr(shape, 'spray_dots') and shape.spray_dots:
            shape.spray_dots = [(2 * center_x - x, y) for x, y in shape.spray_dots]
    
    @staticmethod
    def flip_vertical(shape, center_y=None):
        if center_y is None:
            bounds = shape.get_bounds()
            if bounds: center_y = (bounds[1] + bounds[3]) / 2
            else: return
        shape.points = [(x, 2 * center_y - y) for x, y in shape.points]
        # 🛠️ 关键修复：同步翻转喷枪
        if hasattr(shape, 'spray_dots') and shape.spray_dots:
            shape.spray_dots = [(x, 2 * center_y - y) for x, y in shape.spray_dots]
    
    @staticmethod
    def copy_and_offset(shape, offset_x=20, offset_y=20):
        new_shape = shape.copy()
        # 🛠️ 关键修复：拷贝时要将喷枪列表深度拷贝，不然墨点会粘连在原图形上
        if hasattr(shape, 'spray_dots') and shape.spray_dots:
            new_shape.spray_dots = shape.spray_dots.copy()
        TransformManager.move(new_shape, offset_x, offset_y)
        return new_shape

class TransformHelper:
    @staticmethod
    def create_shadow_shape(shape, shadow_offset=5, shadow_color='gray'):
        shadow = shape.copy()
        if hasattr(shape, 'spray_dots') and shape.spray_dots:
            shadow.spray_dots = shape.spray_dots.copy()
        shadow.color = shadow_color
        shadow.width = shape.width + 1
        TransformManager.move(shadow, shadow_offset, shadow_offset)
        return shadow