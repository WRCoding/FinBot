# -*- coding: utf-8 -*-

import importlib
import inspect
import logging
import os
import pkgutil
from typing import Dict, List, Type, Optional

from scheduler.base_task import BaseTask
from scheduler.task_scheduler import TaskScheduler


class TaskManager:
    """
    任务管理器，用于管理所有的任务
    """
    
    def __init__(self):
        self.scheduler = TaskScheduler()
        self.tasks: Dict[str, BaseTask] = {}
        self.logger = logging.getLogger("TaskManager")
    
    def register_task(self, task: BaseTask) -> bool:
        """
        注册一个任务
        
        Args:
            task: 任务实例
            
        Returns:
            bool: 是否注册成功
        """
        try:
            task_id = task.task_id
            
            if task_id in self.tasks:
                self.logger.warning(f"任务 {task_id} 已存在，将被替换")
            
            self.tasks[task_id] = task
            
            # 将任务添加到调度器
            trigger_type = task.get_trigger_type()
            trigger_args = task.get_cron_config()
            
            success = self.scheduler.add_job(
                job_id=task_id,
                func=task.run,
                trigger=trigger_type,
                **trigger_args
            )
            
            if success:
                self.logger.info(f"成功注册任务: {task}")
            else:
                self.logger.error(f"注册任务到调度器失败: {task}")
                del self.tasks[task_id]
                
            return success
        except Exception as e:
            self.logger.error(f"注册任务失败: {str(e)}")
            return False
    
    def unregister_task(self, task_id: str) -> bool:
        """
        注销一个任务
        
        Args:
            task_id: 任务唯一标识
            
        Returns:
            bool: 是否注销成功
        """
        try:
            if task_id not in self.tasks:
                self.logger.warning(f"任务 {task_id} 不存在")
                return False
            
            # 从调度器中移除任务
            success = self.scheduler.remove_job(task_id)
            
            if success:
                task = self.tasks.pop(task_id)
                self.logger.info(f"成功注销任务: {task}")
            else:
                self.logger.error(f"从调度器中移除任务失败: {task_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"注销任务失败: {str(e)}")
            return False
    
    def get_task(self, task_id: str) -> Optional[BaseTask]:
        """
        获取任务实例
        
        Args:
            task_id: 任务唯一标识
            
        Returns:
            Optional[BaseTask]: 任务实例，如果不存在则返回None
        """
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[BaseTask]:
        """
        获取所有任务
        
        Returns:
            List[BaseTask]: 所有任务实例
        """
        return list(self.tasks.values())
    
    def start(self) -> None:
        """
        启动任务管理器
        """
        self.scheduler.start()
        self.logger.info("任务管理器已启动")
    
    def shutdown(self) -> None:
        """
        关闭任务管理器
        """
        self.scheduler.shutdown()
        self.logger.info("任务管理器已关闭")

    def run_task_now(self, task_id: str) -> bool:
        """
        立即执行一个任务
        
        Args:
            task_id: 任务唯一标识
            
        Returns:
            bool: 是否执行成功
        """
        try:
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"任务 {task_id} 不存在")
                return False
            
            task.run()
            return True
        except Exception as e:
            self.logger.error(f"执行任务 {task_id} 失败: {str(e)}")
            return False 