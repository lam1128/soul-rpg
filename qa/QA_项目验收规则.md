# 魂师修炼RPG｜项目验收规则

> **文件职责：** 定义治理、职责分立、路由、状态边界与 Git-only 架构的 PASS 条件。
>
> **权威范围：** “什么状态算通过/失败”；不拥有被验收业务的实现规则。
>
> **不负责：** 不复制业务常量、公式、固定时长、价格、门槛、菜单或篇章实现。

## Incremental QA

目标修改后至少检查：

1. 文件可解析、无截断。
2. 文件职责与 `runtime/registry.json` 登记一致。
3. 目标领域只有一个业务 owner；其他消费者只保留引用、占位符或编排语义。
4. 直接消费者和 route 引用仍有效。
5. 不存在被删除文件、旧接口、别名、补丁、施工史或无消费者容器残留。
6. UI 不保存机械常量；交互层不保存机械公式；Kernel 不保存领域常量；状态 schema 不保存可由领域 owner 读取的重复业务常量。
7. 普通运行只允许形成一个 `runtime_working_state` 候选；校验后必须经 registry 的 `STATE_COMMIT` 写入稳定 Git current state。外部 checkpoint 只由明确的导入/导出/迁移事务产生或消费。
8. 受影响的 registry、owner 引用和 QA 结构已经同步。
9. 大型内容 owner 的结构约束必须在全部受管对象上仍完整覆盖。
10. 选择型内容不得重复询问同一关系问题；后续节点应消费前文结果。
11. 每个伙伴单章必须显式登记 `基础CG画面` 与 `高好感CG画面`，二者都为可观察场面且不能被局部分流意外删除；不得继续依赖单一旧CG锚点由运行时猜第二张。
12. 若修改 CG 大厅，检查入口、只读边界、未解锁隐藏策略与既有 UI 约束同步。
13. 所有会重复出现的游戏 UI 必须登记在通用 UI owner 或魂兽遭遇 UI owner 中；不得长期保留未登记的临时状态卡、伙伴卡、篇章卡、读档卡、存档确认卡、现实活动卡、猎魂卡或角色创建卡。
14. 同一 UI 类型的标题、字段顺序、分组和底部导航应稳定；动态值和条件行可由领域 owner 注入/省略，但不得每轮重新设计结构。
15. CG 收藏文案只描述直接可见的构图、动作、视线、表情、物件、光线和互动，不得加入关系总结、意义解释、剧情总结或抒情收尾。
16. 普通自由对白/连续叙事不得被 UI 模板反向限制；固定模板只覆盖菜单、导航、选择卡、状态卡和结果卡等重复界面。
17. CG 收藏不得建立第二套持久化状态；基础/高好感两个版本都必须能由现有篇章首通与历史最高分字段按篇章 owner 规则确定。
18. CG 成对解锁必须满足单向包含：高好感版已解锁时基础版必定已解锁；基础版已解锁不要求高版已解锁；后续重放提高历史最高分可以补开高版，但较低重放不得反锁已收录CG。
19. 若修改恋爱/关系弧，关系确认章位置、资格门槛与重放语义必须只读取 `data/companions/DM_ONLY_C00_伙伴篇章库.md` 当前声明；不得在单章、交互层或 QA 复制第二套关系门。
20. 关系资格若允许当前关系门章本身贡献好感/关键旗标，必须在该章常规选择与本章记录刷新后再判定；不得用进入章节前的旧累计值提前锁死本次新达成资格。
21. 关系门之后仍存在的章节必须消费当前 `ROMANCE_ACTIVE`，并提供人物专属的情侣版与同等完整的亲密伙伴版；不得把后续章节继续写成首次关系确认，也不得把非恋爱分支写成失败/缩水路线。
22. 修改关系章时必须对照 `rules/01_人物性格.md` 当前人物段落检查语言、主动方式、压力反应、幽默与亲密表达；进入恋爱不得覆盖人物稳定性格锚点或套用同一种甜宠模板。
23. 若为了承载关系门调整章节 TYPE，公开索引、单章故事骨架与全库题材配额必须仍与 `C00` 当前声明一致；QA 只验证一致性，不复制具体配额常量。
24. 每个CG收藏槽必须能回溯到唯一 `CHAPTER_ID` 的单章显式CG字段；CG大厅/UI不得替换成同章其他场面、补造未发生的关键动作/物件/身体接触，也不得提供脱离篇章记录的独立解锁路径。
25. 若某章已具备CG解锁状态但单章缺少足够明确、可观察的对应CG字段，增量QA应判为内容缺口并要求修复单章 owner；不得允许显示层临场创作一个替代画面来“补齐”。
26. 关系门之后的后续章不能只写一句“情侣版/伙伴版”声明；必须在单章内登记可执行的具体分流契约（或语义等价结构），说明哪些距离、主动动作、共同习惯、称呼/身体接触属于情侣版，哪些亲密在伙伴版仍然成立，并逐项兼容人物性格 owner。
27. 普通“存档 / 保存进度”必须是 Git current state 的只读确认，不得触发 `SAVE_EXPORT`、生成 ZIP 或增加 `STATE_REV`；只有明确外部导出/备份/checkpoint/ZIP 意图才允许进入 Save Manager。
28. canonical Git state 的历史压缩、派生缓存清理与无消费者 legacy 字段去冗余必须在 canonical 候选提交/外部导入物化时完成，不能依赖“以后某次 SAVE_EXPORT”。
29. 项目不得维护 `release`、`MAJOR.MINOR`、SemVer 或 `v3.11` 一类人工项目版本号；项目精确身份只认 Git commit SHA。
30. 仓库结构或文档排版修改后必须通过 `qa/check_repository_hygiene.py`：不得把 ZIP、backup、patch、build/dist、缓存、旧 package manifest、compatibility runtime 目录/成员表/导出器/审计脚本，或写死的旧 runtime package 文件名重新提交进 source tree；受管文本保持 UTF-8、LF 与完整文件结尾。

