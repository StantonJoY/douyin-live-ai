"""
抖音直播弹幕AI回复助手 - 配置文件
请在此处填写你的直播间信息和API Key
"""
import os

# ==================== 直播间配置 ====================
# 抖音直播间ID（URL最后的数字，如 https://live.douyin.com/349873582969）
ROOM_ID = "444109467716"



# ==================== 主播简介配置 ====================
# 主播名称
HOST_NAME = "乐享莓园"

HOST_INTRO = """
主播是带货主播，直播风格热情朴实，邀请观众来买蓝莓和露营
"""

# ====================  API 配置 ====================
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

LLM_API_URL = "https://aihubmix.com/v1"

# 使用的模型
LLM_MODEL = "gpt-4.1-free"

# ==================== 缓存配置 ====================
# 获取脚本所在目录，缓存文件保存在同目录下
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 弹幕缓存文件路径
CACHE_FILE = os.path.join(_BASE_DIR, "danmu_cache.jsonl")

# 回复记录文件路径
REPLY_FILE = os.path.join(_BASE_DIR, "ai_replies.jsonl")

# ==================== TTS 配置 ====================
# 是否启用AI语音播报功能
USE_TTS = True  # 设置为False可关闭语音功能


# TTS语音引擎 (可选: 'sapi5' for Windows, 'nsss' for Mac, 'espeak' for Linux)
TTS_ENGINE = 'sapi5'

# 语音速度 (-10 to 10, 默认0)
TTS_RATE = 2

# 语音音量 (0.0 to 1.0, 默认1.0)
TTS_VOLUME = 1.0

# 语音音色索引 (0开始，具体取决于系统可用音色，默认为None自动选择中文音色)
TTS_VOICE_INDEX = None

# ==================== 过滤配置 ====================
# 忽略的用户名列表 (如机器人、管理员)
IGNORED_USERS = ["管理员", "系统消息"]

# 忽略的关键词 (如纯表情、无意义内容)
IGNORED_KEYWORDS = ["666", "哈哈哈", "...", "???", "点点关注"]

# 最小消息长度 (小于此长度将忽略)
MIN_MESSAGE_LENGTH = 2