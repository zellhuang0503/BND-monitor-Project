import json
import logging
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# 設定 Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_report(raw_data_file="data/raw_data.json", analyzed_data_file="data/analyzed_summary.json", output_dir="reports"):
    """
    載入抓取的資料與 LLM 分析結果，並透過 Jinja2 渲染 HTML
    """
    if not os.path.exists(raw_data_file) or not os.path.exists(analyzed_data_file):
        logger.error("找不到所需的資料檔 (raw_data 或是 analyzed_summary)，請確認已執行 collector 以及 analyzer！")
        return None

    with open(raw_data_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    with open(analyzed_data_file, 'r', encoding='utf-8') as f:
        analyzed_data = json.load(f)

    # 設定 Jinja2 環境
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    try:
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('template.html')
    except Exception as e:
        logger.error(f"載入 HTML 模板失敗: {e}")
        return None

    # 準備渲染變數
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    html_content = template.render(
        date=today_str,
        total_articles=analyzed_data.get("total_articles", 0),
        summary_markdown=analyzed_data.get("summary_markdown", "分析結果為空。"),
        raw_data=raw_data
    )

    # 確保 reports 目錄存在
    os.makedirs(output_dir, exist_ok=True)
    report_filename = os.path.join(output_dir, f"report_{today_str}.html")

    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"網頁報告生成成功，檔案儲存於：{report_filename}")
        return report_filename
    except Exception as e:
        logger.error(f"寫入 HTML 檔案失敗: {e}")
        return None

if __name__ == "__main__":
    generate_report()
