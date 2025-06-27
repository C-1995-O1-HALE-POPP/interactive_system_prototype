"""
LLM和多模态模型服务 - 集成百炼平台DeepSeek-v3
支持文本生成、多模态分析、情感增强等功能
"""

import os
import json
import base64
import requests
from openai import OpenAI
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BailianDeepSeekService:
    """百炼平台DeepSeek服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化百炼平台DeepSeek服务
        
        Args:
            api_key: 百炼平台API密钥，如果不提供则从环境变量获取
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 支持的模型列表
        self.models = {
            "deepseek-r1": {
                "name": "deepseek-r1",
                "description": "DeepSeek-R1 推理增强模型",
                "max_tokens": 131072,
                "supports_reasoning": True
            },
            "deepseek-r1-0528": {
                "name": "deepseek-r1-0528",
                "description": "DeepSeek-R1 升级版模型",
                "max_tokens": 131072,
                "supports_reasoning": True
            },
            "deepseek-v3": {
                "name": "deepseek-v3",
                "description": "DeepSeek-V3 MoE模型",
                "max_tokens": 65536,
                "supports_reasoning": False
            }
        }
        
        self.default_model = "deepseek-v3"
        self.image_model = "qvq-max"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        
        logger.info(f"百炼平台DeepSeek服务初始化完成，默认模型: {self.default_model}")
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        if not self.api_key:
            logger.warning("未配置DASHSCOPE_API_KEY环境变量")
            return False
        
        try:
            # 测试API连接
            response = self._make_request(
                method="POST",
                endpoint="/chat/completions",
                data={
                    "model": self.default_model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                }
            )
            return response.get("choices") is not None
        except Exception as e:
            logger.error(f"服务可用性检查失败: {str(e)}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """发送HTTP请求到百炼平台"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=60)
            else:
                response = requests.get(url, headers=self.headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            raise Exception(f"百炼平台API调用失败: {str(e)}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天完成API调用
        
        Args:
            messages: 对话消息列表
            model: 使用的模型名称
            max_tokens: 最大输出token数
            temperature: 温度参数
            stream: 是否使用流式输出
            **kwargs: 其他参数
            
        Returns:
            API响应结果
        """
        if not self.api_key:
            raise Exception("未配置百炼平台API密钥")
        
        model = model or self.default_model
        
        # 构建请求数据
        request_data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        # 添加其他参数
        request_data.update(kwargs)
        
        try:
            response = self._make_request("POST", "/chat/completions", request_data)
            
            # 处理响应
            if response.get("choices"):
                choice = response["choices"][0]
                message = choice.get("message", {})
                
                result = {
                    "content": message.get("content", ""),
                    "model": model,
                    "usage": response.get("usage", {}),
                    "timestamp": datetime.now().isoformat()
                }
                
                # 如果是R1模型，包含推理过程
                if self.models.get(model, {}).get("supports_reasoning"):
                    result["reasoning_content"] = message.get("reasoning_content", "")
                
                return result
            else:
                raise Exception("API响应格式异常")
                
        except Exception as e:
            logger.error(f"聊天完成调用失败: {str(e)}")
            raise
    
    def generate_text(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            model: 使用的模型
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            生成的文本内容
        """
        messages = [{"role": "user", "content": prompt}]
        model = model or self.default_model
        response = self.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return response.get("content", "")
    
    def analyze_emotion_with_llm(
        self,
        text: str,
        context: Dict = None,
        model: str = None
    ) -> Dict[str, Any]:
        """
        使用LLM进行情感分析
        
        Args:
            text: 待分析文本
            context: 上下文信息
            model: 使用的模型
            
        Returns:
            情感分析结果
        """
        # 构建情感分析提示
        prompt = f"""请对以下文本进行详细的情感分析，按照PAD三维情感模型（Pleasure-Arousal-Dominance）进行评估：

文本内容："{text}"

请从以下维度进行分析：
1. Pleasure（愉悦度）：0-1之间的数值，0表示非常不愉快，1表示非常愉快
2. Arousal（唤醒度）：0-1之间的数值，0表示非常平静，1表示非常兴奋
3. Dominance（支配度）：0-1之间的数值，0表示感觉被控制，1表示感觉有控制力

请以JSON格式返回结果，包含：
- pad_values: {{pleasure: 数值, arousal: 数值, dominance: 数值}}
- emotion_category: {{emotion: 情感类别, label: positive/negative/neutral, intensity: 强度}}
- analysis_reasoning: 分析推理过程
- detected_emotions: 检测到的具体情感列表
- confidence: 置信度

示例格式：
{{
  "pad_values": {{"pleasure": 0.7, "arousal": 0.6, "dominance": 0.5}},
  "emotion_category": {{"emotion": "happy", "label": "positive", "intensity": 0.7}},
  "analysis_reasoning": "分析推理...",
  "detected_emotions": ["开心", "兴奋"],
  "confidence": 0.85
}}"""

        if context:
            prompt += f"\n\n上下文信息：{json.dumps(context, ensure_ascii=False)}"
        
        try:
            response = self.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model or self.default_model,
                temperature=0.3  # 降低温度以获得更一致的结果
            )
            
            content = response.get("content", "")
            
            # 尝试解析JSON响应
            try:
                # 提取JSON部分
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_content = content[json_start:json_end].strip()
                elif "{" in content and "}" in content:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_content = content[json_start:json_end]
                else:
                    json_content = content
                
                result = json.loads(json_content)
                
                # 添加元数据
                result.update({
                    "analysis_method": "llm_enhanced",
                    "model_used": model or self.default_model,
                    "timestamp": datetime.now().isoformat(),
                    "raw_response": content
                })
                
                return result
                
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基础结果
                logger.warning("LLM情感分析响应JSON解析失败，返回基础结果")
                return {
                    "pad_values": {"pleasure": 0.5, "arousal": 0.5, "dominance": 0.5},
                    "emotion_category": {"emotion": "neutral", "label": "neutral", "intensity": 0.0},
                    "analysis_reasoning": content,
                    "detected_emotions": [],
                    "confidence": 0.5,
                    "analysis_method": "llm_fallback",
                    "model_used": model or self.default_model,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"LLM情感分析失败: {str(e)}")
            raise
    
    def generate_persona_insights(
        self,
        persona_data: Dict,
        interaction_history: List[Dict],
        model: str = None
    ) -> Dict[str, Any]:
        """
        生成角色洞察
        
        Args:
            persona_data: 角色数据
            interaction_history: 交互历史
            model: 使用的模型
            
        Returns:
            角色洞察结果
        """
        prompt = f"""基于以下角色信息和交互历史，生成深度的角色洞察分析：

角色信息：
{json.dumps(persona_data, ensure_ascii=False, indent=2)}

交互历史（最近10条）：
{json.dumps(interaction_history[-10:], ensure_ascii=False, indent=2)}

请从以下角度进行分析：
1. 性格特征分析
2. 情感倾向和模式
3. 交互风格和偏好
4. 关系发展趋势
5. 建议的互动策略

请以JSON格式返回结果，包含：
- personality_analysis: 性格分析
- emotional_patterns: 情感模式
- interaction_style: 交互风格
- relationship_trends: 关系趋势
- interaction_suggestions: 互动建议
- insights_summary: 洞察总结

示例格式：
{{
  "personality_analysis": "性格分析内容...",
  "emotional_patterns": ["模式1", "模式2"],
  "interaction_style": "交互风格描述...",
  "relationship_trends": "关系发展趋势...",
  "interaction_suggestions": ["建议1", "建议2"],
  "insights_summary": "总结..."
}}"""
        
        try:
            response = self.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model or self.default_model,
                temperature=0.4
            )
            
            content = response.get("content", "")
            
            # 解析JSON响应
            try:
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_content = content[json_start:json_end].strip()
                elif "{" in content and "}" in content:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_content = content[json_start:json_end]
                else:
                    json_content = content
                
                result = json.loads(json_content)
                
                # 添加元数据
                result.update({
                    "analysis_method": "llm_insights",
                    "model_used": model or self.default_model,
                    "timestamp": datetime.now().isoformat(),
                    "persona_id": persona_data.get("persona_id"),
                    "analysis_depth": "comprehensive"
                })
                
                return result
                
            except json.JSONDecodeError:
                logger.warning("角色洞察响应JSON解析失败")
                return {
                    "personality_analysis": content,
                    "emotional_patterns": [],
                    "interaction_style": "分析中...",
                    "relationship_trends": "数据收集中...",
                    "interaction_suggestions": [],
                    "insights_summary": content[:200] + "...",
                    "analysis_method": "llm_fallback",
                    "model_used": model or self.default_model,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"角色洞察生成失败: {str(e)}")
            raise
    
    def chat_with_persona(
        self,
        user_message: str,
        persona_data: Dict,
        conversation_history: List[Dict] = None,
        model: str = None
    ) -> Dict[str, Any]:
        """
        与角色对话
        
        Args:
            user_message: 用户消息
            persona_data: 角色数据
            conversation_history: 对话历史
            model: 使用的模型
            
        Returns:
            角色回复结果
        """
        # 构建角色设定提示
        persona_prompt = f"""你现在要扮演以下角色进行对话：

角色信息：
- 姓名：{persona_data.get('name', '未知')}
- 描述：{persona_data.get('description', '普通角色')}
- 性格特征：{', '.join(persona_data.get('personality_traits', []))}
- 交流风格：{persona_data.get('communication_style', '自然')}
- 角色类型：{persona_data.get('avatar_type', 'friend')}

请严格按照这个角色的特点进行回复，保持角色的一致性。回复要自然、符合角色设定，并体现出相应的性格特征。"""
        
        # 构建消息列表
        messages = [{"role": "system", "content": persona_prompt}]
        
        # 添加对话历史
        if conversation_history:
            for msg in conversation_history[-10:]:  # 只保留最近10条
                messages.append(msg)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.chat_completion(
                messages=messages,
                model=model or self.default_model,
                temperature=0.8  # 提高温度以获得更自然的对话
            )
            
            return {
                "persona_reply": response.get("content", ""),
                "persona_id": persona_data.get("persona_id"),
                "persona_name": persona_data.get("name"),
                "model_used": model or self.default_model,
                "timestamp": datetime.now().isoformat(),
                "conversation_context": len(messages)
            }
            
        except Exception as e:
            logger.error(f"角色对话失败: {str(e)}")
            raise

    
    def image_analysis(
        self,
        image_base64: str,
        image_format: str = "png",
        context: Dict = None,
        model: str = None,
        chat: bool = False,
        persona_data: Dict = None,
        conversation_history: List[Dict] = [],

    ) -> Dict[str, Any]:
        """
        图像内容分析

        Args:
            image_base64: 图像的Base64编码
            image_format: 图像格式（默认png）
            context: Dict = None,
            model: str = None,
            chat: 是否启用聊天模式
            persona_data: 角色数据（如果需要角色对话）
            conversation_history: 对话历史（如果需要角色对话）
            text: 

        Returns:
            多模态分析结果
        """
        # 构建多模态分析提示

        prompt = "请对提供的图片内容进行综合分析：\n\n"
        
        modalities_used = []
        
        if context:
            prompt += f"上下文信息：{json.dumps(context, ensure_ascii=False)}\n\n"
        
        prompt += """请结合提供的图片"""
        if context:
            prompt += "和上下文信息"
        prompt += """进行详细的情感分析，按照PAD三维情感模型（Pleasure-Arousal-Dominance）进行评估：

请从以下维度进行分析：
1. Pleasure（愉悦度）：0-1之间的数值，0表示非常不愉快，1表示非常愉快
2. Arousal（唤醒度）：0-1之间的数值，0表示非常平静，1表示非常兴奋
3. Dominance（支配度）：0-1之间的数值，0表示感觉被控制，1表示感觉有控制力

请以JSON格式返回结果，包含：
- pad_values: {{pleasure: 数值, arousal: 数值, dominance: 数值}}
- emotion_category: {{emotion: 情感类别, label: positive/negative/neutral, intensity: 强度}}
- analysis_reasoning: 分析推理过程
- detected_emotions: 检测到的具体情感列表
- confidence: 置信度

示例格式：
{{
  "pad_values": {{"pleasure": 0.7, "arousal": 0.6, "dominance": 0.5}},
  "emotion_category": {{"emotion": "happy", "label": "positive", "intensity": 0.7}},
  "analysis_reasoning": "分析推理...",
  "detected_emotions": ["开心", "兴奋"],
  "confidence": 0.85
}}"""
        if not image_base64:
            raise ValueError("图像Base64编码不能为空")
        if image_format in ["jpe", "jpg"]:
            image_format = "jpeg"
        elif image_format in ["tif", "tiff"]:
            image_format = "tiff"
        elif image_format not in ["bmp", "png", "webp", "heic"]:
            raise ValueError(f"不支持的图像格式: {image_format}")
        
        model = model or self.image_model

        try:
            reasoning_content = ""  # 定义完整思考过程
            answer_content = ""     # 定义完整回复
            is_answering = False   # 判断是否结束思考过程并开始回复

            completion = self.client.chat.completions.create(
                messages=[{"role": "user", 
                           "content": [
                                { 
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{image_format};base64,{image_base64}"
                                    }
                                },
                                {   
                                    "type": "text", 
                                    "text": prompt
                                }
                           ]}],
                model=model,
                stream=True,
                temperature=0.3
            )
            for chunk in completion:
                # 如果chunk.choices为空，则打印usage
                if not chunk.choices:
                    print("\nUsage:")
                    print(chunk.usage)
                else:
                    delta = chunk.choices[0].delta
                    # 打印思考过程
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                        print(delta.reasoning_content, end='', flush=True)
                        reasoning_content += delta.reasoning_content
                    else:
                        # 开始回复
                        if delta.content != "" and is_answering is False:
                            print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                            is_answering = True
                        # 打印回复过程
                        print(delta.content, end='', flush=True)
                        answer_content += delta.content
            
            # 解析JSON响应
            try:
                if "```json" in answer_content:
                    json_start = answer_content.find("```json") + 7
                    json_end = answer_content.find("```", json_start)
                    json_content = answer_content[json_start:json_end].strip()
                elif "{" in answer_content and "}" in answer_content:
                    json_start = answer_content.find("{")
                    json_end = answer_content.rfind("}") + 1
                    json_content = answer_content[json_start:json_end]
                else:
                    json_content = answer_content
                
                result = json.loads(json_content)
                
                # 添加元数据
                result.update({
                    "analysis_method": "multimodal_llm",
                    "modalities_used": modalities_used,
                    "model_used": model or self.default_model,
                    "timestamp": datetime.now().isoformat()
                })
                
            except json.JSONDecodeError:
                logger.warning("多模态分析响应JSON解析失败")
                return {
                    "overall_sentiment": {"emotion": "neutral", "confidence": 0.5},
                    "key_themes": [],
                    "modality_consistency": answer_content,
                    "emotional_intensity": 0.5,
                    "response_suggestions": [],
                    "analysis_summary": answer_content[:200] + "...",
                    "analysis_method": "multimodal_fallback",
                    "modalities_used": modalities_used,
                    "model_used": model or self.default_model,
                    "timestamp": datetime.now().isoformat()
                }
            # 处理聊天模式，如果启用聊天模式，则返回聊天结果
            if chat and persona_data:
                persona_prompt = f"""你现在要扮演以下角色进行对话：

角色信息：
- 姓名：{persona_data.get('name', '未知')}
- 描述：{persona_data.get('description', '普通角色')}
- 性格特征：{', '.join(persona_data.get('personality_traits', []))}
- 交流风格：{persona_data.get('communication_style', '自然')}
- 角色类型：{persona_data.get('avatar_type', 'friend')}

请结合图片内容"""
                if conversation_history != []:
                    persona_prompt += f"""和以下对话历史进行回复：{json.dumps(conversation_history, ensure_ascii=False, indent=2)}\n\n"""
                persona_prompt += """
注意：严格按照这个角色的特点进行回复，保持角色的一致性。回复要自然、符合角色设定，体现提供的图片内容，并体现出相应的性格特征。"""
                # 构建对话消息
                messages = [
                    {"role": "system", "content": persona_prompt},
                    {"role": "user", 
                           "content": [
                                { 
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{image_format};base64,{image_base64}"
                                    }
                                }
                           ]}]
                reasoning_content = ""  # 定义完整思考过程
                answer_content = ""     # 定义完整回复
                is_answering = False   # 判断是否结束思考过程并开始回复
                try:
                    completion = self.client.chat.completions.create(
                        messages=messages,
                        model=model,
                        stream=True,
                        temperature=0.3
                    )
                    for chunk in completion:
                        # 如果chunk.choices为空，则打印usage
                        if not chunk.choices:
                            print("\nUsage:")
                            print(chunk.usage)
                        else:
                            delta = chunk.choices[0].delta
                            # 打印思考过程
                            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                                print(delta.reasoning_content, end='', flush=True)
                                reasoning_content += delta.reasoning_content
                            else:
                                # 开始回复
                                if delta.content != "" and is_answering is False:
                                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                                    is_answering = True
                                # 打印回复过程
                                print(delta.content, end='', flush=True)
                                answer_content += delta.content
                except Exception as e:
                    logger.error(f"角色对话失败: {str(e)}")
                    raise
                result["reply"] = answer_content
                result["reasoning_content"] = reasoning_content
            return result 
        except Exception as e:
            logger.error(f"多模态内容分析失败: {str(e)}")
            raise
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "百炼平台DeepSeek服务",
            "is_available": self.is_available(),
            "api_key_configured": bool(self.api_key),
            "base_url": self.base_url,
            "supported_models": list(self.models.keys()),
            "default_model": self.default_model,
            "capabilities": [
                "文本生成",
                "多轮对话", 
                "情感分析",
                "角色洞察",
                "多模态分析",
                "推理增强（R1模型）"
            ],
            "timestamp": datetime.now().isoformat()
        }

