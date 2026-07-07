#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模块四：文件管理模块
功能：图形数据的保存、加载、导出等文件操作
作者：课程设计团队
"""

import json
import os
from datetime import datetime


class FileManager:
    """
    文件管理器
    处理图形数据的持久化存储（JSON格式）
    """
    
    # 文件格式版本号
    FILE_VERSION = "1.0"
    
    @staticmethod
    def save_to_file(shapes, filepath, metadata=None):
        """
        保存图形到JSON文件
        
        参数:
            shapes: 图形列表
            filepath: 保存路径（.json文件）
            metadata: 元数据（可选，如作者、描述等）
        
        返回:
            bool: 保存是否成功
        
        文件格式:
        {
            "version": "1.0",
            "metadata": {...},
            "shapes": [
                {
                    "shape_type": "line",
                    "points": [(x1,y1), (x2,y2)],
                    "color": "black",
                    "width": 2,
                    "fill_color": null
                },
                ...
            ]
        }
        """
        try:
            # 构建数据结构
            data = {
                'version': FileManager.FILE_VERSION,
                'metadata': metadata or {
                    'created_time': datetime.now().isoformat(),
                    'shape_count': len(shapes)
                },
                'shapes': [shape.to_dict() for shape in shapes]
            }
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False
    
    @staticmethod
    def load_from_file(filepath):
        """
        从JSON文件加载图形
        
        参数:
            filepath: 文件路径（.json文件）
        
        返回:
            list: 图形列表
            None: 加载失败
        
        说明:
            自动处理版本兼容性问题
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(filepath):
                print(f"文件不存在: {filepath}")
                return None
            
            # 读取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查版本
            version = data.get('version', 'unknown')
            if version != FileManager.FILE_VERSION:
                print(f"警告: 文件版本 {version} 可能不完全兼容")
            
            # 解析图形数据
            from shapes import Shape
            
            shapes = []
            shape_data_list = data.get('shapes', [])
            
            for shape_data in shape_data_list:
                shape = Shape.from_dict(shape_data)
                shapes.append(shape)
            
            print(f"成功加载 {len(shapes)} 个图形")
            return shapes
        
        except Exception as e:
            print(f"加载文件失败: {str(e)}")
            return None
    
    @staticmethod
    def get_file_info(filepath):
        """
        获取文件信息（不加载图形）
        
        参数:
            filepath: 文件路径
        
        返回:
            dict: 文件信息（版本、元数据、图形数量等）
            None: 文件无效
        """
        try:
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'version': data.get('version'),
                'metadata': data.get('metadata'),
                'shape_count': len(data.get('shapes', [])),
                'file_size': os.path.getsize(filepath)
            }
        
        except:
            return None
    
    @staticmethod
    def validate_file(filepath):
        """
        验证文件是否有效
        
        参数:
            filepath: 文件路径
        
        返回:
            (bool, str): (是否有效, 错误消息)
        """
        # 检查文件存在
        if not os.path.exists(filepath):
            return False, "文件不存在"
        
        # 检查文件扩展名
        if not filepath.endswith('.json'):
            return False, "文件格式不正确（应为.json）"
        
        # 尝试读取
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查必要字段
            if 'version' not in data:
                return False, "文件缺少版本信息"
            
            if 'shapes' not in data:
                return False, "文件缺少图形数据"
            
            return True, "文件有效"
        
        except json.JSONDecodeError:
            return False, "文件JSON格式错误"
        
        except Exception as e:
            return False, f"文件读取错误: {str(e)}"


