import json
import threading
import time
from pathlib import Path

import requests
from typing import Dict
import lark_oapi as lark
from lark_oapi.api.drive.v1 import *
from lark_oapi.api.sheets.v3 import GetSpreadsheetRequest, GetSpreadsheetResponse, QuerySpreadsheetSheetRequest, \
    QuerySpreadsheetSheetResponse

import config
from config import SHEET_TOKEN, WORK_TABLE, CSV_PATH
from util.common_util import find_project_root


class FeishuTable:
    """飞书消息发送器"""

    def __init__(self, app_id: str, app_secret: str, token: str = SHEET_TOKEN) -> None:
        """
        初始化飞书消息发送器

        Args:
            app_id: 飞书应用的App ID
            app_secret: 飞书应用的App Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{token}/values_prepend"
        self._access_token = None
        self.sheet_token = token
        self.table_name = None
        self.sheet_name = None
        self.client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()

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
        if not self._access_token:
            self._access_token = self._get_tenant_access_token()

        return {
            "Authorization": f"Bearer {self._access_token}",
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

    def get_table_name(self) -> Optional[str]:
        if self.table_name:
            return self.table_name
        # 构造请求对象
        request: GetSpreadsheetRequest = GetSpreadsheetRequest.builder() \
            .spreadsheet_token(self.sheet_token) \
            .user_id_type("open_id") \
            .build()

        # 发起请求
        response: GetSpreadsheetResponse = self.client.sheets.v3.spreadsheet.get(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.sheets.v3.spreadsheet.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return None

        # 处理业务结果
        self.table_name = response.data.spreadsheet.title
        return self.table_name

    def get_sheet_name(self) -> Optional[str]:
        if self.sheet_name:
            return self.sheet_name
        # 构造请求对象
        request: QuerySpreadsheetSheetRequest = QuerySpreadsheetSheetRequest.builder() \
            .spreadsheet_token(self.sheet_token) \
            .build()

        # 发起请求
        response: QuerySpreadsheetSheetResponse = self.client.sheets.v3.spreadsheet_sheet.query(request)
        self.sheet_name = response.data.sheets[0].title
        return self.sheet_name

    def async_export_table(self):
        thread = threading.Thread(target=self.export_table)
        thread.start()

    def export_table(self):
        ticket = self._create_export_task()
        file_token = self._query_task(ticket)
        if file_token:
            self._download_file(file_token)

    def _create_export_task(self) -> Optional[str]:
        request: CreateExportTaskRequest = CreateExportTaskRequest.builder() \
            .request_body(ExportTask.builder()
                          .file_extension("csv")
                          .token(self.sheet_token)
                          .type("sheet")
                          .sub_id(WORK_TABLE)
                          .build()) \
            .build()

        # 发起请求
        response: CreateExportTaskResponse = self.client.drive.v1.export_task.create(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.drive.v1.export_task.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data.ticket

    def _query_task(self, ticket: Optional[str] = None) -> Optional[str]:
        # 构造请求对象
        for i in range(10):
            request: GetExportTaskRequest = GetExportTaskRequest.builder() \
                .ticket(ticket) \
                .token(self.sheet_token) \
                .build()

            # 发起请求
            response: GetExportTaskResponse = self.client.drive.v1.export_task.get(request)
            if not response.success():
                lark.logger.error(
                    f"查询导出任务异常, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
                return None
            result = response.data.result
            if result.job_status == 0:
                return result.file_token
            if result.job_status != 1 and result.job_status != 2:
                print(f'查询导出任务job异常, job_status: {result.job_status}, msg: {result.job_error_msg}')
                return None
            time.sleep(1)
        return None

    def _download_file(self, file_token: str) -> None:
        # 构造请求对象
        request: DownloadExportTaskRequest = DownloadExportTaskRequest.builder() \
            .file_token(file_token) \
            .build()

        # 发起请求
        response: DownloadExportTaskResponse = self.client.drive.v1.export_task.download(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.drive.v1.export_task.download failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return
        file_path = f'{find_project_root()}/{response.file_name}'
        Path(file_path).unlink(missing_ok=True)
        # 处理业务结果
        f = open(f"{file_path}", "wb")
        f.write(response.file.read())
        f.close()
        pass

    def get_file_path(self):
        return f'{find_project_root()}/{self.get_table_name()}-{self.get_sheet_name()}.csv'