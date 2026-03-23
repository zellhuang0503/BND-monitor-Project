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
    
    # 步驟 3.5: 即時同步至 GitHub 讓網頁生效
    if report_path:
        import os
        filename = os.path.basename(report_path)
        # 建立一個首頁 (index.html) 來自動跳轉到最新報告，解決 GitHub Pages 根目錄 404 的問題
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f'<html><head><meta http-equiv="refresh" content="0; url=reports/{filename}" /></head><body>Redirecting to latest report...</body></html>')
            
        logger.info("正在執行備份腳本以同步網頁報告至 GitHub Pages...")
        import subprocess
        # 報告與首頁剛產生，立即呼叫 backup.bat 同步上傳至 Github
        subprocess.run(["backup.bat"], shell=True)

    # 步驟 4: 推播通知
    if report_path:
        import os
        filename = os.path.basename(report_path)
        # 將原本的本機路徑 (file:///) 改為 GitHub Pages 的公開網址
        github_pages_url = f"https://zellhuang0503.github.io/BND-monitor-Project/reports/{filename}"
        push_notifications(report_url=github_pages_url)
    else:
        push_notifications(report_url=None)
    
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
