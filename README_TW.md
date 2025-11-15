# MBBuddy (My Brainstorming Buddy)

###### Click here to enter the English version: [`README.md`](README.md)
## 📱 應用程式說明

**MBBuddy** 是一款專為「內部討論協作」打造的本地私有化 AI 互動平台，整合了匿名意見收集、即時投票、AI 智能助理及自動統整等功能，提供全新的討論互動體驗。

### 核心特色：

- **匿名意見表達**：參與者可匿名提交意見，降低發言心理門檻
- **即時投票機制**：對提出的意見快速進行正負面投票，突顯共識與分歧
- **本地 AI 助理**：提供即時討論資訊統整與摘要，無需雲端連接
- **跨裝置支援**：主持人可在電腦管理討論，參與者用手機掃碼即可加入
- **PDF 報告匯出**：一鍵產生包含圖表分析的完整討論記錄

### 技術亮點：

- **隱私安全**：全程本地推理，無雲端資料傳輸，保障討論資訊安全
- **NPU 加速**：支援高通 Snapdragon X 系列裝置 NPU 加速，提升 AI 處理效能
- **輕量部署**：前後端分離架構，可輕鬆部署於各種環境
- **互動體驗**：即時更新的投票機制與討論計時器，增強討論參與感

## 👥 參賽團隊成員

| 姓名 | 電子郵件 |
| --- | --- |
| 趙祖威 | t110ab0012@ntut.org.tw |
| 賴聖元 | 11046015@ntub.edu.tw |
| 吳承諺 | t111ab0011@ntut.org.tw |
| 陳以珊 | t112ab0025@ntut.org.tw |
| 林佑亦 | t112ab0004@ntut.org.tw |

## 📦 安裝與使用指引

### 1. 下載專案

```bash
git clone https://github.com/UIE47061/MBBuddy.git
cd MBBuddy
```

### 2. 安裝方式（一鍵安裝）

執行一鍵安裝腳本，自動完成 Docker 安裝、AnythingLLM 設置及服務部署：

```batch
# 雙擊執行或在命令提示字元中執行
scripts\0_one_click_install_TW.bat
```

**安裝步驟包含**：
- 自動檢查並安裝 Docker Desktop
- 引導下載和設置 AnythingLLM
- 獲取 API 金鑰並配置環境變數
- 一鍵部署 MBBuddy 正式環境
- 完成後顯示訪問地址和控制指令


### 3. 查詢您的 IP 地址（區域網路訪問）

```bash
# Windows (命令提示字元)
ipconfig | findstr "IPv4"

# 會顯示類似：	
#      IPv4 地址 . . . . . . . . . . . . : 192.168.0.114                (Windows)
# 則 192.168.0.114 就會是您的IP位址！
```

**訪問地址**：
- 前端：`http://[您的IP地址]`
- 後端：`http://[您的IP地址]:8000`

### 停止開發服務

```bash
# Windows - 停止開發服務
scripts\stop_dev.bat
```

## 📱 使用流程

1. **建立討論室**：
   - 在首頁輸入討論主題
   - 點擊「建立討論室」按鈕
   - 填寫討論設定（名稱、議題、時間等）

2. **邀請參與者**：
   - 使用生成的 QR Code 或連結邀請參與者
   - 參與者掃描 QR Code 即可加入

3. **開始討論**：
   - 主持人可發起、暫停或結束討論
   - 設定倒數計時器
   - 隨時切換討論主題

4. **互動參與**：
   - 參與者提交意見/問題
   - 為他人意見投票（贊成/反對）
   - 查看即時排序的意見列表

5. **AI 輔助**：
   - 點擊「AI 統整」獲取當前討論摘要
   - AI 可自動產生議程主題建議

6. **匯出結果**：
   - 討論結束後點擊「匯出 PDF」
   - 獲取完整討論記錄，含意見、投票統計與圖表分析

## ⚡ Snapdragon X 系列裝置 NPU 加速

若使用 Snapdragon X 系列筆電，可啟用 NPU 加速：

1. 確認已安裝最新 Windows 11 與 NPU 驅動程式
2. 修改 `ai_api.py` 中的模型載入參數：
   ```python
   llm = Llama(
       model_path=MODEL_PATH, 
       n_ctx=2048,
       n_gpu_layers=0,  # 不使用 GPU
       n_threads=8,     # CPU 線程數
       n_npu_layers=20  # 啟用 NPU 加速
   )
   ```

