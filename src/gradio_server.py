import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器
import json

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径
    return report, report_file_path  # 返回报告内容和报告文件路径

def github_repo_remove(value):
    subscription_manager.remove_subscription(value)
    return json.dumps(subscription_manager.list_subscriptions()) 

def github_repo_additional(value):
    subscription_manager.add_subscription(value)
    return json.dumps(subscription_manager.list_subscriptions()) 

# 创建Gradio界面
with gr.Blocks() as demo:
    with gr.Tab("生成报告"):
        dropdown = gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        )
        slider = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")
        create_btn = gr.Button("生成报告")
        create_btn.click(fn=export_progress_by_date_range, inputs=[dropdown, slider], outputs=[gr.Markdown(), gr.File(label="下载报告")])
        pass
    with gr.Tab("订阅管理"):
        with gr.Column():
             name = gr.Textbox(label="添加订阅 repo")
             add_btn = gr.Button("添加订阅")
             add_btn.click(fn=github_repo_additional, inputs=name, outputs=gr.Markdown(), api_name="github_repo_additional")
        with gr.Column():
            name = gr.Textbox(label="移除订阅 repo")
            rem_btn = gr.Button("移除订阅")
            rem_btn.click(fn=github_repo_remove, inputs=name, outputs=gr.Markdown(), api_name="github_repo_remove")

if __name__ == "__main__":
     demo.launch()
    # second.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))