import json
import logging
import os
from duckduckgo_search import DDGS
from dotenv import load_dotenv

# 設定 Logging 的輸出格式與層級
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def collect_news(query="Boy Next Door BOYNEXTDOOR", max_results=15):
    """
    優先透過 Tavily.ai 搜集新聞，若無金鑰則回退至 DuckDuckGo API。
    為了增加命中率，包含英文縮寫及連著寫的變體。
    """
    logger.info(f"開始搜集「{query}」的最新新聞...")
    results = []
    
    load_dotenv()
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if tavily_api_key and tavily_api_key != "your_tavily_api_key_here":
        try:
            logger.info("偵測到 TAVILY_API_KEY，使用 Tavily.ai 進行新聞搜尋")
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(
                query=query,
                topic="news",
                days=2,
                max_results=max_results
            )
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("content", ""),
                    "url": item.get("url", ""),
                    "source": "Tavily News",
                    "date": item.get("published_date", "")[:10] if item.get("published_date") else ""
                })
            
            logger.info(f"成功透過 Tavily 搜集 {len(results)} 篇新聞。")
            if results:
                return results
        except Exception as e:
            logger.error(f"透過 Tavily 搜集新聞時發生錯誤: {e}，將改用 DuckDuckGo...")

    try:
        logger.info("使用 DuckDuckGo 進行新聞搜尋")
        with DDGS() as ddgs:
            # timelimit='d' 代表搜尋過去一天的資料
            # 使用 ddgs.news 搜尋新聞分頁
            news_generator = ddgs.news(
                keywords=query,
                region="wt-wt",
                safesearch="moderate",
                timelimit="d",
                max_results=max_results
            )
            
            for item in news_generator:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "url": item.get("url", ""),
                    "source": item.get("source", ""),
                    "date": item.get("date", "")
                })
        
        logger.info(f"成功搜集 {len(results)} 篇新聞。")
        return results
        
    except Exception as e:
        logger.error(f"搜集新聞時發生錯誤: {e}")
        return []

def save_to_file(data, filename="data/raw_data.json"):
    """將抓取的資料存成 JSON 檔案供後續分析使用"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"原始資料已儲存至 {filename}")

if __name__ == "__main__":
    # 測試執行：搜集資料並儲存
    news_data = collect_news()
    if news_data:
        print("\n=== 最新新聞範例 ===")
        print(json.dumps(news_data[0], ensure_ascii=False, indent=2))
        save_to_file(news_data)
