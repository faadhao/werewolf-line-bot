# Werewolf LINE Bot

這是一個用於在 LINE 群組中玩狼人殺的機器人。該機器人支持多種角色，包括平民、女巫、預言家、獵人和狼人。

## 功能

- 支持多玩家遊戲
- 自動管理遊戲狀態
- 處理玩家的消息和命令

## 安裝

1. 克隆此存儲庫：
   ```bash
   git clone <repository-url>
   ```

2. 進入專案目錄：
   ```bash
   cd werewolf-line-bot
   ```

3. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```

## 使用

1. 配置環境變數，設置 LINE Bot 的 API 金鑰。
2. 運行應用：
   ```bash
   python src/app.py
   ```

## 部署

此專案可以部署到 Render 上，請參考 `Procfile` 以獲取啟動命令。

## 測試

運行測試以確保所有功能正常：
```bash
pytest
```

## 貢獻

歡迎任何形式的貢獻！請提交問題或拉取請求。