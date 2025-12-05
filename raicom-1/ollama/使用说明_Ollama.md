# 垃圾分类AI问答助手 - Ollama版使用说明

## 快速开始

### 1. 安装Ollama

**Windows:**
1. 访问 https://ollama.ai
2. 下载并安装Ollama for Windows
3. 安装完成后，Ollama会自动添加到系统PATH

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. 启动Ollama服务

```bash
ollama serve
```

### 3. 安装模型

选择一个适合的模型安装：

```bash
# 推荐使用deepseek-chat（中文支持好）
ollama pull deepseek-chat

# 或者使用其他模型
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

### 4. 运行应用

```bash
# 方法1：使用启动脚本（推荐）
python start_ollama.py

# 方法2：直接运行
python main.py
```

## 功能使用

### 1. 常见问题
- 点击左侧的常见问题按钮
- 系统会自动发送问题并显示AI回答

### 2. 自定义问题
- 在底部输入框中输入您的问题
- 按回车键或点击"发送"按钮
- 等待AI回答

### 3. 连接状态
- 查看右上角的连接状态指示器
- 🟢 已连接：服务正常
- 🔴 未连接：服务异常

## 问题示例

### 基础分类问题
- "塑料瓶属于什么垃圾？"
- "电池应该怎么处理？"
- "剩饭剩菜是什么垃圾？"

### 详细咨询问题
- "玻璃瓶可以回收吗？回收后能做什么？"
- "过期药品怎么处理？为什么不能随便丢弃？"
- "塑料袋是什么垃圾？有什么环保替代品？"

### 知识普及问题
- "什么是可回收垃圾？包括哪些？"
- "有害垃圾有哪些？为什么要单独处理？"
- "厨余垃圾如何处理？有什么用途？"

## 故障排除

### 1. 连接失败
**问题：** 显示"🔴 未连接"
**解决：**
1. 检查Ollama服务是否启动：`ollama serve`
2. 确认端口11434未被占用
3. 检查防火墙设置

### 2. 模型未找到
**问题：** 提示"未找到可用模型"
**解决：**
1. 运行 `ollama list` 查看已安装模型
2. 安装模型：`ollama pull deepseek-chat`
3. 等待模型下载完成

### 3. 回答异常
**问题：** AI回答不准确或异常
**解决：**
1. 检查模型是否正确安装
2. 尝试重启Ollama服务
3. 更换其他模型测试

### 4. 性能问题
**问题：** 回答速度慢
**解决：**
1. 确保有足够的系统内存
2. 使用GPU加速（如果支持）
3. 选择较小的模型

## 高级配置

### 1. 更换模型
在 `deepseek_config.py` 中修改：
```python
OLLAMA_CONFIG = {
    "model": "llama2",  # 改为您想要的模型
    # ... 其他配置
}
```

### 2. 调整回答参数
```python
OLLAMA_CONFIG = {
    "temperature": 0.5,    # 提高创造性
    "max_tokens": 1000,    # 增加回答长度
    # ... 其他配置
}
```

### 3. 自定义提示词
在 `deepseek_config.py` 中修改 `GARBAGE_CLASSIFICATION_SYSTEM_PROMPT`

## 系统要求

### 最低要求
- Python 3.7+
- 4GB RAM
- 2GB 可用磁盘空间

### 推荐配置
- Python 3.8+
- 8GB+ RAM
- GPU支持（可选）
- 10GB+ 可用磁盘空间

## 支持的模型

### 推荐模型
- **deepseek-chat**: 中文支持好，回答准确
- **llama2**: 通用性强，性能稳定
- **mistral**: 轻量级，速度快

### 其他模型
- codellama: 代码相关
- vicuna: 对话能力强
- wizard-vicuna: 多轮对话

## 注意事项

1. **首次使用**：需要下载模型，请确保网络连接稳定
2. **内存使用**：大模型需要较多内存，建议8GB以上
3. **响应速度**：首次运行可能较慢，后续会加快
4. **模型更新**：定期运行 `ollama pull` 更新模型

## 技术支持

如果遇到问题，请：
1. 查看控制台错误信息
2. 检查Ollama服务状态
3. 确认模型安装正确
4. 参考官方文档：https://ollama.ai
