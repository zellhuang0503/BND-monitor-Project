import logging
import os
import schedule
import time
from datetime import datetime

from collector import collect_news, save_to_file
from analyzer import analyze_news
from reporter import generate_report
from notifier import push_notifications

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    """執行完整監測流程的函式"""
    logger.info("=== BND 輿情監測系統：開始執行今日任務 ===")
    
    # 步驟 1: 搜集資料
    news_data = collect_news()
    if news_data:
        save_to_file(news_data, "data/raw_data.json")
    else:
        logger.warning("搜集新聞失敗或無新資料，今日任務終止。")
        return

    # 步驟 2: AI 分析
    analyzed_data = analyze_news(input_filename="data/raw_data.json", output_filename="data/analyzed_summary.json")
    if not analyzed_data:
        logger.warning("AI 分析失敗，今日任務終止。")
        return

    # 步驟 3: 產生網頁報告
    report_path = generate_report("data/raw_data.json", "data/analyzed_summary.json", "reports")
    
    # 步驟 4: 推播通知
    # 依賴本機環境，我們將傳遞檔案的絕對/相對路徑
    abs_report_path = os.path.abspath(report_path) if report_path else None
    push_notifications(report_url=f"file:///{abs_report_path.replace(chr(92), '/')}" if abs_report_path else None)
    
    logger.info("=== BND 輿情監測系統：今日任務執行完畢 ===")

if __name__ == "__main__":
    import sys
    # 若給定執行參數 `run_now`，則直接執行一次 (供 Task Scheduler 調用)
    if len(sys.argv) > 1 and sys.argv[1] == "run_now":
        job()
    else:
        # 開發環境下可使用 Python 的 schedule 啟動長駐程式
        logger.info("啟動排程守護進程，預計每天上午 08:45 執行一次。")
        # 設定每天 08:45 執行，確保 09:00 前收到
        schedule.every().day.at("08:45").do(job)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
