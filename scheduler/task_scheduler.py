# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, Callable, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.job import Job

class TaskScheduler:
    """
    任务调度器，用于管理和执行定时任务
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[str, Job] = {}
        self.logger = logging.getLogger("TaskScheduler")
    
    def add_job(self, 
                job_id: str, 
                func: Callable, 
                trigger: str = 'cron', 
                **trigger_args) -> bool:
        """
        添加一个定时任务
        
        Args:
            job_id: 任务唯一标识
            func: 要执行的函数
            trigger: 触发器类型，默认为cron
            **trigger_args: 触发器参数，如hour, minute等
            
        Returns:
            bool: 是否添加成功
        """
        try:
            if job_id in self.jobs:
                self.logger.warning(f"任务 {job_id} 已存在，将被替换")
                self.remove_job(job_id)
                
            job = self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                misfire_grace_time=None,
                **trigger_args
            )
            self.jobs[job_id] = job
            self.logger.info(f"成功添加任务: {job_id}")
            return True
        except Exception as e:
            self.logger.error(f"添加任务 {job_id} 失败: {str(e)}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        移除一个定时任务
        
        Args:
            job_id: 任务唯一标识
            
        Returns:
            bool: 是否移除成功
        """
        try:
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                self.logger.info(f"成功移除任务: {job_id}")
                return True
            else:
                self.logger.warning(f"任务 {job_id} 不存在")
                return False
        except Exception as e:
            self.logger.error(f"移除任务 {job_id} 失败: {str(e)}")
            return False
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """
        获取所有任务信息
        
        Returns:
            List[Dict[str, Any]]: 任务信息列表
        """
        jobs_info = []
        for job_id, job in self.jobs.items():
            trigger_info = str(job.trigger)
            jobs_info.append({
                "id": job_id,
                "trigger": trigger_info,
                "next_run_time": str(job.next_run_time) if job.next_run_time else "未调度"
            })
        return jobs_info
    
    def start(self) -> None:
        """
        启动调度器
        """
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("任务调度器已启动")
    
    def shutdown(self) -> None:
        """
        关闭调度器
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("任务调度器已关闭")
    
    def pause_job(self, job_id: str) -> bool:
        """
        暂停一个任务
        
        Args:
            job_id: 任务唯一标识
            
        Returns:
            bool: 是否暂停成功
        """
        try:
            if job_id in self.jobs:
                self.scheduler.pause_job(job_id)
                self.logger.info(f"成功暂停任务: {job_id}")
                return True
            else:
                self.logger.warning(f"任务 {job_id} 不存在")
                return False
        except Exception as e:
            self.logger.error(f"暂停任务 {job_id} 失败: {str(e)}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """
        恢复一个任务
        
        Args:
            job_id: 任务唯一标识
            
        Returns:
            bool: 是否恢复成功
        """
        try:
            if job_id in self.jobs:
                self.scheduler.resume_job(job_id)
                self.logger.info(f"成功恢复任务: {job_id}")
                return True
            else:
                self.logger.warning(f"任务 {job_id} 不存在")
                return False
        except Exception as e:
            self.logger.error(f"恢复任务 {job_id} 失败: {str(e)}")
            return False 