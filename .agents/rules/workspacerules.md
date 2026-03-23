---
trigger: always_on
---

# BND Monitor Project - Workspace Rules

## 專案核心目標 (Project Objective)
本專案旨在開發一個全自動化的 AI 輿情監測代理系統 (AI Agent)，專門監測並分析「Boy Next Door (BND)」相關的網路聲量與討論。

## 系統架構與自動化流程 (System Workflow)
在進行開發、除錯或新增功能時，請嚴格遵循以下五大核心模組的流程定義：

1. 📡 資訊搜集 (Data Collection)
   - 核心動作：透過搜尋引擎、爬蟲工具或 API (Search Tools) 自動抓取資料。
   - 資料來源：必須涵蓋各大社群平台、網路新聞中心以及公開社團/論壇訊息。

2. 🧠 AI 分析 (AI Analysis)
   - 核心動作：將擷取的原始文本送入大型語言模型 (LLM) 進行語意分析。
   - 分析指標：
     - 情緒分析 (Sentiment Analysis)：精準判斷內容為「正向」或「負向」。
     - 聲量波動 (Volume Fluctuation)：監測討論熱度變化，提前預警突發危機。

3. 📊 網頁報告 (Reporting Dashboard)
   - 核心動作：將 LLM 產生的分析結果數據化與視覺化。
   - 呈現方式：自動生成易於閱讀的網頁報告 (Web Dashboard)，供客戶隨時查閱。

4. 🔔 即時通知 (Alert & Notification)
   - 核心動作：於分析或報告生成完畢後，發出主動提醒。
   - 發送管道：串接並整合 Line 與 Telegram API，推播濃縮後的精華摘要或異常警報予團隊。

5. ⏱️ 定時排程 (Scheduled Execution)
   - 核心動作：系統自動化運行，減少人工干預。
   - 執行頻率：設定為「每日 (Daily)」定期觸發並完整執行上述 ① 至 ④ 步驟。

## 開發與回覆準則 (Development Guidelines)
- 在撰寫程式碼或設計架構時，請確保上述每個步驟皆為「模組化 (Modular)」，以便未來輕鬆抽換資料來源或更新 LLM 模型。
- 進行任何開發或測試前，須考量第三方 API 的速率限制 (Rate Limits) 及錯誤處理 (Error Handling)，確保自動化排程穩定不中斷。
- 所有回覆與文件說明，請一律使用繁體中文。
