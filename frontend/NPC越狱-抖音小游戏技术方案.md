## 1. 文档概述

本文档用于定义 `NPC 越狱` 项目的正式技术方案，目标形态为 `抖音小游戏原生前端 + Python Flask API 后端 + PostgreSQL 数据库 + DeepSeek 大模型对话能力`。

项目定位为一款轻量、可快速体验、可反复尝试、具备分享传播能力的 AI 对话小游戏。技术设计以比赛场景为前提，优先保证以下目标：

- 在短周期内完成可交付 Demo
- 支持完整的单局对话、结算、排行和挑战分享闭环
- 保证大模型密钥安全，不在前端暴露
- 控制小游戏包体与系统复杂度，避免过度工程化

## 2. 总体架构

### 2.1 技术栈

- 前端：抖音小游戏原生开发 + TypeScript
- 后端：Python + Flask API
- 数据库：PostgreSQL
- AI 服务：DeepSeek Chat API
- ORM：SQLAlchemy
- 数据迁移：Flask-Migrate
- 限流：Flask-Limiter
- 部署：Gunicorn + Nginx

### 2.2 架构分层

```text
抖音小游戏前端
  ├─ 首页/选关
  ├─ 游戏页
  ├─ 结果页
  ├─ 排行榜页
  └─ 挑战页
        │
        ▼
Flask API 服务
  ├─ 关卡配置
  ├─ 对局创建
  ├─ 聊天编排
  ├─ 结算评分
  ├─ 排行统计
  └─ 挑战分享
        │
        ├─ DeepSeek API
        └─ PostgreSQL
```

### 2.3 设计原则

- 前端只负责交互与展示，不保存敏感信息
- 后端统一处理 AI 调用、对局状态、得分计算和排行逻辑
- 数据库只保存关键业务数据，不保存无用冗余快照
- 关卡配置和 Prompt 配置化，便于快速扩展 5 关以上内容
- 先保证 1 关完整跑通，再复制扩展到全部关卡

## 3. 前端技术方案

### 3.1 方案选择

前端采用 `抖音小游戏原生开发`，不使用 Unity、Unreal、Cocos 等重引擎。

选择原生方案的原因：

- 项目核心是文字对话与 UI 反馈，不需要重度实时渲染
- 包体更容易控制在比赛要求范围内
- 页面式交互更适合小游戏原生容器
- 更容易接入抖音平台的分享、缓存、页面跳转能力
- 开发成本低，便于快速完成 Demo

### 3.2 前端职责

- 展示关卡列表、规则、场景与目标
- 发起对局并保存当前局内状态
- 渲染玩家与 NPC 聊天消息
- 展示剩余句数、动摇度、成功或失败结果
- 调用后端接口获取排行榜与挑战数据
- 调起原生分享能力进行传播

### 3.3 页面结构

- `首页`
  - 游戏标题
  - 一句话玩法说明
  - 五个关卡卡片
  - 排行榜入口
- `游戏页`
  - 场景描述
  - 目标说明
  - NPC 信息卡
  - 聊天记录区
  - 输入框与发送按钮
  - 动摇度进度条
  - 剩余句数提示
- `结果页`
  - 通关或失败状态
  - 最终得分
  - 最佳一句
  - 最后一条 NPC 回复
  - 再试一次
  - 生成挑战
- `排行榜页`
  - 总榜
  - 单关榜
- `挑战页`
  - 挑战文案
  - 指定关卡信息
  - 开始挑战按钮

### 3.4 前端目录建议

```text
frontend/
├─ game.js
├─ game.json
├─ pages/
│  ├─ home/
│  ├─ game/
│  ├─ result/
│  ├─ rank/
│  └─ challenge/
├─ components/
│  ├─ level-card/
│  ├─ npc-panel/
│  ├─ chat-list/
│  ├─ chat-bubble/
│  ├─ input-bar/
│  ├─ shake-bar/
│  └─ result-card/
├─ services/
│  ├─ request.ts
│  ├─ game.ts
│  ├─ rank.ts
│  └─ challenge.ts
├─ store/
│  ├─ app.ts
│  ├─ user.ts
│  └─ run.ts
├─ utils/
│  ├─ storage.ts
│  ├─ format.ts
│  ├─ guard.ts
│  └─ constants.ts
└─ assets/
```

### 3.5 前端状态设计

#### appStore

- `loading`：全局加载状态
- `networkError`：全局网络错误提示
- `version`：当前版本号

#### userStore

- `deviceId`：玩家设备匿名标识
- `nickname`：玩家昵称
- `historyBest`：历史最高分缓存

#### runStore

