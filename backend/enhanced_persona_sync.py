"""
LLM-Driven PersonaSync (自建 LLM Request 轮子)
===========================================

> **更新**：应用户要求，完全去除对现有 `llm_service` 依赖，
>   重新实现一个最小可用的 LLM 请求封装 **`LLMRequester`**。
>
> 该封装支持：
> * 直接 HTTP `POST` 请求 OpenAI-Compatible 接口（如 DashScope / OpenAI）。
> * 简单重试 + 超时控制。
> * `chat()` 返回值只保留 `content` 与 `raw_json`，方便上层解析。
>
> 之后所有子任务（情感分析/实体抽取/风格解析/...）统一调用
> `self.llm.chat(prompt, **kwargs)` → `_parse_json_safe()`，保持与之前逻辑一致。

示例
----
```python
ps = LLMDrivenPersonaSync(db_path="ris.db", api_key="YOUR-KEY")
res = ps.process_interaction("u1", "今天和张三在北京参加发布会，超级兴奋！")
print(json.dumps(res, ensure_ascii=False, indent=2))
```
"""
from __future__ import annotations
import json, os, time, logging, random, re
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence
from openai import OpenAI
import base64
import requests
import jieba

from ris_data_model import RISDataModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ────────────────────────────────────────────────────────────────────────────────
# 1. 统一 LLM 请求封装
# ────────────────────────────────────────────────────────────────────────────────

class LLMRequester:
    """最小可用 OpenAI-Compatible ChatCompletion 请求器。"""

    def __init__(
        self,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key: Optional[str] = None,
        model: str = "qwen-turbo",
        timeout: int = 30,
        max_retries: int = 2,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.image_model = "qwen-vl-max-latest"  # 可选：如果需要图像处理
        self.image_client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        logger.info(f"LLMRequester 初始化成功，使用模型: {self.model}, 基础 URL: {self.base_url}")
        logger.info(f"API Key: {'已设置' if self.api_key else '未设置'}")


    # ------------------------------------------------------------------
    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                rsp = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
                rsp.raise_for_status()
                print(rsp.text)  # 调试输出
                return rsp.json()
            except Exception as e:
                last_err = e
                sleep = (attempt + 1) * 2 + random.random()
                logger.warning(f"LLM 请求失败，第 {attempt+1}/{self.max_retries} 次重试…: {e}")
                time.sleep(sleep)
        raise RuntimeError(f"LLM 请求最终失败: {last_err}")

    # ------------------------------------------------------------------
    def chat(self, prompt, temperature: float = 0.3, max_tokens: int = 2048) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}] if isinstance(prompt, str) else prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = self._post("/chat/completions", payload)
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"content": content, "raw_json": data}
    
    def chat_with_image(self, prompt: List[Dict], temperature: float = 0.3, max_tokens: int = 2048) -> Dict[str, Any]:
        payload = {
            "model": self.image_model,
            "messages": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = self._post("/chat/completions", payload)
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"content": content, "raw_json": data}
    # ------------------------------------------------------------------
    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            self.chat("ping", max_tokens=8)
            return True
        except Exception:
            return False

# ────────────────────────────────────────────────────────────────────────────────
# 2. PersonaSync 主类
# ────────────────────────────────────────────────────────────────────────────────

_JSON_FALLBACK_ENTITIES = {k: [] for k in ["persons", "locations", "time_expressions", "events", "organizations"]}

