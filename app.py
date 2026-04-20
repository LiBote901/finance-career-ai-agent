import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import re

# ================= 尝试导入 PDF 解析库 =================
try:
    import PyPDF2

    HAS_PDF_READER = True
except ImportError:
    HAS_PDF_READER = False

# ================= 页面与 UI 配置 =================
st.set_page_config(page_title="金融求职一条龙助手", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

# ================= 全局动态背景与高级 CSS 样式 (Amalfi 尚雅轻玻璃风格 + GPU加速) =================
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">

    <div class="liquid-bg">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
    </div>

    <style>
    /* ================= 1. 背景与氛围 (柔沙杏 + 轻霓虹) ================= */
    .liquid-bg {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -999; 
        overflow: hidden;
        background: #F8F9FA; /* 温润的柔沙杏底色，高级非纯白 */
        pointer-events: none; 
    }

    .blob {
        position: absolute;
        filter: blur(150px); /* 极度虚化，形成柔和光晕 */
        opacity: 0.1; /* 极低透明度，若有若无的氛围感 */

        /* === 核心：强制开启 GPU 硬件加速，解决掉帧卡顿 === */
        will-change: transform; 
        -webkit-transform: translateZ(0);
        -moz-transform: translateZ(0);
        -ms-transform: translateZ(0);
        -o-transform: translateZ(0);
        transform: translateZ(0);
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        perspective: 1000px;

        animation: liquidFloat 35s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* 霓虹水青 */
    .blob-1 { width: 70vw; height: 70vw; background: #2DD4BF; top: -20vw; left: -10vw; }
    /* 霓虹紫 */
    .blob-2 { width: 60vw; height: 60vw; background: #A855F7; bottom: -15vw; right: -15vw; animation-delay: -12s; }
    /* 霓虹粉 */
    .blob-3 { width: 50vw; height: 50vw; background: #EC4899; top: 30vh; left: 30vw; animation-delay: -18s; animation-direction: alternate-reverse; }

    /* === 核心：使用 3D 转换来强制调用 GPU === */
    @keyframes liquidFloat {
        0% { transform: translate3d(0, 0, 0) rotate(0deg) scale(1); border-radius: 40% 60% 60% 40% / 50% 50% 50% 50%; }
        50% { transform: translate3d(3vw, 7vh, 0) rotate(180deg) scale(1.05); border-radius: 50% 50% 40% 60% / 60% 40% 50% 50%; }
        100% { transform: translate3d(-3vw, -5vh, 0) rotate(360deg) scale(0.95); border-radius: 60% 40% 50% 50% / 40% 60% 50% 50%; }
    }

    /* ================= 2. 全局字体与 Streamlit 原生组件覆写 (雅致高对比) ================= */
    .stApp { background-color: transparent !important; font-family: 'Inter', sans-serif; }

    /* 所有主标题为墨黛蓝，极具行政感 */
    h1, h2, h3, h4 { color: #1E293B !important; font-weight: 800; letter-spacing: -0.8px; text-shadow: none !important; }

    /* 所有基础正文文字为烟石蓝，清晰柔和 */
    p, span, label, .stMarkdown div, .stRadio label, .stFileUploader label, li { color: #475569 !important; }

    /* 数据指标 (Metric) 雅致化 */
    div[data-testid="metric-container"] label { color: #64748B !important; } /* 指标名称：灰蓝 */
    div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #020617 !important; font-weight: 800; } /* 指标数字：深黑蓝 */

    /* 侧边栏及顶部栏 */
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { 
        background: rgba(255, 255, 255, 0.6) !important; /* 轻磨砂纯白 */
        border-right: 1px solid rgba(226, 232, 240, 0.6) !important; 
        backdrop-filter: blur(25px) saturate(180%) !important; 
    }

    /* 覆写原生单选框颜色为雅致蓝 */
    div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] + div div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p { color: #1E293B !important; font-weight: 600; }
    div[data-testid="stRadio"] input[type="radio"]:checked + div { background-color: #0284C7 !important; } /* 选中的圆形 */
    div[data-testid="stRadio"] input[type="radio"] + div { border-color: #94A3B8 !important; } /* 未选中的圆形边框 */

    /* ================= 3. 玻璃态卡片系统 (温润行政版) ================= */
    .job-card, .details-box, .tip-panel, div[data-testid="metric-container"] { 
        background: rgba(255, 255, 255, 0.8) !important; /* 卡片底色：高透明度纯白 */
        border: 1px solid rgba(226, 232, 240, 0.7) !important; /* 极浅灰描边 */
        border-radius: 16px !important; 
        box-shadow: 0 4px 15px rgba(30, 41, 59, 0.03) !important; /* 极轻柔阴影 */
        backdrop-filter: blur(20px) saturate(180%) !important; 
        transition: all 0.3s ease; 
    }

    .job-card:hover { 
        transform: translateY(-4px); 
        background: rgba(255, 255, 255, 1.0) !important; /* 悬浮时完全不透明 */
        box-shadow: 0 10px 30px rgba(30, 41, 59, 0.08) !important; /* 阴影加深，体现悬浮 */
        border-color: rgba(226, 232, 240, 0.9) !important; 
    }

    .company-header { color: #0F172A !important; border-left: 6px solid #0284C7; padding-left: 14px; margin-top: 35px; margin-bottom: 18px; font-size: 24px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }

    /* ================= 4. 水粉色标签系统 (低饱和高清晰配色) ================= */
    .tag-group { margin: 12px 0; display: flex; flex-wrap: wrap; gap: 8px; }
    .tag { padding: 5px 12px; border-radius: 8px; font-size: 12px; font-weight: 700; letter-spacing: 0.3px; backdrop-filter: none; }

    /* 地点：水鸭蓝水粉 */
    .tag-loc { background-color: #E0F2FE; color: #075985; border: 1px solid #BAE6FD; }
    /* 薪资：茱萸粉水粉 */
    .tag-sal { background-color: #FCE7F3; color: #9D174D; border: 1px solid #FBCFE8; }
    /* HC：鼠尾草绿水粉 */
    .tag-hc { background-color: #E2E8F0; color: #334155; border: 1px solid #CBD5E1; }
    /* 留用：暖沙黄水粉 */
    .tag-ro { background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
    /* 学历：雾霾蓝水粉 */
    .tag-degree { background-color: #E0E7FF; color: #3730A3; border: 1px solid #C7D2FE; }
    /* 部门：钛银灰水粉 */
    .tag-dept { background-color: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }
    /* 毕业：胭脂红水粉 */
    .tag-exp { background-color: #FFE4E6; color: #9F1239; border: 1px solid #FECDD3; }
    /* 实习标签：幽暗虚线框 */
    .tag-intel { background-color: rgba(15, 23, 42, 0.04); color: #64748B; border: 1px dashed rgba(15, 23, 42, 0.15); font-style: italic;}

    /* ================= 5. 其他组件雅致覆写 ================= */
    /* 标记提示框 (st.info, st.success 等) */
    .stAlert div[data-testid="stMarkdownContainer"] p { color: #1E293B !important; font-weight: 600; }
    .stAlert { background-color: rgba(255, 255, 255, 0.7) !important; border: 1px solid rgba(226, 232, 240, 0.6) !important; color: #1E293B !important; border-radius: 12px; }

    /* 覆写 st.fileUploader 的原生样式 */
    [data-testid="stFileUploader"] section { background-color: rgba(255, 255, 255, 0.6) !important; border-radius: 12px; border: 1px dashed rgba(203, 213, 225, 0.6) !important; }
    [data-testid="stFileUploader"] section:hover { border-color: #0284C7 !important; background-color: rgba(255, 255, 255, 0.9) !important; }

    /* 语音输入按钮图标颜色强制墨蓝 */
    [data-testid="stAudioInput"] button svg path { fill: #1E293B !important; }

    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ================= 全局 API KEY 配置 =================
import os
API_KEY = os.environ.get("SILICONFLOW_API_KEY")
if not API_KEY:
    st.error("❌ 未检测到 API Key，请在 Streamlit Cloud 的 Secrets 中配置 SILICONFLOW_API_KEY。")
    st.stop()

# ================= 初始化状态引擎 =================
if 'target_role' not in st.session_state:
    st.session_state.target_role = None
if 'my_jobs' not in st.session_state:
    st.session_state.my_jobs = pd.DataFrame(columns=[
        "公司", "岗位", "赛道", "地点", "投递链接",
        "投递日期", "笔试日期", "面试日期", "当前状态", "简历得分", "笔试完成", "面试模拟完成"
    ])


# ================= 硅基流动 AI 评分函数 (简历诊断) =================
def evaluate_resume_with_ai(resume_text, target_role, job_name):
    url = "https://api.siliconflow.cn/v1/chat/completions"

    prompt = f"""
    # Role
    你是一位金融机构的招聘总监兼业务合伙人。

    # Task
    请对目标赛道为【{target_role}】、岗位为【{job_name}】的候选人简历进行深度诊断。

    # Evaluation Rubric (满分100分，85分及格)
    1. 经历含金量与对口度 (40%)
    2. 业绩量化与 STAR 法则 (30%)
    3. 技能栈与关键词匹配 (30%)

    # Format Requirement
    1. 必须在回复的第一行严格按此格式输出：【得分：XX】（XX为纯数字）。
    2. 从第二行开始，输出整段的专业点评（避免列点）：总结优势，指出不足，给出具体的修改意见,并把修改后的简历给我。

    【简历文本】：
    {resume_text[:2000]}
    """

    payload = {"model": "Pro/deepseek-ai/DeepSeek-V3.2", "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.6}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_json = response.json()
        full_content = res_json['choices'][0]['message']['content']

        think_match = re.search(r'<think>(.*?)</think>', full_content, re.DOTALL)
        if think_match:
            thinking_process = think_match.group(1).strip()
            final_answer = full_content.replace(think_match.group(0), '').strip()
        else:
            thinking_process = "（模型直接输出，无推理过程）"
            final_answer = full_content.strip()

        score_match = re.search(r'【得分：(\d+)】', final_answer)
        score = int(score_match.group(1)) if score_match else 75
        return score, final_answer, thinking_process
    except Exception as e:
        return 70, f"API 调用失败。请检查网络。错误: {e}", ""


# ================= 基于真实招聘信息的岗位数据库（大幅扩充版）=================
@st.cache_data
def generate_job_database():
    today = datetime.now()
    jobs = []

    # ---------- 赛道1：券商/投行（扩充至20+） ----------

    # 1. 中金公司 (CICC)
    cicc_departments = ["投资银行", "股票业务", "固定收益", "私募股权", "资产管理", "财富管理", "研究业务"]
    cicc_locations = ["📍北京", "📍上海", "📍深圳", "📍香港"]
    cicc_degree_reqs = ["硕士及以上", "金融/经济/理工复合背景优先", "CPA/CFA优先", "Wind/Bloomberg熟练"]
    cicc_remote_tags = ["👀 每周≥4天", "👀 核心项目参与", "👀 可转正留用", "👀 导师带教", "👀 轮岗机会", "👀 国际化团队"]
    for dept in cicc_departments:
        loc = random.choice(cicc_locations)
        exam_date = today + timedelta(days=random.randint(7, 45))
        jobs.append({
            "公司": "中金公司 (CICC)",
            "岗位": f"暑期实习 - {dept}",
            "赛道": "券商/投行",
            "地点": loc,
            "薪资": f"¥{random.randint(250, 450)}/天" if "香港" not in loc else f"HK${random.randint(600, 1200)}/天",
            "HC数量": f"HC: {random.randint(3, 12)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 答辩通过可转正" if random.random() > 0.3 else "⚠️ 名额有限",
            "学历要求": random.sample(cicc_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["财务建模", "估值分析", "尽职调查经验", "熟练使用Excel/Python", "英语流利"][
                :random.randint(3, 5)],
            "实习标签": random.sample(cicc_remote_tags, k=random.randint(3, 5)),
            "部门": dept,
            "毕业时间要求": "2026.09-2027.08",
            "部门介绍": f"中金公司{dept}部门，国内顶尖投行核心业务线。该部门通过发股、发债或兼并收购等方式帮助客户融资，是应届生竞争最激烈的部门之一。" if dept == "投资银行" else f"中金公司{dept}部门，负责相关领域的专业服务与产品设计。",
            "具体职责": f"协助{dept}团队进行行业研究、财务分析、项目执行与客户沟通；参与项目尽职调查与材料准备；完成团队分配的其他工作。",
            "福利待遇": "七险二金，顶配办公设备，项目奖金，餐补交通补，年度体检，带薪年假",
            "投递链接": "http://cicc.zhiye.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 2. 华泰证券
    ht_departments = ["财富管理与机构业务", "投资银行", "固定收益", "研究业务", "金融科技"]
    ht_locations = ["📍南京", "📍上海", "📍北京", "📍深圳", "📍广州", "📍杭州", "成都武汉"]
    ht_degree_reqs = ["本科及以上", "经济金融/营销管理/理工类", "复合背景优先", "证券从业资格优先"]
    ht_remote_tags = ["👀 覆盖全国30+城市", "👀 科技驱动", "👀 综合券商第一方阵", "👀 导师制", "👀 暑期实习优先秋招",
                      "👀 滚动招聘"]
    for dept in ht_departments:
        loc = random.choice(ht_locations)
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "华泰证券",
            "岗位": f"{'暑期实习' if random.random() > 0.5 else '春季校招'} - {dept}",
            "赛道": "券商/投行",
            "地点": loc,
            "薪资": "¥8K-10K/月",
            "HC数量": f"HC: {random.randint(5, 20)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 实习考察通过录用",
            "学历要求": random.sample(ht_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["客户服务意识", "金融产品知识", "数据分析能力", "沟通表达", "抗压能力"][:random.randint(3, 5)],
            "实习标签": random.sample(ht_remote_tags, k=random.randint(3, 5)),
            "部门": dept,
            "毕业时间要求": "2026.01-2026.07 (校招) / 2027.01-2027.07 (暑期)",
            "部门介绍": f"华泰证券{dept}部门，公司核心业务线。华泰证券是国内领先的科技驱动型综合证券集团，综合实力位居国内证券业第一方阵。",
            "具体职责": f"协助{dept}相关业务开展，包括客户服务、产品分析、市场研究等；参与团队项目执行与日常运营；完成导师安排的其他工作。",
            "福利待遇": "月薪8K-10K，五险一金，补充医疗，餐补交通补，节日福利，员工培训",
            "投递链接": "https://www.htsc.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 3. 中信证券
    citics_departments = ["投资银行", "研究部", "固定收益", "资产管理", "财富管理", "股权衍生品"]
    citics_locations = ["📍北京", "📍上海", "📍深圳", "📍香港"]
    citics_degree_reqs = ["硕士及以上", "金融/经济/会计/法律", "理工科+金融复合背景", "CPA/CFA/法律职业资格优先"]
    citics_remote_tags = ["👀 头部券商", "👀 系统培训", "👀 项目制工作", "👀 留用比例高", "👀 导师制", "👀 出差机会"]
    for dept in citics_departments[:4]:
        loc = random.choice(citics_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "中信证券",
            "岗位": f"暑期实习 - {dept}",
            "赛道": "券商/投行",
            "地点": loc,
            "薪资": f"¥{random.randint(200, 400)}/天" if "香港" not in loc else f"HK${random.randint(500, 1000)}/天",
            "HC数量": f"HC: {random.randint(5, 15)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 答辩通过可转正",
            "学历要求": random.sample(citics_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["财务分析", "估值建模", "行业研究", "Excel/PPT", "英语流利"][:random.randint(3, 5)],
            "实习标签": random.sample(citics_remote_tags, k=random.randint(3, 5)),
            "部门": dept,
            "毕业时间要求": "2026.09-2027.08",
            "部门介绍": f"中信证券{dept}，国内头部券商核心部门。中信证券是‘三中一华’之一，业务规模与市场地位领先。",
            "具体职责": f"协助{dept}团队完成项目执行、行业分析、尽职调查、材料撰写等工作；参与客户沟通与项目协调。",
            "福利待遇": "行业领先薪资，七险二金，补充公积金，员工宿舍/房补，年度体检，团建活动",
            "投递链接": "https://www.citics.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 4. 摩根士丹利证券（外资投行）
    ms_locations = ["📍上海", "📍北京"]
    exam_date = today + timedelta(days=random.randint(15, 50))
    jobs.append({
        "公司": "摩根士丹利证券",
        "岗位": "2026 Summer Analyst - 投资银行部",
        "赛道": "券商/投行",
        "地点": random.choice(ms_locations),
        "薪资": "¥400-600/天",
        "HC数量": f"HC: {random.randint(3, 8)}人",
        "面试轮数": "面试: 3-4轮",
        "留用机会": "✅ 有机会成为全职分析师",
        "学历要求": ["专业不限", "英语流利", "成绩优异"],
        "能力要求": ["财务建模", "尽职调查", "沟通协作", "主观能动性", "领导才能"],
        "实习标签": ["👀 10周实习项目", "👀 全球网络资源", "👀 正式录用机会", "👀 培训+软实力"],
        "部门": "投资银行部",
        "毕业时间要求": "2026.10-2027.07",
        "部门介绍": "摩根士丹利证券（中国）是摩根士丹利设立于中国的证券经营机构，为国内外客户提供业内领先的投资银行等金融服务，业务范围包括股票和债券的承销与保荐、证券自营等。",
        "具体职责": "参与IPO、并购等投行项目执行；进行行业研究与财务分析；协助准备项目建议书与尽职调查材料。",
        "福利待遇": "具有竞争力的实习薪酬，完善的培训体系，参与真实项目机会，表现优异者可获得全职Offer",
        "投递链接": "https://www.morganstanleychina.com",
        "笔试日期": exam_date.strftime("%Y-%m-%d"),
        "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
    })

    # 5. 国联民生证券
    glms_directions = ["投资研究类", "投资银行类", "财富管理类", "AI&金融科技类", "运营支持类"]
    glms_locations = ["📍上海", "📍北京", "📍深圳", "📍南京", "📍广州", "📍无锡"]
    for direction in glms_directions:
        loc = random.choice(glms_locations)
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "国联民生证券",
            "岗位": f"暑期实习 - {direction}",
            "赛道": "券商/投行",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(3, 12)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 正式录用机会",
            "学历要求": ["硕士及以上", "2027届及以后毕业", "复合专业背景优先"],
            "能力要求": ["行业研究", "数据分析", "沟通协作", "创新思维"][:random.randint(2, 4)],
            "实习标签": ["👀 项目实践", "👀 资深导师", "👀 业务培训", "👀 职业指导"],
            "部门": direction,
            "毕业时间要求": "2027届及以后",
            "部门介绍": f"国联民生证券股份有限公司创立于1992年，2015年港股上市，2020年A股上市。公司主体信用评级连续多年保持AAA级，拥有7家子公司，证券金融控股集团构架初具。",
            "具体职责": f"参与{direction}相关项目实践，在导师指导下完成业务研究与执行；参与团队日常运营与客户沟通。",
            "福利待遇": "项目实践机会，资深导师带教，业务培训，职业指导，表现优异可转正",
            "投递链接": "https://www.glsc.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 6. 招商证券
    cmb_departments = ["投资银行类", "研究类", "固定收益类", "资产管理类"]
    cmb_locs = ["📍深圳", "📍北京", "📍上海", "📍广州", "📍杭州", "📍南京", "📍武汉", "📍成都"]
    for dept in cmb_departments:
        loc = random.choice(cmb_locs)
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "招商证券",
            "岗位": f"暑期实习 - {dept}",
            "赛道": "券商/投行",
            "地点": loc,
            "薪资": "¥200-400/天",
            "HC数量": f"HC: {random.randint(4, 15)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": ["硕士及以上", "金融/经济/会计/法律", "理工复合背景优先"],
            "能力要求": ["投行业务", "行业研究", "财务分析", "尽职调查"][:random.randint(2, 4)],
            "实习标签": ["👀 央企平台", "👀 可同时投递3岗", "👀 导师制", "👀 轮岗机会"],
            "部门": dept,
            "毕业时间要求": "2027届应届生",
            "部门介绍": f"招商证券是招商局集团旗下的证券公司，综合实力位居行业前列，{dept}部门为公司核心业务板块。",
            "具体职责": f"协助{dept}团队完成项目承做、行业研究、数据分析等工作；参与尽职调查与材料撰写。",
            "福利待遇": "央企平台，完善培训，导师带教，实习补贴，留用机会",
            "投递链接": "https://cms.cmschina.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 7. 国泰君安期货
    gtj_directions = ["量化交易", "投研", "运营创新", "场外衍生品"]
    for direction in gtj_directions[:3]:
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "国泰君安期货",
            "岗位": f"金衍新星计划 - {direction}方向",
            "赛道": "券商/投行",
            "地点": "📍上海",
            "薪资": "¥250-400/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 有留用机会",
            "学历要求": ["硕士及以上", "计算机/金融工程/数学", "2026届应届生"],
            "能力要求": ["C++", "量化策略", "金融衍生品", "数据分析"][:random.randint(2, 4)],
            "实习标签": ["👀 专项培养", "👀 策略总监方向", "👀 实战项目", "👀 导师制"],
            "部门": direction,
            "毕业时间要求": "2026届应届生",
            "部门介绍": "国泰君安期货是国泰君安证券的全资子公司，注册资本40亿元，是国内期货行业领先企业。",
            "具体职责": f"参与{direction}相关业务实践，协助策略开发与维护、数据分析、市场研究等工作。",
            "福利待遇": "具有竞争力的实习薪资，完善的培养体系，实战项目经验，留用机会",
            "投递链接": "https://www.gtja.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 8. 海通证券/国泰海通
    ht_dirs = ["投行业务", "研究业务", "财富管理"]
    for direction in ht_dirs:
        exam_date = today + timedelta(days=random.randint(10, 45))
        jobs.append({
            "公司": "国泰海通证券",
            "岗位": f"2026届校招 - {direction}",
            "赛道": "券商/投行",
            "地点": random.choice(["📍上海", "📍北京", "📍深圳"]),
            "薪资": "面议（行业竞争力）",
            "HC数量": f"HC: {random.randint(5, 15)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 通过考核可录用",
            "学历要求": ["硕士及以上", "2026届毕业生", "相关专业背景"],
            "能力要求": ["投行实务", "研究分析", "沟通协作"][:random.randint(2, 3)],
            "实习标签": ["👀 头部券商", "👀 系统培养", "👀 导师带教", "👀 留用机会"],
            "部门": direction,
            "毕业时间要求": "2026.01-2026.07",
            "部门介绍": "国泰海通证券是合并后的头部券商，综合实力位居行业前列，业务覆盖投行、研究、资管等全领域。",
            "具体职责": f"协助{direction}团队进行业务执行、数据分析、客户沟通等工作。",
            "福利待遇": "行业竞争力薪酬，完善福利，培训体系，职业发展通道",
            "投递链接": "https://www.htsc.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 9. 广发证券
    gf_directions = ["投行业务", "研究业务", "财富管理", "金融科技"]
    for direction in gf_directions[:3]:
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "广发证券",
            "岗位": f"广培之星暑期训练营 - {direction}",
            "赛道": "券商/投行",
            "地点": random.choice(["📍广州", "📍深圳", "📍上海", "📍北京"]),
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(5, 20)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 训练营表现优异可转正",
            "学历要求": ["本科及以上", "2026年及以后毕业", "相关专业背景"],
            "能力要求": ["数据分析", "行业研究", "客户服务", "沟通能力"][:random.randint(2, 4)],
            "实习标签": ["👀 广培之星", "👀 导师制", "👀 内推优先", "👀 系统培训"],
            "部门": direction,
            "毕业时间要求": "2026届及以后",
            "部门介绍": "广发证券成立于1991年，是国内首批综合类证券公司，先后在深交所及港交所上市。",
            "具体职责": f"参与{direction}业务实践，协助项目执行、数据分析、客户服务等工作。",
            "福利待遇": "系统培训，导师带教，实习补贴，表现优异可转正",
            "投递链接": "https://www.gf.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 10. 兴业证券
    xy_directions = ["投资银行业务", "研究业务", "固定收益", "财富管理"]
    for direction in xy_directions[:3]:
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "兴业证券",
            "岗位": f"暑期实习 - {direction}",
            "赛道": "券商/投行",
            "地点": random.choice(["📍上海", "📍北京", "📍深圳", "📍福州"]),
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(3, 12)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": ["硕士及以上", "金融/经济/理工", "复合背景优先"],
            "能力要求": ["投行实务", "财务分析", "行业研究", "沟通能力"][:random.randint(2, 4)],
            "实习标签": ["👀 头部券商", "👀 系统培训", "👀 项目实战", "👀 导师带教"],
            "部门": direction,
            "毕业时间要求": "2026届及以后",
            "部门介绍": "兴业证券是中国证监会核准的全国性、综合类、创新型、集团化、国际化证券公司，成立于1991年。",
            "具体职责": f"协助{direction}团队完成项目承做、行业分析、尽职调查等工作。",
            "福利待遇": "系统培训，项目实战经验，导师带教，实习补贴，留用机会",
            "投递链接": "https://www.xyzq.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 11. 中信建投证券
    zxjt_directions = ["投行业务", "证券研究", "资产管理", "财富管理"]
    for direction in zxjt_directions[:3]:
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "中信建投证券",
            "岗位": f"暑期实习 - {direction}",
            "赛道": "券商/投行",
            "地点": random.choice(["📍北京", "📍上海", "📍深圳", "📍广州"]),
            "薪资": "¥200-400/天",
            "HC数量": f"HC: {random.randint(4, 15)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 通过考核可录用",
            "学历要求": ["硕士及以上", "金融/经济/法律", "理工复合背景优先"],
            "能力要求": ["投行业务", "行业研究", "财务分析", "尽职调查"][:random.randint(2, 4)],
            "实习标签": ["👀 头部券商", "👀 远程/线下", "👀 导师制", "👀 留用机会"],
            "部门": direction,
            "毕业时间要求": "2026届应届生",
            "部门介绍": "中信建投证券是国内头部综合性券商，投行、研究、资管等业务均位居行业前列。",
            "具体职责": f"协助{direction}团队完成项目执行、行业研究、数据分析等工作。",
            "福利待遇": "行业竞争力薪酬，完善培训，导师带教，表现优异可转正",
            "投递链接": "https://www.csc108.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 12. 申万宏源证券
    swhy_directions = ["投行业务", "研究业务", "财富管理", "金融科技"]
    for direction in swhy_directions[:3]:
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "申万宏源证券",
            "岗位": f"新申力计划 - {direction}",
            "赛道": "券商/投行",
            "地点": random.choice(["📍上海", "📍北京", "📍深圳", "📍天津"]),
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(4, 15)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 校招提前批",
            "学历要求": ["硕士及以上", "2026届应届生", "相关专业背景"],
            "能力要求": ["行业研究", "数据分析", "沟通协作", "创新思维"][:random.randint(2, 4)],
            "实习标签": ["👀 新申力计划", "👀 覆盖100+城市", "👀 校招提前批", "👀 导师制"],
            "部门": direction,
            "毕业时间要求": "2026届应届生",
            "部门介绍": "申万宏源证券是由申银万国证券和宏源证券合并组建的大型综合性券商，注册资本520亿元。",
            "具体职责": f"参与{direction}相关业务实践，协助完成项目执行、研究分析、客户服务等工作。",
            "福利待遇": "系统培训，导师带教，实习补贴，表现优异可获校招提前批Offer",
            "投递链接": "https://www.swhysc.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # ---------- 赛道2：行研岗（扩充至20+） ----------

    # 1. 易方达基金
    efunds_positions = ["行业研究员", "多资产研究员", "宏观研究员", "策略研究员", "信用研究员", "量化研究员",
                        "ESG研究员"]
    efunds_locations = ["📍北京", "📍上海", "📍广州", "📍深圳", "📍香港", "珠海横琴"]
    efunds_degree_reqs = ["硕士及以上", "金融/经济/理工复合", "CFA/CPA优先", "Wind熟练", "Python/SQL优先"]
    efunds_remote_tags = ["👀 实习期1个月", "👀 实习时间可协商", "👀 管理规模超4.1万亿", "👀 平台型机构", "👀 滚动实习考察",
                          "👀 5月开始"]
    for pos in efunds_positions:
        loc = random.choice(efunds_locations)
        exam_date = today + timedelta(days=random.randint(5, 30))
        jobs.append({
            "公司": "易方达基金",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": f"¥{random.randint(200, 350)}/天" if "香港" not in loc else f"HK${random.randint(500, 1000)}/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 实习面试考察通过后发放正式留用offer",
            "学历要求": random.sample(efunds_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["深度报告撰写", "财务分析", "数据处理", "行业洞察", "逻辑思维"][:random.randint(3, 5)],
            "实习标签": random.sample(efunds_remote_tags, k=random.randint(3, 5)),
            "部门": "投研类",
            "毕业时间要求": "2026.09-2027.08",
            "部门介绍": f"易方达基金投研团队，截至2025年底管理资产规模超4.1万亿元。公司秉承规范、稳健、开放的经营理念，以资产管理和财富管理双轮驱动。",
            "具体职责": f"协助研究员进行行业数据收集分析、公司基本面研究、财务模型搭建；撰写研究报告投资建议；参与投研团队讨论。",
            "福利待遇": "五险一金，企业年金，补充医疗，餐补交通补，员工基金投资优惠，年度体检，带薪年假",
            "投递链接": "https://job.efunds.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 2. 华夏基金
    chinaamc_positions = ["行业研究员", "信用研究员", "转债研究员", "多资产研究员", "量化研究员", "指数研究员",
                          "资产配置研究员"]
    chinaamc_locations = ["📍北京", "📍上海", "📍香港", "📍杭州", "📍济南"]
    chinaamc_degree_reqs = ["硕士及以上", "金融/经济/理工复合", "CFA/CPA优先", "编程能力优先"]
    chinaamc_remote_tags = ["👀 管理资产超3.2万亿", "👀 28年投资经验", "👀 金牛奖80座", "👀 最多申请2个岗位", "👀 通用笔试",
                            "👀 4月26截止"]
    for pos in chinaamc_positions[:5]:
        loc = random.choice(chinaamc_locations)
        exam_date = today + timedelta(days=random.randint(5, 35))
        jobs.append({
            "公司": "华夏基金",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": f"¥{random.randint(180, 350)}/天" if "香港" not in loc else f"HK${random.randint(500, 1000)}/天",
            "HC数量": f"HC: {random.randint(2, 10)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 实习考察通过可转正",
            "学历要求": random.sample(chinaamc_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["财务分析", "估值建模", "行业研究", "Excel/PPT", "逻辑表达"][:random.randint(3, 5)],
            "实习标签": random.sample(chinaamc_remote_tags, k=random.randint(3, 5)),
            "部门": "投研类",
            "毕业时间要求": "2026.09-2027.08",
            "部门介绍": f"华夏基金是中国管理资产规模最大的基金管理公司之一，累计服务个人投资者超2.5亿人。公司拥有28年投资管理经验，累计荣获金牛奖80座。",
            "具体职责": f"协助研究员进行行业跟踪、公司分析、数据整理；撰写研究报告；参与投资策略讨论。",
            "福利待遇": "行业竞争力薪资，五险一金，企业年金，补充医疗，员工基金投资优惠，年度体检",
            "投递链接": "http://chinamc.zhiye.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 3. 天弘基金（新增）
    thfund_positions = ["行业研究员", "债券交易员", "互金业务经理", "产品经理", "机构销售", "渠道销售", "金融工程岗"]
    thfund_locations = ["📍北京", "📍上海", "📍广州", "📍深圳", "📍成都"]
    thfund_degree_reqs = ["硕士及以上", "理工科背景优先", "2027届应届毕业生", "经济金融相关专业"]
    thfund_remote_tags = ["👀 余额宝管理人", "👀 资管规模超1.2万亿", "👀 表现优秀可留用", "👀 5月5日截止", "👀 公募基金前列"]
    for pos in thfund_positions:
        loc = random.choice(thfund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "天弘基金",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(3, 10)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀者将有机会获得正式留用offer",
            "学历要求": random.sample(thfund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "数据分析", "逻辑思维", "沟通协作", "抗压能力"][:random.randint(3, 5)],
            "实习标签": random.sample(thfund_remote_tags, k=random.randint(3, 5)),
            "部门": "投研/业务部门",
            "毕业时间要求": "2026.09-2027.08",
            "部门介绍": f"天弘基金成立于2004年，注册资本5.143亿元。2013年与支付宝合作推出余额宝，截至2025年12月31日，资产管理总规模12,759.41亿元，公募基金管理规模12,542.23亿元。",
            "具体职责": f"深入行业研究、数据收集分析、撰写研究报告；协助基金经理进行资产配置建议与投资决策支持。",
            "福利待遇": "五险一金，补充医疗，餐补交通补，员工培训，节日福利",
            "投递链接": "https://app.mokahr.com/campus-recruitment/thfund",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 4. 嘉实基金（新增）
    jsfund_positions = ["行业研究员", "固收研究员", "量化研究员", "养老金产品", "互金营销"]
    jsfund_locations = ["📍北京", "📍上海", "📍深圳"]
    jsfund_degree_reqs = ["硕士及以上", "经济金融/理工复合", "博士优先", "CPA/CFA优先"]
    jsfund_remote_tags = ["👀 年度实习项目", "👀 表现优异提前录用", "👀 导师制", "👀 首批规范基金公司"]
    for pos in jsfund_positions[:4]:
        loc = random.choice(jsfund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "嘉实基金",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-400/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 实习期间表现优异者会提前获得正式录用offer",
            "学历要求": random.sample(jsfund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业分析", "财务建模", "数据处理", "研究报告撰写"][:random.randint(2, 4)],
            "实习标签": random.sample(jsfund_remote_tags, k=random.randint(3, 4)),
            "部门": "投研/产品",
            "毕业时间要求": "2027届硕博在校生",
            "部门介绍": "嘉实基金是国内最早成立的10家基金管理公司之一，行业地位名列前茅，以专业稳健著称。",
            "具体职责": f"协助研究员进行行业与公司研究，参与投资策略讨论与报告撰写。",
            "福利待遇": "行业竞争力薪资，五险一金，企业年金，补充医疗，员工培训",
            "投递链接": "https://www.jsfund.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 5. 南方基金（新增）
    nffund_positions = ["行业研究员", "产品开发岗", "机构销售岗", "交易员（量化方向）", "风险绩效管理"]
    nffund_locations = ["📍深圳", "📍北京", "📍上海", "📍合肥"]
    nffund_degree_reqs = ["硕士及以上", "数理/经济/金融", "复合背景优先", "海外院校优先"]
    nffund_remote_tags = ["👀 首批规范基金公司", "👀 1998年成立", "👀 总部深圳", "👀 27届暑期实习"]
    for pos in nffund_positions[:4]:
        loc = random.choice(nffund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "南方基金",
            "岗位": f"2027届暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(3, 10)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": random.sample(nffund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "金融产品知识", "数据分析", "沟通协作"][:random.randint(2, 4)],
            "实习标签": random.sample(nffund_remote_tags, k=random.randint(3, 4)),
            "部门": "投研/产品/市场",
            "毕业时间要求": "2027届应届生",
            "部门介绍": "南方基金管理股份有限公司成立于1998年3月6日，是国内首批规范的基金管理公司，我国‘新基金时代’的起始标志，总部位于深圳。",
            "具体职责": f"参与{pos}相关工作，协助业务执行、数据分析、客户服务等。",
            "福利待遇": "系统培训，导师带教，实习补贴，表现优秀可留用",
            "投递链接": "https://www.nffund.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 6. 博时基金（新增）
    bsfund_positions = ["行业研究员", "固定收益研究员", "公募REITs承做", "机构销售"]
    bsfund_locations = ["📍深圳", "📍北京", "📍上海", "📍南京"]
    bsfund_degree_reqs = ["硕士及以上", "金融/经济/统计/管理", "985/211优先", "Wind熟练"]
    bsfund_remote_tags = ["👀 老牌基金公司", "👀 北京/深圳/上海面试", "👀 春季校招", "👀 系统培训"]
    for pos in bsfund_positions[:3]:
        loc = random.choice(bsfund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "博时基金",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 有留用机会",
            "学历要求": random.sample(bsfund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "数据分析", "报告撰写", "沟通能力"][:random.randint(2, 4)],
            "实习标签": random.sample(bsfund_remote_tags, k=random.randint(3, 4)),
            "部门": "投研/业务",
            "毕业时间要求": "2027届应届生",
            "部门介绍": "博时基金是国内首批成立的五家基金管理公司之一，综合实力长期位居行业前列。",
            "具体职责": f"协助{pos}相关工作，包括行业分析、数据整理、材料制作等。",
            "福利待遇": "五险一金，补充医疗，餐补交通补，员工培训",
            "投递链接": "https://www.bosera.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 7. 富国基金（新增）
    fgfund_positions = ["行业研究员", "机构销售", "电子商务", "营销策划"]
    fgfund_locations = ["📍上海", "📍北京", "📍香港"]
    fgfund_degree_reqs = ["硕士及以上", "经济金融/计算机", "经管类专业", "985高校优先"]
    fgfund_remote_tags = ["👀 完善培训", "👀 留用机会", "👀 机构条线", "👀 暑期管培"]
    for pos in fgfund_positions[:3]:
        loc = random.choice(fgfund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "富国基金",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 提供留用机会",
            "学历要求": random.sample(fgfund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["研究分析", "市场洞察", "沟通协作", "内容策划"][:random.randint(2, 4)],
            "实习标签": random.sample(fgfund_remote_tags, k=random.randint(3, 4)),
            "部门": "投研/市场",
            "毕业时间要求": "2026或2027年毕业",
            "部门介绍": "富国基金成立于1999年，是国内首批十家基金管理公司之一，综合实力位居行业前列。",
            "具体职责": f"参与{pos}相关业务，协助完成市场分析、客户服务、产品运营等工作。",
            "福利待遇": "系统培训，导师带教，实习补贴，表现优秀可留用",
            "投递链接": "https://www.fullgoal.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 8. 广发基金（新增）
    gffund_positions = ["行业研究员", "产品研究助理", "养老金研究", "互金运营策划"]
    gffund_locations = ["📍广州", "📍北京", "📍上海"]
    gffund_degree_reqs = ["硕士及以上", "金融/经济/统计", "计算机/数学", "复合背景优先"]
    gffund_remote_tags = ["👀 4月26日截止", "👀 暑期实习", "👀 广发系基金", "👀 多地base"]
    for pos in gffund_positions[:3]:
        loc = random.choice(gffund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "广发基金",
            "岗位": f"2026暑期实习 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": random.sample(gffund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "数据分析", "编程能力", "报告撰写"][:random.randint(2, 4)],
            "实习标签": random.sample(gffund_remote_tags, k=random.randint(3, 4)),
            "部门": "投研/产品",
            "毕业时间要求": "2027届应届生",
            "部门介绍": "广发基金管理有限公司成立于2003年，是广发证券控股子公司，公募基金管理规模位居行业前列。",
            "具体职责": f"协助{pos}相关工作，包括行业分析、数据处理、材料制作等。",
            "福利待遇": "五险一金，补充医疗，餐补交通补，员工培训",
            "投递链接": "https://www.gffunds.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 9. 工银瑞信（新增）
    gyfx_positions = ["行业研究员", "量化研究", "固定收益研究"]
    gyfx_locations = ["📍北京", "📍上海"]
    gyfx_degree_reqs = ["硕士及以上", "金融/经济/理工", "数理背景优先"]
    gyfx_remote_tags = ["👀 工行系基金", "👀 春季校招", "👀 4月中旬笔试", "👀 5月签约"]
    for pos in gyfx_positions[:3]:
        loc = random.choice(gyfx_locations)
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "工银瑞信",
            "岗位": f"2026春季校招 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(2, 10)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 实习考察后可签约",
            "学历要求": random.sample(gyfx_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "量化分析", "财务建模", "Python/R"][:random.randint(2, 4)],
            "实习标签": random.sample(gyfx_remote_tags, k=random.randint(3, 4)),
            "部门": "投研",
            "毕业时间要求": "2026届应届生",
            "部门介绍": "工银瑞信基金管理有限公司是中国工商银行控股的基金管理公司，成立于2005年，是国内首家银行系基金公司。",
            "具体职责": f"协助研究员进行行业与公司研究，参与量化策略开发、数据分析与报告撰写。",
            "福利待遇": "银行系基金，福利完善，系统培训，导师带教，留用机会",
            "投递链接": "https://www.icbccs.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 10. 汇添富基金（新增）
    htf_positions = ["助理行业分析师", "固定收益助理分析师", "助理量化分析师", "助理指数分析师"]
    htf_locations = ["📍上海"]
    htf_degree_reqs = ["硕士及以上", "金融/经济/理工", "2026应届毕业生"]
    htf_remote_tags = ["👀 添才计划", "👀 投研暑期选拔", "👀 一流资管", "👀 2005年成立"]
    for pos in htf_positions[:3]:
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "汇添富基金",
            "岗位": f"投研暑期选拔 - {pos}",
            "赛道": "行研岗",
            "地点": random.choice(htf_locations),
            "薪资": "¥250-400/天",
            "HC数量": f"HC: {random.randint(2, 6)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": random.sample(htf_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "财务分析", "量化建模", "报告撰写"][:random.randint(2, 4)],
            "实习标签": random.sample(htf_remote_tags, k=random.randint(3, 4)),
            "部门": "投研类",
            "毕业时间要求": "2026届应届生",
            "部门介绍": "汇添富基金成立于2005年，是中国一流的综合性资产管理公司之一，总部设立于上海。",
            "具体职责": f"协助分析师进行行业研究、公司分析、数据整理与报告撰写；参与投资策略讨论。",
            "福利待遇": "行业竞争力薪资，系统培训，导师带教，员工福利",
            "投递链接": "https://www.htffund.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 11. 招商基金（新增）
    cmb_fund_positions = ["行业研究员", "指数研究员", "全球配置研究员"]
    cmb_fund_locations = ["📍深圳", "📍北京", "📍上海"]
    cmb_fund_degree_reqs = ["硕士及以上", "金融/经济/理工", "2026/2027届"]
    cmb_fund_remote_tags = ["👀 招商系基金", "👀 春季招聘", "👀 2-3个月实习", "👀 留用机会"]
    for pos in cmb_fund_positions[:3]:
        loc = random.choice(cmb_fund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "招商基金",
            "岗位": f"2026春招 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 实习考察通过可录用",
            "学历要求": random.sample(cmb_fund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "数据分析", "报告撰写", "英文阅读"][:random.randint(2, 4)],
            "实习标签": random.sample(cmb_fund_remote_tags, k=random.randint(3, 4)),
            "部门": "投研",
            "毕业时间要求": "2026/2027届硕士",
            "部门介绍": "招商基金是招商银行控股的基金管理公司，成立于2002年，是国内首批中外合资基金管理公司之一。",
            "具体职责": f"协助研究员进行行业与公司研究，参与数据分析、模型搭建与报告撰写。",
            "福利待遇": "系统培训，导师带教，实习补贴，表现优秀可转正",
            "投递链接": "https://www.cmfchina.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 12. 国泰基金（新增）
    gt_fund_positions = ["行业研究员", "量化研究员", "固收研究员"]
    gt_fund_locations = ["📍上海", "📍北京"]
    gt_fund_degree_reqs = ["硕士及以上", "金融/经济/理工", "复合背景优先"]
    gt_fund_remote_tags = ["👀 菁英计划", "👀 1998年成立", "👀 首批规范基金公司", "👀 4月30日截止"]
    for pos in gt_fund_positions[:3]:
        loc = random.choice(gt_fund_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "国泰基金",
            "岗位": f"菁英计划 - {pos}",
            "赛道": "行研岗",
            "地点": loc,
            "薪资": "¥200-350/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 未来骨干力量培养",
            "学历要求": random.sample(gt_fund_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "财务分析", "数据处理", "逻辑思维"][:random.randint(2, 4)],
            "实习标签": random.sample(gt_fund_remote_tags, k=random.randint(3, 4)),
            "部门": "投研",
            "毕业时间要求": "2027届应届生",
            "部门介绍": "国泰基金成立于1998年3月，国内首批规范成立的基金管理公司之一，27年来已发展成为综合性、多元化的大型资产管理公司。",
            "具体职责": f"协助研究员进行行业与公司分析，参与研究报告撰写与投资策略讨论。",
            "福利待遇": "系统培训，导师带教，实习补贴，菁英计划培养",
            "投递链接": "https://www.gtfund.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # ---------- 赛道3：量化岗（扩充至20+） ----------

    # 1. 九坤投资
    ubiquant_departments = ["量化策略部", "量化实现部", "AI Lab", "Data Lab"]
    ubiquant_positions = ["量化研究员", "AI算法实习生", "量化分析", "数据科学", "量化风险管理"]
    ubiquant_locations = ["📍北京", "📍上海"]
    ubiquant_degree_reqs = ["硕士及以上", "数学/统计/物理/计算机", "博士优先", "竞赛获奖优先", "顶会论文优先"]
    ubiquant_remote_tags = ["👀 965上班制", "👀 头部量化私募", "👀 极客文化", "👀 硬核笔面试", "👀 高薪", "👀 扁平管理"]
    for dept in ubiquant_departments:
        pos = random.choice(ubiquant_positions)
        loc = random.choice(ubiquant_locations)
        exam_date = today + timedelta(days=random.randint(7, 40))
        jobs.append({
            "公司": "九坤投资",
            "岗位": f"梧桐计划 - {dept} {pos}",
            "赛道": "量化岗",
            "地点": loc,
            "薪资": f"¥{random.randint(400, 800)}/天",
            "HC数量": f"HC: {random.randint(2, 6)}人",
            "面试轮数": f"面试: {random.randint(4, 6)}轮",
            "留用机会": "✅ 梧桐计划专项培养，通过可转正",
            "学历要求": random.sample(ubiquant_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["C++/Python精通", "机器学习/深度学习", "数理统计扎实", "算法设计", "高频交易经验"][
                :random.randint(3, 5)],
            "实习标签": random.sample(ubiquant_remote_tags, k=random.randint(3, 5)),
            "部门": dept,
            "毕业时间要求": "2026届应届生",
            "部门介绍": f"九坤投资是国内成立最早的量化投资机构之一，资产管理规模位居前列，获得100+行业荣誉及奖项。梧桐计划是面向全球优秀本硕博应届生的专项人才计划。",
            "具体职责": f"在{dept}参与量化策略研究、模型开发、数据分析与回测；探索前沿量化技术；与团队协作优化交易策略。",
            "福利待遇": "行业顶尖薪资，965工作制，顶配办公设备，不限量零食，健身房，年度体检，团建旅游",
            "投递链接": "https://app.mokahr.com/campus-recruitment/ubiquantrecruit/37031",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 2. 蒙玺投资（新增）
    mx_positions = ["量化策略研究员", "AI算法研究员", "算法开发工程师"]
    mx_locations = ["📍上海"]
    mx_degree_reqs = ["本科及以上", "理工科背景", "顶尖高校", "2027届应届生"]
    mx_remote_tags = ["👀 蒙新计划", "👀 量化先行者", "👀 资管200亿+", "👀 深度布局AI"]
    for pos in mx_positions:
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "蒙玺投资",
            "岗位": f"蒙新计划 - {pos}",
            "赛道": "量化岗",
            "地点": random.choice(mx_locations),
            "薪资": "¥400-600/天",
            "HC数量": f"HC: {random.randint(3, 10)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 表现优秀可转正",
            "学历要求": random.sample(mx_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["Python/MATLAB/C++", "机器学习", "数理统计", "算法设计"][:random.randint(3, 5)],
            "实习标签": random.sample(mx_remote_tags, k=random.randint(3, 4)),
            "部门": "量化投研",
            "毕业时间要求": "2027届应届生（2026.09-2027.08毕业）",
            "部门介绍": "蒙玺投资成立于2016年，是国内量化行业先行者之一。依托强大的数据挖掘、统计分析和软件开发能力，构建了覆盖多市场、多品种、全频段的量化资产管理平台，资管规模200多亿元。",
            "具体职责": f"跟踪市场价格变动，研究总结投资逻辑；发掘数据规律，从海量数据中挖掘有效因子，研究交易策略；策略持续跟踪优化。",
            "福利待遇": "行业竞争力薪资，前沿技术实践，资深导师带教，留用机会",
            "投递链接": "https://www.mengxiinvestment.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 3. 顽岩资产（新增）
    wy_positions = ["量化策略研究员（QR）", "量化开发工程师（QD）"]
    wy_locations = ["📍上海"]
    wy_degree_reqs = ["本科及以上", "计算机/软件工程/AI/金融工程", "2027届及之后"]
    wy_remote_tags = ["👀 滚石计划", "👀 暑期训练营", "👀 直接发放正式Offer", "👀 全品种覆盖"]
    for pos in wy_positions:
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "顽岩资产",
            "岗位": f"滚石计划 - {pos}",
            "赛道": "量化岗",
            "地点": random.choice(wy_locations),
            "薪资": "¥12,000+/月",
            "HC数量": f"HC: {random.randint(5, 10)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 实习表现优异将直接发放正式Offer",
            "学历要求": random.sample(wy_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["C++/Python/Golang", "量化策略", "算法开发", "AI Infra"][:random.randint(2, 4)],
            "实习标签": random.sample(wy_remote_tags, k=random.randint(3, 4)),
            "部门": "投研/技术",
            "毕业时间要求": "2027届及之后",
            "部门介绍": "上海顽岩私募基金管理有限公司成立于2015年，总部位于上海陆家嘴，已完成全品种覆盖，交易品种涵盖股票、商品期货、股指期货、可转债、期权等。",
            "具体职责": "深度参与核心技术平台开发，为策略研究和交易提供框架支持，方向包括C++交易系统开发、Python量化开发、AI Infra开发等。",
            "福利待遇": "一线资深技术专家指导，专属职业发展路径，表现优异直接发放正式Offer",
            "投递链接": "https://www.wanyanasset.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 4. 微观博易（新增）
    wg_positions = ["量化策略研究员", "量化交易员", "C++开发工程师"]
    wg_locations = ["📍上海"]
    wg_degree_reqs = ["本科及以上", "知名高校", "2027届毕业生"]
    wg_remote_tags = ["👀 Micro量化夏令营", "👀 2022年成立项目", "👀 真实业务场景", "👀 合伙人级别Mentor"]
    for pos in wg_positions:
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "微观博易",
            "岗位": f"Micro量化夏令营 - {pos}",
            "赛道": "量化岗",
            "地点": random.choice(wg_locations),
            "薪资": "¥400-700/天",
            "HC数量": f"HC: {random.randint(3, 10)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 提前锁定全职Offer",
            "学历要求": random.sample(wg_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["Python/Matlab/C++", "统计分析", "机器学习", "Linux/Unix"][:random.randint(2, 4)],
            "实习标签": random.sample(wg_remote_tags, k=random.randint(3, 4)),
            "部门": "量化投研",
            "毕业时间要求": "2027届应届毕业生",
            "部门介绍": "Micro量化夏令营是微观博易自2022年成立的暑期实习项目，旨在为有志于探索量化领域的在校生提供优质的实践机会。",
            "具体职责": "通过观察和分析各类数据，开发量化交易信号；深入研究统计、机器学习方法，开展量化交易模型研究。",
            "福利待遇": "丰厚实习薪资，合伙人级别Mentor带教，硬核实战项目，表现优异提前锁定全职Offer",
            "投递链接": "https://www.microby.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 5. 思勰投资（新增）
    sx_positions = ["量化研究员", "机器学习研究员", "量化交易员", "C++开发工程师"]
    sx_locations = ["📍上海"]
    sx_degree_reqs = ["本科及以上", "理工科（数学/物理/化学/计算机）", "2025-2027届"]
    sx_remote_tags = ["👀 10周实习", "👀 向上·探无穹", "👀 酌情远程", "👀 表现决定正式offer"]
    for pos in sx_positions[:3]:
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "思勰投资",
            "岗位": f"2026校招 - {pos}",
            "赛道": "量化岗",
            "地点": random.choice(sx_locations),
            "薪资": "¥10,000/月",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 实习结束后表现评价并决定正式offer发放",
            "学历要求": random.sample(sx_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["Python/C++", "数理统计", "时间序列", "机器学习"][:random.randint(2, 4)],
            "实习标签": random.sample(sx_remote_tags, k=random.randint(3, 4)),
            "部门": "量化部",
            "毕业时间要求": "2025-2027届",
            "部门介绍": "思勰投资是一家专注于量化投资的私募基金管理公司，致力于用量化方法为投资者创造稳定收益。",
            "具体职责": "参与量化策略研究、因子挖掘、模型开发与回测；协助策略优化与实盘监控。",
            "福利待遇": "10,000元/月实习工资，系统培训，导师带教，表现优秀可留用",
            "投递链接": "https://www.sixieinvestment.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 6. 黑翼资产（新增）
    hy_positions = ["量化策略研究员", "机器学习研究员", "量化开发工程师"]
    hy_locations = ["📍北京", "📍上海", "📍成都"]
    hy_degree_reqs = ["本科及以上", "数学/统计/计算机/物理/AI", "竞赛获奖加分"]
    hy_remote_tags = ["👀 11年量化", "👀 300亿+资管", "👀 连续6年金牛奖", "👀 日常/暑期均可"]
    for pos in hy_positions:
        loc = random.choice(hy_locations)
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "黑翼资产",
            "岗位": f"量化实习 - {pos}",
            "赛道": "量化岗",
            "地点": loc,
            "薪资": "¥15k-16k/月",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": random.sample(hy_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["Python/C++", "数理统计", "机器学习", "量化模型"][:random.randint(2, 4)],
            "实习标签": random.sample(hy_remote_tags, k=random.randint(3, 4)),
            "部门": "投研",
            "毕业时间要求": "2026届及以后",
            "部门介绍": "黑翼资产，国内顶尖的量化对冲基金之一，只用了11年就把资产管理规模做到300+亿，连续6年捧回中国私募'奥斯卡'——金牛奖。",
            "具体职责": "开发量化模型策略，发掘有效规律；参与策略回测、优化与实盘监控。",
            "福利待遇": "行业竞争力薪资，顶尖量化团队，系统培训，留用机会",
            "投递链接": "https://www.blackwingasset.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 7. 灵均投资（新增）
    lj_positions = ["量化研究员", "股票高频研究员", "期货高频研究员"]
    lj_locations = ["📍深圳", "📍北京", "📍上海"]
    lj_degree_reqs = ["硕士及以上", "理工科/金融工程", "博士优先", "因子相关经验优先"]
    lj_remote_tags = ["👀 头部量化私募", "👀 专属导师", "👀 一对一带教", "👀 留用计划"]
    for pos in lj_positions[:3]:
        loc = random.choice(lj_locations)
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "灵均投资",
            "岗位": f"量化实习 - {pos}",
            "赛道": "量化岗",
            "地点": loc,
            "薪资": "¥400-600/天",
            "HC数量": f"HC: {random.randint(2, 8)}人",
            "面试轮数": f"面试: {random.randint(3, 5)}轮",
            "留用机会": "✅ 实习生留用计划",
            "学历要求": random.sample(lj_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["Python/C++/Java", "机器学习", "高频策略", "因子挖掘"][:random.randint(2, 4)],
            "实习标签": random.sample(lj_remote_tags, k=random.randint(3, 4)),
            "部门": "量化投研",
            "毕业时间要求": "2026年12月及以后毕业",
            "部门介绍": "灵均投资是国内头部量化私募，通过'实习生留用计划'识别和培养人才，为人才配备专属导师开展一对一定制化带教与实战指导。",
            "具体职责": "针对量化投资业务进行专题数据分析及开发；研究国内外金融市场，参与量化交易策略的设计开发和程序化实现。",
            "福利待遇": "专属导师一对一，实战指导，资源支持，鼓励探索前沿，表现优秀可留用",
            "投递链接": "https://www.lingjuninvest.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 8. 中欧瑞博（新增）
    zorb_positions = ["行业研究员（科技）", "行业研究员（医药）", "行业研究员（消费）", "行业研究员（周期）"]
    zorb_locations = ["📍深圳"]
    zorb_degree_reqs = ["硕士及以上", "金融/经济/财会/STEM", "2027届"]
    zorb_remote_tags = ["👀 最早阳光私募之一", "👀 二级市场证券投资", "👀 实习津贴10000元/月", "👀 提供住宿"]
    for pos in zorb_positions[:4]:
        exam_date = today + timedelta(days=random.randint(7, 35))
        jobs.append({
            "公司": "中欧瑞博",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "量化岗",
            "地点": random.choice(zorb_locations),
            "薪资": "¥10,000/月",
            "HC数量": f"HC: {random.randint(2, 10)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 晋升通畅，激励机制完善",
            "学历要求": random.sample(zorb_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["行业研究", "财务分析", "投资机会把握", "组合管理"][:random.randint(2, 4)],
            "实习标签": random.sample(zorb_remote_tags, k=random.randint(3, 4)),
            "部门": "投研",
            "毕业时间要求": "2027届毕业生（硕士、博士）",
            "部门介绍": "中欧瑞博是中国最早的阳光私募基金管理公司之一，专注于二级市场证券投资，公司福利优厚，晋升通畅，激励机制完善。",
            "具体职责": "进行行业研究，把握投资机会，协助构建管理行业投资组合。",
            "福利待遇": "实习津贴10000元/月，报销往返学校长途交通费，提供住宿或相应补贴",
            "投递链接": "https://www.rabbitfund.net",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # ---------- 赛道4：银行/销售交易（扩充至20+） ----------

    # 1. 招商银行总行
    cmb_directions = ["零售金融", "公司金融", "投行与金融市场", "计划财务", "法律合规", "信息技术AI应用"]
    cmb_locations = ["📍深圳", "📍上海", "📍北京", "📍杭州", "📍广州", "📍成都", "📍西安"]
    cmb_degree_reqs = ["硕士及以上", "金融/经济/管理/法律/计算机", "英语六级", "数据分析能力"]
    cmb_remote_tags = ["👀 总行直招", "👀 专属导师", "👀 前沿课题参与", "👀 培训体系完善", "👀 答辩通过可获27届校招提前批",
                       "👀 活动丰富"]
    for direction in cmb_directions[:5]:
        loc = random.choice(cmb_locations)
        exam_date = today + timedelta(days=random.randint(10, 50))
        jobs.append({
            "公司": "招商银行总行",
            "岗位": f"梦工场实习生 - {direction}方向",
            "赛道": "银行/销售交易",
            "地点": loc,
            "薪资": f"¥{random.randint(150, 250)}/天",
            "HC数量": f"HC: {random.randint(3, 10)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 顺利结业可获得2027届校招提前批offer",
            "学历要求": random.sample(cmb_degree_reqs, k=random.randint(2, 3)),
            "能力要求": ["沟通表达", "分析能力", "团队协作", "学习能力", "抗压能力"][:random.randint(3, 5)],
            "实习标签": random.sample(cmb_remote_tags, k=random.randint(3, 5)),
            "部门": direction,
            "毕业时间要求": "2027.01-2027.07",
            "部门介绍": f"招商银行总行{direction}方向。招商银行2025年银行家全球银行1000强排名第8位，蝉联中资银行综合10强首位。",
            "具体职责": f"参与{direction}相关业务实践，深入一线了解银行业务流程；在导师指导下完成项目任务；参与团队日常运营客户沟通。",
            "福利待遇": "实习补贴，总行大厦参观，体育赛事/桌游竞技，结业证书，表现优异者获校招提前批offer",
            "投递链接": "http://career.cmbchina.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 2. 中国银行（新增）
    boc_positions = ["总行部门实习生（信科）", "综合类实习生", "信科类实习生", "营业网点营销服务类实习生"]
    boc_locations = ["📍北京", "📍上海", "📍武汉", "📍成都"]
    boc_degree_reqs = ["本科及以上", "信息科技相关专业", "2027届应届毕业生"]
    boc_remote_tags = ["👀 百年中行", "👀 全球网络", "👀 直接留用机会", "👀 3月30日截止"]
    for pos in boc_positions:
        loc = random.choice(boc_locations)
        exam_date = today + timedelta(days=random.randint(5, 30))
        jobs.append({
            "公司": "中国银行",
            "岗位": f"2026实习生 - {pos}",
            "赛道": "银行/销售交易",
            "地点": loc,
            "薪资": "¥150-250/天",
            "HC数量": f"HC: {random.randint(5, 20)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 实习表现优秀可直接留用，签订劳动合同",
            "学历要求": random.sample(boc_degree_reqs, k=random.randint(1, 2)),
            "能力要求": ["专业知识", "沟通表达", "团队协作", "学习能力"][:random.randint(2, 4)],
            "实习标签": random.sample(boc_remote_tags, k=random.randint(3, 4)),
            "部门": "总行/分支机构",
            "毕业时间要求": "2027届应届毕业生",
            "部门介绍": "中国银行于1912年2月正式成立，是中国持续经营时间最久的银行，也是中国全球化和综合化程度最高的银行，在中国内地及境外64个国家和地区设有机构。",
            "具体职责": "分配至总行信息科技、主要业务部门或各级管理机构开展暑期实习，参与业务实践与项目执行。",
            "福利待遇": "百年大行平台，系统培训，实习补贴，表现优秀直接留用",
            "投递链接": "https://www.boc.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 3. 杭州银行（新增）
    hzbank_positions = ["总行实习生", "分行实习生", "营销实习生", "运营实习生"]
    hzbank_locations = ["📍杭州", "📍北京", "📍上海", "📍深圳", "📍南京", "📍合肥"]
    hzbank_degree_reqs = ["本科及以上", "经济类/理工类", "2026届应届生"]
    hzbank_remote_tags = ["👀 摘星计划", "👀 校招提前批", "👀 实习期2个月", "👀 年度十佳城商行"]
    for pos in hzbank_positions:
        loc = random.choice(hzbank_locations)
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "杭州银行",
            "岗位": f"摘星计划 - {pos}",
            "赛道": "银行/销售交易",
            "地点": loc,
            "薪资": "¥10,000-15,000/月",
            "HC数量": f"HC: {random.randint(5, 30)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀可获得2026届校招录用通知书",
            "学历要求": random.sample(hzbank_degree_reqs, k=random.randint(1, 2)),
            "能力要求": ["沟通能力", "学习能力", "团队合作", "创新意识"][:random.randint(2, 4)],
            "实习标签": random.sample(hzbank_remote_tags, k=random.randint(3, 4)),
            "部门": "总行/分支行",
            "毕业时间要求": "2026届应届生",
            "部门介绍": "杭州银行成立于1996年9月，是浙江省首家在上交所主板挂牌的上市银行，综合实力居全国城市商业银行前列，多年蝉联'年度十佳城商行'。",
            "具体职责": "在总行部门或分支行参与业务实践，协助开展营销推动、数据分析、综合管理等相关工作。",
            "福利待遇": "实习津贴，提供工作餐，系统培训，表现优秀可获得校招录用通知书",
            "投递链接": "https://myjob.hzbank.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 4. 工商银行总行（新增）
    icbc_locations = ["📍北京"]
    icbc_degree_reqs = ["本科及以上", "专业不限", "2027届毕业生"]
    icbc_remote_tags = ["👀 宇宙行", "👀 计划招聘120人", "👀 3月31日截止", "👀 实习表现优先考虑"]
    exam_date = today + timedelta(days=random.randint(5, 30))
    jobs.append({
        "公司": "工商银行总行",
        "岗位": "暑期实习生",
        "赛道": "银行/销售交易",
        "地点": random.choice(icbc_locations),
        "薪资": "¥150-250/天",
        "HC数量": "HC: 120人左右",
        "面试轮数": f"面试: {random.randint(2, 4)}轮",
        "留用机会": "✅ 实习表现优秀者将在校招录用时优先考虑",
        "学历要求": random.sample(icbc_degree_reqs, k=1),
        "能力要求": ["沟通表达", "学习能力", "团队协作", "分析能力"][:random.randint(2, 4)],
        "实习标签": random.sample(icbc_remote_tags, k=random.randint(3, 4)),
        "部门": "总行各业务部门",
        "毕业时间要求": "2027届毕业生",
        "部门介绍": "中国工商银行总行本部，全球最大的商业银行之一，业务范围覆盖广泛，平台资源丰富。",
        "具体职责": "安排在总行各业务部门实习锻炼，参与业务实践与项目执行。",
        "福利待遇": "全球最大商业银行平台，系统培训，实习补贴，表现优秀优先录用",
        "投递链接": "https://job.icbc.com.cn",
        "笔试日期": exam_date.strftime("%Y-%m-%d"),
        "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
    })

    # 5. 建设银行（新增）
    ccb_positions = ["金融科技实习生", "管理培训生", "综合营销岗"]
    ccb_locations = ["📍北京", "📍上海", "📍深圳", "📍广州"]
    ccb_degree_reqs = ["本科及以上", "金融/经济/计算机", "2026届应届生"]
    ccb_remote_tags = ["👀 国有大行", "👀 金融科技方向", "👀 表现优异者优先录用", "👀 系统培养"]
    for pos in ccb_positions[:3]:
        loc = random.choice(ccb_locations)
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "建设银行",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "银行/销售交易",
            "地点": loc,
            "薪资": "¥150-250/天",
            "HC数量": f"HC: {random.randint(5, 20)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 针对表现优异者优先录用",
            "学历要求": random.sample(ccb_degree_reqs, k=random.randint(1, 2)),
            "能力要求": ["专业知识", "数据分析", "沟通表达", "学习能力"][:random.randint(2, 4)],
            "实习标签": random.sample(ccb_remote_tags, k=random.randint(3, 4)),
            "部门": "分支机构/总行",
            "毕业时间要求": "2026届应届生",
            "部门介绍": "中国建设银行是国有大型商业银行，业务范围覆盖广泛，综合实力位居全球银行业前列。",
            "具体职责": "参与金融科技课题研究、创新技术探索、大数据分析与应用、金融科技项目开发建设等核心工作。",
            "福利待遇": "国有大行平台，系统培训，实习补贴，表现优异可留用",
            "投递链接": "https://job.ccb.com",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 6. 上海银行（新增）
    shbank_positions = ["总行业务类实习生", "金融市场实习生", "风险管理实习生", "运营管理实习生"]
    shbank_locations = ["📍上海"]
    shbank_degree_reqs = ["本科及以上", "金融/经济/管理", "2026届应届生"]
    shbank_remote_tags = ["👀 上海银行", "👀 总行部门", "👀 业务类实习", "👀 留用机会"]
    for pos in shbank_positions[:3]:
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "上海银行",
            "岗位": f"暑期实习 - {pos}",
            "赛道": "银行/销售交易",
            "地点": random.choice(shbank_locations),
            "薪资": "¥150-250/天",
            "HC数量": f"HC: {random.randint(3, 10)}人",
            "面试轮数": f"面试: {random.randint(2, 4)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": random.sample(shbank_degree_reqs, k=random.randint(1, 2)),
            "能力要求": ["业务分析", "沟通协作", "学习能力", "金融知识"][:random.randint(2, 4)],
            "实习标签": random.sample(shbank_remote_tags, k=random.randint(3, 4)),
            "部门": "总行部门",
            "毕业时间要求": "2026届应届生",
            "部门介绍": "上海银行是上海证券交易所主板上市公司，是国内头部城市商业银行之一，综合实力位居城商行前列。",
            "具体职责": "在总行部门公司业务、零售业务、金融市场、风险管理、计划财务、运营管理等领域参与实习。",
            "福利待遇": "系统培训，导师带教，实习补贴，表现优秀可留用",
            "投递链接": "https://www.bosc.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    # 7. 广州银行（新增）
    gzbank_positions = ["总行实习生", "营销推动助理", "数据分析助理"]
    gzbank_locations = ["📍广州"]
    gzbank_degree_reqs = ["本科及以上", "金融/经济/统计", "相关专业"]
    gzbank_remote_tags = ["👀 广州银行大厦", "👀 总行部门", "👀 综合管理", "👀 2026年1月启动"]
    for pos in gzbank_positions[:3]:
        exam_date = today + timedelta(days=random.randint(10, 40))
        jobs.append({
            "公司": "广州银行",
            "岗位": f"2026实习生 - {pos}",
            "赛道": "银行/销售交易",
            "地点": random.choice(gzbank_locations),
            "薪资": "¥150-250/天",
            "HC数量": f"HC: {random.randint(3, 12)}人",
            "面试轮数": f"面试: {random.randint(2, 3)}轮",
            "留用机会": "✅ 表现优秀可留用",
            "学历要求": random.sample(gzbank_degree_reqs, k=random.randint(1, 2)),
            "能力要求": ["数据分析", "营销推动", "综合管理", "沟通协作"][:random.randint(2, 4)],
            "实习标签": random.sample(gzbank_remote_tags, k=random.randint(3, 4)),
            "部门": "总行部门",
            "毕业时间要求": "在校学生",
            "部门介绍": "广州银行是广东省重要的地方性商业银行，总部位于广州市天河区广州银行大厦。",
            "具体职责": "协助开展营销推动、数据分析、综合管理等相关工作。",
            "福利待遇": "系统培训，导师带教，实习补贴",
            "投递链接": "https://www.gzcb.com.cn",
            "笔试日期": exam_date.strftime("%Y-%m-%d"),
            "面试日期": (exam_date + timedelta(days=random.randint(10, 20))).strftime("%Y-%m-%d"),
        })

    return pd.DataFrame(jobs)


all_jobs_df = generate_job_database()

# ================= 目标赛道选择界面 =================
if st.session_state.target_role is None:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align: center; color: #1E293B !important; font-size: 3.5rem;'>金融求职助手<span style='color:#0284C7;'>.</span></h1>",
        unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #475569 !important; font-size: 1.2rem; margin-bottom: 40px;'>追踪岗位 · 优化简历 · 模拟笔试面试</p>",
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.8); padding: 40px; border-radius: 20px; box-shadow: 0 10px 40px rgba(30, 41, 59, 0.03); backdrop-filter: blur(25px); border: 1px solid rgba(226, 232, 240, 0.7);'>
            <h3 style='text-align: center; margin-bottom: 30px; color: #1E293B !important;'>请选择目标赛道</h3>
        </div>
        """, unsafe_allow_html=True)

        selected_role = st.radio("主攻方向:", ("券商/投行", "行研岗", "量化岗", "银行/销售交易"), index=None,
                                 horizontal=True)

        st.write("")
        if st.button("进入工作台", use_container_width=True, type="primary"):
            if selected_role:
                st.session_state.target_role = selected_role
                st.rerun()
            else:
                st.error("请先选择一个赛道！")
    st.stop()

# ================= 主界面 =================
st.sidebar.markdown(
    f"<p style='color:#64748B; margin-bottom: 5px; font-size:14px;'>当前赛道</p><span style='color:#0284C7; font-size: 26px; font-weight:800;'>{st.session_state.target_role}</span>",
    unsafe_allow_html=True)
st.sidebar.markdown("<div style='height: 20px; border-bottom: 1px solid rgba(226, 232, 240, 0.6);'></div>",
                    unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
menu = st.sidebar.radio("导航",
                        ("📊 全流程看板", "🌐 岗位情报库", "📄 简历评分", "📝 笔试练习", "👨‍💼 模拟面试"))
target_jobs = all_jobs_df[all_jobs_df["赛道"] == st.session_state.target_role].reset_index(drop=True)

# ================= 页面 1：全流程看板 =================
if menu == "📊 全流程看板":
    st.markdown("## 📊 全流程看板 <span style='font-size: 18px; color: #64748B; font-weight: normal;'>/ 概览</span>",
                unsafe_allow_html=True)

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    total_applied = len(st.session_state.my_jobs)
    avg_score = st.session_state.my_jobs['简历得分'].mean() if total_applied > 0 else 0
    pending_exam = len(st.session_state.my_jobs[st.session_state.my_jobs['当前状态'] == '笔试准备中'])
    pending_interview = len(st.session_state.my_jobs[st.session_state.my_jobs['当前状态'] == '面试准备中'])

    m_col1.metric("投递总数", f"{total_applied} 家")
    m_col2.metric("简历均分", f"{avg_score:.1f} 分", delta="待优化" if avg_score < 85 and total_applied > 0 else None)
    m_col3.metric("待笔试", f"{pending_exam} 场")
    m_col4.metric("待面试", f"{pending_interview} 场")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.my_jobs.empty:
        st.info("暂无投递记录。请前往岗位情报库添加岗位。")
    else:
        df_display = st.session_state.my_jobs.copy()
        today = datetime.now()
        df_display['距笔试(天)'] = pd.to_datetime(df_display['笔试日期']).apply(lambda x: (x - today).days)
        df_display['距面试(天)'] = pd.to_datetime(df_display['面试日期']).apply(lambda x: (x - today).days)

        show_cols = ["公司", "岗位", "当前状态", "简历得分", "距笔试(天)", "投递链接"]


        # 专为尚雅风设计的表格高亮 (采用温柔的水粉色系)
        def highlight_status(row):
            if row['当前状态'] == '简历修改中':
                return ['border-left: 3px solid #E11D48; background-color: #FFF1F2; color: #9F1239;'] * len(row)
            elif row['当前状态'] == '笔试准备中':
                return ['border-left: 3px solid #D97706; background-color: #FFFBEB; color: #92400E;'] * len(row)
            elif row['当前状态'] == '面试准备中':
                return ['border-left: 3px solid #0284C7; background-color: #F0F9FF; color: #075985;'] * len(row)
            elif 'Offer' in row['当前状态']:
                return ['border-left: 3px solid #059669; background-color: #ECFDF5; color: #065F46;'] * len(row)
            return ['background-color: transparent'] * len(row)


        st.dataframe(
            df_display[show_cols].style.apply(highlight_status, axis=1),
            column_config={"投递链接": st.column_config.LinkColumn("网申入口", display_text="🔗 打开"),
                           "当前状态": "进度"},
            hide_index=True, use_container_width=True, height=400
        )

# ================= 页面 2：岗位情报库 =================
elif menu == "🌐 岗位情报库":
    st.markdown(
        "## 📡 岗位情报库 <span style='font-size: 18px; color: #64748B; font-weight: normal;'>/ 可投递岗位</span>",
        unsafe_allow_html=True)
    st.markdown("<p style='font-size: 14px;'>以下为基于2026年金融机构真实招聘公告筛选的岗位信息。</p>",
                unsafe_allow_html=True)

    unique_companies = target_jobs['公司'].unique()

    for comp in unique_companies:
        st.markdown(f"<div class='company-header'>{comp}</div>", unsafe_allow_html=True)
        comp_jobs = target_jobs[target_jobs['公司'] == comp]

        for _, job in comp_jobs.iterrows():
            is_applied = not st.session_state.my_jobs.empty and not st.session_state.my_jobs[
                (st.session_state.my_jobs['公司'] == job['公司']) & (
                            st.session_state.my_jobs['岗位'] == job['岗位'])].empty

            with st.container():
                tag_html = ""
                tag_html += f"<span class='tag tag-loc'>{job['地点']}</span>"
                tag_html += f"<span class='tag tag-sal'>{job['薪资']}</span>"
                tag_html += f"<span class='tag tag-hc'>{job['HC数量']}</span>"
                tag_html += f"<span class='tag tag-ro'>{job['留用机会']}</span>"
                if '学历要求' in job:
                    for req in job['学历要求'][:2]: tag_html += f"<span class='tag tag-degree'>{req}</span>"
                if '部门' in job:
                    tag_html += f"<span class='tag tag-dept'>{job['部门']}</span>"
                if '实习标签' in job:
                    for t in job['实习标签'][:4]: tag_html += f"<span class='tag tag-intel'>{t}</span>"
                if '毕业时间要求' in job:
                    tag_html += f"<span class='tag tag-exp'>毕业: {job['毕业时间要求']}</span>"

                duties_str = " | ".join(job['能力要求'][:4])

                card_html = f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #1E293B; font-size: 18px;">{job['岗位']}</h4>
                        <span style="font-size: 13px; color: #64748B; font-weight: 600;">笔试: {job['笔试日期']}</span>
                    </div>
                    <div class="tag-group">
                        {tag_html}
                    </div>
                    <div style="font-size: 13px; color: #475569; margin-top: 10px; padding-top: 10px; border-top: 1px dashed rgba(226, 232, 240, 0.7);">
                        <b style="color: #1E293B;">能力要求：</b>{duties_str}
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

                with st.expander("🔍 查看详细职位描述"):
                    # 尚雅风要求描述颜色要温润
                    st.markdown(f"""
                    <div class="details-box">
                        <p><b>部门介绍：</b><br>{job.get('部门介绍', '')}</p>
                        <p><b>主要职责：</b><br>{job.get('具体职责', '')}</p>
                        <p><b>福利待遇：</b><br>{job.get('福利待遇', '')}</p>
                        <p><b>面试轮数：</b>{job.get('面试轮数', '')}</p>
                        <p style="color: #94A3B8; font-size: 12px; margin-top: 12px;"><i>* 岗位信息基于2026年官方招聘公告整理，投递前请以官网最新信息为准。</i></p>
                    </div>
                    """, unsafe_allow_html=True)

                col_btn, col_link, _ = st.columns([2.5, 2.5, 5])
                with col_link:
                    st.markdown(
                        f"<a href='{job['投递链接']}' target='_blank' style='display:inline-block; margin-top:5px; font-size:14px; font-weight:600; color:#0284C7; text-decoration:none;'>🔗 前往官网投递</a>",
                        unsafe_allow_html=True)
                with col_btn:
                    if is_applied:
                        st.button("已添加追踪", disabled=True, key=f"dis_{job['公司']}_{job['岗位']}",
                                  use_container_width=True)
                    else:
                        if st.button("➕ 添加追踪", type="primary", key=f"btn_{job['公司']}_{job['岗位']}",
                                     use_container_width=True):
                            new_job = {
                                "公司": job['公司'], "岗位": job['岗位'], "赛道": job['赛道'], "地点": job['地点'],
                                "投递链接": job['投递链接'], "投递日期": datetime.now().strftime("%Y-%m-%d"),
                                "笔试日期": job['笔试日期'], "面试日期": job['面试日期'],
                                "当前状态": "简历修改中", "简历得分": 0, "笔试完成": False, "面试模拟完成": False
                            }
                            st.session_state.my_jobs = pd.concat([st.session_state.my_jobs, pd.DataFrame([new_job])],
                                                                 ignore_index=True)
                            st.success("已添加至全流程看板。")
                            st.rerun()

# ================= 页面 3：简历评分 =================
elif menu == "📄 简历评分":
    st.markdown("## 📑 简历评分 <span style='font-size: 18px; color: #64748B; font-weight: normal;'>/ AI 诊断</span>",
                unsafe_allow_html=True)

    col_main, col_side = st.columns([7, 3])
    with col_side:
        st.markdown("""
        <div class="tip-panel">
            <h4>评分参考</h4>
            <ul style='color: #475569 !important; font-size:14px; padding-left:20px; line-height: 1.8;'>
                <li><b style="color: #059669;">85分+：</b> 竞争力强，过筛率高。</li>
                <li><b style="color: #D97706;">75-84分：</b> 中等偏上，建议优化。</li>
                <li><b style="color: #E11D48;"><75分：</b> 难度较大，必须修改。</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_main:
        need_resume_jobs = st.session_state.my_jobs[st.session_state.my_jobs['当前状态'] == '简历修改中']
        if need_resume_jobs.empty:
            st.success("所有已添加岗位的简历均已评分通过。")
        else:
            selected_job_idx = st.selectbox("选择要评分的岗位：", need_resume_jobs.index, format_func=lambda
                x: f"{need_resume_jobs.loc[x, '公司']} - {need_resume_jobs.loc[x, '岗位']}")
            st.info("上传简历 PDF 文件，AI 将根据岗位要求进行评分与点评。")
            uploaded_file = st.file_uploader("上传简历 (PDF)", type=['pdf'])

            if uploaded_file:
                if st.button("开始评分", type="primary", use_container_width=True):
                    with st.spinner("AI 分析中..."):
                        resume_text = ""
                        if HAS_PDF_READER:
                            try:
                                reader = PyPDF2.PdfReader(uploaded_file)
                                for page in reader.pages: resume_text += page.extract_text()
                            except Exception:
                                pass
                        if len(resume_text) < 20:
                            resume_text = "（示例文本）候选人国内211本科，GPA 3.5，实习经历包括数据收集与基础分析，Python 入门水平。"

                        job_name = need_resume_jobs.loc[selected_job_idx, '岗位']
                        score, feedback, thinking = evaluate_resume_with_ai(resume_text, st.session_state.target_role,
                                                                            job_name)

                        st.markdown("---")
                        with st.expander("查看 AI 推理过程"):
                            st.markdown(f"<p style='color: #64748B; font-style: italic;'>{thinking}</p>",
                                        unsafe_allow_html=True)

                        st.markdown(f"### 评分结果")
                        # 结果反馈也要美化
                        if score < 75:
                            st.error(f"得分：{score} 分 (及格线: 75分)")
                            st.markdown(
                                f"<div style='background: #FFF1F2; padding:20px; border-radius:12px; border:1px solid #FECDD3; color: #9F1239;'>{feedback}</div>",
                                unsafe_allow_html=True)
                            st.warning("请根据建议修改简历后重新上传。")
                        else:
                            st.balloons()
                            st.success(f"得分：{score} 分，简历已达标！")
                            st.markdown(
                                f"<div style='background: #ECFDF5; padding:20px; border-radius:12px; border:1px solid #A7F3D0; color: #065F46;'>{feedback}</div>",
                                unsafe_allow_html=True)
                            st.session_state.my_jobs.loc[selected_job_idx, '简历得分'] = score
                            st.session_state.my_jobs.loc[selected_job_idx, '当前状态'] = '笔试准备中'
                            st.button("进入笔试练习", on_click=lambda: st.rerun(), type="primary")

# ================= 页面 4：笔试练习 =================
elif menu == "📝 笔试练习":
    st.markdown(
        "## 🧠 笔试练习 <span style='font-size: 18px; color: #64748B; font-weight: normal;'>/ 模拟出题与阅卷</span>",
        unsafe_allow_html=True)

    col_main, col_side = st.columns([7, 3])
    with col_side:
        st.markdown("""
        <div class="tip-panel">
            <h4>常见考点</h4>
            <div style='color: #475569 !important; font-size:14px; line-height: 1.8;'>
                <p><b>券商投行：</b> 估值模型、财务分析</p>
                <p><b>行研/买方：</b> 逻辑推演、商业分析</p>
                <p><b>量化私募：</b> 算法、概率统计</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_main:
        today = datetime.now()
        test_jobs = st.session_state.my_jobs[st.session_state.my_jobs['当前状态'] == '笔试准备中'].copy()

        if test_jobs.empty:
            st.info("当前没有处于笔试准备阶段的岗位。")
        else:
            test_jobs['距笔试(天)'] = pd.to_datetime(test_jobs['笔试日期']).apply(lambda x: (x - today).days)
            urgent_tests = test_jobs[test_jobs['距笔试(天)'] <= 7]

            if urgent_tests.empty:
                st.success("所有笔试均在一周以后，时间充裕。")
            else:
                selected_job_idx = st.selectbox("选择即将笔试的岗位：", urgent_tests.index, format_func=lambda
                    x: f"{urgent_tests.loc[x, '公司']} - {urgent_tests.loc[x, '岗位']}")
                job_info = urgent_tests.loc[selected_job_idx]
                url = "https://api.siliconflow.cn/v1/chat/completions"
                headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
                exam_q_key, exam_feedback_key = f"exam_q_{selected_job_idx}", f"exam_feedback_{selected_job_idx}"

                if exam_q_key not in st.session_state: st.session_state[exam_q_key] = None
                if exam_feedback_key not in st.session_state: st.session_state[exam_feedback_key] = None

                if st.button("生成一道模拟题", type="primary"):
                    with st.spinner("生成题目中..."):
                        prompt = f"你现在是【{job_info['赛道']}】岗位的一位笔试出题官，请为【{job_info['赛道']}】岗位出一道简答题或计算题，只出题干，不要答案。直接给出题目，不要输出其他无关文字"
                        try:
                            res = requests.post(url, json={"model": "Pro/deepseek-ai/DeepSeek-V3.2",
                                                           "messages": [{"role": "user", "content": prompt}],
                                                           "temperature": 0.7}, headers=headers).json()
                            raw_q = res['choices'][0]['message']['content']
                            # 尚雅风不展示推理
                            st.session_state[exam_q_key] = re.sub(r'<think>.*?</think>', '', raw_q,
                                                                  flags=re.DOTALL).strip()
                            st.session_state[exam_feedback_key] = None
                        except Exception as e:
                            st.error(f"出题失败: {e}")

                if st.session_state[exam_q_key]:
                    st.markdown(
                        f"<div style='background: rgba(255, 255, 255, 0.6); padding:25px; border-radius:12px; border:1px solid rgba(226, 232, 240, 0.7);'><h4 style='margin-top:0;'>模拟题：</h4><p style='color: #475569;'>{st.session_state[exam_q_key]}</p></div>",
                        unsafe_allow_html=True)
                    st.write("")
                    user_answer = st.text_area("输入你的回答：", height=200)

                    if st.button("提交批改"):
                        if not user_answer.strip():
                            st.warning("请先作答！")
                        else:
                            with st.spinner("AI 阅卷中..."):
                                eval_prompt = f"作为阅卷人批改：题目“{st.session_state[exam_q_key]}”，作答“{user_answer}”。输出格式：第一行【得分：XX】，然后直接给出整段的精炼的点评并给出整段形式的标准答案，避免列点，不要输出无关文字。"
                                try:
                                    res = requests.post(url, json={"model": "Pro/deepseek-ai/DeepSeek-V3.2",
                                                                   "messages": [
                                                                       {"role": "user", "content": eval_prompt}],
                                                                   "temperature": 0.6}, headers=headers).json()
                                    fb_text = res['choices'][0]['message']['content']
                                    st.session_state[exam_feedback_key] = re.sub(r'<think>.*?</think>', '', fb_text,
                                                                                 flags=re.DOTALL).strip()
                                except Exception:
                                    st.error("批改失败")

                if st.session_state[exam_feedback_key]:
                    st.markdown("### 批改结果")
                    # 行政级批改反馈框
                    st.markdown(
                        f"<div style='background: #F1F5F9; padding:20px; border-radius:12px; border-top:5px solid #0284C7; border-left:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0; color: #475569;'>{st.session_state[exam_feedback_key]}</div>",
                        unsafe_allow_html=True)
                    st.write("")
                    if st.button("标记笔试已完成", type="primary"):
                        st.session_state.my_jobs.loc[selected_job_idx, '笔试完成'] = True
                        st.session_state.my_jobs.loc[selected_job_idx, '当前状态'] = '面试准备中'
                        st.success("状态已更新为面试准备中。")
                        st.rerun()

# ================= 页面 5：模拟面试 =================
elif menu == "👨‍💼 模拟面试":
    st.markdown(
        "## 🎤 模拟面试 <span style='font-size: 18px; color: #64748B; font-weight: normal;'>/ 语音作答与评估</span>",
        unsafe_allow_html=True)

    col_main, col_side = st.columns([7, 3])
    with col_side:
        st.markdown("""
        <div class="tip-panel">
            <h4>表达要点</h4>
            <div style='color: #475569 !important; font-size:14px; line-height: 1.8;'>
                <p><b style="color: #059669;">🟢 结构化：</b>结论先行，论据支撑。</p>
                <p><b style="color: #059669;">🟢 量化：</b>用数据替代形容词。</p>
                <p><b style="color: #E11D48;">🔴 避免：</b>口头禅、模糊表述。</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_main:
        interview_jobs = st.session_state.my_jobs[st.session_state.my_jobs['当前状态'] == '面试准备中']
        if interview_jobs.empty:
            st.warning("当前没有处于面试准备阶段的岗位。")
        else:
            selected_job_idx = st.selectbox("选择面试岗位：", interview_jobs.index, format_func=lambda
                x: f"{interview_jobs.loc[x, '公司']} - {interview_jobs.loc[x, '岗位']}")
            st.markdown(
                f"<div style='background: rgba(255, 255, 255, 0.6); padding:25px; border-radius:12px; border:1px solid rgba(226, 232, 240, 0.7); border-left:5px solid #0284C7;'><h3 style='margin:0; color: #1E293B;'>面试问题：</h3><p style='font-size:18px; margin-top:15px; font-weight:600; color: #1E293B;'>“请谈谈你为什么适合【{interview_jobs.loc[selected_job_idx, '岗位']}】这个岗位？”</p></div>",
                unsafe_allow_html=True)
            st.write("")

            audio_value = st.audio_input("点击录制你的回答")

            if audio_value is not None:
                st.audio(audio_value, format="audio/wav")
                mock_feedback_key = f"mock_feedback_{selected_job_idx}"
                if mock_feedback_key not in st.session_state: st.session_state[mock_feedback_key] = None

                if st.button("提交语音并评估", type="primary", use_container_width=True):
                    with st.spinner("语音转文字中..."):
                        asr_url, headers_asr = "https://api.siliconflow.cn/v1/audio/transcriptions", {
                            "Authorization": f"Bearer {API_KEY}"}
                        try:
                            user_text = requests.post(asr_url, files={
                                "file": ("interview.wav", audio_value.getvalue(), "audio/wav")},
                                                      data={"model": "FunAudioLLM/SenseVoiceSmall"},
                                                      headers=headers_asr).json().get("text", "")
                        except Exception:
                            user_text = ""

                    if user_text:
                        st.markdown(
                            f"<div style='background: #F1F5F9; padding:15px; border-radius:8px; color: #475569;'><b style='color: #1E293B;'>识别内容：</b><br>{user_text}</div>",
                            unsafe_allow_html=True)
                        st.write("")
                        with st.spinner("AI 评估中..."):
                            prompt = f"作为面试官评估以下回答：“{user_text}”。输出【综合得分：XX】及整段的连贯点评，指出优缺点。避免列点，不要输出无关文字。"
                            try:
                                fb = requests.post("https://api.siliconflow.cn/v1/chat/completions",
                                                   json={"model": "Pro/deepseek-ai/DeepSeek-V3.2",
                                                         "messages": [{"role": "user", "content": prompt}],
                                                         "temperature": 0.6}, headers=headers_asr).json()['choices'][0][
                                    'message']['content']
                                st.session_state[mock_feedback_key] = re.sub(r'<think>.*?</think>', '', fb,
                                                                             flags=re.DOTALL).strip()
                            except Exception:
                                st.error("评估失败")

                if st.session_state.get(mock_feedback_key):
                    st.success("评估完成")
                    # 温润行政级点评框
                    st.markdown(
                        f"<div style='background: #F1F5F9; padding:25px; border-radius:12px; border-top:5px solid #059669; border-left:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0; color: #475569;'><h4 style='margin-top:0; color:#065F46;'>面试官点评：</h4><p style='color: #475569;'>{st.session_state[mock_feedback_key]}</p></div>",
                        unsafe_allow_html=True)
                    st.write("")
                    st.session_state.my_jobs.loc[selected_job_idx, '面试模拟完成'] = True
                    st.session_state.my_jobs.loc[selected_job_idx, '当前状态'] = '🏆 Offer 等待中'
                    if st.button("更新状态并返回看板"): st.rerun()