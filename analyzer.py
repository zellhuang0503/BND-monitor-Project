import json
import logging
import os
from dotenv import load_dotenv

# 設定 Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def analyze_news(input_filename="data/raw_data.json", output_filename="data/analyzed_summary.json"):
    """
    讀取原始新聞資料，送入 LLM 進行分析
    並統整出每日的摘要與情緒分析報告
    """
    if not os.path.exists(input_filename):
        logger.error(f"找不到檔案 {input_filename}，請先執行 collector.py。")
        return None

    with open(input_filename, 'r', encoding='utf-8') as f:
        news_data = json.load(f)

    if not news_data:
        logger.warning("搜集到的新聞資料為空，無法進行分析。")
        return None

    # 將新聞組合成送給 LLM 的文本
    articles_text = ""
    for idx, item in enumerate(news_data, 1):
        articles_text += f"[{idx}] 標題: {item.get('title')}\n"
        articles_text += f"    摘要: {item.get('snippet')}\n"
        articles_text += f"    來源: {item.get('source')} | 日期: {item.get('date')}\n\n"

    system_prompt = (
        "你是一個專業的行銷公關分析師。請根據提供的「Boy Next Door (BND)」相關網路新聞與社群發文的摘要片段，"
        "進行綜合分析。請分析：\n"
        "1. 整體情緒向性（正向、負向或中立）與討論熱度。\n"
        "2. 重大事件或主要討論話題摘要（列點說明）。\n"
        "3. 行銷公關建議（例如是否需要介入或有特定亮點可操作）。\n\n"
        "請務必以繁體中文回答，並且格式要求結構清晰、容易閱讀。"
    )

    logger.info("準備發送資料給 LLM 進行分析...")
    # 這裡依照用戶提供的環境變數自動決定要用哪一家的 API
    summary_result = ""
    
    try:
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"以下是今日收集到的資料：\n\n{articles_text}"}
                ]
            )
            summary_result = response.choices[0].message.content
        elif os.getenv("GEMINI_API_KEY"):
            from google import genai
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            prompt = f"{system_prompt}\n\n以下是今日收集到的資料：\n{articles_text}"
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            summary_result = response.text
        elif os.getenv("CLAUDE_API_KEY"):
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"以下是今日收集到的資料：\n\n{articles_text}"}
                ]
            )
            summary_result = response.content[0].text
        else:
            logger.error("未設定任何 LLM API Key，請檢查 .env 檔案。")
            # 建立一個測試用的假資料，以便於在沒有金鑰的情況下後續開發網頁與推播模組
            summary_result = "### ⚠️ 警告：未提供 API Key，這是一份測試用的假報告\n\n**1. 整體情緒向性**\n目前市場對於 Boy Next Door 的討論度呈現【正向】。粉絲對於新發布的資訊反應熱烈。\n\n**2. 主要討論話題**\n- 討論新MV預告片的視覺風格。\n- 關於成員造型的熱烈討論。\n\n**3. 行銷公關建議**\n- 建議多釋出幕後花絮以維持目前的熱度。\n- 未觀察到負面新聞，安全過關。"

        # 將分析結果儲存為 JSON
        analyzed_data = {
            "date": os.getenv("CURRENT_DATE", ""), # 這個可以讓外部傳入日期或由腳本自己抓當天日期
            "summary_markdown": summary_result,
            "total_articles": len(news_data)
        }
        
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"AI 分析完成，報告已儲存至 {output_filename}")
        return analyzed_data

    except Exception as e:
        logger.error(f"呼叫 LLM 分析時發生錯誤: {e}")
        return None

if __name__ == "__main__":
    result = analyze_news()
    if result:
        print("\n=== AI 分析報告預覽 ===")
        print(result["summary_markdown"])
