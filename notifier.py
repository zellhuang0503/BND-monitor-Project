import requests
import os
import logging
import json
from dotenv import load_dotenv

# 設定 Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

def get_summary_text(json_file="data/analyzed_summary.json"):
    """讀取分析結果作為推播摘要內容"""
    if not os.path.exists(json_file):
        return "⚠️ 今日無 BND 輿情分析報告或尚未產生。"
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("summary_markdown", "今日無分析內容。")

def send_line_message(message):
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    if not token or token == "your_line_channel_access_token_here" or not user_id or user_id == "your_line_user_id_here":
        logger.warning("未設定 LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID，略過 Line 發送。")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info("Line 訊息推播成功!")
            return True
        else:
            logger.error(f"Line 推播失敗! 狀態碼: {response.status_code}, 內容: {response.text}")
            return False
    except Exception as e:
        logger.error(f"發送 Line 訊息時發生例外狀況: {e}")
        return False

def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or bot_token == "your_telegram_bot_token_here" or not chat_id or chat_id == "your_telegram_chat_id_here":
        logger.warning("未設定 Telegram Token/Chat ID，略過 Telegram 發送。")
        return False

    # Telegram API 規定字串長度與 Markdown 符號解析較為嚴格，若直接發送長文本可考慮不使用 parse_mode
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("Telegram 發送成功!")
            return True
        else:
            logger.error(f"Telegram 發送失敗! 狀態碼: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"發送 Telegram 時發生例外狀況: {e}")
        return False

def push_notifications(report_url=None):
    """
    發送今日的大綱。如果在本機運行，可以附上報告路徑，
    或者是假設有放在靜態伺服器的 URL。
    """
    summary = get_summary_text()
    
    push_message = "🔔 【Boy Next Door (BND) 每日輿情監測】\n"
    push_message += "---------------------------\n"
    # 擷取摘要的一部分避免 Line/Telegram 訊息過長
    short_summary = summary[:500] + ("..." if len(summary) > 500 else "")
    push_message += short_summary
    
    if report_url:
        push_message += f"\n\n📂 詳細報告請見：{report_url}"
    else:
        push_message += "\n\n📂 詳細報告已生成於本機資料夾。"
        
    logger.info("開始推播至通訊軟體...")
    send_line_message(push_message)
    send_telegram_message(push_message)

if __name__ == "__main__":
    push_notifications()
