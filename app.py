from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import Flask, redirect, render_template, request, url_for


app = Flask(__name__)
DEFAULT_DATA_FILE = Path("/tmp/todos.json") if os.environ.get("VERCEL") else Path(__file__).with_name("todos.json")
DATA_FILE = Path(os.environ.get("TODO_DATA_FILE", DEFAULT_DATA_FILE))
KV_KEY = "flask_todos"


def _kv_request(command: list[str]) -> Optional[object]:
    kv_url = os.environ.get("KV_REST_API_URL")
    kv_token = os.environ.get("KV_REST_API_TOKEN")
    if not kv_url or not kv_token:
        return None

    req = Request(
        kv_url,
        data=json.dumps(command).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {kv_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError):
        return None

    return payload.get("result") if isinstance(payload, dict) else None


def _normalize_todos(data: object) -> list[dict[str, str]]:
    if not isinstance(data, list):
        return []

    return [
        {"id": str(item["id"]), "title": str(item["title"])}
        for item in data
        if isinstance(item, dict) and item.get("id") and item.get("title")
    ]


def load_todos() -> list[dict[str, str]]:
    kv_data = _kv_request(["GET", KV_KEY])
    if isinstance(kv_data, str):
        try:
            return _normalize_todos(json.loads(kv_data))
        except json.JSONDecodeError:
            return []

    if not DATA_FILE.exists():
        return []

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    return _normalize_todos(data)


def save_todos(todos: list[dict[str, str]]) -> None:
    serialized = json.dumps(todos, ensure_ascii=False)
    if _kv_request(["SET", KV_KEY, serialized]) is not None:
        return

    DATA_FILE.write_text(
        json.dumps(todos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@app.get("/")
def index():
    return render_template("index.html", todos=load_todos())


@app.post("/todos")
def add_todo():
    title = request.form.get("title", "").strip()
    if title:
        todos = load_todos()
        todos.append({"id": uuid.uuid4().hex, "title": title})
        save_todos(todos)
    return redirect(url_for("index"))


@app.post("/todos/<todo_id>/delete")
def delete_todo(todo_id: str):
    todos = [todo for todo in load_todos() if todo["id"] != todo_id]
    save_todos(todos)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
