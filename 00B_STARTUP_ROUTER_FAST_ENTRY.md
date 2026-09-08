# 魂师修炼RPG｜Startup Router Fast Entry

> **文件职责：** 新窗口的极小启动入口，只决定下一步读取什么。
>
> **权威范围：** 启动顺序与“禁止无条件全文加载”的快速门。
>
> **不负责：** 不执行存档选择、状态恢复、结算、业务判断或写入。
>
> **读取策略：** `BOOT`。

## 1. 新窗口顺序

Git `main` 中：

`runtime/registry.json 启动切片`
→ `current.startup_router_fast_entry`
→ `current.control_intent_pre_router`
→ `control_intents.<candidate>.recognition_owner`。

本项目没有 compatibility runtime ZIP 启动分支，也没有第二份 package manifest。fast exception 是否存在、指向哪里，只读取当前 registry；本文件不写死当前值。

## 2. registry 启动切片

BOOT 只解析启动必需键：

- `project / status / source_authority`
- `current`
- `fast_exceptions`
- `control_intents`
- `state_model.current_state_owner` 与 `internal_services.state_commit` 的入口元数据
- `external_sources.checkpoint_import` 的外部 checkpoint 入口元数据

完整 `topic_routes / interaction_route_activation` 仍是机器权威，但只在对应事务确认后取当前需要的条目。

## 3. 状态入口

- “继续游戏 / 继续 / 恢复游戏”默认直接读取 `state_model.current_state_owner`，不触发外部存档选择。
- 新窗口没有会话候选态但存在合法 current state 时，直接从 Git `main` 当前 state owner 建立本轮 `runtime_working_state`。
- 只有用户明确要求“加载/恢复某个存档 ZIP、导入旧存档、切回某个外部 checkpoint”时才进入 `LOAD_SAVE`。外部候选合法性、排序与冲突规则只读取 `external_sources.checkpoint_import` 与 `12`，本文件不复制选择算法。
- Git current state 不存在时不得依赖聊天记忆重建状态；只有明确新游戏意图才进入 `NEW_GAME`。项目不会退回旧 runtime ZIP 作为替代运行源。

## 4. 禁止事项

- 不得在识别意图前全文读取全部游戏文件。
- 不得启动时加载大型 DM ONLY 数据库。
- recognition 只决定“去哪里”，不代表事务已经执行成功。
- 不得把 `12_状态存档.md` 当某次冒险的数据文件。
- 不得原地修改已有外部 checkpoint ZIP；不得绕过 `STATE_COMMIT` 直接写稳定 Git state。
- 未确认控制事务时才进入普通游戏链。
- 不得寻找、生成或加载 compatibility runtime package / package manifest 作为 fallback。
