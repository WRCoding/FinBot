# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTask(ABC):
    """
    任务基类，所有具体的任务都应该继承这个类
    """
    
    def __init__(self, task_id: str, description: str = ""):
        """
        初始化任务
        
        Args:
            task_id: 任务唯一标识
            description: 任务描述
        """
        self.task_id = task_id
        self.description = description
        self.logger = logging.getLogger(f"Task.{task_id}")
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        执行任务的具体逻辑，子类必须实现这个方法
        
        Returns:
            Any: 任务执行结果
        """
        pass

    @abstractmethod
    def get_cron_config(self) -> Dict[str, Any]:
        """
        获取任务的cron配置
        
        Returns:
            Dict[str, Any]: cron配置，包含hour, minute等参数
        """
        pass
    
    def get_trigger_type(self) -> str:
        """
        获取触发器类型
        
        Returns:
            str: 触发器类型，默认为cron
        """
        # 默认使用cron触发器，子类可以覆盖这个方法
        return "cron"
    
    def on_success(self, result: Any) -> None:
        """
        任务执行成功后的回调
        
        Args:
            result: 任务执行结果
        """
        self.logger.info(f"任务 {self.task_id} 执行成功: {result}")
    
    def on_error(self, error: Exception) -> None:
        """
        任务执行失败后的回调
        
        Args:
            error: 异常信息
        """
        self.logger.error(f"任务 {self.task_id} 执行失败: {str(error)}")
    
    def run(self, *args, **kwargs) -> Any:
        """
        运行任务，包含异常处理和回调
        
        Returns:
            Any: 任务执行结果
        """
        try:
            result = self.execute(*args, **kwargs)
            self.on_success(result)
            return result
        except Exception as e:
            self.on_error(e)
            raise
    
    def __str__(self) -> str:
        return f"Task[{self.task_id}]: {self.description}" 