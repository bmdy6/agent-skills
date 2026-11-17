# GitHub Issue 截图证据

只在 Issue 需要本地截图时读取。

## 1. 先检查尺寸，再压图

macOS 可直接用 `sips`：

```bash
sips -g pixelWidth -g pixelHeight /path/to/input.png
```

如果宽度明显超过 1400 px：

```bash
sips --resampleWidth 1400 /path/to/input.png --out /tmp/issue-image.png
sips -g pixelWidth -g pixelHeight /tmp/issue-image.png
```

第二次输出才是正文里可使用的真实尺寸。不要把原图尺寸抄到压缩后的 `<img>` 上；不需要强制高度时只写 `width` 更不容易变形。

## 2. 本地文件先拿到 GitHub attachment URL

`gh issue create --body-file` 只负责提交正文，**没有本地图片上传参数**。本地截图必须先经 GitHub 页面上传，拿到类似：

```text
https://github.com/user-attachments/assets/...
```

已有可访问的 GitHub attachment URL 就直接复用，不要重复上传。

需要浏览器上传时使用当前 `ego-browser` 的公开 API：

```js
const chooserPromise = page.waitForFileChooser({ timeout: 10_000 });
await page.click("<从 snapshot 得到的上传按钮定位器>");
const chooser = await chooserPromise;
await chooser.setFiles("/absolute/path/issue-image.png");
```

如果页面已经有稳定的 file input，也可以：

```js
await page.setInputFiles("<从 snapshot 得到的 file input 定位器>", [
  "/absolute/path/issue-image.png",
]);
```

先通过页面 snapshot 找当前定位器，不把 GitHub 的 DOM selector 或 CDP 细节长期写死。上传完成后读编辑器内容，确认 attachment URL 已生成，再组装最终 body。

## 3. 正文放图

普通情况优先 Markdown：

```markdown
![问题复现](https://github.com/user-attachments/assets/...)
```

需要控制宽度时：

```html
<img src="https://github.com/user-attachments/assets/..." width="1400" alt="问题复现">
```

如果同时写 `width` 和 `height`，必须使用压缩后重新读取的真实尺寸。

图片放在它证明的那条证据下面。图片已经把错误提示、界面状态或前后对比讲清时，正文只写“看哪里”，不要再把图中文字复述一次。

## 4. 发布后回读

创建/更新 Issue 后至少确认两件事：

1. API/`gh issue view` 中正文包含正确的 `user-attachments` URL；
2. 浏览器打开 Issue，图片正常渲染且没有被错误尺寸拉伸。
