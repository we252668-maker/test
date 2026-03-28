# ForgeDesk

PyQt 打造的工程工作台，將 **提醒排程、技術筆記、程式片段管理、關鍵字搜尋與 Discord 通知** 整合在同一個桌面應用程式中。  
專案定位不是單一用途的小工具，而是面向開發者日常工作的本機效率平台，適合整理任務、沉澱知識並集中管理常用程式碼資產。

---

## 專案簡介

**ForgeDesk** 是一套以桌面端為核心的開發工作輔助工具，使用 **PyQt** 建構互動介面，並以 **SQLite** 作為本機資料儲存層。  
它聚焦在工程實務中最常見的幾個資訊管理場景：

- 追蹤具時程性的提醒事項
- 整理技術筆記與工作紀錄
- 保存可重用的程式片段
- 透過關鍵字快速檢索內容
- 在重要提醒建立或到期時推送 Discord 通知

整體設計採取模組化分層，讓 UI、流程控制、資料存取與通知整合彼此分離，便於後續維護與擴充。

---

## 功能特色

- 📅 **排程提醒系統**
  - 建立、編輯、刪除提醒事項
  - 支援日期、時間、分類、優先度與備註
  - 背景輪詢到期提醒，處理通知發送流程

- 📝 **技術筆記管理**
  - 建立與維護技術筆記
  - 適合整理故障排查、設計想法與工作紀錄

- 💻 **Code Snippet 保存**
  - 保存常用程式碼片段
  - 便於重複使用與內部知識累積

- 🔎 **關鍵字搜尋**
  - 以統一介面快速查找提醒、筆記與內容資料
  - 提升本機知識檢索效率

- 🔔 **Discord 通知**
  - 支援 Discord Webhook 設定
  - 可用於提醒建立通知與到期通知

---

## 技術架構

- **PyQt6**：桌面 UI 與互動流程
- **SQLite**：本機資料儲存
- **requests**：HTTP 請求，用於 Discord Webhook 發送
- **Discord Webhook**：提醒通知整合
- **Python 3**：主要開發語言

---

## 系統架構說明

專案目前採用典型的桌面應用分層架構：

- **views**
  - 負責畫面元件、表單輸入與畫面布局
- **controllers**
  - 負責事件綁定、互動流程與 UI 協調
- **services**
  - 負責提醒邏輯、通知整合、資料操作與查詢服務
- **models**
  - 定義資料模型與應用內部資料結構
- **database**
  - 負責 SQLite 初始化與連線管理
- **utils**
  - 放置共用工具與設定

這種拆分方式讓通知邏輯不會直接耦合在 UI 層，也讓未來新增整合或替換模組時更容易控制影響範圍。

---

## 安裝與執行方式

### 1. 取得專案

```bash
git clone <your-repository-url>
cd Engineer-Hub
```

### 2. 建立虛擬環境

```bash
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

### 3. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 4. 啟動應用程式

```bash
python main.py
```

---

## 設定說明

### Discord Webhook 設定

若要啟用 Discord 通知，請先準備一組有效的 Discord Webhook URL。

設定步驟：

1. 啟動應用程式
2. 開啟上方選單中的「**通知設定**」
3. 在「**Discord 通知設定**」區塊輸入 Webhook URL
4. 點擊「**連接 Discord**」
5. 成功時會顯示 `Discord 連接成功`

若連接失敗，請優先檢查：

- Webhook URL 是否完整
- Discord 頻道中的 Webhook 是否仍有效
- 本機網路是否能正常對外連線

> 合理假設：目前通知功能以 Discord 為主要外部通知通道，且不包含其他第三方通知服務。

---

## 使用方式

### 提醒事項

1. 進入提醒頁面
2. 點擊「新增提醒」
3. 輸入標題、日期、時間、分類、優先度與備註
4. 儲存後，提醒資料會寫入本機 SQLite
5. 若已設定 Discord，系統可在提醒建立與到期時發送通知

### 技術筆記

1. 切換到筆記頁面
2. 建立或編輯筆記內容
3. 將工作知識、操作紀錄或技術整理保存在本機

### Code Snippet

1. 進入程式片段頁面
2. 建立常用 snippet
3. 作為日後重用與查找的程式碼資產

### 搜尋

1. 開啟搜尋頁面
2. 輸入關鍵字
3. 依搜尋結果快速定位需要的內容

---

## 專案結構

```text
Engineer Hub/
├─ controllers/      # 畫面流程控制與事件處理
├─ database/         # SQLite 初始化與資料庫連線
├─ data/             # 本機資料檔案
├─ models/           # 資料模型
├─ services/         # 核心業務邏輯與 Discord 通知服務
├─ utils/            # 共用設定與工具函式
├─ views/            # PyQt 畫面元件
├─ main.py           # 應用程式入口
└─ requirements.txt  # Python 相依套件
```

---

## 未來規劃

- [ ] 提升提醒通知的可靠性與例外處理
- [ ] 改善搜尋結果呈現與篩選能力
- [ ] 為筆記與 snippet 增加更完整的分類/標籤管理
- [ ] 強化資料匯出與備份能力
- [ ] 提供更完整的桌面打包與發佈流程
- [ ] 增加測試覆蓋率與開發者文件

> Roadmap 為合理規劃建議，並不代表目前版本已全部實作。

---

## 授權

建議採用 **MIT License**。  
若你準備將此專案公開於 GitHub，MIT 是相對成熟且常見的選擇，易於展示與再利用。

---

## 作者資訊

**Author**：Your Name  
**Project Type**：Desktop Productivity Tool / Developer Workspace  
**Stack**：Python, PyQt6, SQLite, requests, Discord Webhook

若用於公開展示，建議補上：

- GitHub 個人頁面
- Email
- LinkedIn 或作品集連結

---

## 備註

本 README 內容依目前專案可見結構與功能撰寫，未描述未實作或無法確認的功能。  
若未來調整提醒通知策略、資料模型或 UI 流程，建議同步更新文件內容，確保 README 與實際版本一致。
