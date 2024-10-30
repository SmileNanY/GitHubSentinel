import requests
from bs4 import BeautifulSoup
from logger import LOG  # 导入日志模块
import os  # 导入os模块用于文件和目录操作
from datetime import datetime, date, timedelta  # 导入日期处理模块

class HackerNewsClient:
    def __init__(self):
        self.base_url = 'https://news.ycombinator.com/'
    def fetch_top_stories(self):
        LOG.debug(f"准备获取 Hacker news 的技术排行内容")
        response = requests.get(self.base_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找所有的标题和链接
            titles = soup.select('span.titleline a')
            # 提取标题和链接
            if titles:
                stories = []
                for title in titles:
                    stories.append({'title': title.text, 'link': {title["href"]}})
                LOG.debug(f"从 Hacker news 获取 技术排行内容成功")
                return stories
            else: 
              LOG.error(f"从 Hacker news 获取 技术排行内容为空")
              return []
        else:
            LOG.error(f"从 Hacker news 获取 技术排行内容 失败：{response.status_code}")
            return []
        
    def export_stories(self):
      today = date.today()  # 获取当前日期
      stories = self.fetch_top_stories()  # 获取指定日期范围内的更新
      repo_dir = os.path.join('daily_progress', 'hacker_news')  # 构建目录路径
      os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
      
      # 更新文件名以包含日期范围
      date_str = f"{today}"
      file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
      
      with open(file_path, 'w') as file:
          file.write(f"# Top Stories {today})\n\n")
          for content in stories:  # 写入在爬取的内容
              file.write(f"- {content['title']} #{content['link']}\n")
      
      LOG.info(f"Hacker news 项目最新热点文件生成： {file_path}")  # 记录日志
      return file_path