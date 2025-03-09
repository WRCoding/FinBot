# FinBot - 个人财务管理助手

FinBot是一个基于微信机器人的个人财务管理助手，能够通过微信自动捕获、记录个人财务数据，并提供汇总和AI对话分析数据功能。

## 核心功能

### 1. 交易信息捕获与处理
- 识别并解析微信中的银行交易提醒消息
- 智能识别交易类型、金额、时间等关键信息
<img width="621" alt="image" src="https://github.com/user-attachments/assets/db5c819c-b178-434d-b344-87de17ab41b3" />


### 2. 数据存储与管理
- 本地SQLite数据库存储交易记录
- 自动同步数据至飞书电子表格，便于远程访问和共享
  <img width="731" alt="image" src="https://github.com/user-attachments/assets/0f523734-c60c-424b-a779-7e09192b3b8e" />


### 3. 财务分析与报告
- 提供日常财务数据汇总与分析
- 支持按日期查询交易记录
- 生成每日收支汇总报告
- 通过AI辅助分析财务数据及趋势
<img width="657" alt="image" src="https://github.com/user-attachments/assets/8e38d2ce-c48a-4cf6-87f1-b86749b24dcf" />
<img width="603" alt="image" src="https://github.com/user-attachments/assets/0eeb9831-4f3f-4b96-af4f-1934e23f3ff0" />


### 4. 多平台集成
- 微信机器人实时接收并处理消息
- 飞书数据同步与展示
- 支持通过简单指令查询财务信息

## 项目结构

```
FinBot/
├── ai/                 # AI服务集成模块
├── analysis/           # 财务数据分析模块
├── db/                 # 数据库模型和服务
│   ├── models/         # 数据模型
│   └── services/       # 数据库服务
├── feishu/             # 飞书API集成
├── scheduler/          # 定时任务管理
│   └── jobs/           # 具体任务实现
├── util/               # 通用工具函数
├── config.py           # 配置文件
├── finbot.py           # 机器人核心实现
├── main.py             # 程序入口
├── parse_msg.py        # 消息解析模块
└── requirements.txt    # 项目依赖
```

## 使用指南

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置项目
1. 修改`config.py`，填入相应Key

### 启动服务
```bash
python main.py
```

### 支持的指令
- `#今日数据` - 查询今日交易记录
- `#昨日数据` - 查询昨日交易记录
- `#汇总@日期` - 指定日期的收支汇总（如：`#汇总@2023-01-01`）
- `@DS` - 与AI助手对话，分析财务数据


FinBot让个人财务管理变得简单高效，通过自动化的数据捕获和智能分析，帮助用户更好地了解自己的财务状况，实现财务目标。 