## Global QA

以下全部 PASS 才可正式交付 Git-only 结构或把某个精确 Git commit 作为正式候选：

### A. Git-only 治理

1. `governance/project.md` 明确 Git `main` HEAD 为源码与当前状态持久化权威。
2. `runtime/registry.json` 是唯一机器运行主源；不得携带 ZIP 成员 bytes/SHA 注册表或第二套 package manifest。
3. registry 不得存在项目/package `release` 字段或独立 `versioning` block；`source_authority.identity` 必须是 `git_commit_sha`。
4. `.github/workflows/qa.yml` 和 `qa/` 回归脚本存在且可运行。
5. `main` source tree 不保存临时 build、backup、patch、测试输出、导出 ZIP、compatibility runtime 目录、package manifest、runtime member list、runtime exporter、package audit 或其它无运行职责的派生包级生成物。

### B. 单一职责

6. 每个业务规则只能有一个 owner。
7. 非 owner 文件不得复制该规则的固定数字、公式、门槛、完整表格或判定文本。
8. 不存在仅靠 current 指针存活、却没有独立职责或真实消费者的第二主源。
9. 玩家帮助内容只有一个交互 owner；不另维护同步副本。
10. UI 模板只拥有字段/顺序/排版，业务值运行时从 owner 注入。
11. Kernel 只拥有编排，不重新实现战斗、成长、经济、世界、篇章或状态规则。
12. QA 本身不携带业务常量。
13. 重复 UI 必须落在正式 UI owner；除魂兽遭遇/战斗专用卡外，其余通用重复界面不得分散复制到交互、世界、状态或篇章 owner 中。

### C. 路由

14. control intent 先于 ordinary gameplay route；control 可直接 dispatch 到 route 或 Skill。
15. 所有 `ordinary_gameplay` route 必须且只能在 `interaction_route_activation` 出现一次，最终有且仅有一个 fallback。
16. 非 support route 必须存在真实入口；Skill 型 control intent 不得保留同职责空壳 route。
17. 过宽 route 必须拆分到单一主 owner；嵌套事务使用 `delegates_to`。
18. 常见用户意图必须有明确 dispatcher；route 必须有 owner、最小 source、access policy 与 state access。
19. 大型 DM ONLY 文件只按对象/章节/节点选择性读取。
20. BOOT 只读取启动切片，不无条件注入完整 registry。
21. `SAVE_CURRENT` 必须是只读 route 事务，外部 checkpoint `SAVE_EXPORT` 必须继续由 Save Manager Skill 独占；显式导出 recognition 优先于普通保存确认，二者不得共享模糊的裸“存档”语义。

### D. 状态

22. `rules/12_状态存档.md` 只拥有 schema、恢复/迁移、原子提交与持久化协议，不保存某次冒险当前值。
23. registry 必须登记唯一 `current_state_owner`，且该文件真实存在于 source tree、没有被 `.gitignore` 排除；Git `main` HEAD 是当前状态权威。
24. 普通游戏 route 不得原地改写已有外部 checkpoint，也不得绕过 `STATE_COMMIT` 建立第二个 current state。
25. 外部 checkpoint 只能是 `checkpoint_import` / `SAVE_EXPORT` 的显式输入输出，不能作为普通启动优先源。
26. `STATE_REV` 只表示外部 checkpoint lineage；普通 Git state commit 与 `SAVE_CURRENT` 不自动递增，也不得被称为项目版本。
27. legacy 字段只有仍有合法恢复/迁移消费者时才保留；序列化去冗余不得删除防重复或连续性职责数据。
28. 未明确执行 `STATE_MIGRATION` / `LOAD_SAVE` 时，不得用外部 checkpoint 覆盖 current Git state。
29. canonical state 的近期日志压缩、重复派生缓存与可安全删除旧容器清理不得依赖外部导出；最终 canonical 候选在 `STATE_COMMIT` 前就应符合当前序列化规范。
30. `RUNTIME_PACKAGE / RUNTIME_PACKAGE_SHA256 / RUNTIME_RELEASE` 已退出现行状态协议；canonical state 不得携带，现行 `SAVE_EXPORT` 也不得重新生成这些字段。

