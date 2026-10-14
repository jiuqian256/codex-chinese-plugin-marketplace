# 本地编辑服务模板

这是一个用于可编辑 HTML Deck 的最小本地服务模板。

它提供：

- 为一个 Deck 目录提供静态文件服务。
- `GET /api/state`：读取 `deck-state.json`。
- `POST /api/save-state`：原子写入 `deck-state.json`。
- `POST /api/export-pdf`：在安装 `playwright` 和 `pdf-lib` 后，可选导出截图式 PDF。

## 启动

在某个 Deck 目录里运行：

```bash
node path/to/templates/edit-server/server.js
```

或显式指定 Deck 目录：

```bash
HTML_PPT_DECK_DIR=/path/to/deck HTML_PPT_EDIT_PORT=8801 node server.js
```

打开：

```text
http://127.0.0.1:8801/
```

## 保存契约

Deck 应向服务发送：

```json
{
  "deckId": "basic-deck",
  "state": {
    "deckId": "basic-deck",
    "revision": 1,
    "slideOrder": [],
    "dirtySlides": [],
    "notes": {
      "slide-1": "按稳定 slideId 保存的演讲备注"
    }
  }
}
```

服务会把状态写到 Deck 的 `index.html` 同级目录下：

```text
deck-state.json
```

备注、文本、页面顺序和对象位置都应写进同一个状态文件。演示者备注不要只保存在 textarea、localStorage 或当前页序号上；应按稳定 `slideId` 保存，避免关闭演示者视图、插入/删除页面或重新打开 Deck 后丢失/错位。

## 可选 PDF 导出

在模板目录安装可选依赖：

```bash
npm install
```

然后调用：

```text
POST /api/export-pdf
```

服务会以观众/导出模式打开 Deck，逐页截图 `.stage`，并把 PDF 写入 `exports/`。
