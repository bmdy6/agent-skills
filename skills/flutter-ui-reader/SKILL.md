---
name: flutter-ui-reader
description: "【能力/自动按需】用于 Android Flutter App 的界面自动化，`uiautomator dump` 读不到文字，或需要按界面文字精确定位、点击时；iOS-on-Mac 不适用。"
---

# Flutter UI Reader（读取 Flutter 界面）

Flutter 常把界面画在 SurfaceView/画布上，普通 `uiautomator dump` 只能看到空壳。开 Android 无障碍并重启 App 后，让 Flutter 重建语义树，再用 `uiautomator` 读文字和 bounds。目标是按文字精确操作，不靠截图猜坐标。

## 适用与不适用

适用于：

- Android 真机或模拟器里的 Flutter App。
- `uiautomator dump` 节点很少、可读文字为 0，但界面实际有内容。
- 需要按按钮/标签文字点击，而不是只能盲点坐标。

不适用：

- macOS 上的 iOS-on-Mac 客户端。实测没有等效的无障碍开关，System Events 读按钮会返回 `missing value`；改用 Android 模拟器路径。
- 需要读取受保护页面或绕过 App 权限的场景。

## 操作流程

1. 确认目标是 Android 设备和 App 包名：

```bash
adb devices
adb shell pm list packages | grep <关键词>
```

2. 读取无障碍当前状态。开启设置会改变设备状态，先告诉用户；记下原值，结束后按需恢复：

```bash
adb shell settings get secure accessibility_enabled
adb shell settings put secure accessibility_enabled 1
```

3. 彻底停掉并重启 App，让 Flutter 重建语义树：

```bash
adb shell am force-stop <包名>
adb shell monkey -p <包名> -c android.intent.category.LAUNCHER 1
```

4. dump 控件树，并确认文字节点数量明显增加：

```bash
DUMP_DIR=$(mktemp -d)
trap 'rm -rf "$DUMP_DIR"' EXIT
REMOTE_XML="/sdcard/window-$$.xml"

adb shell rm -f "$REMOTE_XML"
adb shell uiautomator dump "$REMOTE_XML"
adb pull "$REMOTE_XML" "$DUMP_DIR/window.xml"
adb shell rm -f "$REMOTE_XML"

test -s "$DUMP_DIR/window.xml" || { echo "dump 或 pull 失败，停止操作"; exit 1; }
```

5. 用文字找节点，取 bounds 中心点击。不要只靠上一次截图里的固定坐标：

```bash
python3 - "$DUMP_DIR/window.xml" <<'PY'
import xml.etree.ElementTree as ET
import sys

root = ET.parse(sys.argv[1]).getroot()
for node in root.iter("node"):
    text = node.attrib.get("text", "")
    desc = node.attrib.get("content-desc", "")
    if text or desc:
        print(text or desc, node.attrib.get("bounds"))
PY
```

6. 点击后重新 dump，确认页面状态真的变了。金额、地址、订单状态这类关键数据，如果后续动作有风险，再和权威来源（RPC/API/数据库）核对一次，不能只信一次 UI 读取。

## 判断是否生效

- dump XML 从“几乎没有文字节点”变成有目标文字和 bounds。
- 点击后目标页面/字段发生变化，或出现预期的新文字。
- 读到的数据能和权威来源对上；对不上时先停下说明差异。

## 常见错误

- 不重启 App 就直接 dump，Flutter 语义树还没重建。
- 用整页截图猜坐标，误触系统区域或相邻控件。
- 把 iOS-on-Mac 当成同一条路径。
- 把一次 UI 文本当成最终真相，关键金额/地址不做外部核对。
- 忘记恢复无障碍开关，或没记原值就说已经恢复。
