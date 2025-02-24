from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass
class TemplateVariable:
    transactions: List[Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactions": self.transactions
        }

@dataclass
class TemplateData:
    template_id: str
    template_version_name: str
    template_variable: TemplateVariable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "template_version_name": self.template_version_name,
            "template_variable": self.template_variable.to_dict()
        }

@dataclass
class Template:
    type: str
    data: TemplateData

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "data": self.data.to_dict()
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    def to_escaped_json(self) -> str:
        """返回转义后的JSON字符串，适用于需要转义的场景（如HTTP请求体）"""
        return json.dumps(json.dumps(self.to_dict(), ensure_ascii=False))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        template_data = data["data"]
        return cls(
            type=data["type"],
            data=TemplateData(
                template_id=template_data["template_id"],
                template_version_name=template_data["template_version_name"],
                template_variable=TemplateVariable(
                    transactions=template_data["template_variable"]["transactions"]
                )
            )
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Template':
        return cls.from_dict(json.loads(json_str)) 