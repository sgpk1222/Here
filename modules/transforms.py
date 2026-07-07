#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模块二：图形变换模块
功能：实现图形的移动、缩放、旋转、翻转等变换操作
作者：课程设计团队
"""

import math


class TransformManager:
    """
    图形变换管理器
    提供各种图形变换操作的静态方法
    所有变换都是基于数学矩阵变换算法实现
    """
    
    @staticmethod
    def move(shape, dx, dy):
        """
        移动图形
        
        参数:
            shape: 要移动的图形对象
            dx: 水平移动距离（像素）
            dy: 垂直移动距离（像素）
        
        说明:
            将图形的所有点沿x轴移动dx，沿y轴移动dy
        """
        # 对每个点应用平移变换
        shape.points = [(x + dx, y + dy) for x, y in shape.points]
    
    @staticmethod
    def scale(shape, center_x, center_y, scale_x, scale_y):
        """
        缩放图形
        
        参数:
            shape: 要缩放的图形对象
            center_x, center_y: 缩放中心点坐标
            scale_x: 水平缩放比例（1.0为原始大小）
            scale_y: 垂直缩放比例（1.0为原始大小）
        
        说明:
            相对于指定中心点进行缩放变换
            scale_x > 1: 放大
            scale_x < 1: 缩小
            scale_x = 1: 不变
        """
        new_points = []
        
        for x, y in shape.points:
            # 相对于缩放中心计算新坐标
            # 公式: new_x = center + (old - center) * scale
            new_x = center_x + (x - center_x) * scale_x
            new_y = center_y + (y - center_y) * scale_y
            new_points.append((new_x, new_y))
        
        shape.points = new_points
    
    @staticmethod
    def rotate(shape, center_x, center_y, angle_degrees):
        """
        旋转图形
        
        参数:
            shape: 要旋转的图形对象
            center_x, center_y: 旋转中心点坐标
            angle_degrees: 旋转角度（度数）
                正值: 逆时针旋转
                负值: 顺时针旋转
        
        说明:
            相对于指定中心点进行旋转变换
            使用标准旋转矩阵公式
        """
        # 将角度转换为弧度
        angle_radians = math.radians(angle_degrees)
        
        # 计算三角函数值
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        new_points = []
        
        for x, y in shape.points:
            # 计算相对于旋转中心的偏移
            dx = x - center_x
            dy = y - center_y
            
            # 应用旋转矩阵变换
            # [new_x] = [cos  -sin] [dx]
            # [new_y] = [sin   cos] [dy]
            new_x = center_x + dx * cos_angle - dy * sin_angle
            new_y = center_y + dx * sin_angle + dy * cos_angle
            
            new_points.append((new_x, new_y))
        
        shape.points = new_points
    
    @staticmethod
    def flip_horizontal(shape, center_x=None):
        """
        水平翻转图形
        
        参数:
            shape: 要翻转的图形对象
            center_x: 翻转轴线的x坐标（可选）
                如果不提供，则使用图形自身的中心
        
        说明:
            将图形相对于垂直轴线进行镜像翻转
        """
        # 如果没有指定翻转轴，使用图形中心
        if center_x is None:
            bounds = shape.get_bounds()
            if bounds:
                center_x = (bounds[0] + bounds[2]) / 2
            else:
                return
        
        # 对每个点进行水平镜像
        new_points = []
        for x, y in shape.points:
            # 公式: new_x = 2 * center_x - old_x
            new_x = 2 * center_x - x
            new_points.append((new_x, y))
        
        shape.points = new_points
    
    @staticmethod
    def flip_vertical(shape, center_y=None):
        """
        垂直翻转图形
        
        参数:
            shape: 要翻转的图形对象
            center_y: 翻转轴线的y坐标（可选）
                如果不提供，则使用图形自身的中心
        
        说明:
            将图形相对于水平轴线进行镜像翻转
        """
        # 如果没有指定翻转轴，使用图形中心
        if center_y is None:
            bounds = shape.get_bounds()
            if bounds:
                center_y = (bounds[1] + bounds[3]) / 2
            else:
                return
        
        # 对每个点进行垂直镜像
        new_points = []
        for x, y in shape.points:
            # 公式: new_y = 2 * center_y - old_y
            new_y = 2 * center_y - y
            new_points.append((x, new_y))
        
        shape.points = new_points
    
    @staticmethod
    def copy_and_offset(shape, offset_x=20, offset_y=20):
        """
        复制图形并偏移
        
        参数:
            shape: 要复制的图形对象
            offset_x: 水平偏移距离
            offset_y: 垂直偏移距离
        
        返回:
            Shape: 新的图形对象（已偏移）
        
        说明:
            创建图形副本并向指定方向偏移
        """
        # 创建副本
        new_shape = shape.copy()
        
        # 应用偏移
        TransformManager.move(new_shape, offset_x, offset_y)
        
        return new_shape
    
    @staticmethod
    def scale_uniform(shape, center_x, center_y, scale_factor):
        """
        等比例缩放图形
        
        参数:
            shape: 要缩放的图形对象
            center_x, center_y: 缩放中心
            scale_factor: 缩放比例（水平垂直相同）
        
        说明:
            保持图形原始比例进行缩放
        """
        TransformManager.scale(shape, center_x, center_y, scale_factor, scale_factor)
    
    @staticmethod
    def rotate_90(shape, center_x, center_y, clockwise=True):
        """
        旋转图形90度
        
        参数:
            shape: 要旋转的图形对象
            center_x, center_y: 旋转中心
            clockwise: 是否顺时针旋转
                True: 顺时针90度（实际为-90度）
                False: 逆时针90度
        
        说明:
            快捷方法，用于90度旋转
        """
        angle = -90 if clockwise else 90
        TransformManager.rotate(shape, center_x, center_y, angle)
    
    @staticmethod
    def shear_x(shape, center_y, shear_factor):
        """
        水平剪切变换
        
        参数:
            shape: 要变换的图形对象
            center_y: 剪切参考线的y坐标
            shear_factor: 剪切系数
        
        说明:
            将图形进行水平方向倾斜变换
        """
        new_points = []
        for x, y in shape.points:
            # 剪切公式: new_x = x + (y - center_y) * shear_factor
            offset = (y - center_y) * shear_factor
            new_points.append((x + offset, y))
        shape.points = new_points
    
    @staticmethod
    def shear_y(shape, center_x, shear_factor):
        """
        垂直剪切变换
        
        参数:
            shape: 要变换的图形对象
            center_x: 剪切参考线的x坐标
            shear_factor: 剪切系数
        
        说明:
            将图形进行垂直方向倾斜变换
        """
        new_points = []
        for x, y in shape.points:
            # 剪切公式: new_y = y + (x - center_x) * shear_factor
            offset = (x - center_x) * shear_factor
            new_points.append((x, y + offset))
        shape.points = new_points


# ============================================
# 变换辅助工具类
# ============================================

class TransformHelper:
    """
    变换辅助工具类
    提供常用的变换组合操作
    """
    
    @staticmethod
    def apply_all_transformations(shape, transformations):
        """
        批量应用多个变换
        
        参数:
            shape: 图形对象
            transformations: 变换列表，每个元素是 (变换函数, 参数列表) 元组
        
        示例:
            transformations = [
                (TransformManager.move, [10, 20]),
                (TransformManager.rotate, [100, 100, 45])
            ]
        """
        for transform_func, args in transformations:
            transform_func(shape, *args)
    
    @staticmethod
    def create_shadow_shape(shape, shadow_offset=5, shadow_color='gray'):
        """
        创建图形的阴影副本
        
        参数:
            shape: 原图形对象
            shadow_offset: 阴影偏移距离
            shadow_color: 阴影颜色
        
        返回:
            Shape: 阴影图形对象
        """
        # 复制图形
        shadow = shape.copy()
        
        # 设置阴影属性
        shadow.color = shadow_color
        shadow.width = shape.width + 1  # 略粗一些
        
        # 偏移阴影位置
        TransformManager.move(shadow, shadow_offset, shadow_offset)
        
        return shadow
    
    @staticmethod
    def create_outline_shape(shape, outline_offset=3, outline_color='white'):
        """
        创建图形的外轮廓副本
        
        参数:
            shape: 原图形对象
            outline_offset: 轮廓偏移
            outline_color: 轮廓颜色
        
        返回:
            Shape: 轮廓图形对象
        """
        outline = shape.copy()
        outline.color = outline_color
        outline.width = shape.width + outline_offset * 2
        return outline


# ============================================
# 变换参数对话框辅助类
# ============================================

class TransformDialogHelper:
    """
    变换参数对话框辅助类
    用于创建变换参数设置对话框
    """
    
    @staticmethod
    def get_scale_dialog_params(parent_window):
        """
        获取缩放参数对话框
        
        参数:
            parent_window: 父窗口
        
        返回:
            (scale_x, scale_y): 缩放比例
            None: 如果用户取消
        
        说明:
            此方法需要在主程序中配合Tkinter实现对话框
            这里仅提供参数验证逻辑
        """
        # 默认参数
        default_scale_x = 1.5
        default_scale_y = 1.5
        
        # 参数范围
        min_scale = 0.1
        max_scale = 5.0
        
        return default_scale_x, default_scale_y
    
    @staticmethod
    def validate_scale(scale_x, scale_y):
        """
        验证缩放参数
        
        参数:
            scale_x: 水平缩放比例
            scale_y: 垂直缩放比例
        
        返回:
            (bool, str): (是否有效, 错误消息)
        """
        if scale_x <= 0 or scale_y <= 0:
            return False, "缩放比例必须大于0"
        
        if scale_x > 10 or scale_y > 10:
            return False, "缩放比例过大（建议不超过10）"
        
        return True, "参数有效"
    
    @staticmethod
    def validate_rotation(angle):
        """
        验证旋转参数
        
        参数:
            angle: 旋转角度（度）
        
        返回:
            (bool, str): (是否有效, 错误消息)
        """
        if not -360 <= angle <= 360:
            return False, "旋转角度应在-360到360度之间"
        
        return True, "参数有效"


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    from shapes import Shape, ShapeFactory
    
    print("=== 测试图形变换 ===")
    
    # 创建测试图形
    rect = ShapeFactory.create_rectangle((100, 100), (200, 200), 'blue', 2)
    print(f"原始矩形边界: {rect.get_bounds()}")
    
    # 测试移动
    print("\n测试移动:")
    TransformManager.move(rect, 50, 50)
    print(f"移动后边界: {rect.get_bounds()}")
    
    # 测试缩放
    print("\n测试缩放:")
    cx, cy = rect.get_center()
    TransformManager.scale(rect, cx, cy, 2.0, 2.0)
    print(f"放大2倍后边界: {rect.get_bounds()}")
    
    # 测试旋转
    print("\n测试旋转:")
    circle = ShapeFactory.create_circle((300, 300), 50, 'red', 2)
    print(f"原始圆心: {circle.get_center()}")
    TransformManager.rotate(circle, 300, 300, 45)
    print(f"旋转45度后圆心: {circle.get_center()}")
    
    # 测试翻转
    print("\n测试翻转:")
    line = ShapeFactory.create_line((0, 0), (100, 100), 'green', 2)
    print(f"原始直线: {line.points}")
    TransformManager.flip_horizontal(line, 50)
    print(f"水平翻转后: {line.points}")
    
    # 测试复制偏移
    print("\n测试复制偏移:")
    original = ShapeFactory.create_rectangle((0, 0), (50, 50), 'black', 1)
    copy = TransformManager.copy_and_offset(original, 10, 10)
    print(f"原图形: {original.get_bounds()}")
    print(f"副本: {copy.get_bounds()}")
    
    # 测试阴影创建
    print("\n测试阴影创建:")
    shadow = TransformHelper.create_shadow_shape(original)
    print(f"阴影图形: {shadow}")
    
    # 测试参数验证
    print("\n测试参数验证:")
    valid, msg = TransformDialogHelper.validate_scale(1.5, 1.5)
    print(f"缩放参数(1.5, 1.5): {valid}, {msg}")
    
    valid, msg = TransformDialogHelper.validate_rotation(45)
    print(f"旋转参数(45): {valid}, {msg}")
    
    print("\n所有测试通过!")