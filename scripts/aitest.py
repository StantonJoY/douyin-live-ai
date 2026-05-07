# 请安装 DashScope SDK 的最新版本
import os
import dashscope
import requests
from playsound import playsound
import tempfile

dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

text = "那我来给大家推荐一款T恤，这款呢真的是超级好看"
# SpeechSynthesizer接口使用方法：dashscope.audio.qwen_tts.SpeechSynthesizer.call(...)
response = dashscope.MultiModalConversation.call(
    # 如需使用指令控制功能，请将model替换为qwen3-tts-instruct-flash
    model="qwen3-tts-flash",
    
    api_key="sk-b16b1cece8784dc68d4d1bcd57caf2cf",
    # api_key=os.getenv("DASHSCOPE_API_KEY"),
    text=text,
    voice="Cherry"
    # 如需使用指令控制功能，请取消下方注释，并将model替换为qwen3-tts-instruct-flash
    # instructions='语速较快，带有明显的上扬语调，适合介绍时尚产品。',
    # optimize_instructions=True
)

# 获取音频URL
audio_url = response.output.audio.url
print("音频链接：", audio_url)

# 下载并直接播放
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
    temp_path = temp_file.name

# 下载音频到临时文件
audio_data = requests.get(audio_url).content
with open(temp_path, "wb") as f:
    f.write(audio_data)

# 播放音频
print("正在播放音频...")
playsound(temp_path)

# 清理临时文件
os.unlink(temp_path)
print("播放完成！")