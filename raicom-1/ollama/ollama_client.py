import requests
import json
import time
from typing import Generator, Optional
from PyQt5.QtCore import QObject, pyqtSignal
from .deepseek_config import DEEPSEEK_CONFIG, GARBAGE_CLASSIFICATION_SYSTEM_PROMPT

class OllamaClient(QObject):
    """Ollama API客户端"""
    
    # 信号定义
    response_received = pyqtSignal(str)  # 接收到响应
    error_occurred = pyqtSignal(str)     # 发生错误
    connection_status = pyqtSignal(bool) # 连接状态
    
    def __init__(self, base_url: str = "localhost:11434", model: str = "deepseek-r1:1.5b"):
        super().__init__()
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
    def test_connection(self) -> bool:
        """测试与Ollama API的连接"""
        try:
            # 尝试获取模型列表
            response = self.session.get(f"http://{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.connection_status.emit(True)
                return True
            else:
                self.connection_status.emit(False)
                return False
        except Exception as e:
            print(f"连接测试失败: {e}")
            self.connection_status.emit(False)
            return False
    
    def generate_response(self, prompt: str, model: str = None, 
                         temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
        """发送生成请求到Ollama"""
        try:
            if model is None:
                model = self.model
                
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = self.session.post(
                f"http://{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'response' in result:
                    content = result['response']
                    self.response_received.emit(content)
                    return content
                else:
                    error_msg = "API响应格式错误"
                    self.error_occurred.emit(error_msg)
                    return None
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                self.error_occurred.emit(error_msg)
                return None
                
        except requests.exceptions.Timeout:
            error_msg = "请求超时，请检查网络连接"
            self.error_occurred.emit(error_msg)
            return None
        except requests.exceptions.ConnectionError:
            error_msg = "无法连接到Ollama服务，请确保服务已启动"
            self.error_occurred.emit(error_msg)
            return None
        except Exception as e:
            error_msg = f"请求失败: {str(e)}"
            self.error_occurred.emit(error_msg)
            return None
    
    def stream_generate(self, prompt: str, model: str = None,
                       temperature: float = 0.7, max_tokens: int = 1000) -> Generator[str, None, None]:
        """流式生成请求"""
        try:
            if model is None:
                model = self.model
                
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = self.session.post(
                f"http://{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        try:
                            json_data = json.loads(line)
                            if 'response' in json_data:
                                yield json_data['response']
                            if json_data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                error_msg = f"流式请求失败: {response.status_code}"
                self.error_occurred.emit(error_msg)
                
        except Exception as e:
            error_msg = f"流式请求失败: {str(e)}"
            self.error_occurred.emit(error_msg)
    
    def get_garbage_classification_answer(self, question: str) -> str:
        """获取垃圾分类专业回答"""
        # 构造完整的提示词
        full_prompt = f"{GARBAGE_CLASSIFICATION_SYSTEM_PROMPT}\n\n用户问题：{question}"
        
        response = self.generate_response(full_prompt, temperature=0.3, max_tokens=800)
        
        # 过滤思考过程，直接返回答案
        if response:
            filtered = self._filter_thinking_process(response)
            corrected = self._postprocess_answer(question, filtered)
            return corrected
        return response
    
    def _filter_thinking_process(self, text: str) -> str:
        """过滤AI回答中的思考过程，确保按序号格式显示"""
        if not text:
            return text
        
        import re
        
        # 定义需要完全移除的思考性段落
        thinking_paragraphs = [
            r"好的，我现在来仔细分析一下这个问题.*?总结一下",
            r"我需要.*?确保用户能够清楚理解",
            r"让我.*?直接给出答案",
            r"根据.*?分析.*?问题",
            r"我需要.*?组织.*?信息"
        ]
        
        # 移除完整的思考性段落
        for pattern in thinking_paragraphs:
            text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
        
        # 定义需要过滤的思考性句子
        thinking_sentences = [
            "好的，我现在来仔细分析一下这个问题",
            "用户问的是",
            "这涉及到",
            "我需要将这些信息",
            "条理清晰地组织起来",
            "直接给出答案",
            "不使用任何思考性的语言",
            "确保用户能够清楚理解",
            "总结一下，我需要",
            "我需要分析",
            "让我分析",
            "根据我的知识",
            "我需要考虑",
            "让我判断",
            "我需要回忆",
            "让我想想",
            "根据经验",
            "我需要思考",
            "让我仔细",
            "我需要整理",
            "让我组织"
        ]
        
        # 移除包含思考过程的句子
        for sentence in thinking_sentences:
            if sentence in text:
                # 移除包含该句子的整行
                lines = text.split('\n')
                filtered_lines = []
                for line in lines:
                    if sentence not in line:
                        filtered_lines.append(line)
                text = '\n'.join(filtered_lines)
        
        # 查找实际答案的开始位置 - 更严格的序号匹配
        answer_indicators = [
            "1. 分类判断", "1.分类判断", "1. 分类判断：", "1.分类判断：",
            "1. 处理建议", "1.处理建议", "1. 处理建议：", "1.处理建议：",
            "1. 分类原因", "1.分类原因", "1. 分类原因：", "1.分类原因：",
            "1. 环保建议", "1.环保建议", "1. 环保建议：", "1.环保建议："
        ]
        
        lines = text.split('\n')
        start_index = 0
        
        # 找到第一个包含实际答案的行
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if any(indicator in line_clean for indicator in answer_indicators):
                start_index = i
                break
        
        # 如果找到了答案开始位置，返回从该位置开始的内容
        if start_index > 0:
            filtered_lines = lines[start_index:]
            result = '\n'.join(filtered_lines).strip()
        else:
            result = text.strip()
        
        # 进一步确保格式正确 - 只保留1-4的序号行
        lines = result.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            # 只保留以1.、2.、3.、4.开头的行
            if re.match(r'^[1-4]\.\s*', line):
                formatted_lines.append(line)
        
        # 如果找到了格式化的行，使用它们；否则返回原始结果
        if formatted_lines:
            result = '\n'.join(formatted_lines)
        
        # 清理多余的空行和空格
        result = re.sub(r'\n\s*\n', '\n', result)  # 移除多余空行
        result = re.sub(r'^\s+|\s+$', '', result, flags=re.MULTILINE)  # 移除行首行尾空格
        
        return result.strip()

    def _postprocess_answer(self, question: str, answer: str) -> str:
        """基于关键词的保护性后处理，修正明显误分类。

        规则：含电子/电器相关关键词时，禁止判为厨余；优先判为有害垃圾，并给出规范处理建议。
        """
        if not answer:
            return answer

        import re

        # 电子/电器相关关键词
        ewaste_keywords = [
            "旧电器", "电器", "电子", "手机", "电脑", "笔记本", "平板", "相机", "摄像头", "耳机",
            "充电器", "充电宝", "电池", "电源", "适配器", "路由器", "机顶盒", "主板", "电路板",
            "数据线", "线缆", "U盘", "硬盘", "移动硬盘", "显示器", "电视", "小家电"
        ]

        text = f"{question}\n{answer}"
        if any(k in text for k in ewaste_keywords):
            # 解析行
            lines = answer.split('\n')
            new_lines = []
            has_category_override = False
            for line in lines:
                content = line.strip()
                # 修正分类判断
                if re.match(r"^1\.\s*分类判断", content):
                    if ("厨余" in content) or ("其他" in content):
                        content = "1. 分类判断：有害垃圾"
                        has_category_override = True
                    # 若模型本就给出可回收/有害，保留
                # 修正处理建议：避免堆肥/普通垃圾桶
                elif re.match(r"^2\.\s*处理建议", content):
                    if ("堆肥" in content) or ("绿" in content) or ("厨余" in content) or ("灰色" in content):
                        content = "2. 处理建议：送至电子废弃物回收点或有资质网点；含电池/屏幕部件按红色垃圾桶（有害垃圾）处理"
                # 修正分类原因
                elif re.match(r"^3\.\s*分类原因", content):
                    if ("厨余" in content) or ("易腐" in content) or ("食物" in content) or ("生物" in content):
                        content = "3. 分类原因：含电池/电路板/重金属或难以自然降解，需专业回收"
                # 环保建议增强
                elif re.match(r"^4\.\s*环保建议", content):
                    content = "4. 环保建议：不要随意丢弃或混入生活垃圾，优先交电子回收渠道"

                new_lines.append(content)

            # 若未命中第1条但需要强制覆盖
            if not any(l.startswith("1. 分类判断：") for l in new_lines):
                new_lines.insert(0, "1. 分类判断：有害垃圾")
                has_category_override = True

            # 确保格式为1-4四行
            ordered = []
            found = {1: False, 2: False, 3: False, 4: False}
            for i in range(1, 5):
                prefix = f"{i}. "
                for l in new_lines:
                    if l.startswith(prefix):
                        ordered.append(l)
                        found[i] = True
                        break
            # 填充缺失项
            if not found[2]:
                ordered.append("2. 处理建议：送至电子废弃物回收点或有资质网点；含电池/屏幕部件按红色垃圾桶（有害垃圾）处理")
            if not found[3]:
                ordered.append("3. 分类原因：含电池/电路板/重金属或难以自然降解，需专业回收")
            if not found[4]:
                ordered.append("4. 环保建议：不要随意丢弃或混入生活垃圾，优先交电子回收渠道")

            return "\n".join(ordered)

        # 其他情况直接返回
        return answer
    
    def chat_completion(self, messages: list, model: str = None, 
                       temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
        """聊天完成接口（兼容原有接口）"""
        # 将消息列表转换为单个提示词
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                prompt_parts.append(f"系统指令：{content}")
            elif role == 'user':
                prompt_parts.append(f"用户：{content}")
            elif role == 'assistant':
                prompt_parts.append(f"助手：{content}")
        
        full_prompt = "\n\n".join(prompt_parts)
        return self.generate_response(full_prompt, model, temperature, max_tokens)