- `runId`：当前对局 ID
- `levelId`：当前关卡 ID
- `messages`：消息列表
- `remainingTurns`：剩余句数
- `shakeValue`：动摇度
- `status`：当前对局状态
- `bestLine`：本局最佳一句
- `score`：结算得分

### 3.6 前端交互流程

1. 首页调用接口获取关卡列表
2. 玩家选择关卡，调用后端创建一局游戏
3. 后端返回 `runId`、开场对白、句数上限、初始状态
4. 玩家输入一句话并发送
5. 前端调用聊天接口，等待后端返回 NPC 回复
6. 根据返回结果更新聊天记录、动摇度、剩余句数
7. 若对局结束则进入结果页
8. 结果页可发起挑战或查看排行榜

### 3.7 前端性能与包体策略

- 不引入大型 UI 框架
- 不引入重型游戏引擎
- 资源图片尽量压缩，优先使用轻量图
- 背景尽量用渐变和样式实现，不依赖大图
- 聊天记录只保留当前局所需内容
- 首页首屏资源最小化，排行榜按需请求

## 4. 后端技术方案

### 4.1 方案选择

后端采用 `Flask API`，原因如下：

- 轻量、结构清晰，适合比赛项目快速开发
- 适合提供纯接口服务，不需要复杂后台模板能力
- 易于接入 DeepSeek、SQLAlchemy、限流和日志方案
- 对于当前项目规模，复杂度比 Django 更低

### 4.2 后端职责

- 管理关卡静态配置与 Prompt
- 创建对局并初始化局内状态
- 调用 DeepSeek 完成 NPC 对话
- 判断通关、失败和结算逻辑
- 保存对局记录和聊天记录
- 维护排行榜和统计信息
- 生成挑战码与分享信息

### 4.3 后端目录建议

```text
backend/
├─ app.py
├─ config.py
├─ extensions.py
├─ blueprints/
│  ├─ level.py
│  ├─ run.py
│  ├─ chat.py
│  ├─ rank.py
│  └─ challenge.py
├─ models/
│  ├─ player.py
│  ├─ level.py
│  ├─ game_run.py
│  ├─ run_message.py
│  ├─ level_stat.py
│  └─ challenge.py
├─ services/
│  ├─ deepseek_service.py
│  ├─ prompt_service.py
│  ├─ run_service.py
│  ├─ scoring_service.py
│  ├─ rank_service.py
│  └─ challenge_service.py
├─ schemas/
│  ├─ level.py
│  ├─ run.py
│  ├─ chat.py
│  └─ rank.py
├─ utils/
│  ├─ response.py
│  ├─ validators.py
│  └─ security.py
└─ migrations/
```

### 4.4 模块划分

#### level blueprint

- 获取关卡列表
- 获取关卡详情

#### run blueprint

- 创建对局
- 获取对局状态
- 手动结束对局

#### chat blueprint

- 接收玩家输入
- 调用 AI
- 返回 NPC 回复和更新后的对局状态

#### rank blueprint

- 返回排行榜
- 返回单关统计

#### challenge blueprint

- 创建挑战码
- 获取挑战详情

### 4.5 对局状态机

对局状态建议采用以下枚举：

- `playing`：进行中
- `success`：已通关
- `fail`：已失败
- `finished`：已完成并结算

状态流转：

```text
创建对局 -> playing
playing + 命中成功条件 -> success -> finished
playing + 句数耗尽 -> fail -> finished
```

## 5. AI 对话设计

### 5.1 DeepSeek 调用方式

所有 AI 请求统一由后端完成，前端只与 Flask API 通信。

后端每次请求 DeepSeek 时需拼装：

- 当前关卡的 system prompt
- 历史对话消息
- 玩家当前输入

### 5.2 Prompt 配置原则

每关 Prompt 固定包含：

- NPC 身份
- 规则限制
- 性格描述
- 弱点说明
- 输出格式约束
- 成功触发词
- 禁止泄题规则

### 5.3 返回结构建议

为了降低解析难度，要求模型返回 JSON：

```json
{
  "reply": "你这话听着倒像是真的，可我也不能随便坏规矩啊。",
  "passed": false,
  "shake_delta": 18,
  "judgement": "玩家给出紧急性，但信息还不够充分",
  "best_line_hit": true
}
```

### 5.4 AI 返回后的后端处理

后端收到结果后需执行：

- 校验 JSON 格式是否合法
- 对 `shake_delta` 做上下限保护
- 判断当前局是否已经应该结束
- 扣减剩余句数
- 保存当前轮聊天记录
- 更新 `bestLine`
- 必要时触发结算

## 6. 数据库设计

### 6.1 数据库选型

推荐使用 `PostgreSQL`，原因如下：

