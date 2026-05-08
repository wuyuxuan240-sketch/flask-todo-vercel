# Flask Todo

一个极简待办事项网站，支持添加、删除任务，并自动保存到 `todos.json`。

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

打开浏览器访问 `http://127.0.0.1:5000`。

## 部署到 Vercel

Vercel 会读取 `app.py` 和 `requirements.txt`。直接导入这个项目，或在登录 Vercel CLI 后运行：

```bash
vercel deploy
```

本地开发时任务保存到 `todos.json`。部署到 Vercel 后，建议在项目里添加 Vercel KV；配置完成后，代码会自动读取 `KV_REST_API_URL` 和 `KV_REST_API_TOKEN` 来长期保存任务。