# 全局服务实例
bailian_service = BailianDeepSeekService()

# 兼容性函数，保持与原有代码的兼容
class LLMMultimodalService:
    """LLM和多模态服务兼容类"""
    
    def __init__(self):
        self.bailian_service = bailian_service
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.bailian_service.is_available()
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        return self.bailian_service.generate_text(prompt, **kwargs)
    
    def analyze_emotion(self, text: str, context: Dict = None) -> Dict[str, Any]:
        """情感分析"""
        return self.bailian_service.analyze_emotion_with_llm(text, context)
    
    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        return self.bailian_service.chat_completion(messages, **kwargs)
    
    def multimodal_analysis(self, **kwargs) -> Dict[str, Any]:
        """多模态分析"""
        return self.bailian_service.multimodal_content_analysis(**kwargs)
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return self.bailian_service.get_service_status()

# 创建兼容实例
llm_service = LLMMultimodalService()

if __name__ == "__main__":
    # 测试代码
    print("百炼平台DeepSeek服务测试")
    
    service = BailianDeepSeekService()
    status = service.get_service_status()
    
    print(f"服务状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    if service.is_available():
        print("\n测试文本生成...")
        try:
            result = service.generate_text("你好，请介绍一下你自己。")
            print(f"生成结果: {result}")
        except Exception as e:
            print(f"测试失败: {e}")
    else:
        print("服务不可用，请检查API密钥配置")