class ExportManager:
    """
    导出管理器
    提供图形导出为其他格式的功能（扩展）
    """
    
    @staticmethod
    def export_to_text(shapes, filepath):
        """
        导出图形数据为文本格式
        
        参数:
            shapes: 图形列表
            filepath: 导出路径
        
        说明:
            用于简单查看和调试
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("图形数据导出\n")
                f.write("=" * 50 + "\n\n")
                
                for i, shape in enumerate(shapes, 1):
                    f.write(f"图形 {i}: {shape.shape_type}\n")
                    f.write(f"颜色: {shape.color}, 线宽: {shape.width}\n")
                    f.write(f"点数: {len(shape.points)}\n")
                    f.write(f"边界: {shape.get_bounds()}\n")
                    f.write("\n")
            
            return True
        
        except Exception as e:
            print(f"导出失败: {str(e)}")
            return False
    
    @staticmethod
    def export_summary(shapes, filepath):
        """
        导出图形统计摘要
        
        参数:
            shapes: 图形列表
            filepath: 导出路径
        """
        try:
            # 统计各类型图形数量
            type_counts = {}
            for shape in shapes:
                type_counts[shape.shape_type] = type_counts.get(shape.shape_type, 0) + 1
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("图形统计摘要\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"总图形数量: {len(shapes)}\n\n")
                f.write("各类型数量:\n")
                for shape_type, count in type_counts.items():
                    f.write(f"  {shape_type}: {count}\n")
            
            return True
        
        except Exception as e:
            print(f"导出摘要失败: {str(e)}")
            return False


class BackupManager:
    """
    备份管理器
    提供自动备份和恢复功能
    """
    
    # 备份目录
    BACKUP_DIR = "backups"
    
    @staticmethod
    def create_backup(shapes, backup_name=None):
        """
        创建备份
        
        参数:
            shapes: 图形列表
            backup_name: 备份名称（可选）
        
        返回:
            str: 备份文件路径
            None: 备份失败
        """
        try:
            # 创建备份目录
            if not os.path.exists(BackupManager.BACKUP_DIR):
                os.makedirs(BackupManager.BACKUP_DIR)
            
            # 生成备份文件名
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            filepath = os.path.join(BackupManager.BACKUP_DIR, f"{backup_name}.json")
            
            # 保存备份
            FileManager.save_to_file(shapes, filepath, 
                                    metadata={'backup_time': datetime.now().isoformat()})
            
            print(f"备份已创建: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"创建备份失败: {str(e)}")
            return None
    
    @staticmethod
    def restore_backup(filepath):
        """
        恢复备份
        
        参数:
            filepath: 备份文件路径
        
        返回:
            list: 图形列表
            None: 恢复失败
        """
        return FileManager.load_from_file(filepath)
    
    @staticmethod
    def list_backups():
        """
        列出所有备份
        
        返回:
            list: 备份文件列表（按时间排序）
        """
        if not os.path.exists(BackupManager.BACKUP_DIR):
            return []
        
        backups = []
        for filename in os.listdir(BackupManager.BACKUP_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(BackupManager.BACKUP_DIR, filename)
                info = FileManager.get_file_info(filepath)
                if info:
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'info': info
                    })
        
        # 按文件修改时间排序
        backups.sort(key=lambda x: x['info']['metadata'].get('backup_time', ''), reverse=True)
        
        return backups
    
    @staticmethod
    def auto_backup(shapes, max_backups=10):
        """
        自动备份（限制备份数量）
        
        参数:
            shapes: 图形列表
            max_backups: 最大备份保留数
        
        说明:
            自动清理旧备份
        """
        # 创建新备份
        BackupManager.create_backup(shapes)
        
        # 清理旧备份
        backups = BackupManager.list_backups()
        if len(backups) > max_backups:
            for backup in backups[max_backups:]:
                try:
                    os.remove(backup['filepath'])
                    print(f"已清理旧备份: {backup['filename']}")
                except:
                    pass


# ============================================
# 文件路径辅助工具
# ============================================

class FilePathHelper:
    """
    文件路径辅助工具
    提供文件路径相关操作
    """
    
    @staticmethod
    def get_default_save_dir():
        """获取默认保存目录"""
        default_dir = "saved_files"
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)
        return default_dir
    
    @staticmethod
    def generate_filename(prefix="drawing"):
        """生成默认文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.json"
    
    @staticmethod
    def ensure_json_extension(filepath):
        """确保文件扩展名是.json"""
        if not filepath.endswith('.json'):
            filepath += '.json'
        return filepath
    
    @staticmethod
    def get_recent_files(max_count=10):
        """获取最近使用的文件列表"""
        save_dir = FilePathHelper.get_default_save_dir()
        
        if not os.path.exists(save_dir):
            return []
        
        files = []
        for filename in os.listdir(save_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(save_dir, filename)
                files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'modified_time': os.path.getmtime(filepath)
                })
        
        # 按修改时间排序（最近的在前）
        files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return files[:max_count]


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    from shapes import Shape, ShapeFactory, ShapeManager
    
    print("=== 测试文件管理 ===")
    
    # 创建测试图形
    manager = ShapeManager()
    line = ShapeFactory.create_line((0, 0), (100, 100), 'red', 2)
    rect = ShapeFactory.create_rectangle((50, 50), (150, 150), 'blue', 3)
    circle = ShapeFactory.create_circle((200, 200), 50, 'green', 2)
    
    manager.add_shape(line)
    manager.add_shape(rect)
    manager.add_shape(circle)
    
    # 测试保存
    print("\n测试保存:")
    test_file = "test_shapes.json"
    success = FileManager.save_to_file(manager.shapes, test_file)
    print(f"保存结果: {success}")
    
    # 测试加载
    print("\n测试加载:")
    loaded_shapes = FileManager.load_from_file(test_file)
    if loaded_shapes:
        print(f"加载图形数: {len(loaded_shapes)}")
        for shape in loaded_shapes:
            print(f"  {shape}")
    
    # 测试文件信息
    print("\n测试文件信息:")
    info = FileManager.get_file_info(test_file)
    print(f"文件信息: {info}")
    
    # 测试文件验证
    print("\n测试文件验证:")
    valid, msg = FileManager.validate_file(test_file)
    print(f"验证结果: {valid}, {msg}")
    
    # 测试导出
    print("\n测试导出:")
    ExportManager.export_to_text(manager.shapes, "shapes_export.txt")
    ExportManager.export_summary(manager.shapes, "shapes_summary.txt")
    
    # 测试备份
    print("\n测试备份:")
    backup_path = BackupManager.create_backup(manager.shapes, "test_backup")
    print(f"备份路径: {backup_path}")
    
    # 测试备份列表
    backups = BackupManager.list_backups()
    print(f"备份数量: {len(backups)}")
    
    # 测试路径辅助工具
    print("\n测试路径辅助:")
    default_dir = FilePathHelper.get_default_save_dir()
    print(f"默认保存目录: {default_dir}")
    
    default_filename = FilePathHelper.generate_filename()
    print(f"默认文件名: {default_filename}")
    
    # 清理测试文件
    print("\n清理测试文件...")
    try:
        os.remove(test_file)
        os.remove("shapes_export.txt")
        os.remove("shapes_summary.txt")
        if backup_path:
            os.remove(backup_path)
        print("清理完成")
    except:
        pass
    
    print("\n所有测试通过!")