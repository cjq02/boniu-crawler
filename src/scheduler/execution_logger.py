"""
执行日志记录工具
用于记录爬虫任务的执行情况，支持手动执行和定时任务执行
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

from ..crawler.utils.db import connect


class ExecutionLogger:
    """执行日志记录器"""
    
    def __init__(self, environment: str = "production", execution_type: str = "manual"):
        self.environment = environment
        self.execution_type = execution_type  # 'scheduled' or 'manual'
        self.execution_id: Optional[int] = None
        self.logger = logging.getLogger(__name__)
    
    def start_execution(self, pages: int = 2, command: str = None, parameters: Dict[str, Any] = None) -> int:
        """记录任务开始执行
        
        Args:
            pages: 爬取页数
            command: 执行命令
            parameters: 执行参数字典
            
        Returns:
            执行记录ID
        """
        try:
            conn = connect()
            with conn.cursor() as cursor:
                # 将参数字典转换为JSON字符串
                parameters_json = json.dumps(parameters, ensure_ascii=False) if parameters else None
                
                # 插入执行记录
                cursor.execute("""
                    INSERT INTO ims_mdkeji_im_boniu_crawler_log 
                    (start_time, status, execution_type, environment, command, parameters, pages, created_at) 
                    VALUES (NOW(), 'running', %s, %s, %s, %s, %s, NOW())
                """, (self.execution_type, self.environment, command, parameters_json, pages))
                
                # 获取刚插入的记录ID
                self.execution_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"任务开始执行，记录ID: {self.execution_id}, 类型: {self.execution_type}")
                return self.execution_id
                
        except Exception as e:
            self.logger.error(f"记录任务开始失败: {e}")
            return None
    
    def end_execution(self, status: str, message: str = "", posts_count: int = 0):
        """记录任务执行结束
        
        Args:
            status: 执行状态 (success/failed/timeout/error)
            message: 执行消息或错误信息
            posts_count: 本次爬取的帖子数量
        """
        if not self.execution_id:
            self.logger.warning("没有执行记录ID，跳过结束记录")
            return
            
        try:
            conn = connect()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE ims_mdkeji_im_boniu_crawler_log 
                    SET end_time = NOW(), 
                        status = %s, 
                        message = %s, 
                        posts_count = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (status, message, posts_count, self.execution_id))
                conn.commit()
                
                self.logger.info(f"任务执行结束，状态: {status}, 消息: {message}")
                
        except Exception as e:
            self.logger.error(f"记录任务结束失败: {e}")
    
    @contextmanager
    def execution_context(self, pages: int = 2, command: str = None, parameters: Dict[str, Any] = None):
        """执行上下文管理器，自动记录开始和结束
        
        Args:
            pages: 爬取页数
            command: 执行命令
            parameters: 执行参数字典
            
        Yields:
            ExecutionLogger: 执行日志记录器实例
        """
        execution_id = self.start_execution(pages, command, parameters)
        try:
            yield self
        except Exception as e:
            self.end_execution('error', str(e))
            raise
        else:
            # 如果没有手动调用end_execution，则记录为成功
            if self.execution_id:
                self.end_execution('success', '任务执行成功')


def get_execution_logger(environment: str = None, execution_type: str = "manual") -> ExecutionLogger:
    """获取执行日志记录器实例
    
    Args:
        environment: 执行环境，默认从环境变量获取
        execution_type: 执行类型，'scheduled' 或 'manual'
        
    Returns:
        ExecutionLogger实例
    """
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'production')
    return ExecutionLogger(environment, execution_type)
