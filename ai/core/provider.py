from enum import Enum

class AIProvider(Enum):
    """AI服务提供商枚举"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    
    @classmethod
    def get_priority_list(cls) -> list['AIProvider']:
        """获取优先级排序的提供商列表"""
        return [cls.DEEPSEEK, cls.OPENAI]  # 按优先级排序