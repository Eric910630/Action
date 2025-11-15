"""
Agent基类
提供统一的Agent接口和基础功能
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from loguru import logger
from app.utils.deepseek import DeepSeekClient


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, model_name: str = "deepseek-chat", api_key: Optional[str] = None):
        """
        初始化Agent
        
        Args:
            model_name: 模型名称，默认deepseek-chat
            api_key: API密钥，如果为None则从配置读取
        """
        self.model_name = model_name
        self.llm_client = DeepSeekClient(api_key=api_key)
        self.tools = self._init_tools()
        self.agent = self._create_agent()
        logger.info(f"初始化Agent: {self.__class__.__name__}")
    
    @abstractmethod
    def _init_tools(self) -> List:
        """初始化Agent工具"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    def _create_agent(self):
        """
        创建LangChain Agent
        
        注意：由于当前LangChain版本可能不支持DeepSeek直接集成，
        这里先使用简化的实现，后续可以升级到支持DeepSeek的版本
        """
        try:
            # 尝试使用LangChain创建Agent
            from langchain.agents import create_agent
            from langchain.chat_models import init_chat_model
            
            # 注意：LangChain可能不支持deepseek模型，这里使用兼容方式
            # 实际使用时需要根据LangChain版本调整
            try:
                model = init_chat_model(f"openai:gpt-4")  # 临时使用，后续改为deepseek
            except:
                # 如果LangChain不支持，使用自定义包装
                model = self._create_custom_model()
            
            return create_agent(
                model,
                tools=self.tools,
                system_prompt=self._get_system_prompt()
            )
        except ImportError:
            logger.warning("LangChain未安装或版本不兼容，使用简化实现")
            return self._create_simple_agent()
        except Exception as e:
            logger.warning(f"创建LangChain Agent失败: {e}，使用简化实现")
            return self._create_simple_agent()
    
    def _create_custom_model(self):
        """创建自定义模型包装器（兼容DeepSeek）"""
        # 这里创建一个简单的包装器，将LangChain接口适配到DeepSeek
        class DeepSeekModelWrapper:
            def __init__(self, client):
                self.client = client
            
            def bind_tools(self, tools):
                return self
            
            def invoke(self, messages):
                # 转换消息格式并调用DeepSeek
                prompt = self._format_messages(messages)
                response = self.client.generate(prompt)
                return response
        
        return DeepSeekModelWrapper(self.llm_client)
    
    def _create_simple_agent(self):
        """创建简化版Agent（不依赖LangChain）"""
        class SimpleAgent:
            def __init__(self, llm_client, tools, system_prompt):
                self.llm_client = llm_client
                self.tools = tools
                self.system_prompt = system_prompt
            
            def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                """执行Agent任务"""
                messages = input_data.get("messages", [])
                user_message = messages[-1].get("content", "") if messages else ""
                
                # 构建完整提示词
                full_prompt = f"{self.system_prompt}\n\n用户请求: {user_message}"
                
                # 调用LLM
                response = self.llm_client.generate(
                    prompt=full_prompt,
                    system_prompt=self.system_prompt
                )
                
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": response.get("choices", [{}])[0].get("message", {}).get("content", "")
                    }]
                }
        
        return SimpleAgent(self.llm_client, self.tools, self._get_system_prompt())
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent任务
        
        Args:
            input_data: 输入数据字典
        
        Returns:
            执行结果字典
        """
        pass
    
    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        """格式化消息为提示词"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)

