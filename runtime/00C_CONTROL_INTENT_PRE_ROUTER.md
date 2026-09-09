# 魂师修炼RPG｜Control Intent Pre-Router

> **文件职责：** 每条用户主动消息执行控制事务的最小前置分流流程。
>
> **权威范围：** pre-router 的执行程序；不拥有控制意图清单、优先级、recognition 语义、dispatcher 映射或任何业务实现。
>
> **读取策略：** `BOOT`。

## 1. 固定程序

1. 读取当前 registry `control_intents` 的最小元数据。
2. 按每个 intent 登记的 `priority` 从小到大检查。
3. 对当前候选只加载其 `recognition_owner + recognition_sections`，不得提前加载事务完整 route。
4. recognition owner 明确确认命中后，从同一 intent 条目读取 `dispatch_type`：若为 `route`，取得 `route` 并加载其最小 sources；若为 `skill`，直接调用登记的 Skill，并把当前 intent/operation 交给该 Skill。不得保留同职责空壳 route；若必需 Skill 未安装或不可用，当前控制事务失败关闭并明确提示缺失，不得临时用旧 route 或聊天记忆模拟。
5. 第一个确认命中的控制事务抢占当前轮；后续候选不再检查。
6. 全部未命中时，才把当前消息交给普通游戏 `interaction_route_activation`。

## 2. 边界

- 本文件不保存“哪些话算存档确认/外部 checkpoint 导出/继续/帮助/状态/现实活动/项目维护”的第二套语义；分别由 registry 指向的 recognition owner 负责。尤其不得因为两者都含“存档”二字，就在 pre-router 内把 `SAVE_CURRENT` 与 `SAVE_EXPORT` 合并成一个事务。
- recognition 只回答“是不是这个事务”，不能代替事务执行。
- pre-router 不修改 `runtime_working_state`，不推进世界时间，也不写 checkpoint。
- 项目维护、状态迁移、外部恢复、新游戏、Git存档确认、外部 checkpoint 导出、帮助、查看、现实活动等控制事务的存在、优先级与 dispatcher 都只认当前 registry；新增/删除 intent 或把事务在 route/Skill 间迁移时，不需要同步维护第二张表。
- 本项目没有 compatibility runtime package 控制事务，也不得在 pre-router 中为旧运行包恢复旁路。