class EnhancedPersonaSync:
    DEFAULT_PERSONA = {
        "name": "小助手",
        "description": "一个友善、耐心的AI助手，专门帮助用户记录和分析情感体验",
        "personality_traits": ["友善", "耐心", "理解", "支持"],
        "communication_style": "温和",
        "avatar_type": "friend",
    }

    # ------------------------------------------------------------------
    def __init__(
        self,
        db_path: str = "ris_system.db",
        *,
        api_key: Optional[str] = None,
        base_url: str | None = None,
        model: str = "qwen-turbo",
    ) -> None:
        self.db = RISDataModel(db_path)
        self.llm = LLMRequester(base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1", api_key, model)
        self.llm_ok = self.llm.is_available()
        jieba.initialize()

    # ─────────────── 公共 API ───────────────
    def process_interaction(
        self,
        user_id: str,
        text: str,
        input_type: str = "topic",
        image_path: Optional[str] = None,
        persona_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.db.get_user_profile(user_id):
            self.db.create_user_profile(user_id)
        self._ensure_default_persona(user_id)
        if image_path and image_path is not None:
            image_content = self._analyze_image(image_path)
            text = f"""我向你提供了一张图片：\n{image_content}\n\n同时我告诉你这段文字：\n{text}"""
        pad = self._analyze_emotion(text)
        log_id = self.db.log_interaction(
            user_id=user_id,
            input_type=input_type,
            detected_emotion=pad.get("pad_values", {}),
            emotion_label=pad.get("emotion_category", {}).get("label", "neutral"),
            raw_input_data={"text": text, "image": image_content if image_path else None},
        )
        self.db.save_emotion_analysis(log_id, pad.get("pad_values", {}), pad.get("emotion_category", {}),
                                      {"confidence": pad.get("confidence", 0.5)}, pad.get("analysis_method", "llm"))

        entities = self._extract_entities(text)
        style = self._analyze_style(text)
        temporal = self._extract_temporal(text)

        new_ps = self._create_personas(user_id, entities, text, style)
        upd_ps = self._update_personas(user_id, entities)
        memories = self._create_memories(user_id, log_id, text, entities, pad, temporal)
        reply = self._get_response_to_interaction(user_id, persona_id, text)

        return {
            "interaction_log_id": log_id,
            "pad_analysis": pad,
            "entities": entities,
            "new_personas": new_ps,
            "updated_personas": upd_ps,
            "new_memories": memories,
            "timestamp": datetime.now().isoformat(),
            "reply": reply,
        }
        
    # ─────────────── LLM-辅助工具 ───────────────
    def _ask_json(self, prompt, fallback: Any) -> Any:
        system_prompt = """你是一个智能助手，擅长从用户输入中提取情感、实体、风格等信息，并返回结构化的 JSON 格式数据。
每次请求，你都需要返回一个 JSON 对象，格式如下：
```json
{  "key1": <value1>,
  "key2": <value2>,
  ...
  "keyN": <valuen>
}
```
请确保返回的 JSON 格式正确，包含用户提示中所有必要的字段，不要包含任何额外的文本或解释。
请严格地遵循 JSON 格式规范，不要返回任何非 JSON 的内容。
"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ] if isinstance(prompt, str) else prompt
            rsp = self.llm.chat(messages)
            txt = rsp["content"]
            start, end = txt.find("{"), txt.rfind("}") + 1
            return json.loads(txt[start:end])
        except Exception as e:
            logger.warning(f"解析 LLM JSON 失败: {e}")
            return fallback

    # 1. 情感分析 ----------------------------------------------------------
    def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        system_prompt = (
            # "请对以下文本进行 PAD 情感分析并返回 JSON：\n" + text + "\n"
            # "返回格式：{\"pad_values\":{...},\"emotion_category\":{...},\"confidence\":0-1}"
            """请对用户提供的文本进行详细的情感分析，按照PAD三维情感模型（Pleasure-Arousal-Dominance）进行评估：

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
```json
    {{
        "pad_values": {{"pleasure": 0.7, "arousal": 0.6, "dominance": 0.5}},
        "emotion_category": {{"emotion": "happy", "label": "positive", "intensity": 0.7}},
        "analysis_reasoning": "分析推理...",
        "detected_emotions": ["开心", "兴奋"],
        "confidence": 0.85
    }}
```
注意：
- 请确保返回的 JSON 格式正确，包含所有必要字段。
- 请严格地遵循 JSON 格式规范，不要返回任何非 JSON 的内容。
"""
        )
        payload = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
        return self._ask_json(payload, {
            "pad_values": {"pleasure": 0.5, "arousal": 0.5, "dominance": 0.5},
            "emotion_category": {"label": "neutral", "emotion": "neutral", "intensity": 0},
            "analysis_method": "fallback",
        })

    # 2. 实体抽取 ----------------------------------------------------------
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        prompt = (
            "抽取实体并返回 JSON：{persons, locations, time_expressions, events, organizations}。\n文本：" + text
        )
        return self._ask_json(prompt, _JSON_FALLBACK_ENTITIES)

    # 3. 风格分析 ----------------------------------------------------------
    def _analyze_style(self, text: str) -> Dict[str, str]:
        prompt = "分析交流风格并返回 JSON：{formality, emotion_expression, sentence_structure, tone, length_category}.\n文本：" + text
        return self._ask_json(prompt, {})

    # 4. 时空信息 ----------------------------------------------------------
    def _extract_temporal(self, text: str) -> Dict[str, Any]:
        prompt = "解析文本时空信息，分 temporal / spatial 两部分，JSON 返回。\n文本：" + text
        return self._ask_json(prompt, {})

    # 5-6. 角色创建/推断 ----------------------------------------------------
    def _create_personas(self, user_id: str, entities: Dict, context: str, style: Dict):
        new_list = []
        for name in entities.get("persons", []):
            if any(p["name"] == name for p in self.db.get_personas(user_id)):
                continue
            info = self._ask_json(
                f"为角色{name}推断 personality_traits (list) 与 avatar_type，并返回 JSON。上下文：{context}",
                {"personality_traits": ["普通"], "avatar_type": "friend"},
            )
            pid = self.db.create_persona(user_id=user_id, name=name,
                                         description=f"对话中出现的角色：{name}",
                                         personality_traits=info["personality_traits"],
                                         communication_style=style.get("formality", "neutral"),
                                         avatar_type=info.get("avatar_type", "friend"))
            new_list.append({"persona_id": pid, **info, "name": name})
        return new_list

    def _update_personas(self, user_id: str, entities: Dict):
        return [p for p in self.db.get_personas(user_id) if p["name"] in entities.get("persons", [])]

    # 8-10. 记忆相关 --------------------------------------------------------
    def _create_memories(self, user_id, log_id, text, entities, pad, temporal):
        topic = self._ask_json("用一个词概括主题并返回 {topic:""}" + text, {"topic": "日常对话"})["topic"]
        score = self._ask_json(
            f"对事件评分 0-1，返回 {{score:x}}\n文本:{text}\n实体:{json.dumps(entities, ensure_ascii=False)}", {"score": 0.5}
        )["score"]
        mid = self.db.create_memory_event(user_id, log_id, pad, topic,
                                          pad.get("emotion_category", {}).get("label", "neutral"),
                                          score, [], entities)
        return [{"memory_id": mid, "topic": topic, "importance_score": score, "entities": entities, "temporal": temporal}]

    # ------------------------------------------------------------------
    def _ensure_default_persona(self, user_id):
        for p in self.db.get_personas(user_id):
            if p["name"] == self.DEFAULT_PERSONA["name"]:
                return p["persona_id"]
        return self.db.create_persona(user_id=user_id, **self.DEFAULT_PERSONA)
    
    # 11. 获取历史和记忆 ────────────────────────────────────────────────────────────────────
    def _get_response_to_interaction(self, user_id: str, persona_id: str, text: str) -> Dict[str, Any]:
        """
        根据用户当前输入 text，结合历史日志、记忆和 persona 信息，
        调用 LLM 生成一条自然语言回复，并返回结构化结果。
        """

        # ------ 1. 选取对话 persona -------------------------------------
        personas = self.db.get_personas(user_id)
        if not personas:
            self._ensure_default_persona(user_id)
            personas = self.db.get_personas(user_id)
        else:
            # 如果指定了 persona_id，则寻找对应的 persona
            if persona_id:
                try:
                    speaker = next((p for p in personas if p["persona_id"] == persona_id), None)
                    if not speaker:
                        raise ValueError(f"未找到指定的 persona_id: {persona_id}")
                except Exception as e:
                    logger.error(f"获取 persona 失败: {e}")
                    speaker = None
            else:
                speaker = None
        # 默认：寻找名为“小助手”的 persona
        speaker = next((p for p in personas if p["name"] == self.DEFAULT_PERSONA["name"]), personas[0]) if not speaker else speaker

        # ------ 2. 准备历史上下文 --------------------------------------
        # 最近 5 条交互


        # ------ 3. 组装 LLM 消息 --------------------------------------
        persona_desc = (
            f"你是一位 {speaker['avatar_type']} 形象的 AI 助手，名字叫 {speaker['name']}。"
            f"你的性格特征：{', '.join(speaker['personality_traits'])}。"
            f"沟通风格：{speaker['communication_style']}。请保持一致的口吻。"
        )

        # system message
        messages = [
            {"role": "system", "content": persona_desc},
        ]
        
        recent_logs = self.db.get_interaction_logs(user_id, limit=5)
        logs_snippet = []
        for lg in reversed(recent_logs):         # 按时间正序
            human_txt = lg["raw_input_data"].get("text", "")
            emo = lg["emotion_label"]
            logs_snippet.append(f'[{emo}] 用户: {human_txt}')

        # 最近 3 条高重要度记忆
        memories = [m for m in self.db.get_memory_events(user_id, limit=20) 
                    if m["importance_score"] >= 0.7][:3]
        mem_snippet = []
        for m in memories:
            mem_snippet.append(f'记忆({m["linked_topic"]}): {m["entities"]}')

        # 可选：加入记忆
        if mem_snippet:
            messages.append({
                "role": "system",
                "content": "以下是与用户相关的关键记忆，请在合适时参考但不要直接复述：\n" + "\n".join(mem_snippet)
            })

        # 最近对话上下文
        if logs_snippet:
            messages.append({
                "role": "assistant",
                "content": "以下是最近几轮对话摘要：\n" + "\n".join(logs_snippet)
            })

        # 当前用户输入
        messages.append({"role": "user", "content": text})

        # ------ 4. 调用 LLM -------------------------------------------
        rsp = self.llm.chat(messages, temperature=0.7, max_tokens=1024)
        reply = rsp["content"].strip()

        # ------ 5. 落库 & 更新统计 ------------------------------------
        # ① 在最后一条 interaction_log 的 processing_metadata 里保存回复
        if recent_logs:
            last_log_id = recent_logs[0]["log_id"]
            self.db.save_assistant_reply(last_log_id, reply)       # ✨ 调用封装方法

        self.db.increment_persona_interaction(speaker["persona_id"])
        # ------ 6. 返回 -----------------------------------------------
        return {
            "reply": reply,
            "speaker_persona": {
                "persona_id": speaker["persona_id"],
                "name": speaker["name"],
                "avatar_type": speaker["avatar_type"]
            },
            "used_memories": [m["memory_id"] for m in memories],
            "llm_raw": rsp["raw_json"]  # 方便调试，可按需移除
        }
    # 12. 图像风格分析/时空信息/场景内容识别 ------------------------------------------------------------------
    def _analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        输入图片 URL → 返回一段连贯的中文描述：
            · 先点出拍摄场景与主体
            · 简要交代可能的时间/季节/地点
            · 概括色调、光线和情绪氛围
        """
        prompt = """你是一位专业的摄影评论与场景分析师。请结合视觉信息，尽可能详细的给出一段流畅的中文描述，覆盖以下要点但不要列条目：
1. 场景与主体
2. 场景可能的拍摄时段/季节/地点线索
3. 色彩与光线风格
4. 整体情绪或叙事氛围。
……
你可以根据图片内容自由发挥，但请确保描述连贯且富有表现力。
请注意：
    - 语言应当是口语化，同时进行详细的描述，避免使用过于专业的术语。
    - 语言风格应当自然流畅，适合普通读者阅读。
    - 务必写成完整段落，无需返回 JSON。"""

        image_base64 = base64.b64encode(open(image_path, 'rb').read()).decode('utf-8')
        image_format = image_path.split('.')[-1]
        if not image_base64:
            raise ValueError("图像Base64编码不能为空")
        if image_format in ["jpe", "jpg"]:
            image_format = "jpeg"
        elif image_format in ["tif", "tiff"]:
            image_format = "tiff"
        elif image_format not in ["bmp", "png", "webp", "heic"]:
            raise ValueError(f"不支持的图像格式: {image_format}")
        image_url = f"data:image/{image_format};base64,{image_base64}"
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt}
                ]
            },
        ]
        resp = self.llm.chat_with_image(messages, temperature=0.6, max_tokens=300)
        return resp["content"].strip()