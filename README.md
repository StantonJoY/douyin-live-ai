# 抖音直播弹幕 AI 智能回复助手

## 🖥️ 效果预览

```
============================================================
[2026-03-19 20:30:15] [API] 暴躁的嘉文四世: W什么技能
------------------------------------------------------------
DeepSeek AI回复: @暴躁的嘉文四世 朋友，W是黄金圣盾！
开盾减速还能加护甲，对线换血的神技，物理打手必出！
============================================================

============================================================
[2026-03-19 20:31:02] [缓存] 嘦姕: 龙女改版了？
------------------------------------------------------------
DeepSeek AI回复: @嘦姕 朋友好眼力！龙女确实改版了，
新 W 加了额外移速，清野效率更高，晚点给大家演示一波！
============================================================
```

> `[API]` 表示实时调用生成，`[缓存]` 表示命中本地缓存

## 🚀 快速开始
**配置参数**

编辑 `scripts/config.py`：

```python
# 直播间 ID（URL 最后的数字）
ROOM_ID = "349873582969"

# 直播类型：ecommerce / education / entertainment
LIVE_TYPE = "entertainment"

# 主播信息
HOST_NAME = "英雄联盟游戏主播"
HOST_INTRO = """
主播是英雄联盟游戏主播，专注于LOL游戏直播。
擅长各种英雄操作，经常分享游戏技巧、出装思路、对线细节。
"""

# DeepSeek API Key（https://platform.deepseek.com 获取）
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
```

> 也可通过环境变量注入：`set DEEPSEEK_API_KEY=sk-xxxx`（推荐，更安全）

**启动程序**

```bash
# 或手动启动基础版
python main.py

# 推荐：自动重连版（网络断开自动恢复）
python main_with_reconnect.py
```

---

## ⚙️ 配置说明

`scripts/config.py` 完整配置项：

```python
# ==================== 直播间配置 ====================
ROOM_ID = "349873582969"          # 直播间ID，取自 URL 末尾数字
LIVE_TYPE = "entertainment"        # 直播类型

# ==================== 主播人设配置 ====================
HOST_NAME = "主播名称"
HOST_INTRO = """主播详细介绍..."""
HOST_PERSONA = "幽默风趣的游戏玩家"
REPLY_STYLE = "humorous"           # humorous / professional / friendly

# ==================== DeepSeek API ====================
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
DEEPSEEK_MODEL = "deepseek-chat"
TEMPERATURE = 0.7                  # 0=严谨，1=均衡，2=创意
MAX_TOKENS = 500

# ==================== 过滤配置 ====================
IGNORED_USERS = ["管理员", "系统消息"]
IGNORED_KEYWORDS = ["666", "哈哈哈"]
MIN_MESSAGE_LENGTH = 2
```

### 直播类型说明

| `LIVE_TYPE` 值 | 适用场景 | AI 话术风格 |
|---------------|---------|-----------|
| `ecommerce` | 电商带货 | 引导下单、强调优惠、处理异议 |
| `education` | 知识教育 | 专业解答、耐心指导、鼓励学习 |
| `entertainment` | 游戏娱乐 | 轻松幽默、积极互动、活跃氛围 |

---

## 📁 项目结构

```
douyin-live-ai/
└── scripts/
    ├── main.py                  # 程序入口（基础版）
    ├── main_with_reconnect.py   # 程序入口（自动重连版）
    ├── douyinlive.py            # WebSocket 连接与弹幕解析
    ├── deepseek_ai.py           # DeepSeek AI 集成
    ├── reply_cache.py           # LRU 缓存管理
    ├── config.py                # 全局配置
    ├── sign.js                  # 抖音签名生成
    ├── get_sign_wrapper.js      # Node.js 包装器
    ├── CoreUtils/               # 加密工具
    │   └── Encrypt.py
    └── douyin/                  # Protobuf 协议定义
        ├── douyin.proto
        └── douyin_pb2.py
```

**运行后生成的数据文件：**

| 文件 | 说明 |
|------|------|
| `ai_replies.jsonl` | 所有 AI 回复记录（含时间戳、用户名、弹幕、回复） |
| `danmu_cache.jsonl` | 弹幕缓存持久化文件 |

## 📦 依赖列表

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | 3.7+ | 运行环境 |
| Node.js | 任意版本 | 执行签名生成脚本 |
| websocket-client | - | WebSocket 连接 |
| requests | - | HTTP 请求 |
| PyExecJS | - | 调用 JS 签名脚本 |
| protobuf | - | 解析抖音 Protobuf 消息 |