- 稳定成熟，适合结构化业务数据
- 便于做排行榜查询和聚合统计
- 与 SQLAlchemy 配合成熟
- 可选择自建或托管版本

### 6.2 核心数据表

#### 1. players

用于记录匿名玩家。

字段：

- `id`
- `device_id`
- `nickname`
- `created_at`

#### 2. levels

用于记录关卡配置。

字段：

- `id`
- `name`
- `difficulty`
- `scene`
- `goal`
- `max_turns`
- `base_score`
- `success_token`
- `opening_message`
- `system_prompt`
- `status`

#### 3. game_runs

用于记录每一局游戏状态和结果。

字段：

- `id`
- `player_id`
- `level_id`
- `status`
- `remaining_turns`
- `shake_value`
- `passed`
- `score`
- `best_line`
- `final_reply`
- `created_at`
- `finished_at`

#### 4. run_messages

用于记录每一轮对话消息。

字段：

- `id`
- `run_id`
- `role`
- `content`
- `turn_index`
- `shake_delta`
- `created_at`

#### 5. level_stats

用于保存关卡统计结果。

字段：

- `level_id`
- `play_count`
- `pass_count`
- `avg_score`
- `best_score`
- `updated_at`

#### 6. challenges

用于分享挑战。

字段：

- `id`
- `creator_player_id`
- `level_id`
- `source_run_id`
- `challenge_code`
- `share_title`
- `expires_at`
- `created_at`

### 6.3 建表 SQL 草案

```sql
create table players (
  id uuid primary key,
  device_id varchar(64) not null unique,
  nickname varchar(32),
  created_at timestamp not null default current_timestamp
);

create table levels (
  id varchar(32) primary key,
  name varchar(64) not null,
  difficulty int not null,
  scene text not null,
  goal text not null,
  max_turns int not null,
  base_score int not null,
  success_token varchar(32) not null,
  opening_message text not null,
  system_prompt text not null,
  status varchar(16) not null default 'active'
);

create table game_runs (
  id uuid primary key,
  player_id uuid not null,
  level_id varchar(32) not null,
  status varchar(16) not null,
  remaining_turns int not null,
  shake_value int not null default 0,
  passed boolean not null default false,
  score int not null default 0,
  best_line text,
  final_reply text,
  created_at timestamp not null default current_timestamp,
  finished_at timestamp
);

create table run_messages (
  id bigserial primary key,
  run_id uuid not null,
  role varchar(16) not null,
  content text not null,
  turn_index int not null,
  shake_delta int not null default 0,
  created_at timestamp not null default current_timestamp
);

create table level_stats (
  level_id varchar(32) primary key,
  play_count int not null default 0,
  pass_count int not null default 0,
  avg_score numeric(10,2) not null default 0,
  best_score int not null default 0,
  updated_at timestamp not null default current_timestamp
);

create table challenges (
  id uuid primary key,
  creator_player_id uuid not null,
  level_id varchar(32) not null,
  source_run_id uuid not null,
  challenge_code varchar(32) not null unique,
  share_title varchar(128) not null,
  expires_at timestamp,
  created_at timestamp not null default current_timestamp
);
```

### 6.4 索引建议

- `players.device_id` 唯一索引
- `game_runs.level_id, score desc` 排行索引
- `game_runs.player_id, created_at` 历史查询索引
- `run_messages.run_id, turn_index` 消息顺序索引
- `challenges.challenge_code` 唯一索引

## 7. 核心接口设计

### 7.1 获取关卡列表

- 方法：`GET /api/v1/levels`
- 说明：返回可玩的关卡概览

响应示例：

```json
{
  "items": [
    {
      "id": "level_1",
      "name": "老陈·门卫",
      "difficulty": 1,
      "goal": "进楼取快递",
      "maxTurns": 5,
      "intro": "善良但守规矩，可被情感打动"
    }
  ]
}
```

### 7.2 获取关卡详情

- 方法：`GET /api/v1/levels/<level_id>`
- 说明：返回场景、目标、规则等详情

### 7.3 创建对局

- 方法：`POST /api/v1/runs`
- 说明：初始化一局新游戏

请求示例：

```json
{
  "deviceId": "tt_device_001",
  "levelId": "level_1"
}
```

响应示例：

```json
{
  "runId": "9c3f9e3d-xxxx",
  "status": "playing",
  "remainingTurns": 5,
  "shakeValue": 0,
  "openingMessage": "站住，没业主确认可不能进。"
}
```

### 7.4 查询对局状态

- 方法：`GET /api/v1/runs/<run_id>`
- 说明：用于恢复页面状态或查看聊天历史

### 7.5 发送玩家一句话

- 方法：`POST /api/v1/chat/send`
- 说明：发送玩家输入并获取 NPC 回复

