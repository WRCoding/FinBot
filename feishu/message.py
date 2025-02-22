import requests
import json
from typing import Dict, Optional, Union

class FeishuMessageSender:
    """飞书消息发送器"""
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书消息发送器
        
        Args:
            app_id: 飞书应用的App ID
            app_secret: 飞书应用的App Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        self._token = None

    def _get_tenant_access_token(self) -> str:
        """获取tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["tenant_access_token"]

    def _get_headers(self) -> Dict:
        """获取请求头"""
        if not self._token:
            self._token = self._get_tenant_access_token()
            
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json; charset=utf-8"
        }

    def send_message(
        self,
        receive_id: str,
        msg_type: str,
        content: str,
        receive_id_type: str = "open_id"
    ) -> Dict:
        """
        发送消息
        
        Args:
            receive_id: 接收者的ID(用户ID或群组ID)
            msg_type: 消息类型(text/post/image/interactive等)
            content: 消息内容
            receive_id_type: 接收者ID类型(chat_id/open_id/user_id/union_id/email)
            
        Returns:
            Dict: 发送结果
        """
            
        data = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }
        
        response = requests.post(
            self.base_url,
            headers=self._get_headers(),
            json=data
        )
        # response.raise_for_status()
        return response.json()