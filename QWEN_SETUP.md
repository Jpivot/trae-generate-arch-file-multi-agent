# 通义千问API配置说明

本项目已从OpenAI API迁移到阿里云通义千问API。

## 配置步骤

### 1. 获取API密钥

1. 访问[阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 开通DashScope服务
4. 创建API Key

### 2. 配置API密钥

在 `config.yaml` 文件中配置您的API密钥：

```yaml
api:
  dashscope_api_key: "your_actual_api_key_here"  # 替换为您的实际API密钥
  base_url: "https://dashscope.aliyuncs.com/api/v1"
  model: "qwen-turbo"  # 可选模型: qwen-turbo, qwen-plus, qwen-max
  temperature: 0.7
  max_tokens: 2000
```

### 3. 可用模型

- `qwen-turbo`: 快速响应，适合日常对话
- `qwen-plus`: 平衡性能和质量
- `qwen-max`: 最高质量，适合复杂任务

### 4. 环境变量配置（可选）

您也可以通过环境变量设置API密钥：

```bash
export DASHSCOPE_API_KEY="your_actual_api_key_here"
```

### 5. 安装依赖

```bash
pip install -r requirements.txt
```

## 主要变更

1. **API端点**: 从OpenAI改为DashScope
2. **认证方式**: 使用DashScope API Key
3. **请求格式**: 适配通义千问API格式
4. **响应解析**: 适配通义千问响应结构

## 注意事项

- 确保您的阿里云账户有足够的余额
- API调用会产生费用，请合理使用
- 建议在测试环境先验证配置正确性

## 故障排除

如果遇到API调用错误，请检查：

1. API密钥是否正确
2. 网络连接是否正常
3. 账户余额是否充足
4. 模型名称是否正确