#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模块三：特殊曲线生成模块
功能：生成各种数学特殊曲线（正弦曲线、阿基米德螺线、螺旋线等）
作者：课程设计团队
"""

import math


class CurveGenerator:
    """
    特殊曲线生成器
    提供各种数学曲线的生成算法
    """
    
    @staticmethod
    def generate_sine_curve(start_x, start_y, amplitude=50, period=200, cycles=2, points_count=200):
        """
        生成正弦曲线
        
        参数:
            start_x: 曲线起点x坐标
            start_y: 曲线起点y坐标（零点位置）
            amplitude: 振幅（波峰到零点的距离）
            period: 周期（一个完整波形的水平宽度）
            cycles: 周期数（要绘制多少个完整波形）
            points_count: 生成点数量（越多曲线越平滑）
        
        返回:
            list: 点坐标列表 [(x1,y1), (x2,y2), ...]
        
        数学公式:
            y = start_y + amplitude * sin(2π * x / period)
            x从0到cycles*period
        """
        points = []
        
        # 计算总长度
        total_length = period * cycles
        
        # 生成点
        for i in range(points_count + 1):
            # 当前进度（从0到total_length）
            progress = total_length * i / points_count
            
            # 计算x坐标
            x = start_x + progress
            
            # 计算y坐标（使用正弦函数）
            # 参数: 2π * cycles * i / points_count 确保绘制完整周期
            phase = 2 * math.pi * cycles * i / points_count
            y = start_y + amplitude * math.sin(phase)
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_archimedean_spiral(center_x, center_y, a=5, b=10, turns=3, points_count=500):
        """
        生成阿基米德螺线
        
        参数:
            center_x, center_y: 螺线中心点坐标
            a: 内径参数（起始半径）
            b: 螺距参数（每圈半径增量）
            turns: 圈数（螺线旋转的圈数）
            points_count: 生成点数量
        
        返回:
            list: 点坐标列表 [(x1,y1), (x2,y2), ...]
        
        数学公式:
            r = a + b * θ  (阿基米德螺线的极坐标方程)
            x = center_x + r * cos(θ)
            y = center_y + r * sin(θ)
            θ从0到turns * 2π
        """
        points = []
        
        # 计算最大角度（圈数转换为弧度）
        max_theta = turns * 2 * math.pi
        
        # 生成点
        for i in range(points_count + 1):
            # 当前角度
            theta = max_theta * i / points_count
            
            # 计算半径（阿基米德螺线方程）
            r = a + b * theta
            
            # 转换为笛卡尔坐标
            x = center_x + r * math.cos(theta)
            y = center_y + r * math.sin(theta)
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_logarithmic_spiral(center_x, center_y, a=10, b=0.1, turns=3, points_count=500):
        """
        生成对数螺线
        
        参数:
            center_x, center_y: 螺线中心点坐标
            a: 基准参数
            b: 增长率参数
            turns: 圈数
            points_count: 生成点数量
        
        返回:
            list: 点坐标列表
        
        数学公式:
            r = a * e^(b * θ)  (对数螺线的极坐标方程)
        """
        points = []
        max_theta = turns * 2 * math.pi
        
        for i in range(points_count + 1):
            theta = max_theta * i / points_count
            
            # 对数螺线方程
            r = a * math.exp(b * theta)
            
            x = center_x + r * math.cos(theta)
            y = center_y + r * math.sin(theta)
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_heart_curve(center_x, center_y, size=50, points_count=200):
        """
        生成心形曲线
        
        参数:
            center_x, center_y: 心形中心坐标
            size: 心形大小
            points_count: 生成点数量
        
        返回:
            list: 点坐标列表
        
        数学公式（参数方程）:
            x = size * 16 * sin³(t)
            y = size * (13cos(t) - 5cos(2t) - 2cos(3t) - cos(4t))
        """
        points = []
        
        for i in range(points_count + 1):
            # 参数t从0到2π
            t = 2 * math.pi * i / points_count
            
            # 心形参数方程
            x = center_x + size * 16 * math.pow(math.sin(t), 3) / 16
            y = center_y - size * (13 * math.cos(t) - 5 * math.cos(2*t) - 
                                   2 * math.cos(3*t) - math.cos(4*t)) / 16
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_lissajous_curve(center_x, center_y, a=100, b=100, 
                                  frequency_x=3, frequency_y=2, 
                                  phase=0, points_count=500):
        """
        生成利萨如曲线
        
        参数:
            center_x, center_y: 中心坐标
            a: 水平振幅
            b: 垂直振幅
            frequency_x: 水平频率
            frequency_y: 垂直频率
            phase: 相位差（弧度）
            points_count: 生成点数量
        
        返回:
            list: 点坐标列表
        
        数学公式:
            x = a * sin(frequency_x * t + phase)
            y = b * sin(frequency_y * t)
        """
        points = []
        
        for i in range(points_count + 1):
            t = 2 * math.pi * i / points_count
            
            x = center_x + a * math.sin(frequency_x * t + phase)
            y = center_y + b * math.sin(frequency_y * t)
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_star_shape(center_x, center_y, outer_radius=100, 
                            inner_radius=50, num_points=5, points_count=200):
        """
        生成星形曲线
        
        参数:
            center_x, center_y: 中心坐标
            outer_radius: 外顶点半径
            inner_radius: 内顶点半径
            num_points: 星形顶点数（五角星为5）
            points_count: 生成点数量
        
        返回:
            list: 点坐标列表
        """
        points = []
        
        # 每个顶点之间的角度
        angle_step = 2 * math.pi / num_points
        
        # 生成点
        for i in range(points_count + 1):
            # 当前角度（从顶部开始）
            angle = angle_step * i / (points_count / num_points) - math.pi / 2
            
            # 判断是外顶点还是内顶点
            if i % (points_count // (num_points * 2)) < points_count // (num_points * 2):
                # 使用外半径
                r = outer_radius
            else:
                # 使用内半径
                r = inner_radius
            
            # 计算当前半径（平滑过渡）
            segment = i / points_count * num_points * 2
            local_pos = segment % 2
            
            if local_pos < 1:
                # 从内到外
                r = inner_radius + (outer_radius - inner_radius) * local_pos
            else:
                # 从外到内
                r = outer_radius - (outer_radius - inner_radius) * (local_pos - 1)
            
            # 计算角度（每隔半个顶点角度切换）
            total_angle = angle_step * (i / points_count * num_points * 2) - math.pi / 2
            
            x = center_x + r * math.cos(total_angle)
            y = center_y + r * math.sin(total_angle)
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_flower_curve(center_x, center_y, radius=80, petals=5, points_count=360):
        """
        生成花瓣曲线
        
        参数:
            center_x, center_y: 中心坐标
            radius: 基础半径
            petals: 花瓣数量
            points_count: 生成点数量
        
        返回:
            list: 点坐标列表
        
        数学公式:
            r = radius * |sin(petals * θ)|
        """
        points = []
        
        for i in range(points_count + 1):
            theta = 2 * math.pi * i / points_count
            
            # 花瓣方程
            r = radius * abs(math.sin(petals * theta))
            
            x = center_x + r * math.cos(theta)
            y = center_y + r * math.sin(theta)
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_cosine_curve(start_x, start_y, amplitude=50, period=200, cycles=2, points_count=200):
        """
        生成余弦曲线
        
        参数:
            start_x: 起点x坐标
            start_y: 零点y坐标
            amplitude: 振幅
            period: 周期
            cycles: 周期数
            points_count: 点数量
        
        返回:
            list: 点坐标列表
        """
        points = []
        total_length = period * cycles
        
        for i in range(points_count + 1):
            progress = total_length * i / points_count
            x = start_x + progress
            
            phase = 2 * math.pi * cycles * i / points_count
            y = start_y + amplitude * math.cos(phase)
            
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_tangent_curve(start_x, start_y, amplitude=50, period=200, cycles=2, points_count=200):
        """
        生成正切曲线
        
        参数:
            start_x: 起点x坐标
            start_y: 零点y坐标
            amplitude: 振幅
            period: 周期
            cycles: 周期数
            points_count: 点数量
        
        返回:
            list: 点坐标列表
        
        注意:
            正切函数在奇点处有无限值，已做限制处理
        """
        points = []
        total_length = period * cycles
        
        for i in range(points_count + 1):
            progress = total_length * i / points_count
            x = start_x + progress
            
            phase = 2 * math.pi * cycles * i / points_count
            
            # 防止奇点（限制在有限范围内）
            try:
                tan_value = math.tan(phase)
                # 限制值范围
                tan_value = max(min(tan_value, 5), -5)
                y = start_y + amplitude * tan_value
                points.append((x, y))
            except:
                # 跳过奇点附近的点
                pass
        
        return points


# ============================================
# 曲线参数预设类
# ============================================

class CurvePresets:
    """
    曲线参数预设类
    提供常用曲线参数的预设值
    """
    
    # 正弦曲线预设
    SINE_SMALL = {'amplitude': 30, 'period': 150, 'cycles': 1}
    SINE_MEDIUM = {'amplitude': 50, 'period': 200, 'cycles': 2}
    SINE_LARGE = {'amplitude': 80, 'period': 300, 'cycles': 3}
    
    # 阿基米德螺线预设
    SPIRAL_SMALL = {'a': 3, 'b': 5, 'turns': 2}
    SPIRAL_MEDIUM = {'a': 5, 'b': 10, 'turns': 3}
    SPIRAL_LARGE = {'a': 8, 'b': 15, 'turns': 5}
    
    # 心形曲线预设
    HEART_SMALL = {'size': 30}
    HEART_MEDIUM = {'size': 50}
    HEART_LARGE = {'size': 80}
    
    # 星形曲线预设
    STAR_5 = {'outer_radius': 100, 'inner_radius': 50, 'num_points': 5}
    STAR_6 = {'outer_radius': 100, 'inner_radius': 50, 'num_points': 6}
    STAR_8 = {'outer_radius': 100, 'inner_radius': 50, 'num_points': 8}
    
    # 花瓣曲线预设
    FLOWER_5 = {'radius': 80, 'petals': 5}
    FLOWER_6 = {'radius': 80, 'petals': 6}
    FLOWER_8 = {'radius': 80, 'petals': 8}


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("=== 测试特殊曲线生成 ===")
    
    # 测试正弦曲线
    print("\n测试正弦曲线:")
    sine_points = CurveGenerator.generate_sine_curve(50, 300, 
                                                       amplitude=50, 
                                                       period=200, 
                                                       cycles=2)
    print(f"正弦曲线点数: {len(sine_points)}")
    print(f"起点: {sine_points[0]}, 终点: {sine_points[-1]}")
    
    # 测试阿基米德螺线
    print("\n测试阿基米德螺线:")
    spiral_points = CurveGenerator.generate_archimedean_spiral(400, 300,
                                                                a=5, b=10, turns=3)
    print(f"螺线点数: {len(spiral_points)}")
    print(f"中心: ({400}, {300})")
    
    # 测试心形曲线
    print("\n测试心形曲线:")
    heart_points = CurveGenerator.generate_heart_curve(600, 300, size=50)
    print(f"心形点数: {len(heart_points)}")
    
    # 测试利萨如曲线
    print("\n测试利萨如曲线:")
    lissajous_points = CurveGenerator.generate_lissajous_curve(800, 300,
                                                                a=80, b=80,
                                                                frequency_x=3,
                                                                frequency_y=2)
    print(f"利萨如曲线点数: {len(lissajous_points)}")
    
    # 测试星形曲线
    print("\n测试星形曲线:")
    star_points = CurveGenerator.generate_star_shape(1000, 300,
                                                     outer_radius=100,
                                                     inner_radius=50,
                                                     num_points=5)
    print(f"星形点数: {len(star_points)}")
    
    # 测试花瓣曲线
    print("\n测试花瓣曲线:")
    flower_points = CurveGenerator.generate_flower_curve(1200, 300,
                                                          radius=80,
                                                          petals=5)
    print(f"花瓣点数: {len(flower_points)}")
    
    # 测试预设
    print("\n测试预设参数:")
    print(f"正弦曲线预设(中等): {CurvePresets.SINE_MEDIUM}")
    print(f"螺线预设(中等): {CurvePresets.SPIRAL_MEDIUM}")
    
    print("\n所有测试通过!")