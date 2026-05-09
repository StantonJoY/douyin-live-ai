"""
DeepSeek AI 回复生成器
调用 DeepSeek API 根据主播简介和用户聊天内容生成回复
"""
from typing import Dict
import json
import os
from config import (
    LLM_API_KEY, 
    LLM_API_URL, 
    LLM_MODEL, 
    HOST_NAME,
    HOST_INTRO,
)

# 全局TTS引擎实例
tts_engine = None

def load_qa_context(file_path=None):
    """
    加载KB.md文件内容作为上下文
    """
    if file_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "..", "references", "KB.md")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"警告: 未找到文件 {file_path}，将使用基础提示。")
        return ""
    except Exception as e:
        print(f"加载KB文件出错: {e}，将使用基础提示。")
        return ""

def generate_prompt(query: str) -> str:
    """
    生成包含QA知识库上下文的提示
    """
    # 加载知识库上下文
    qa_context = load_qa_context()
    
    # 主播信息
    host_info = f"主播姓名: {HOST_NAME}\n主播介绍: {HOST_INTRO}\n" if HOST_NAME and HOST_INTRO else ""
    
    # 构建完整的提示
    if qa_context:
        prompt = f"""你是抖音直播间的主播助手，负责根据用户的问题生成自然、贴切的回答。请参考以下信息：

        {host_info}
        知识库信息：
        {qa_context}

        用户刚刚说了："{query}"

        请根据以上知识库信息和主播信息，生成回答。如果知识库中有相关内容，请优先参考；如果没有，则根据主播的人设和直播场景生成合适的回答。
        回答要求：
        1. 请注意回答中不要有表情和不必要的符号，因为会用于朗读
        2. 不要书面语，表达亲切口语化
        3. 直接回答关键信息，10-20字
        4. 称呼客户为老板
        """
    else:
        # 如果没有知识库，只使用基本的上下文
        prompt = f"""你是抖音直播间的主播助手，负责根据用户的问题生成自然、贴切的回答。
        {host_info}
        用户刚刚说了："{query}"
        请根据主播的人设和直播场景生成合适的回答。请注意回答中不要有表情和不必要的符号，因为会用于朗读"""
    
    return prompt


def speak_reply(text: str):
    """
    使用文本转语音(TTS)技术朗读AI回复
    
    Args:
        text: 要朗读的文本
    """
    try:
        import config
        import dashscope
        import requests
        from playsound import playsound
        import tempfile
        import os
        
        if not config.USE_TTS:
            return

        response = dashscope.MultiModalConversation.call(
            model="qwen3-tts-flash",
            api_key=config.DASHSCOPE_API_KEY,
            text=text,
            voice="Cherry"
        )
        
        if response.status_code == 200:
            # 获取音频URL
            audio_url = response.output.audio.url
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # 下载音频到临时文件
            audio_data = requests.get(audio_url).content
            with open(temp_path, "wb") as f:
                f.write(audio_data)
            
            # 播放音频
            playsound(temp_path)
            
            # 清理临时文件
            os.unlink(temp_path)
        else:
            print(f"语音合成失败")
        
    except Exception as e:
        # print(f"语音播报失败: {e}")
        pass


def generate_reply(user_name: str, user_message: str) -> Dict:
    """
    生成回复，优先使用缓存，最后调用 DeepSeek API
    
    Args:
        user_name: 用户名
        user_message: 用户消息内容
        
    Returns:
        {
            'user_name': str,
            'user_message': str,
            'reply': str,
            'success': bool,
            'from_cache': bool,  # 是否来自缓存
            'error': str (如果失败)
        }
    """
    from reply_cache import get_cached_reply, cache_reply
    from datetime import datetime
    
    # 先检查缓存
    cached_reply = get_cached_reply(user_message)
    if cached_reply:
        return {
            'user_name': user_name,
            'user_message': user_message,
            'reply': cached_reply,
            'success': True,
            'from_cache': True,
            'error': None
        }
  
    try:
        import openai
        client = openai.OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_API_URL
        )

        # 使用新实现的generate_prompt函数
        prompt = generate_prompt(user_message)
        
        response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user",
             "content": prompt}
        ]
        )
        reply = response.choices[0].message.content

        # 缓存新回复
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cache_reply(user_message, reply, timestamp)
        
        return {
            'user_name': user_name,
            'user_message': user_message,
            'reply': reply,
            'success': True,
            'from_cache': False,
            'error': None
        }

    except Exception as e:
        return {
            'user_name': user_name,
            'user_message': user_message,
            'reply': None,
            'success': False,
            'from_cache': False,
            'error': str(e)
        }

def generate_stub_reply(user_name: str, user_message: str) -> Dict:
    """
    Stub 版本的回复生成函数，不调用 DeepSeek API，也不做缓存
    直接返回固定回复
    """
    # Stub 方法，直接返回固定回复
    return {
        'user_name': user_name,
        'user_message': user_message,
        'reply': "",
        'success': True,
        'from_cache': False,  # Stub 方法不使用缓存
        'error': None
    }



def test_deepseek():
    """测试 DeepSeek API (带缓存)"""
    print("正在测试 DeepSeek API (带缓存)...")
    print("-" * 60)
    
    # 测试消息
    test_cases = [
        ("用户A", "樊老师孩子高敏感怎么引导"),  # 第一次调用API
        ("用户B", "这本书适合多大孩子看"),      # 第一次调用API
        ("用户C", "樊老师孩子高敏感怎么引导"),  # 第二次应该命中缓存
        ("用户D", "晚上好樊老师"),              # 第一次调用API
    ]
    
    for user, msg in test_cases:
        print(f"\n用户: {user}")
        print(f"消息: {msg}")
        print("-" * 40)
        
        result = generate_reply(user, msg)
        
        if result['success']:
            cache_status = "[缓存命中]" if result.get('from_cache') else "[API调用]"
            print(f"{cache_status} AI回复: {result['reply']}")
        else:
            print(f"错误: {result['error']}")
        print("=" * 60)
    
    # 显示缓存统计
    from reply_cache import get_cache
    stats = get_cache().get_stats()
    print(f"\n缓存统计: 已缓存 {stats['total_cached']} 条，总使用 {stats['total_uses']} 次")


if __name__ == '__main__':
    test_deepseek()