## 📂 目錄結構
```
MBBuddy/
├── 📁 backend/                      # FastAPI 後端服務
│   ├── main.py                      # 後端主入口點
│   ├── requirements.txt             # Python 依賴套件
│   └── api/                         # API 模組
│       ├── __init__.py              # 套件初始化
│       ├── ai_api.py                # AI 相關 API（模型推理、摘要）
│       ├── ai_client.py             # AI 客戶端
│       ├── ai_config.py             # AI 配置設定
│       ├── ai_prompts.py            # AI 提示詞模板
│       ├── hostStyle_api.py         # 主持人風格 API
│       ├── local_llm_client.py      # 本地 LLM 客戶端
│       ├── mindmap_api.py           # 心智圖 API
│       ├── network_api.py           # 網路相關 API
│       ├── participants_api.py      # 討論參與 API（用戶管理、投票）
│       ├── pdf_generate.py          # PDF 生成
│       ├── snapdragon_config.py     # Snapdragon NPU 配置
│       └── transparent_fusion.py    # 透明融合功能
│
├── 🎨 frontend/                     # 前端應用
│   ├── index.html               # 主 HTML 模板
│   ├── package.json             # 前端依賴配置
│   ├── vite.config.js           # Vite 建置配置
│   ├── public/                  # 靜態資源
│   │   └── AIresult.txt         # AI 結果範例
│   └── src/                     # 源碼目錄
│       ├── App.vue              # 根組件
│       ├── main.js              # 應用入口點
│       ├── assets/              # 樣式資源
│       │   ├── base.css         # 基礎樣式
│       │   ├── main.css         # 主要樣式
│       │   └── styles.css       # 自定義樣式
│       ├── components/          # Vue 組件
│       │   ├── ControlPanel.vue       # 控制面板
│       │   ├── CreateRoomModal.vue    # 建立討論室彈窗
│       │   ├── Home.vue               # 首頁組件
│       │   ├── HostPanel.vue          # 主持人面板
│       │   ├── JoinRoomModal.vue      # 加入討論室彈窗
│       │   ├── MindMapModal.vue       # 心智圖彈窗
│       │   ├── NicknameModals.vue     # 暱稱設定彈窗
│       │   ├── NotificationToast.vue  # 通知訊息
│       │   ├── ParticipantPanel.vue   # 參與者面板
│       │   ├── QRCodeModal.vue        # QR Code 彈窗
│       │   ├── QuestionsList.vue      # 問題列表
│       │   ├── ScoreJudgePanel.vue    # 評分面板
│       │   ├── TimerModal.vue         # 計時器彈窗
│       │   ├── TopicEditModal.vue     # 主題編輯彈窗
│       │   └── TopicsSidebar.vue      # 主題側邊欄
│       ├── composables/         # Vue Composition API
│       │   └── useRoom.js       # 討論室邏輯
│       ├── router/              # 路由配置
│       │   └── index.js         # 路由定義
│       └── utils/               # 工具函數
│           └── api.js           # API 請求封裝
│
├── 🐳 docker/                       # Docker 部署配置
│   ├── README.md                    # Docker 使用說明
│   ├── docker-compose.yml          # 生產環境配置
│   ├── docker-compose.dev.yml      # 開發環境配置
│   ├── Dockerfile.backend          # 後端容器配置
│   ├── Dockerfile.frontend         # 前端生產容器配置
│   ├── Dockerfile.frontend.dev     # 前端開發容器配置
│   └── nginx.conf                  # Nginx 配置
│
├── 📥 scripts/                      # 自動化腳本目錄
│   ├── 0_one_click_install_TW.bat   # 一鍵安裝腳本（中文）
│   ├── 0_one_click_install_US.bat   # 一鍵安裝腳本（英文）
│
└── 📄 文檔
    ├── README.md                   # 專案說明文檔（本檔案）
    └── LICENSE                     # MIT 授權條款
```

### 📋 關鍵檔案說明

| 檔案/目錄 | 功能說明 |
|-----------|---------|
| `backend/api/ai_api.py` | 核心 AI 功能，包括文本生成和討論摘要 |
| `backend/api/ai_client.py` | AI 客戶端，處理 AI 模型的載入和推理 |
| `backend/api/participants_api.py` | 討論參與邏輯，用戶管理和投票系統 |
| `backend/api/mindmap_api.py` | 心智圖功能，AI 自動生成討論脈絡 |
| `backend/api/transparent_fusion.py` | 透明融合技術，整合多種 AI 服務 |
| `backend/api/snapdragon_config.py` | Snapdragon NPU 加速配置 |
| `frontend/src/components/` | Vue 組件，實現各種 UI 功能 |
| `frontend/src/composables/useRoom.js` | 討論室狀態管理和 WebSocket 通訊 |
| `docker/` | 容器化部署配置，支援開發和生產環境 |
| `scripts/` | 自動化腳本目錄，包含安裝、部署和開發環境管理 |
| `scripts/0_one_click_install_TW.bat` | Windows 一鍵安裝腳本，自動化完整安裝流程 |

## 🛡️ 隱私保障

本系統全程本地推理、無雲端資料傳輸，任何討論訊息、AI 討論、決策過程**均不會外洩**。特別適合需要高隱私、高安全的組織與團隊使用。

## 常見問題排除：

1. **首次啟動**：初次下載和構建可能需要較長時間，特別是 AI 模型檔案較大
2. **記憶體需求**：確保 Docker 有足夠記憶體來載入 AI 模型（建議 8GB+）
3. **端口衝突**：確保端口 80、5173、8000、8001 沒有被其他服務占用
4. **IP 變化**：前端會自動偵測並連接到正確的後端端口，無需手動配置

### 無法從其他設備訪問時
1. 確保所有設備連接到相同的 WiFi 網路
2. 檢查「防火牆」設定
3. 確認 IP 地址是否正確

## 📄 授權資訊

本專案採用 [MIT License](https://choosealicense.com/licenses/mit/) 授權，可自由使用、修改、散布本程式碼，但請保留原始授權聲明。