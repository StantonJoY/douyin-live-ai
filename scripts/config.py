"""
抖音直播弹幕AI回复助手 - 配置文件
请在此处填写你的直播间信息和API Key
"""
import os

# ==================== 直播间配置 ====================
# 乐享
# ROOM_ID = "444109467716"
# 测试
ROOM_ID = "836906580899"
# 是否启用AI语音播报功能
USE_TTS = False  # 设置为False可关闭语音功能
USE_API_REPLY = False

# ==================== 主播简介配置 ====================
# 主播名称
HOST_NAME = "乐享莓园"

HOST_INTRO = """
主播是带货主播，直播风格热情朴实，邀请观众来买蓝莓和露营
"""

# ====================  API 配置 ====================

DASHSCOPE_API_URL = 'https://dashscope.aliyuncs.com/api/v1'

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

# ==================== 过滤配置 ====================
# 忽略的用户名列表 (如机器人、管理员)
IGNORED_USERS = ["管理员", "系统消息", "nn."]

# 忽略的关键词 (如纯表情、无意义内容)
IGNORED_KEYWORDS = ["666", "哈哈哈", "...", "???", "点点关注"]

# 最小消息长度 (小于此长度将忽略)
MIN_MESSAGE_LENGTH = 2