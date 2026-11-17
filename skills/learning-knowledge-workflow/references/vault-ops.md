# Knowledge / Obsidian 维护

## 定位

knowledge-mcp 是唯一知识真源。

Obsidian 是本地 Markdown 的查看、编辑和图谱工具；Workbench 是给本人日常阅读的派生层。Canvas、Bases、Graph 都只是视图，不保存第二份正文。

## 当前目录原则

- personal/：长期主文章默认扁平。
- personal/辅助材料/：保存可回查的原文、历史资料和既有待整理入口；调研沿用当前库内既有文章与命名。
- company/：按公司项目边界维护。
- archive/：历史归档，默认不参与日常检索。

目录与命名以知识库当前 AGENTS.md 和实际文件为准。保留已有的「知识待整理」作为单一收集入口，不恢复旧生成阅读层、平行草稿箱、概念卡体系或待投喂目录。

## 维护动作

优先使用 knowledge-mcp 的受保护能力：

- search：查已有主题；
- read：读原文；
- show_diff / apply_change：更新已有文档；
- create_document：确实是独立新主题时创建；
- move_document：目录整理或改名；
- validate：结构和元数据巡检。

批量移动前先查引用；move_document 不会自动改其他文档里的路径引用。

## Obsidian 相关

- 可以用 Obsidian 打开 knowledge-mcp 目录阅读或本地编辑。
- Canvas / Bases 可以做视图，但不要复制正文。
- Web Clipper 或外部剪藏只算素材；用户要求先存时放入既有待整理入口，要求整理时再按内容归入调研或主文章。
- 不为了漂亮图谱大量创建原子概念文件。

## Workbench

Workbench 只发布：

- 00–03 的长期入口；
- 带 阅读/沉淀 tag 的长期文章。

调研、历史学习稿、过程件不会直接发布。出现 Workbench 展示问题时，先判断是“内容真源问题”还是“派生阅读层问题”，不要直接在 WebDAV 快照里修正文。

## 验收

库结构调整后至少检查：

1. validate 无新增 findings；
2. 旧路径引用是否清零；
3. 新路径引用是否真实存在；
4. 相关测试通过；
5. Workbench 发布白名单没有意外扩大。