请求示例：

```json
{
  "runId": "9c3f9e3d-xxxx",
  "content": "大叔，我妈买的药快超时了，她腿脚不好下不来。"
}
```

响应示例：

```json
{
  "runId": "9c3f9e3d-xxxx",
  "status": "playing",
  "remainingTurns": 4,
  "shakeValue": 22,
  "shakeDelta": 22,
  "passed": false,
  "assistantReply": "你这话听着倒像是真的，可我也不能随便坏规矩啊。",
  "bestLineUpdated": true
}
```

### 7.6 结束并结算对局

- 方法：`POST /api/v1/runs/<run_id>/finish`
- 说明：手动结算或异常兜底

### 7.7 获取排行榜

- 方法：`GET /api/v1/rankings`
- 说明：支持总榜和单关榜

### 7.8 获取关卡统计

- 方法：`GET /api/v1/stats/<level_id>`
- 说明：返回通关率、平均分等指标

### 7.9 创建挑战

- 方法：`POST /api/v1/challenges`
- 说明：根据完成对局生成挑战码

### 7.10 获取挑战详情

- 方法：`GET /api/v1/challenges/<code>`
- 说明：根据挑战码拉取分享内容

## 8. 评分与结算设计

### 8.1 评分公式

```text
最终得分 = 关卡基础分 × 句数倍率
```

### 8.2 句数倍率

- 1 句通关：`4.0`
- 2 句通关：`3.0`
- 3 句通关：`2.0`
- 4 句通关：`1.2`
- 5 句通关：`1.0`
- 失败：`0`

### 8.3 动摇度规则

- 动摇度作为局内反馈指标，用于增强玩家感知
- 动摇度不直接决定通关，但可作为模型内部判定参考
- 每轮根据 DeepSeek 返回的 `shake_delta` 累加并限制在 `0~100`

### 8.4 最佳一句规则

- 默认记录引发最大 `shake_delta` 的玩家输入
- 若最终通关句触发成功词，则优先记录最终通关句

## 9. 安全与风控设计

### 9.1 安全要求

- DeepSeek API Key 仅保存在后端环境变量
- 前端不保存系统 Prompt
- 排行榜分数以后端结算结果为准
- 所有接口必须通过 HTTPS

### 9.2 限流建议

- 单设备单秒最多发送 1 次聊天请求
- 同一对局不允许超过最大句数
- 连续异常请求触发临时封禁

### 9.3 数据校验

- 校验 `deviceId` 是否存在
- 校验 `runId` 是否有效且未结束
- 校验 `content` 是否为空或超长
- 校验 `levelId` 是否存在并可玩

## 10. 部署方案

### 10.1 前端部署

- 使用抖音开发者工具完成本地调试
- 上传体验版进行真机测试
- 通过审核后发布正式版本

### 10.2 后端部署

- 使用 Gunicorn 运行 Flask
- 使用 Nginx 反向代理并提供 HTTPS
- 使用环境变量管理配置：
  - `DEEPSEEK_API_KEY`
  - `DATABASE_URL`
  - `APP_ENV`
  - `RATE_LIMIT`

### 10.3 数据库部署

- 可使用托管 PostgreSQL
- 开发、测试、生产环境分库
- 定期备份核心业务数据

## 11. 开发计划

### 11.1 第一阶段：跑通一关

- 完成首页、游戏页、结果页静态结构
- 完成后端工程初始化
- 完成数据库表结构
- 打通 `关卡列表 -> 创建对局 -> 单轮聊天 -> 结算`

### 11.2 第二阶段：扩展到五关

- 完成关卡配置化
- 录入全部 5 关 Prompt
- 调整 NPC 风格和成功判定

### 11.3 第三阶段：补全传播能力

- 完成排行榜
- 完成挑战分享
- 优化结果页文案和反馈动画

### 11.4 第四阶段：稳定性与提审

- 真机试玩
- 调优 Prompt
- 修复边界问题
- 压缩包体与资源
- 准备比赛演示材料

## 12. 最小可交付范围

首版 Demo 的最低交付要求如下：

- 5 个关卡全部可玩
- AI 对话链路稳定
- 可正确通关和失败
- 能显示分数与结果
- 排行榜至少支持单关榜
- 可发起基础挑战分享

## 13. 结论

该项目的推荐实现方式为：

- 前端使用抖音小游戏原生开发
- 后端使用 Python Flask API
- 数据库使用 PostgreSQL
- AI 能力通过 DeepSeek 接入

该方案兼顾了比赛所需的 `轻量化`、`完整度`、`传播性` 和 `短周期可落地性`，适合在有限时间内快速打磨出可提交的高完成度 Demo。
