# 魂师修炼RPG｜Runtime Kernel

> **文件职责：** 只定义运行时编排：普通 route 发现、领域主源调用顺序、子 route 委派、原子提交与输出交接。
>
> **权威范围：** runtime orchestration；不拥有任何战斗公式、经验倍率、固定时长、价格、人物设定、篇章结构或 UI 常量。
>
> **写权限：** 正式游戏 route 只能按 `12` 形成并校验 `runtime_working_state` 候选；最终持久化必须交给 registry 登记的 `STATE_COMMIT` 写入稳定 Git state owner。本文件不直接写 Git，也不拥有兼容 checkpoint 导出权限。
>
> **读取策略：** `SELECTIVE_ON_MATCH`，只读取当前需要的 K 节。

## K0. 启动关系

本文件不是新窗口第一读取对象。新窗口与每条新的用户主动消息先执行治理入口与 `CONTROL_INTENT_PRE_ROUTER`；控制事务确认后由 manifest 登记的 dispatcher（route 或 Skill）接管。只有未命中控制事务时才进入普通游戏编排。

任何具体 route、owner、source、access policy 与 state access 都只从 manifest 当前登记读取；本文件不得维护第二套路由表。

## K1. 单轮固定流水线

`冻结玩家输入`
→ `确认/恢复 runtime_working_state`
→ `按 manifest.interaction_route_activation 发现当前普通 route`
→ `读取该 route 的最小 sources`
→ `必要时委派已登记子 route`
→ `各领域 owner 计算候选结果`
→ `12 校验一次最终工作态候选`
→ `STATE_COMMIT 原子写入稳定 Git state owner`
→ `13 / UI / 02 完成玩家可见输出`

运行时只负责把领域结果串起来，不得在编排层重写领域常量。

## K2. 普通 route 发现

普通链的匹配顺序与 activation 条件只使用 manifest 当前登记的 `interaction_route_activation`；`topic_routes` 只登记命中后的 owner、sources、access policy、state access 与 delegates。

规则：

1. 阶段锁定 route 优先于自由世界 fallback。
2. 一个输入可先命中主 route，再按 `delegates_to` 调用必要子 route；子 route 不改变主 route 的领域所有权。
3. 若多个非阶段锁定 route 同时满足，按 manifest 顺序取最具体者；`ordinary_world_action` 永远是最后 fallback。
4. route 未命中时不得靠全文读取所有文件“猜一个答案”。

阶段枚举及其状态字段语义只读取 `12`；各阶段允许的玩家输入语义读取 `13`。本文件不复制枚举值。

## K3. 现实活动编排

命中现实活动后：

1. `13` 解析用户输入的活动类型、开始/结束/补记语义；
2. `12` 提供会话与 Ledger schema、防重复与提交边界；
3. `10` 提供奖励倍率、上限与机械计算；
4. 所有候选变化通过 `12` 一次形成并校验 `runtime_working_state`，随后经 `STATE_COMMIT` 写入稳定 Git state owner；
5. 输出只显示本次实际结算需要的玩家可见字段。

本节不复制活动倍率、每日上限或世界时钟规则。

## K4. 战斗编排

战斗轮转的运行顺序为：

`PLAYER → COMPANION_1 → COMPANION_2 → COMPANION_3 → ENEMY_n → 返回 PLAYER`

不存在的队伍槽位直接跳过。玩家行动真正结算后，只要遭遇仍未结束，本回复继续执行剩余伙伴与敌方槽位，直到再次轮到玩家或遭遇结束；不得停在 NPC / 敌方槽位等待用户发送“继续”。

各行动是否合法、是否耗行动、伤害/治疗/魂力/战败/经验如何计算全部读取 `10`；伙伴人格与自主判断按当前 route 读取 `01`；遭遇时间与世界后果读取 `11`；状态提交读取 `12`；交互与展示读取 `13 / UI / 02`。

## K5. 子 route 委派

主 route 在同一轮产生另一领域事务时，只按 manifest 的 `delegates_to` 加载对应子 route，而不是把所有可能文件永久塞进主 route。

典型情况包括：猎魂发现目标后进入战斗、伙伴篇章节点进入战斗、经济交易完成后进入恢复结算。具体允许委派关系只认 manifest 当前登记。

## K6. 原子提交

每轮最终只能把已经由领域 owner 计算并校验过的候选变化持久化一次。重复叙述、UI 展示、帮助、查看、跨消息恢复都不得再次结算同一事务。

`12` 负责 schema、事务 ID、防重复与候选态校验；实际稳定写入只调用 registry 的 `internal_services.state_commit`。成功写入 `state/current/SOUL_STATE_V1.yaml` 后，该 Git tree 才是下一轮读取的当前状态。本文件不复制字段清单，也不自行执行 Git 写入。

## K7. 输出交接

机械与世界结果确定后：

- `13` 决定当前交互阶段允许展示什么、下一步等待什么输入；
- 命中专用 UI 时只读取对应 UI 模板；
- `02` 负责最终叙事文字；
- 玩家可见数值必须来自刚提交后的工作态或当前领域 owner，不得由 UI 示例自行生成。

## K8. 运行时防漂移检查

输出前只检查跨领域编排不变量：

1. 玩家输入是否被完整保留，没有替玩家补决定；
2. 当前结果是否来自命中 route 的正式 owner，而不是消费者中的复制常量；
3. 本轮是否只发生一次最终状态提交；
4. 是否错误绕过 `STATE_COMMIT`、把兼容 checkpoint 当成当前状态主源，或原地改写外部 ZIP；
5. 是否把 DM ONLY 隐藏信息泄露到玩家可见输出；
6. 若发生子事务，是否通过 manifest 登记的 route 委派，而不是临时全文扩读。

领域数值与业务规则的正确性由对应 owner 与 QA 验证，不在 Kernel 再维护一份清单。
