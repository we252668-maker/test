# Engineer Hub

Engineer Hub 是一套以 **Python + PyQt6** 打造的桌面任務管理與通知系統，專為需要管理待辦、排程提醒與外部通知整合的使用情境而設計。專案支援 **本地桌面執行** 與 **Render 雲端部署**，可用於個人生產力工具、內部團隊提醒系統，或延伸為商業化 SaaS / 工具型產品的基礎版本。

本專案聚焦在一個清楚且具實務價值的核心流程：

- 建立任務
- 設定提醒時間
- 自動觸發通知
- 透過 Discord Webhook 即時推送訊息
- 同時支援 GUI 與雲端 API 版本

如果你正在尋找一個適合展示桌面應用開發能力、通知系統整合能力、以及可部署架構思維的作品，Engineer Hub 是一個兼具作品集價值與商業延伸潛力的專案。

---

## 專案介紹

Engineer Hub 的核心目標，是將「任務建立」、「時間排程」、「通知發送」整合在同一套應用中，讓使用者不需要依賴複雜的外部平台，也能快速建立一個可運作的提醒與通知工作流。

相較於單純的待辦工具，Engineer Hub 更強調：

- 明確的提醒流程
- 可視化桌面操作介面
- Discord 通知整合
- 本地與雲端雙版本架構
- 可持續擴充為多使用者、團隊型產品

這使它不僅適合作為個人開發作品，也適合用來展示工程師在以下面向的能力：

- Desktop App 開發
- GUI / 使用者互動設計
- 排程與通知機制設計
- 本地資料儲存與服務拆分
- 雲端部署與產品化思維

---

## Demo

> 以下區塊可直接替換成你的實際截圖、操作錄影或部署連結。

### 桌面版畫面

![Engineer Hub Desktop Demo](./docs/demo-desktop.png)

### 任務建立流程

![Engineer Hub Create Task Demo](./docs/demo-create-task.png)

### Discord 通知示意

![Engineer Hub Discord Demo](./docs/demo-discord.png)

### 雲端 API / Render 部署示意

![Engineer Hub Cloud Demo](./docs/demo-cloud.png)

---

## 功能

### 核心功能

- 建立任務與提醒事項
- 設定提醒時間與狀態
- 到期後自動發送 Discord 通知
- 建立成功後可立即發送建立通知
- 使用 GUI 介面進行操作
- 支援本地桌面版與雲端 API 版本

### 使用者價值

- 降低手動追蹤任務的成本
- 讓提醒流程更即時、更可視化
- 適合個人工作站、工程團隊、專案管理輔助場景
- 可作為內部工具產品雛形，快速延伸到企業應用

### 商業化潛力

- 可延伸為團隊任務管理工具
- 可增加多通知通道，例如 Email、LINE、Slack
- 可擴充權限、帳號系統與工作區概念
- 可演進為 B2B 內部流程自動化產品

---

## 技術架構

Engineer Hub 採用以 Python 為核心的桌面應用架構，結合本地資料儲存、通知服務與雲端部署能力。

### 技術棧

- Python 3.9
- PyQt6
- requests
- python-dotenv
- Discord Webhook
- SQLite
- Render

### 架構說明

```text
使用者操作 GUI
    ↓
PyQt 視圖層（views）
    ↓
Controller 控制流程（controllers）
    ↓
Service 業務邏輯（services）
    ↓
SQLite / Discord Webhook / Render API
```

### 模組分層

- `views/`
  負責桌面 UI 顯示與互動元件
- `controllers/`
  負責事件處理、畫面流程與使用者操作協調
- `services/`
  負責任務邏輯、通知發送、API 呼叫與排程處理
- `models/`
  負責資料模型與欄位結構
- `database/`
  負責 SQLite 初始化與連線管理
- `render_app.py`
  提供雲端部署用的 API 與排程入口
- `main.py`
  桌面應用程式進入點

### 設計亮點

- 桌面端與雲端端具備可分離的執行模式
- 通知功能可重用既有 Discord service
- 採用清楚的 controller / service 分層，易於維護與擴充
- 適合後續接入更多通知通道與商業需求

---

## 安裝方式

### 1. 取得專案

