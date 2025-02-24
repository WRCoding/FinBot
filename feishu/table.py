import requests
from typing import Dict

from config import SHEET_TOKEN, WORK_TABLE


class FeishuTableSender:
    """飞书消息发送器"""

    def __init__(self, app_id: str, app_secret: str, token: str=SHEET_TOKEN) -> None:
        """
        初始化飞书消息发送器

        Args:
            app_id: 飞书应用的App ID
            app_secret: 飞书应用的App Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{token}/values_prepend"
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

    def insert_data(
            self,
            values
    ) -> Dict:
        """
        插入数据

        Args:
            values: 指定工作表中的范围和在该范围中插入的数据。
        Returns:
            Dict: 发送结果
        """

        data = {"valueRange": {
            "range": f"{WORK_TABLE}!A2:D2",
            "values": values
        }}
        response = requests.post(
            self.base_url,
            headers=self._get_headers(),
            json=data
        )
        # response.raise_for_status()
        return response.json()