### E. Git-only 源码纪律

31. 项目不维护 numbered release；任何正式交付、回滚、比较或审计都以精确 Git commit SHA 为身份。
32. `compatibility/` runtime member list、runtime ZIP exporter、package manifest、derived-export QA 与 package audit 均不得存在于 current tree。
33. `source_authority` 不得暴露 `compatibility_manifest / compatibility_export_identity / compatibility_runtime_fallback` 等第二运行源元数据。
34. Git source/state 不可用时必须失败关闭；不得自动加载旧 runtime ZIP、旧 package manifest 或聊天历史副本作为 fallback。
35. Git tag 若存在，只能是可选的人类导航标签，不构成第二套版本主源，也不要求随普通维护递增。
36. README、治理、索引、CI、QA 与状态协议不得保留已废止 runtime package 的执行说明或生成步骤。

## 存档 / Git state 迁移 QA

只有明确执行 `STATE_MIGRATION` 或首次外部 checkpoint → Git current state bootstrap 时追加检查：

1. 来源 checkpoint 合法且可解析。
2. 新 revision（若本次迁移需要新 checkpoint lineage）与目标 schema 正确。
3. 除迁移协议明确允许的结构/确定性纠错外，既成游戏事实没有变化。
4. 防重复与已结算标记保持语义等价。
5. canonical `state/current/SOUL_STATE_V1.yaml` 可重新解析并通过 state QA。
6. 若同时生成外部便携 checkpoint，必须从磁盘重开后完整状态可读取；它仍不成为项目主权威。

## 章节分片与选择语义专项 QA

- 45 个 `CHAPTER_ID` 必须在 registry `companion_episode_files` 中一对一映射到 45 个不同单章文件。
- `data/companions/DM_ONLY_C00_伙伴篇章库.md` 只保存通用规则、公开导航索引和关系门，不得重新塞回完整故事卡。
- `companion_episode` route 每次运行最多解析并读取 1 个 `data/companions/episodes/*.md`。
- 每个单章文件必须维持既有 8 个不同 `CHOICE01..08` 语义职责与固定场景标签约束。
- 相邻选择不得复问同一关系规则；CG、高理解回报、低分仍有戏、标题回收与角色新信息必须继续由章内具体事件执行。
- 45 个单章都必须显式存在 `基础CG画面` 与 `高好感CG画面`；旧单字段 `记忆画面锚点（CG）` 不得继续作为运行兼容入口。
- 两个CG字段除了满足章内事件要求，还必须能直接转换为纯视觉收藏描述：至少有明确空间、双方位置/距离、动作或手势、关键物件/环境；不得主要依赖旁白解释其意义。
- 每章CG收藏结构固定为“基础 + 高好感”一对。基础版与高版必须是可观察上能区分的两张画面；高版应增强具体互动动作/距离/物件关系，不得只换形容词或说明文字。
- CG大厅在基础已开、高版未开时必须明确保留“高好感版未解锁”槽位；完全未完成章节不得因此泄露隐藏标题、剧情内容或具体高分选项。
- CG剧情绑定专项：每个已显示CG必须来自对应单章实际发生的显式CG字段；显示层不得选取另一个“更漂亮”的剧情瞬间替代，也不得把未发生的动作、物件或亲密程度写进收藏描述。CG解锁只能是篇章进度/本章表现的派生结果。
- 关系弧专项：按 `C00` 当前声明解析每名人物的关系门章与后续章；关系门章不得把固定关系确认塞进与关系无关的重调查/大战结尾，后续章不得残留“首次关系确认/满足门槛后再确认”等旧职责。
- 关系弧专项：后续章的 `ROMANCE_ACTIVE` 两版都必须保留完整8选择和本章核心事件；差异应落在人物允许的称呼、距离、主动动作、共同习惯与回应方式，而不是简单替换“朋友/恋人”标签。
- 关系后续专项：每个第5章都必须具有明确可执行的关系分流内容，不能只靠章节头的一句状态声明让运行时临场猜；伙伴版应保留人物原有的非恋爱亲密方式，情侣版只能在人物性格允许的范围内增加关系专属亲密。
- OOC专项：受修改人物的单章内容需与 `rules/01_人物性格.md` 对应人物锚点逐项兼容；若亲密表达与稳定性格冲突，以性格 owner 为准修改章节，而不是为了恋爱强行改变人物。
