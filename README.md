# finance-career-ai-agent
我的金融求职AI助手
# 🚀 金融求职一条龙 AI 助手

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

## 📌 项目简介

**金融求职一条龙 AI 助手**是一款专为金融行业求职者打造的智能辅助平台。无论你是准备进入投行、券商、基金、PE/VC 还是金融科技领域的应届生或职场人士，这款 AI 助手都能为你提供从简历优化、岗位匹配到模拟面试的全流程支持。

> 💡 **一句话介绍**：用 AI 的力量，让金融求职更高效、更精准、更自信。

## ✨ 核心功能

### 📄 简历智能优化
- 上传你的简历（PDF/Word），AI 自动解析并进行结构化分析
- 针对金融行业特点，提供专业的简历诊断与优化建议
- 智能评分系统，从内容完整性、专业性、关键词匹配度等多维度评估简历质量
- 一键生成优化后的简历，支持中英文双语版本

### 🎯 岗位精准匹配
- 基于你的简历内容和职业偏好，AI 智能匹配适合的金融岗位
- 支持按行业细分（投行、行研、量化、风控、财富管理等）进行筛选
- 实时展示匹配度评分，帮你快速锁定目标机会

### 🤖 AI 模拟面试
- 针对目标岗位自动生成定制化面试题库
- 涵盖行为面试（Behavioral）、技术面试（Technical）、案例面试（Case Study）三大模块
- 提供 AI 实时反馈与改进建议，助你从容应对真实面试

### 📊 求职进度追踪
- 一站式管理你的求职申请状态
- 可视化展示投递数量、面试邀约、Offer 进度等关键指标
- 支持添加备注与待办提醒，不再错过任何重要节点

### 💬 智能问答助手
- 7x24 小时在线的金融求职顾问
- 解答行业认知、职业规划、薪资谈判等各类求职疑问
- 知识库覆盖金融行业最新动态与求职趋势

## 🌐 在线访问

本应用已部署在以下两个地址，均可直接访问：

| 地址类型 | 访问链接 | 备注 |
|---------|---------|------|
| **主站（IP 直连）** | [http://47.120.30.125:8501/](http://47.120.30.125:8501/) | 自托管服务器 |
| **备用站（Streamlit Cloud）** | [https://finance-career-ai-agent-9yaqhed49yzftxdeceebq2.streamlit.app/](https://finance-career-ai-agent-9yaqhed49yzftxdeceebq2.streamlit.app/) | Streamlit 官方托管 |

> ⚠️ **注意**：两个地址均需启用 JavaScript 才能正常运行。如页面显示空白，请检查浏览器设置并确保 JavaScript 已开启。

## 🚀 快速上手

### 第一步：访问应用
点击上方任一访问链接，进入金融求职一条龙 AI 助手首页。

### 第二步：上传简历
在侧边栏或主界面找到「上传简历」区域，点击上传你的简历文件（支持 PDF、DOCX 格式）。AI 将在几秒内完成解析与分析。

### 第三步：查看分析报告
简历上传后，系统会自动生成一份详细的分析报告，包括：
- 综合评分
- 优势亮点
- 待改进项
- 优化建议

### 第四步：使用各功能模块
通过侧边栏导航菜单，你可以自由切换使用以下功能：
- 📝 **简历优化**：查看详细诊断报告，一键生成优化版简历
- 🔍 **岗位匹配**：浏览与你匹配的金融岗位，查看匹配度详情
- 🎤 **模拟面试**：选择目标岗位类型，开始 AI 模拟面试练习
- 📈 **进度看板**：管理你的求职进度，添加面试记录与备注
- 💬 **智能问答**：随时向 AI 求职顾问提问

## 🛠️ 技术架构

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **前端框架** | Streamlit | 快速构建数据驱动的 Web 应用 |
| **后端语言** | Python 3.9+ | 核心业务逻辑与 AI 调用 |
| **AI 引擎** | OpenAI API / Claude API / 国内大模型 | 简历分析、面试模拟、智能问答等核心 AI 能力 |
| **数据处理** | Pandas, PyPDF2, python-docx | 简历解析与数据清洗 |
| **部署方式** | Docker + Streamlit Cloud | 支持自托管与云端双部署 |

## 📁 项目结构
```text
finance-career-ai-agent/
├── app.py                    # Streamlit 主入口文件
├── pages/                    # 多页面模块
│   ├── 01_📄_简历优化.py
│   ├── 02_🎯_岗位匹配.py
│   ├── 03_🤖_模拟面试.py
│   ├── 04_📊_求职看板.py
│   └── 05_💬_智能问答.py
├── src/                      # 核心源码
│   ├── agents/               # AI Agent 模块
│   │   ├── resume_agent.py   # 简历分析智能体
│   │   ├── job_match_agent.py # 岗位匹配智能体
│   │   ├── interview_agent.py # 面试模拟智能体
│   │   └── qa_agent.py       # 问答智能体
│   ├── utils/                # 工具函数
│   │   ├── pdf_parser.py     # PDF 解析
│   │   ├── docx_parser.py    # Word 解析
│   │   └── prompts.py        # Prompt 模板管理
│   └── config.py             # 配置文件
├── data/                     # 数据存储目录
├── requirements.txt          # Python 依赖清单
├── Dockerfile                # Docker 镜像构建文件
└── README.md                 # 项目说明文档
