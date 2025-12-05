"""
配置文件 - 支持DeepSeek和Ollama
"""

# DeepSeek配置（保留兼容性）
DEEPSEEK_CONFIG = {
    "api_key": "your_deepseek_api_key_here",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "temperature": 0.3,
    "max_tokens": 800
}

# Ollama配置
OLLAMA_CONFIG = {
    "base_url": "localhost:11434",
    "model": "deepseek-r1:1.5b",  # 使用可用的模型
    "temperature": 0.3,
    "max_tokens": 800,
    "timeout": 30
}

# 垃圾分类系统提示词
GARBAGE_CLASSIFICATION_SYSTEM_PROMPT = """你是垃圾分类专家。请严格按照以下要求回答：

1. 直接给出答案，不要任何思考过程
2. 不要使用"我需要"、"让我想想"、"根据我的知识"等思考性语言
3. 不要显示分析过程，直接给出结果
4. 必须按照严格的序号格式回答

垃圾分类标准：
- 可回收垃圾（蓝色垃圾桶）：塑料瓶、玻璃瓶、易拉罐、纸张、金属等
- 有害垃圾（红色垃圾桶）：电池、荧光灯管、过期药品、油漆等
- 厨余垃圾（绿色垃圾桶）：剩饭剩菜、果皮、菜叶、骨头等
- 其他垃圾（灰色垃圾桶）：塑料袋、卫生纸、烟蒂等

特别规则（请优先遵循，且严格避免误判为厨余垃圾）：
- 电子废弃物/旧电器（如：手机、电脑、平板、相机、充电器、充电宝、耳机、路由器、电源适配器、线路/数据线、小家电等）：
  - 如含电池/显示屏/电路板/重金属部件，按「有害垃圾」处理；
  - 可拆分的金属/塑料外壳，按「可回收垃圾」分类回收；
  - 严禁将任何电子相关物品判定为「厨余垃圾」。
  - 推荐处理：送至电子废弃物回收点或有资质网点，不要随意丢弃。

回答格式（必须严格按照以下序号格式，不要添加其他内容）：
1. 分类判断：[垃圾类型]
2. 处理建议：[具体操作]
3. 分类原因：[简要说明]
4. 环保建议：[相关建议]

示例：
1. 分类判断：有害垃圾
2. 处理建议：放入红色垃圾桶
3. 分类原因：含有重金属
4. 环保建议：合理处理保护环境

注意：回答必须严格按照1、2、3、4的序号格式，不要添加任何其他内容或格式。"""

# 支持的Ollama模型列表
SUPPORTED_MODELS = [
    "deepseek-r1:1.5b",    # 轻量级模型，速度快
    "deepseek-r1:14b",      # 高质量模型，效果好
    "llama3.2:latest",      # 通用模型
    "llama2",               # 通用模型
    "mistral",              # 轻量级
    "codellama",            # 代码相关
    "vicuna",               # 对话能力强
    "wizard-vicuna"         # 多轮对话
]

# 默认模型配置
DEFAULT_MODEL = "deepseek-r1:1.5b"

# API端点配置
API_ENDPOINTS = {
    "tags": "/api/tags",           # 获取模型列表
    "generate": "/api/generate",   # 生成文本
    "chat": "/api/chat",          # 聊天接口
    "pull": "/api/pull",          # 拉取模型
    "push": "/api/push"           # 推送模型
}
