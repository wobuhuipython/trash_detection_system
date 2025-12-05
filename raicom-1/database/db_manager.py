"""
MySQL数据库配置和连接模块
"""
import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime
import base64
from typing import List, Dict, Optional

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        # MySQL数据库配置
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '123456',  
            'database': 'raicom_history',
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        # 创建数据库和表的SQL语句
        self.create_database_sql = "CREATE DATABASE IF NOT EXISTS raicom_history CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        self.create_table_sql = """
        CREATE TABLE IF NOT EXISTS detection_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            image_path VARCHAR(500) NOT NULL,
            image_data LONGBLOB,
            result_image_path VARCHAR(500),
            result_image_data LONGBLOB,
            detection_results JSON NOT NULL,
            detection_time DATETIME NOT NULL,
            confidence_scores JSON,
            processing_time FLOAT,
            source_type ENUM('upload', 'camera', 'manual_save') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_detection_time (detection_time),
            INDEX idx_source_type (source_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # 反馈表SQL
        self.create_feedback_table_sql = """
        CREATE TABLE IF NOT EXISTS detection_feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            detection_id INT,
            garbage_name VARCHAR(100) NOT NULL,
            predicted_category VARCHAR(50) NOT NULL,
            is_correct TINYINT(1) NOT NULL COMMENT '1=正确, 0=错误',
            correct_category VARCHAR(50) COMMENT '用户纠正的正确分类',
            satisfaction INT COMMENT '满意度评分 1-5',
            feedback_comment TEXT COMMENT '用户反馈意见',
            feedback_time DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_feedback_time (feedback_time),
            INDEX idx_predicted_category (predicted_category),
            INDEX idx_is_correct (is_correct),
            FOREIGN KEY (detection_id) REFERENCES detection_history(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # 题库表SQL
        self.create_quiz_table_sql = """
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question VARCHAR(500) NOT NULL COMMENT '题目内容',
            option_a VARCHAR(100) NOT NULL COMMENT '选项A',
            option_b VARCHAR(100) NOT NULL COMMENT '选项B',
            option_c VARCHAR(100) NOT NULL COMMENT '选项C',
            option_d VARCHAR(100) NOT NULL COMMENT '选项D',
            answer VARCHAR(100) NOT NULL COMMENT '正确答案',
            explanation TEXT COMMENT '答案解析',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """连接到数据库（初始化用）"""
        try:
            # 首先连接到MySQL服务器（不指定数据库）
            temp_config = self.config.config.copy()
            temp_config.pop('database', None)
            
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            # 创建数据库
            cursor.execute(self.config.create_database_sql)
            conn.commit()
            cursor.close()
            conn.close()
            
            # 连接到指定数据库并创建表
            conn = mysql.connector.connect(**self.config.config)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute(self.config.create_table_sql)
            cursor.execute(self.config.create_feedback_table_sql)
            cursor.execute(self.config.create_quiz_table_sql)
            conn.commit()
            cursor.close()
            conn.close()
            
            # 初始化题库数据
            self._init_quiz_data()
            
            print("数据库连接成功")
            return True
            
        except Error as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def _get_connection(self):
        """获取一个新的数据库连接（每次请求独立连接）"""
        try:
            conn = mysql.connector.connect(**self.config.config)
            return conn
        except Error as e:
            print(f"获取数据库连接失败: {e}")
            return None
    
    def disconnect(self):
        """断开数据库连接"""
        pass  # 不再需要，每次请求后自动关闭
    
    def save_detection_record(self, image_path: str, detection_results: List[Dict], 
                            confidence_scores: List[float], processing_time: float,
                            source_type: str = 'upload', image_data: bytes = None,
                            result_image_path: str = None, result_image_data: bytes = None) -> bool:
        """保存检测记录"""
        try:
            if not self._ensure_connection():
                return False
            
            # 准备数据
            detection_time = datetime.now()
            
            # 将检测结果转换为JSON字符串
            results_json = json.dumps(detection_results, ensure_ascii=False)
            confidence_json = json.dumps(confidence_scores, ensure_ascii=False)
            
            # 如果没有提供图片数据，尝试从文件路径读取
            if image_data is None and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            
            # 插入记录
            insert_sql = """
            INSERT INTO detection_history 
            (image_path, image_data, result_image_path, result_image_data, detection_results, detection_time, 
             confidence_scores, processing_time, source_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                image_path,
                image_data,
                result_image_path,
                result_image_data,
                results_json,
                detection_time,
                confidence_json,
                processing_time,
                source_type
            )
            
            self.cursor.execute(insert_sql, values)
            self.connection.commit()
            
            print(f"检测记录已保存: {image_path}")
            return True
            
        except Error as e:
            print(f"保存检测记录失败: {e}")
            return False
    
    def _ensure_connection(self) -> bool:
        """确保数据库可用（仅用于兼容）"""
        return True
    
    def get_detection_history(self, limit: int = 50, offset: int = 0, 
                            source_type: str = None) -> List[Dict]:
        """获取检测历史记录"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            
            # 构建查询SQL
            sql = """
            SELECT id, image_path, detection_results, detection_time, 
                   confidence_scores, processing_time, source_type
            FROM detection_history
            """
            params = []
            
            if source_type:
                sql += " WHERE source_type = %s"
                params.append(source_type)
            
            sql += " ORDER BY detection_time DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # 转换为字典列表
            history = []
            for row in results:
                record = {
                    'id': row[0],
                    'image_path': row[1],
                    'detection_results': json.loads(row[2]) if row[2] else [],
                    'detection_time': row[3],
                    'confidence_scores': json.loads(row[4]) if row[4] else [],
                    'processing_time': row[5],
                    'source_type': row[6]
                }
                history.append(record)
            
            return history
            
        except Error as e:
            print(f"获取检测历史失败: {e}")
            return []
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass
    
    def get_detection_count(self, source_type: str = None) -> int:
        """获取检测记录总数"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return 0
            cursor = conn.cursor()
            
            sql = "SELECT COUNT(*) FROM detection_history"
            params = []
            
            if source_type:
                sql += " WHERE source_type = %s"
                params.append(source_type)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result[0] if result else 0
            
        except Error as e:
            print(f"获取检测记录总数失败: {e}")
            return 0
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass
    
    def get_latest_detection_time(self, source_type: str = None) -> Optional[datetime]:
        """获取最新检测记录的时间"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return None
            cursor = conn.cursor()
            
            sql = "SELECT MAX(detection_time) FROM detection_history"
            params = []
            
            if source_type:
                sql += " WHERE source_type = %s"
                params.append(source_type)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
            
        except Error as e:
            print(f"获取最新检测时间失败: {e}")
            return None
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass
            
        except Error as e:
            print(f" 获取最新检测时间失败: {e}")
            return None
    
    def get_detection_history_after(self, after_time: datetime, source_type: str = None, limit: int = 50) -> List[Dict]:
        """获取指定时间之后的检测记录"""
        try:
            if not self._ensure_connection():
                return []
            
            # 构建查询SQL
            sql = """
            SELECT id, image_path, detection_results, detection_time, 
                   confidence_scores, processing_time, source_type
            FROM detection_history
            WHERE detection_time > %s
            """
            params = [after_time]
            
            if source_type:
                sql += " AND source_type = %s"
                params.append(source_type)
            
            sql += " ORDER BY detection_time DESC LIMIT %s"
            params.append(limit)
            
            self.cursor.execute(sql, params)
            results = self.cursor.fetchall()
            
            # 转换为字典列表
            history = []
            for row in results:
                record = {
                    'id': row[0],
                    'image_path': row[1],
                    'detection_results': json.loads(row[2]) if row[2] else [],
                    'detection_time': row[3],
                    'confidence_scores': json.loads(row[4]) if row[4] else [],
                    'processing_time': row[5],
                    'source_type': row[6]
                }
                history.append(record)
            
            return history
            
        except Error as e:
            print(f"获取增量检测历史失败: {e}")
            return []
    
    def delete_detection_record(self, record_id: int) -> bool:
        """删除检测记录"""
        try:
            if not self._ensure_connection():
                return False
            
            sql = "DELETE FROM detection_history WHERE id = %s"
            self.cursor.execute(sql, (record_id,))
            self.connection.commit()
            
            print(f"检测记录已删除: ID {record_id}")
            return True
            
        except Error as e:
            print(f"删除检测记录失败: {e}")
            return False
    
    def get_image_data(self, record_id: int) -> Optional[bytes]:
        """获取图片数据"""
        try:
            if not self._ensure_connection():
                return None
            
            sql = "SELECT image_data FROM detection_history WHERE id = %s"
            self.cursor.execute(sql, (record_id,))
            result = self.cursor.fetchone()
            
            return result[0] if result and result[0] else None
            
        except Error as e:
            print(f"获取图片数据失败: {e}")
            return None
    
    def get_result_image_data(self, record_id: int) -> Optional[bytes]:
        """获取结果图片数据"""
        try:
            if not self._ensure_connection():
                return None
            
            sql = "SELECT result_image_data FROM detection_history WHERE id = %s"
            self.cursor.execute(sql, (record_id,))
            result = self.cursor.fetchone()
            
            return result[0] if result and result[0] else None
            
        except Error as e:
            print(f"获取结果图片数据失败: {e}")
            return None
    
    def clear_old_records(self, days: int = 30) -> bool:
        """清理旧记录"""
        try:
            if not self._ensure_connection():
                return False
            
            sql = "DELETE FROM detection_history WHERE detection_time < DATE_SUB(NOW(), INTERVAL %s DAY)"
            self.cursor.execute(sql, (days,))
            self.connection.commit()
            
            print(f"已清理{days}天前的检测记录")
            return True
            
        except Error as e:
            print(f"清理旧记录失败: {e}")
            return False

    # ========== 反馈相关方法 ==========
    
    def save_feedback(self, garbage_name: str, predicted_category: str, 
                     is_correct: bool, correct_category: str = None,
                     satisfaction: int = None, feedback_comment: str = None,
                     detection_id: int = None) -> bool:
        """保存用户反馈"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO detection_feedback 
            (detection_id, garbage_name, predicted_category, is_correct, 
             correct_category, satisfaction, feedback_comment, feedback_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                detection_id,
                garbage_name,
                predicted_category,
                1 if is_correct else 0,
                correct_category,
                satisfaction,
                feedback_comment,
                datetime.now()
            )
            
            cursor.execute(sql, values)
            conn.commit()
            return True
            
        except Error as e:
            print(f"保存反馈失败: {e}")
            return False
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass
    
    def get_feedback_stats(self) -> Dict:
        """获取反馈统计数据"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return {}
            cursor = conn.cursor()
            
            stats = {}
            
            # 总反馈数
            cursor.execute("SELECT COUNT(*) FROM detection_feedback")
            stats['total_feedback'] = cursor.fetchone()[0]
            
            # 正确率
            cursor.execute("SELECT COUNT(*) FROM detection_feedback WHERE is_correct = 1")
            correct_count = cursor.fetchone()[0]
            stats['correct_count'] = correct_count
            stats['incorrect_count'] = stats['total_feedback'] - correct_count
            stats['accuracy_rate'] = round(correct_count / stats['total_feedback'] * 100, 2) if stats['total_feedback'] > 0 else 0
            
            # 平均满意度
            cursor.execute("SELECT AVG(satisfaction) FROM detection_feedback WHERE satisfaction IS NOT NULL")
            avg_satisfaction = cursor.fetchone()[0]
            stats['avg_satisfaction'] = round(float(avg_satisfaction), 2) if avg_satisfaction else 0
            
            # 各分类准确率
            cursor.execute("""
                SELECT predicted_category, 
                       COUNT(*) as total,
                       SUM(is_correct) as correct
                FROM detection_feedback 
                GROUP BY predicted_category
            """)
            category_stats = []
            for row in cursor.fetchall():
                category_stats.append({
                    'category': row[0],
                    'total': row[1],
                    'correct': row[2],
                    'accuracy': round(row[2] / row[1] * 100, 2) if row[1] > 0 else 0
                })
            stats['category_stats'] = category_stats
            
            # 满意度分布
            cursor.execute("""
                SELECT satisfaction, COUNT(*) as count
                FROM detection_feedback 
                WHERE satisfaction IS NOT NULL
                GROUP BY satisfaction
                ORDER BY satisfaction
            """)
            satisfaction_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for row in cursor.fetchall():
                if row[0]:
                    satisfaction_dist[row[0]] = row[1]
            stats['satisfaction_distribution'] = satisfaction_dist
            
            # 最近7天趋势
            cursor.execute("""
                SELECT DATE(feedback_time) as date,
                       COUNT(*) as total,
                       SUM(is_correct) as correct
                FROM detection_feedback 
                WHERE feedback_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(feedback_time)
                ORDER BY date
            """)
            daily_trend = []
            for row in cursor.fetchall():
                daily_trend.append({
                    'date': row[0].strftime('%m-%d') if row[0] else '',
                    'total': row[1],
                    'correct': row[2],
                    'accuracy': round(row[2] / row[1] * 100, 2) if row[1] > 0 else 0
                })
            stats['daily_trend'] = daily_trend
            
            return stats
            
        except Error as e:
            print(f"获取反馈统计失败: {e}")
            return {}
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass
    
    def get_feedback_list(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取反馈列表"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            
            sql = """
            SELECT id, detection_id, garbage_name, predicted_category, is_correct, 
                   correct_category, satisfaction, feedback_comment, feedback_time
            FROM detection_feedback
            ORDER BY feedback_time DESC
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(sql, (limit, offset))
            results = cursor.fetchall()
            
            feedback_list = []
            for row in results:
                feedback_list.append({
                    'id': row[0],
                    'detection_id': row[1],
                    'garbage_name': row[2],
                    'predicted_category': row[3],
                    'is_correct': bool(row[4]),
                    'correct_category': row[5],
                    'satisfaction': row[6],
                    'feedback_comment': row[7],
                    'feedback_time': row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else ''
                })
            
            return feedback_list
            
        except Error as e:
            print(f"获取反馈列表失败: {e}")
            return []
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass

    def get_feedback_detection_ids(self) -> List[int]:
        """获取所有已反馈的检测记录ID"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT detection_id FROM detection_feedback WHERE detection_id IS NOT NULL")
            results = cursor.fetchall()
            return [row[0] for row in results]
            
        except Error as e:
            print(f"获取已反馈ID失败: {e}")
            return []
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass

    def delete_feedback(self, feedback_id: int) -> bool:
        """删除反馈记录"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM detection_feedback WHERE id = %s", (feedback_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"删除反馈失败: {e}")
            return False
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass

    # ========== 题库相关方法 ==========
    
    def _init_quiz_data(self):
        """初始化题库数据（如果表为空则导入）"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            
            # 检查是否已有数据
            cursor.execute("SELECT COUNT(*) FROM quiz_questions")
            count = cursor.fetchone()[0]
            if count > 0:
                return  # 已有数据，不重复导入
            
            # 从question_bank.py导入题目
            from question.question_bank import QuestionBank
            qb = QuestionBank()
            
            for q in qb.questions:
                sql = """
                INSERT INTO quiz_questions (question, option_a, option_b, option_c, option_d, answer, explanation)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    q['question'],
                    q['options'][0],
                    q['options'][1],
                    q['options'][2],
                    q['options'][3],
                    q['answer'],
                    f"正确答案是{q['answer']}"
                ))
            
            conn.commit()
            print(f"已导入 {len(qb.questions)} 道题目到数据库")
            
        except Exception as e:
            print(f"初始化题库失败: {e}")
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass
    
    def get_quiz_questions(self, limit: int = 10) -> List[Dict]:
        """获取随机题目"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            
            # 随机获取题目
            sql = f"SELECT id, question, option_a, option_b, option_c, option_d, answer, explanation FROM quiz_questions ORDER BY RAND() LIMIT {limit}"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            questions = []
            for row in results:
                questions.append({
                    'id': row[0],
                    'question': row[1],
                    'options': [row[2], row[3], row[4], row[5]],
                    'answer': row[6],
                    'explanation': row[7]
                })
            
            return questions
            
        except Error as e:
            print(f"获取题目失败: {e}")
            return []
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass
    
    def get_quiz_count(self) -> int:
        """获取题库总数"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                return 0
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM quiz_questions")
            return cursor.fetchone()[0]
        except Error as e:
            print(f"获取题目数量失败: {e}")
            return 0
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass

# 全局数据库管理器实例
db_manager = DatabaseManager()
