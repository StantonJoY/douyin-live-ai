import gzip
import logging
import re
import ssl
import traceback
import time
from collections import deque
import threading

import execjs
import requests
import websocket

from CoreUtils.Encrypt import md5_encrypt
from douyin.douyin_pb2 import PushFrame, Message, Response, ChatMessage, GiftMessage, LikeMessage, MemberMessage, \
    SocialMessage, RoomUserSeqMessage, FansclubMessage, EmojiChatMessage, RoomMessage, RoomStatsMessage, \
    RoomRankMessage, ControlMessage, RoomStreamAdaptationMessage

import logging

# ========== 日志配置 ==========
# 只显示用户聊天，隐藏其他日志
class ChatOnlyFilter(logging.Filter):
    def filter(self, record):
        # 只保留包含特定标记的日志
        msg = str(record.getMessage())
        return '[用户' in msg or '[欢迎' in msg or '[礼物' in msg or '[系统' in msg or '==' in msg

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # 简化格式，只显示消息内容
    handlers=[logging.StreamHandler()]
)

# 隐藏第三方库的日志
logging.getLogger('websocket').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)


class DouYinLive:
    def __init__(self, room_uid):
        self.headers = {
            "user-agent": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }
        self.cookies = {
            "__ac_nonce": "0683ab03200786e902e82"
        }
        self.url = f"https://live.douyin.com/{room_uid}"
        self.ws = None
        self.message_queue = deque()  # 消息队列
        self.is_running = False       # 控制运行状态
        self.last_heartbeat = time.time()  # 上次心跳时间
        
        # 消息处理线程
        self.processing_thread = None

    def start(self):
        room_id, ttwid = self.get_room_id()
        # 获取sign
        sign = self.get_sign(room_id)
        # 发起websocket请求
        self.send_websocket(room_id, sign, ttwid)

    def get_room_id(self):
        """获取room_id"""

        response = requests.get(self.url, headers=self.headers, cookies=self.cookies)

        data = response.text
        room_id = str(re.search(r'\\"roomId\\":\\"(\d+)\\"', data).group(1))
        ttwid = response.cookies.get('ttwid')

        return room_id, ttwid

    def get_s(self, room_id):
        """获取s值"""
        param = {
            "app_name": "douyin_web",
            "version_code": "180800",
            "webcast_sdk_version": "1.0.14-beta.0",
            "update_version_code": "1.0.14-beta.0",
            "compress": "gzip",
            "device_platform": "web",
            "cookie_enabled": 'true',
            "screen_width": 1920,
            "screen_height": 1080,
            "browser_language": "zh-CN",
            "browser_platform": "Win32",
            "browser_name": "Mozilla",
            "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "browser_online": 'true',
            "tz_name": "Asia/Shanghai",
            "cursor": "t-1748834041134_r-7511185012226569781_d-7511185012226523137_u-1_fh-7511184045972533541",
            "internal_ext": "internal_src:dim|wss_push_room_id:7511169016510040832|wss_push_did:7506916920386848296|first_req_ms:1748834041041|fetch_time:1748834041134|seq:1|wss_info:0-1748834041134-0-0|wrds_v:7511184999341623742",
            "host": "https://live.douyin.com",
            "aid": "6383",
            "live_id": 1,
            "did_rule": 3,
            "endpoint": "live_pc",
            "support_wrds": 1,
            "user_unique_id": "7506916920386848296",
            "im_path": "/webcast/im/fetch/",
            "identity": "audience",
            "need_persist_msg_count": "15",
            "insert_task_id": "",
            "live_reason": "",
            "room_id": room_id,
            "heartbeatDuration": "0"
        }
        # 顺序
        order = [
            {
                "param_name": "live_id",
                "param_type": "string"
            },
            {
                "param_name": "aid",
                "param_type": "string"
            },
            {
                "param_name": "version_code",
                "param_type": "string"
            },
            {
                "param_name": "webcast_sdk_version",
                "param_type": "string"
            },
            {
                "param_name": "room_id",
                "param_type": "string"
            },
            {
                "param_name": "sub_room_id",
                "param_type": "string"
            },
            {
                "param_name": "sub_channel_id",
                "param_type": "string"
            },
            {
                "param_name": "did_rule",
                "param_type": "string"
            },
            {
                "param_name": "user_unique_id",
                "param_type": "string"
            },
            {
                "param_name": "device_platform",
                "param_type": "string"
            },
            {
                "param_name": "device_type",
                "param_type": "string"
            },
            {
                "param_name": "ac",
                "param_type": "string"
            },
            {
                "param_name": "identity",
                "param_type": "string"
            }
        ]

        pre_s = ''

        for i in order:
            try:
                param_name = i['param_name']
                value = param[param_name]
                pre_s += ',' + str(param_name) + '=' + str(value)
            except:
                param_name = i['param_name']
                pre_s += ',' + str(param_name) + '=' + ''
        s = md5_encrypt(pre_s[1:])

        return s

    def get_sign(self, room_id):
        """获取sign值 - 通过 Node.js 子进程调用，规避 Windows GBK 编码问题"""
        import os
        import subprocess
        # 获取s值
        s = self.get_s(room_id)

        # 使用 Node.js 子进程执行 get_sign_wrapper.js，通过 stdin/stdout 传参
        wrapper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'get_sign_wrapper.js')
        result = subprocess.run(
            ['node', wrapper_path],
            input=s,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )
        sign = result.stdout.strip()
        return sign

    def send_websocket(self, room_id, sign, ttwid):
        """发起请求"""

        cookie = f"ttwid={ttwid}"
        # WebSocket 服务器地址
        ws_url = f"wss://webcast100-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.0.14-beta.0&update_version_code=1.0.14-beta.0&compress=gzip&device_platform=web&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/137.0.0.0%20Safari/537.36&browser_online=true&tz_name=Asia/Shanghai&cursor=u-1_fh-7511183563078362663_t-1748833761054_r-7511183809635723460_d-7511183805340712963&internal_ext=internal_src:dim|wss_push_room_id:7511169016510040832|wss_push_did:7506916920386848296|first_req_ms:1748833760959|fetch_time:1748833761054|seq:1|wss_info:0-1748833761054-0-0|wrds_v:7511183805340715817&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&endpoint=live_pc&support_wrds=1&user_unique_id=7506916920386848296&im_path=/webcast/im/fetch/&identity=audience&need_persist_msg_count=15&insert_task_id=&live_reason=&room_id={room_id}&heartbeatDuration=0&signature={sign}"
        # 创建 WebSocket 连接
        self.ws = websocket.WebSocketApp(ws_url, header=self.headers, cookie=cookie,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)

        # 启动主循环而不是run_forever
        self.is_running = True
        
        # 启动消息处理线程
        self.processing_thread = threading.Thread(target=self.process_messages)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # 使用一个线程来运行WebSocket，主循环在当前线程中
        ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={'sslopt':{'cert_reqs': ssl.CERT_NONE}})
        ws_thread.daemon = True
        ws_thread.start()
        
        # 启动主循环
        self.run_main_loop()

    def on_error(self, ws, error):
        pass  # 隐藏错误日志

    def on_close(self, ws, close_status_code, close_msg):
        self.is_running = False
        print("\n[系统] 连接已关闭")

    def on_open(self, ws):
        print("[系统] 连接成功，开始接收弹幕...\n")
        # 发送初始化消息（取决于实际网站的协议）

    def on_message(self, ws, message):
        # 第一层
        obj = PushFrame()
        obj.ParseFromString(message)

        # 直播数据，解压缩
        payload = obj.payload
        payload_bytes = gzip.decompress(payload)
        response = Response()
        response.ParseFromString(payload_bytes)
        # 返回ack

        if response.need_ack:
            ack = PushFrame(LogID=obj.LogID, payload=response.internal_ext.encode('utf-8'),
                            payload_type='ack').SerializeToString()
            ws.send(ack, websocket.ABNF.OPCODE_BINARY)

        # 将消息放入队列而不是立即处理
        for msg in response.messages:
            method = msg.method
            # 添加消息到队列，包含接收时间戳
            self.message_queue.append({
                'method': method,
                'payload': msg.payload,
                'timestamp': time.time()
            })

    def process_messages(self):
        """消息处理线程 - 专门处理消息队列中的消息"""
        while self.is_running:
            try:
                if self.message_queue:
                    # 取出队列头部的消息
                    msg_data = self.message_queue.popleft()
                    method = msg_data['method']
                    payload = msg_data['payload']
                    timestamp = msg_data['timestamp']
                    
                    # 检查消息是否超时（超过60秒）
                    if time.time() - timestamp > 60:
                        logging.info(f"跳过超时消息: {method}, 延迟: {time.time() - timestamp:.2f}s")
                        continue

                    handlers = {
                        # 普通文字聊天消息（观众发送的弹幕）
                        'WebcastChatMessage': self.parseChatMsg,
                        # 送礼物消息（包含礼物信息、赠送者、数量等）
                        'WebcastGiftMessage': self.parseGiftMsg,
                        #
                        # 直播间流配置适配信息（用于调节直播流质量等）
                        'WebcastRoomStreamAdaptationMessage': self.parseRoomStreamAdaptationMsg,
                    }

                    handler = handlers.get(method)
                    if handler:
                        try:
                            handler(payload)
                        except Exception as e:
                            logging.error(f"处理消息时出错 {method}: {str(e)}")
                else:
                    # 如果队列为空，短暂休眠
                    time.sleep(0.01)
            except Exception as e:
                logging.error(f"消息处理线程异常: {str(e)}")
                time.sleep(0.01)

    def maintain_heartbeat(self):
        """维护心跳连接"""
        # 每10秒检查一次
        if time.time() - self.last_heartbeat > 10:
            # 尝试发送心跳，如果ws连接可用
            try:
                if self.ws and self.ws.sock and self.ws.sock.connected:
                    self.ws.sock.ping()
            except Exception as e:
                logging.warning(f"心跳发送失败: {str(e)}")
            self.last_heartbeat = time.time()

    def run_main_loop(self):
        """主循环 - 仅维护心跳和监控连接状态"""
        while self.is_running:
            # 维护心跳
            self.maintain_heartbeat()
            
            # 短暂休眠，释放CPU资源
            time.sleep(0.01)

    def parseChatMsg(self, payload):
        """聊天消息 - 调用DeepSeek AI生成回复"""
        from deepseek_ai import generate_reply, generate_stub_reply, speak_reply
        from config import IGNORED_USERS, IGNORED_KEYWORDS, MIN_MESSAGE_LENGTH, REPLY_FILE, USE_API_REPLY
        import json
        from datetime import datetime

        message = ChatMessage()
        message.ParseFromString(payload)

        user_name = message.user.nickname
        content = message.content

        # 过滤无意义内容
        if len(content.strip()) < MIN_MESSAGE_LENGTH:
            return

        if content.strip().isdigit():
            return

        # 过滤忽略的用户
        if user_name in IGNORED_USERS:
            return

        # 过滤忽略的关键词
        for keyword in IGNORED_KEYWORDS:
            if keyword in content:
                return

        # 调用 DeepSeek AI 生成回复
        if USE_API_REPLY:
            result = generate_reply(user_name, content)
        else:
            result = generate_stub_reply(user_name, content)

        # 保存到回复记录
        if result['success']:
            reply_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_name': result['user_name'],
                'user_message': result['user_message'],
                'ai_reply': result['reply']
            }
            with open(REPLY_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(reply_data, ensure_ascii=False) + '\n')

            # 简洁输出
            cache_status = "[缓存]" if result.get('from_cache') else "[API]"
            print(f"\n{'='*60}")
            print(f"[{reply_data['timestamp']}] {cache_status} {user_name}: {content}")
            print(f"-"*60)
            print(f"AI回复: {result['reply']}")
            print(f"{'='*60}")
            
            # 使用TTS朗读AI回复
            speak_reply(result['reply'])

    def parseGiftMsg(self, payload):
        """礼物消息 - 忽略不显示"""
        pass
  
    def parseRoomStreamAdaptationMsg(self, payload):
        """直播间流配置 - 忽略不显示"""
        pass