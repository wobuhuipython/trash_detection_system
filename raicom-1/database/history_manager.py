"""
历史记录管理类
"""
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db_manager
from typing import List, Dict, Optional
import os
import tempfile
from datetime import datetime

class HistoryManager(QObject):
    """历史记录管理器"""
    
    # 信号定义
    record_saved = pyqtSignal(bool, str)  # 记录保存结果
    history_loaded = pyqtSignal(list)     # 历史记录加载完成
    record_deleted = pyqtSignal(bool, str)  # 记录删除结果
    
    def __init__(self):
        super().__init__()
        self.db_manager = db_manager
        
    def save_detection_record(self, image_path: str, detection_results: List[Dict], 
                             confidence_scores: List[float], processing_time: float,
                             source_type: str = 'upload', result_image_path: str = None,
                             result_image_data: bytes = None) -> bool:
        """保存检测记录"""
        try:
            # 确保数据库连接
            if not self.db_manager.connection or not self.db_manager.connection.is_connected():
                if not self.db_manager.connect():
                    self.record_saved.emit(False, "数据库连接失败")
                    return False
            
            # 保存记录
            success = self.db_manager.save_detection_record(
                image_path=image_path,
                detection_results=detection_results,
                confidence_scores=confidence_scores,
                processing_time=processing_time,
                source_type=source_type,
                result_image_path=result_image_path,
                result_image_data=result_image_data
            )
            
            if success:
                self.record_saved.emit(True, f"检测记录已保存: {os.path.basename(image_path)}")
            else:
                self.record_saved.emit(False, "保存检测记录失败")
            
            return success
            
        except Exception as e:
            error_msg = f"保存记录时出错: {str(e)}"
            self.record_saved.emit(False, error_msg)
            return False
    
    def load_detection_history(self, limit: int = 50, offset: int = 0, 
                             source_type: str = None) -> List[Dict]:
        """加载检测历史记录"""
        try:
            history = self.db_manager.get_detection_history(
                limit=limit, 
                offset=offset, 
                source_type=source_type
            )
            self.history_loaded.emit(history)
            return history
            
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            self.history_loaded.emit([])
            return []
    
    def delete_detection_record(self, record_id: int) -> bool:
        """删除检测记录"""
        try:
            success = self.db_manager.delete_detection_record(record_id)
            
            if success:
                self.record_deleted.emit(True, f"记录 ID {record_id} 已删除")
            else:
                self.record_deleted.emit(False, "删除记录失败")
            
            return success
            
        except Exception as e:
            error_msg = f"删除记录时出错: {str(e)}"
            self.record_deleted.emit(False, error_msg)
            return False
    
    def get_detection_count(self, source_type: str = None) -> int:
        """获取检测记录总数"""
        try:
            return self.db_manager.get_detection_count(source_type)
        except Exception as e:
            print(f"获取记录总数失败: {e}")
            return 0
    
    def get_image_data(self, record_id: int) -> Optional[bytes]:
        """获取图片数据"""
        try:
            return self.db_manager.get_image_data(record_id)
        except Exception as e:
            print(f"获取图片数据失败: {e}")
            return None
    
    def get_result_image_data(self, record_id: int) -> Optional[bytes]:
        """获取结果图片数据"""
        try:
            return self.db_manager.get_result_image_data(record_id)
        except Exception as e:
            print(f"获取结果图片数据失败: {e}")
            return None
    
    def clear_old_records(self, days: int = 30) -> bool:
        """清理旧记录"""
        try:
            success = self.db_manager.clear_old_records(days)
            if success:
                self.record_deleted.emit(True, f"已清理{days}天前的记录")
            else:
                self.record_deleted.emit(False, "清理旧记录失败")
            return success
        except Exception as e:
            error_msg = f"清理旧记录时出错: {str(e)}"
            self.record_deleted.emit(False, error_msg)
            return False

class HistoryWorker(QThread):
    """历史记录工作线程"""
    
    # 信号定义
    history_loaded = pyqtSignal(list)
    operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, operation_type: str, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.kwargs = kwargs
        self.history_manager = HistoryManager()
        
    def run(self):
        """执行操作"""
        try:
            if self.operation_type == 'load_history':
                history = self.history_manager.load_detection_history(**self.kwargs)
                self.history_loaded.emit(history)
                
            elif self.operation_type == 'save_record':
                success = self.history_manager.save_detection_record(**self.kwargs)
                self.operation_completed.emit(success, "记录保存完成")
                
            elif self.operation_type == 'delete_record':
                success = self.history_manager.delete_detection_record(**self.kwargs)
                self.operation_completed.emit(success, "记录删除完成")
                
            elif self.operation_type == 'clear_old':
                success = self.history_manager.clear_old_records(**self.kwargs)
                self.operation_completed.emit(success, "清理完成")
                
        except Exception as e:
            self.operation_completed.emit(False, f"操作失败: {str(e)}")

# 全局历史记录管理器实例
history_manager = HistoryManager()
