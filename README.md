# WolfAI (MVP)

单人网页版狼人杀（你 + AI玩家）最小可运行实现。

## 功能
- 快速局（6人，含2狼人）
- 白天 AI 发言、投票放逐、夜晚自动结算
- 云端/本地 LLM 模式切换（抽象层，MVP 为模拟输出）
- Web 页面直接游玩

## 启动
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

浏览器打开：http://localhost:8000

## API
- `POST /api/games` 创建游戏
- `GET /api/games/{game_id}` 获取状态
- `POST /api/games/{game_id}/speeches` 生成 AI 发言
- `POST /api/games/{game_id}/vote` 玩家投票并推进流程
- `POST /api/games/{game_id}/llm/switch` 切换 LLM 模式