```bash
git clone https://github.com/your-username/engineer-hub.git
cd engineer-hub
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

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 設定環境變數

可參考 `.env.example` 建立 `.env` 檔案。

常用設定如下：

```env
DISCORD_WEBHOOK_URL=your_discord_webhook_url
REMINDER_POLL_INTERVAL_SECONDS=10
LOG_LEVEL=INFO
PORT=10000
```

### 5. 啟動桌面版

```bash
python main.py
```

### 6. 啟動雲端 API 版

```bash
python render_app.py
```

---

## 使用教學

### 桌面版使用流程

1. 啟動應用程式。
2. 進入任務 / 提醒管理介面。
3. 建立一筆新的任務。
4. 填入標題、分類、描述、提醒時間與狀態。
5. 儲存後，系統會將資料寫入本地資料庫。
6. 若已設定 Discord Webhook，系統可立即發送建立成功通知。
7. 到達提醒時間後，系統依原本排程邏輯發送正式提醒訊息。

### Discord Webhook 設定

1. 先到 Discord 頻道建立 Webhook。
2. 複製 Webhook URL。
3. 將 URL 填入設定頁或 `.env`。
4. 儲存後即可啟用通知功能。

### 適合展示的使用情境

- 個人工作排程與提醒
- 開發任務追蹤
- 團隊內部提醒機制
- 專案截止時間通知
- 內部工具 MVP 展示

---

## 部署教學（Render）

Engineer Hub 支援部署到 Render，讓提醒 API 與排程功能可在雲端持續運作。

### 1. 建立 GitHub Repository

將專案推送到你的 GitHub 倉庫。

### 2. 登入 Render

前往 [https://render.com](https://render.com) 並建立新的 Web Service。

### 3. 連接 GitHub 專案

選擇你的 `Engineer Hub` Repository。

### 4. 設定部署參數

可參考專案中的 `render.yaml`，或手動設定：

- Runtime: Python
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
python render_app.py
```

### 5. 設定環境變數

在 Render 後台加入：

```env
DISCORD_WEBHOOK_URL=your_discord_webhook_url
REMINDER_POLL_INTERVAL_SECONDS=10
LOG_LEVEL=INFO
PORT=10000
```

### 6. 部署完成後驗證

部署完成後可測試以下端點：

- `/health`
- `/test-discord`
- `/api/reminders`

### Render 部署價值

- 讓排程提醒可在雲端持續執行
- 適合作為桌面版之外的遠端提醒服務
- 可展示從本地應用延伸到雲端服務的完整能力

---

## 專案結構

```text
Engineer Hub/
├─ controllers/         # 控制器層，負責 GUI 事件與流程協調
├─ data/                # SQLite 資料檔
├─ database/            # 資料庫初始化與連線管理
├─ models/              # 資料模型
├─ services/            # 業務邏輯、通知、API、排程服務
├─ utils/               # 共用工具與設定
├─ views/               # PyQt GUI 畫面
├─ .env.example         # 環境變數範例
├─ main.py              # 桌面版入口
├─ render_app.py        # Render / 雲端 API 入口
├─ render.yaml          # Render 部署設定
├─ requirements.txt     # Python 依賴
└─ README.md            # 專案說明文件
```

---

## 未來功能

- 使用者登入與權限系統
- 多使用者 / 多工作區支援
- Slack / Email / LINE 等更多通知通道
- 任務標籤、篩選、優先級視覺化
- 任務統計儀表板
- 匯出報表與歷史紀錄查詢
- 任務附件與檔案管理
- 雲端同步與跨裝置使用
- REST API 文件化與 SDK 支援
- SaaS 化與訂閱制版本擴充

---

## 商業應用方向

Engineer Hub 可作為以下類型產品的原型或基礎版本：

- 團隊任務提醒平台
- 工程管理內部工具
- 專案排程通知系統
- Discord 整合型工作通知工具
- 輕量型企業流程自動化平台

對作品集來說，這個專案能夠呈現：

- 從桌面應用到雲端部署的完整開發能力
- 實用型通知系統設計能力
- 商業產品雛形的架構規劃能力
- 對可維護性與擴充性的工程思維

---


## License

本專案可依需求使用 MIT License。

如果你要將它作為作品集展示，建議保留：

- 清楚的專案定位
- Demo 截圖
- 部署連結
- 技術亮點
- 未來商業化擴充方向

這樣能讓招聘方、客戶或合作夥伴更快理解這個專案的價值。
