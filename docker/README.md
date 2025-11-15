# MBBuddy Docker 使用指南

## 🚀 快速開始

### 開發環境
* 開發環境支援熱重載，修改代碼會自動更新。
* ⚠️ 開發環境須於 `backend` 資料夾內，新增 `.env` 並存入 API key（有提供範例檔參考）
```bash
# 啟動開發環境 (熱重載)
docker-compose -f docker/docker-compose.dev.yml up -d

# 查看日誌
docker-compose -f docker/docker-compose.dev.yml logs -f

# 停止
docker-compose -f docker/docker-compose.dev.yml down

# 重新啟動（停止+啟動）
docker-compose -f docker/docker-compose.dev.yml down
docker-compose -f docker/docker-compose.dev.yml up -d
```

### 生產環境
```bash
# 啟動生產環境
docker-compose -f docker/docker-compose.yml up -d

# 查看日誌
docker-compose -f docker/docker-compose.yml logs -f

# 停止
docker-compose -f docker/docker-compose.yml down

# 更新代碼時使用
docker-compose -f docker/docker-compose.yml up -d --build
```

## 🌐 區域網路訪問

### 查詢您的 IP 地址
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows (命令提示字元)
ipconfig | findstr "IPv4"

# 會顯示類似：	
#      inet 192.168.0.114 netmask 0xffffff00 broadcast 192.168.100.255  (macOS/Linux)
#      IPv4 地址 . . . . . . . . . . . . : 192.168.0.114                (Windows)
# 則 192.168.0.114 就會是您的IP位址！
```

### 區域網路訪問地址
將 `192.168.0.114` 替換為您的實際 IP：

**開發環境：**
- 前端：`http://[您的IP地址]:5173`
- 後端：`http://[您的IP地址]:8001`

**生產環境：**
- 前端：`http://[您的IP地址]`
- 後端：`http://[您的IP地址]:8000`

## 🛠️ 常用命令

```bash
# 查看運行的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 查看特定服務日誌
docker-compose -f docker/docker-compose.dev.yml logs backend
docker-compose -f docker/docker-compose.dev.yml logs frontend

# 重啟特定服務
docker-compose -f docker/docker-compose.dev.yml restart backend
docker-compose -f docker/docker-compose.dev.yml restart frontend

# 一鍵清理：停止容器、刪除容器、刪除映像、刪除 volumes
docker-compose -f docker/docker-compose.dev.yml down --rmi all --volumes
docker-compose -f docker/docker-compose.yml down --rmi all --volumes

# 完全清理（包括未使用的 volumes）
docker-compose -f docker/docker-compose.dev.yml down --rmi all --volumes --remove-orphans
docker-compose -f docker/docker-compose.yml down --rmi all --volumes --remove-orphans

# 刪除未使用的 build cache
docker builder prune

# 系統清理（刪除未使用的映像、容器、網路等）
docker system prune
docker system prune -a  # 更徹底的清理
```

## 📝 注意事項

1. **首次啟動**：初次下載和構建可能需要較長時間，特別是 AI 模型檔案較大
2. **記憶體需求**：確保 Docker 有足夠記憶體來載入 AI 模型（建議 8GB+）
3. **端口衝突**：確保端口 80、5173、8000、8001 沒有被其他服務占用
4. **IP 變化**：前端會自動偵測並連接到正確的後端端口，無需手動配置
5. **熱重載**：開發環境的前後端都支援熱重載，修改代碼會自動生效

## 🔧 故障排除

### 容器無法啟動
```bash
# 檢查端口是否被占用
lsof -i :80
lsof -i :8000

# 查看詳細錯誤
docker-compose -f docker/docker-compose.dev.yml logs
```

### 無法從其他設備訪問
1. 確保所有設備連接到相同的 WiFi 網路
2. 檢查「防火牆」設定
3. 確認 IP 地址是否正確

### AI 模型載入失敗
1. 確認 `backend/ai_models/` 資料夾中有模型檔案
2. 檢查 Docker 記憶體限制
3. 查看後端啟動日誌
