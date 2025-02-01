from openai import OpenAI

from ai.services.manager import AIManager
from ai.core.provider import AIProvider

def main():
    # 使用默认优先级
    # ai_manager = AIManager()
    # try:
    #     response = ai_manager.generate("Hello, AI!")
    #     print("Default provider response:", response.content)
    # except Exception as e:
    #     print(f"Error with default provider: {str(e)}")
    with open('msg.xml', mode='r', encoding='utf-8') as f:
        file_content = f.read()    # 指定特定提供商
    ai_manager = AIManager(preferred_provider=AIProvider.OPENAI)
    try:
        response = ai_manager.generate(file_content)
        print("OpenAI response:", response.content)
    except Exception as e:
        print(f"Error with OpenAI: {str(e)}")

if __name__ == "__main__":
    main() 