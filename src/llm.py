import os
import json
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块
import requests

class LLM:
    def __init__(self, config):
        # 创建一个OpenAI客户端实例
        self.config = config

        self.model = config.llm_model_type.lower()
        if self.model == 'openai':
            key = os.getenv('OPEN_API_KEY', '') # 从环境变量中获取API密钥
            self.client = OpenAI(api_key=key,
                       base_url='https://api.bianxie.ai/v1')
        elif self.model == 'ollama':
            self.api_url = config.ollama_api_url
        else:
            raise ValueError(f"Unsupported model type: {self.model}")  # 如果模型类型不支持，抛出错误


    def load_prompt(self, prompt_file):
         # 从TXT文件加载提示信息
        with open(prompt_file, "r", encoding='utf-8') as file:
            self.system_prompt = file.read()


    def generate_daily_report(self, markdown_content, repo, dry_run=False):
        self.load_prompt(f"prompts/{repo}.txt")
        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt已保存到 daily_progress/prompt.txt")

            return "DRY RUN"
        
        if self.model == 'openai':
            return self.generate_report_openai(messages)
        elif self.model == 'ollama':
            return self.generate_report_ollama(messages)
        else:
            raise ValueError(f"Unsupported model type: {self.model}")

    def generate_report_openai(self, messages):
        """
        使用 OpenAI GPT 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info("使用 OpenAI GPT 模型开始生成报告。")
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model=self.config.openai_model_name,  # 指定使用的模型版本
                messages=messages
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error(f"生成报告时发生错误：{e}")
            raise
    def generate_report_ollama(self, messages):
        """
        使用 Ollama LLaMA 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info("使用 Ollama 托管模型服务开始生成报告。")
        try:
            payload = {
                "model": self.config.ollama_model_name,  # 使用配置中的Ollama模型名称
                "messages": messages,
                "stream": False
            }
            response = requests.post(self.api_url, json=payload)  # 发送POST请求到Ollama API
            response_data = response.json()
            
            # 调试输出查看完整的响应结构
            LOG.debug("Ollama response: {}", response_data)
            
            # 直接从响应数据中获取 content
            message_content = response_data.get("message", {}).get("content", None)
            if message_content:
                return message_content  # 返回生成的报告内容
            else:
                LOG.error("无法从响应中提取报告内容。")
                raise ValueError("Invalid response structure from Ollama API")
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise


