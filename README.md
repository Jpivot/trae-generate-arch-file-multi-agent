# 架构设计文档生成系统

基于多智能体协作的架构设计文档自动生成系统，使用大语言模型生成专业、完整的架构设计文档。

## 🚀 功能特性

- **多智能体协作**：每个章节由专门的智能体负责生成，确保内容专业性
- **并行生成**：支持章节并行生成，提高生成效率
- **依赖管理**：智能处理章节间的依赖关系，确保内容连贯性
- **外部接口集成**：支持调用第三方API获取上下游系统信息
- **模板化输出**：使用标准化模板，确保文档格式统一
- **智能后处理**：使用LLM进行文档连贯性检查和优化

## 📋 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   输入数据      │    │   主智能体        │    │   输出文档      │
│                 │    │                  │    │                 │
│ • 技术栈信息    │───▶│ • 协调调度        │───▶│ • 背景章节      │
│ • 系统描述      │    │ • 依赖管理        │    │ • 应用架构      │
│ • 数据库信息    │    │ • 内容整合        │    │ • 微服务架构    │
│ • 业务需求      │    │                  │    │ • 代码结构      │
└─────────────────┘    └──────────────────┘    │ • 数据库设计    │
                                │               │ • 上下游系统    │
                                │               └─────────────────┘
                                ▼
                       ┌──────────────────┐
                       │   章节智能体      │
                       │                  │
                       │ • 背景智能体      │
                       │ • 架构智能体      │
                       │ • 微服务智能体    │
                       │ • 代码智能体      │
                       │ • 数据库智能体    │
                       │ • 上下游智能体    │
                       └──────────────────┘
```

## 🛠️ 安装和配置

### 1. 环境要求

- Python 3.8+
- OpenAI API Key（或其他兼容的LLM API）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置设置

编辑 `config.yaml` 文件，设置你的API密钥：

```yaml
api:
  openai_api_key: "your_openai_api_key_here"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000
```

## 🚀 快速开始

### 1. 创建示例输入文件

```bash
python main.py --create-sample
```

这将创建一个 `input_data.json` 示例文件。

### 2. 运行文档生成

```bash
python main.py
```

生成的文档将保存在 `output/` 目录下。

### 3. 自定义输入数据

创建你自己的输入数据文件：

```json
{
  "project_name": "你的项目名称",
  "system_id": "your_system_id",
  "system_description": "系统描述信息",
  "tech_stack": {
    "前端": ["React", "TypeScript"],
    "后端": ["Spring Boot", "Java 17"],
    "数据库": ["MySQL 8.0", "Redis"]
  },
  "database_info": {
    "primary_db": "MySQL 8.0",
    "cache_db": "Redis 6.0"
  },
  "business_requirements": [
    "高可用性",
    "高性能",
    "可扩展性"
  ]
}
```

## 📁 项目结构

```
trae-generate-arch-file-multi-agent/
├── src/
│   ├── agents/                 # 智能体模块
│   │   ├── base_agent.py      # 基础智能体类
│   │   ├── section_agent.py   # 章节智能体
│   │   └── master_agent.py    # 主智能体
│   ├── services/              # 服务模块
│   │   ├── llm_service.py     # LLM服务
│   │   └── external_api_service.py # 外部API服务
│   └── factory/               # 工厂模块
│       └── agent_factory.py   # 智能体工厂
├── templates/                 # 模板文件
│   ├── document_template.md   # 文档模板
│   └── prompts/              # 提示词模板
│       ├── background_prompt.txt
│       ├── app_architecture_prompt.txt
│       ├── microservice_prompt.txt
│       ├── code_structure_prompt.txt
│       ├── database_prompt.txt
│       └── upstream_downstream_prompt.txt
├── config.yaml               # 配置文件
├── requirements.txt          # 依赖包
├── main.py                  # 主程序入口
└── README.md               # 项目说明
```

## 🔧 高级配置

### 智能体依赖关系

系统自动管理章节间的依赖关系：

- **背景章节**：无依赖，优先生成
- **应用架构**：依赖背景章节
- **微服务架构**：依赖应用架构
- **代码结构**：依赖微服务架构
- **数据库设计**：依赖微服务架构
- **上下游系统**：依赖应用架构

### 自定义提示词模板

你可以修改 `templates/prompts/` 目录下的提示词模板来定制生成内容的风格和格式。

### 外部API集成

在 `config.yaml` 中配置外部API：

```yaml
external_apis:
  upstream_service_api: "https://api.example.com/upstream"
  downstream_service_api: "https://api.example.com/downstream"
```

## 📊 生成的文档章节

1. **背景**：项目背景、业务目标、技术目标
2. **应用架构**：整体架构、核心组件、技术选型
3. **微服务架构**：服务拆分、通信方式、数据一致性
4. **代码结构**：项目结构、分层架构、编码规范
5. **数据库设计**：数据库架构、表设计、性能优化
6. **上下游系统**：系统集成、接口设计、监控告警

## 🔍 监控和日志

系统提供详细的日志记录：

- 控制台输出：实时查看生成进度
- 日志文件：`architecture_generator.log`
- 生成状态：通过API获取各章节生成状态

## 🚨 错误处理

- **重试机制**：LLM调用失败时自动重试
- **降级策略**：外部API失败时使用模拟数据
- **异常恢复**：单个章节失败不影响其他章节

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 常见问题

### Q: 如何更换LLM模型？
A: 在 `config.yaml` 中修改 `model` 字段，支持所有OpenAI兼容的模型。

### Q: 生成时间太长怎么办？
A: 可以调整 `temperature` 和 `max_tokens` 参数，或者使用更快的模型。

### Q: 如何自定义章节？
A: 可以通过 `AgentFactory.create_custom_agent()` 方法创建自定义智能体。

### Q: 支持中文吗？
A: 完全支持中文，所有提示词模板都是中文，生成的文档也是中文。

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 加入讨论群

---

**让AI帮你写出专业的架构设计文档！** 🎉