import pandas as pd
import streamlit as st
from openai import OpenAI
import json
# 读取数据（核心数据来源,用读execel方法先简单实现后续用数据库操作代替）
df = pd.read_excel("school_major_data.xlsx")
# ---------------------- 智能匹配函数 ----------------------
def calculate_match_score(user_input, df):
    """
    计算匹配度得分
    user_input: 字典，存储用户输入（本科专业、目标分数、意向城市等）
    df: 院校专业数据DataFrame
    """
    df_copy = df.copy()  # 避免修改原数据
    target_score = user_input["target_score"]
    target_cities = user_input["target_cities"]  # 列表，如["上海", "南京"]
    undergrad_major = user_input["undergrad_major"]

    # 1. 分数匹配度（40分）
    df_copy["score_gap"] = abs(df_copy["近3年平均分"] - target_score)
    df_copy["score_match"] = df_copy["score_gap"].apply(
        lambda x: 40 if x <= 10 else (30 if x <= 20 else (20 if x <= 30 else (10 if x <= 50 else 0)))
    )

    # 2. 地域匹配度（20分）
    df_copy["city_match"] = df_copy["所在城市"].apply(lambda x: 20 if x in target_cities else 0)

    # 3. 专业匹配度（20分）
    # 预设专业相关性字典（可扩展更多专业）
    major_correlation = {
        "信息管理与信息系统": {"管理科学与工程": 1.0, "电子信息": 0.9, "图书情报":0.7,"大数据科学与商务分析":0.7,"计算机科学与技术": 0.65,"工程管理":0.6},
        "数据科学与大数据技术": {"电子信息": 1.0, "管理科学与工程": 0.9, "计算机科学与技术": 0.7,"工程管理": 0.6},
        "电子商务":{"管理科学与工程":1.0,"大数据科学与商务分析":0.9,"国际商务":0.8,"图书情报":0.7,"计算机科学与技术":0.6},
        "交叉科学实验班":{"管理科学与工程": 1.0, "电子信息": 0.9, "图书情报":0.7,"大数据科学与商务分析":0.8,"计算机科学与技术": 0.8}
    }
    # 若用户专业不在字典中，默认相关性0.3(三分天注定，七分靠打拼)
    df_copy["major_match"] = df_copy["专业名称"].apply(
        lambda x: 20 * major_correlation.get(undergrad_major, {}).get(x, 0.3)
    )

    # 4. 报录比友好度（10分）
    # 提取报录比数值（如"8:1"→8）
    df_copy["admission_ratio_num"] = df_copy["报录比"].astype(str).str.split(":").str[0].astype(int)
    df_copy["ratio_match"] = df_copy["admission_ratio_num"].apply(
        lambda x: 10 if x <= 5 else (8 if x <= 8 else (6 if x <= 12 else (3 if x <= 15 else 0)))
    )

    # 5. 推免比例友好度（10分）
    # 提取推免比例数值（如"20%"→20）
    def extract_reco_num(reco_str):
        try:
            return int(str(reco_str).strip("%"))
        except (IndexError, ValueError):
            return 25  # 默认推免比例25%

    df_copy["recommendation_ratio_num"] = df_copy["推免比例"].apply(extract_reco_num)
    df_copy["recommendation_match"] = df_copy["recommendation_ratio_num"].apply(
        lambda x: 10 if x <= 20 else (8 if x <= 30 else (5 if x <= 40 else 0))
    )

    # 计算总匹配度得分（四舍五入保留1位小数）
    df_copy["total_match_score"] = (
        df_copy["score_match"] + df_copy["city_match"] + df_copy["major_match"] +
        df_copy["ratio_match"] + df_copy["recommendation_match"]
    ).round(1)

    # 按得分降序排序，返回前10个匹配结果
    result = df_copy.sort_values("total_match_score", ascending=False).head(10)
    return result[["院校名称", "专业名称", "近3年平均分", "报录比", "招生人数", "推免比例", "total_match_score"]]

# ---------------------- 专业查询函数 ----------------------
def query_major_by_code(df, major_code):
    # 精准匹配专业代码（忽略大小写/空格）
    df["专业代码"] = df["专业代码"].astype(str).str.strip()
    filtered_df = df[df["专业代码"] == major_code.strip()]
    return filtered_df

# ---------------------- 院校查询函数 ----------------------
def query_majors_by_school(df, school_name):
    """根据院校名称+院校类型，查询该院校所有专业"""
    df_copy = df.copy()
    # 模糊匹配院校名称（支持输入关键词，如“上海财经”匹配“上海财经大学”）
    if school_name:
        df_copy = df_copy[df_copy["院校名称"].str.contains(school_name, na=False, case=False)]

    return df_copy

# Streamlit页面布局
st.set_page_config(page_title="考研助力（财大信）", page_icon="🐠", layout="wide")
st.title("💻考研助力系统（财大信院专属版）")
#三个页面设计
tab1,tab2,tab3=st.tabs(["考研院校专业智能匹配","专业查询","院校查询"])

# 考研院校专业智能匹配页面
with tab1:
    # 1. 用户输入区域
    with st.form("user_input_form"):
        undergrad_major = st.selectbox("本科专业", ["信息管理与信息系统", "电子商务", "数据科学与大数据技术", "交叉科学实验班"])
        target_score = st.number_input("目标分数", min_value=200, max_value=500, value=360)
        target_cities = st.multiselect("意向城市", ["上海", "北京", "南京", "杭州", "广州","厦门","武汉","西安"], default=["上海"])
        submit_btn = st.form_submit_button("开始匹配")

    # 2. 点击匹配后展示结果
    if submit_btn:
        # 整理用户输入
        user_input = {
            "undergrad_major": undergrad_major,
            "target_score": target_score,
            "target_cities": target_cities
        }
        # 调用算法得到匹配结果
        match_result = calculate_match_score(user_input, df)

        # 展示匹配结果表格
        st.subheader("匹配结果（按匹配度降序）")
        st.dataframe(match_result, use_container_width=True)

        # 展示匹配度柱状图（可视化加分）
        st.subheader("各院校匹配度对比")
        school_avg_score = match_result.groupby("院校名称")["total_match_score"].mean().reset_index()
        school_avg_score.rename(columns={"total_match_score": "匹配度平均分"}, inplace=True)
        st.bar_chart(school_avg_score, x="院校名称", y="匹配度平均分", use_container_width=True)

        # 展示详细信息（点击展开）
        for idx, row in match_result.iterrows():
            with st.expander(f"🔍 {row['院校名称']} - {row['专业名称']}（匹配度：{row['total_match_score']}分）"):
                st.write(f"近3年平均分：{row['近3年平均分']}分")
                st.write(f"报录比：{row['报录比']}（竞争越小越友好）")
                st.write(f"招生人数：{row['招生人数']}人（统考名额=招生人数×(1-推免比例)）")
                st.write(f"推免比例：{row['推免比例']}（比例越低，统考机会越大）")

with tab2:
    st.subheader("专业代码精准查询")
    # 读取全量数据（和Tab1共用同一个Excel）
    df_query = pd.read_excel("school_major_data.xlsx")
    df_query.rename(columns={
        "学校名称": "院校名称",
        "近三年平均分": "近3年平均分",
        "推免率": "推免比例"
    }, inplace=True)

    # 输入专业代码
    major_code_input = st.text_input(
        "请输入专业代码",
        placeholder="例如：120102、081200、120108",
        help="支持纯数字/带字母的专业代码，如085400（电子信息）"
    )
    query_btn = st.button("查询专业信息", type="primary")

    # 查询结果展示
    if query_btn:
        if not major_code_input:
            st.warning("请输入专业代码后再查询！")
        else:
            # 调用查询函数
            result_df = query_major_by_code(df_query, major_code_input)

            if result_df.empty:
                st.error(f"未查询到专业代码【{major_code_input}】对应的专业，请核对代码是否正确！")
            else:
                st.success(f"查询到 {len(result_df)} 条匹配的专业信息：")

                # 展示核心信息表格
                core_columns = ["院校名称", "专业名称", "专业代码", "所在城市", "近3年平均分", "报录比", "推免比例"]
                st.dataframe(result_df[core_columns], use_container_width=True)

                # 展开查看详细信息
                st.subheader("专业详细信息")
                for idx, row in result_df.iterrows():
                    with st.expander(f"📚 {row['院校名称']} - {row['专业名称']}（代码：{row['专业代码']}）"):
                        # 分两列展示，更清晰
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("### 基础信息")
                            st.write(f"✅ 院校名称：{row['院校名称']}")
                            st.write(f"✅ 专业名称：{row['专业名称']}")
                            st.write(f"✅ 专业代码：{row['专业代码']}")
                            st.write(f"✅ 所在城市：{row['所在城市']}")
                            st.write(f"✅ 招生人数：{row['招生人数']} 人/年")
                        with col2:
                            st.write("### 录取相关")
                            st.write(f"📊 近3年平均分：{row['近3年平均分']} 分")
                            st.write(f"📊 报录比：{row['报录比']}（竞争比）")
                            st.write(f"📊 推免比例：{row['推免比例']}（统考名额={row['招生人数']}×(1-{row['推免比例']})）")

with tab3:
    st.subheader("院校精准查询（查看院校所有专业）")
    # 读取全量数据（和前两个Tab共用同一个Excel，无需新增数据）
    df_school = pd.read_excel("school_major_data.xlsx")
    df_school.rename(columns={
        "学校名称": "院校名称",
        "近三年平均分": "近3年平均分",
        "推免率": "推免比例"
    }, inplace=True)

    # 🔧 核心修改1：删除院校类型筛选，仅保留「院校名称模糊搜索」
    school_name_input = st.text_input(
        "输入院校名称/关键词",
        placeholder="例如：上海财经、复旦、西安交大、上海",
        help="支持模糊搜索，输入部分名称即可匹配（如输入“上海”，显示所有上海的院校）",
        label_visibility="visible"
    )

    # 查询按钮
    school_query_btn = st.button("查询院校及专业", type="primary")

    # 查询结果展示（同步简化，删除类型相关统计和表格列）
    if school_query_btn:
        # 调用修改后的院校查询函数（仅传院校名称参数）
        result_school = query_majors_by_school(df_school, school_name_input)

        if result_school.empty:
            st.error(f"未查询到【{school_name_input}】相关院校，请调整查询关键词！")
        else:
            # 统计匹配的院校数量和专业数量（不变，仅删除类型相关）
            school_count = result_school["院校名称"].nunique()
            major_count = len(result_school)
            st.success(f"查询到 {school_count} 所院校，共 {major_count} 个专业：")

            school_columns = [
                "院校名称", "所在城市", "专业名称", "专业代码",
                "近3年平均分", "报录比", "招生人数", "推免比例"
            ]
            st.dataframe(
                result_school[school_columns],
                use_container_width=True,
                column_config={
                    "近3年平均分": st.column_config.NumberColumn(),
                    "招生人数": st.column_config.NumberColumn()
                }
            )

            # 展开查看院校及专业详细信息（按院校分组，无变化）
            st.subheader("院校及专业详细信息")
            unique_schools = result_school["院校名称"].unique()
            for school in unique_schools:
                school_majors = result_school[result_school["院校名称"] == school]
                with st.expander(f"🏫 {school}（共 {len(school_majors)} 个专业）"):
                    # 院校基础信息（删除院校类型展示）
                    school_info = school_majors.iloc[0]
                    st.write("### 院校基础信息")
                    st.write(f"✅ 院校名称：{school_info['院校名称']}")
                    st.write(f"✅ 所在城市：{school_info['所在城市']}")
                    st.write("---")

                    # 该院校所有专业详情（无变化）
                    st.write("### 院校所有专业详情")
                    for idx, major in school_majors.iterrows():
                        st.write(f"#### 📚 专业：{major['专业名称']}（代码：{major['专业代码']}）")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"- 近3年平均分：{major['近3年平均分']} 分")
                            st.write(f"- 报录比：{major['报录比']}（竞争比）")
                        with col_b:
                            st.write(f"- 招生人数：{major['招生人数']} 人/年")
                            st.write(f"- 推免比例：{major['推免比例']}（统考名额充足度）")
                        st.write("---")


#AI智能助手
api_key=""
api_base="https://maas-api.cn-huabei-1.xf-yun.com/v1"
MODEL_ID="xop3qwen1b7"
client=OpenAI(api_key=api_key,base_url=api_base)
def ask_ai(messages,json_type=True,model_id=MODEL_ID) :
    json_messages=[{"role":"user","content":messages}]
    if json_type:
        extra_body={
            "response_format":{"type":"json_object"},
            "search_disable":True

        }
    else:
        extra_body={}
    response=client.chat.completions.create(model=model_id,messages=json_messages,extra_body=extra_body)
    message=response.choices[0].message.content
    if json_type:
        message=json.loads(message)
    return message
def ai_explain(major,score,aim_school,aim_major):
    prompt=f"""
    你是一位考研指导方面的专家，请你根据学生的本科所学的专业{major}，考研目前预估分数{score}，
    目标院校{aim_school}及目标专业{aim_major},给出建议，用中文表述。
    """
    return ask_ai(prompt,json_type=False)

with st.sidebar:
    st.subheader("AI建议")
    major1=st.text_input("输入你所学的专业")
    score1=st.text_input("输入你现水平预估成绩")
    aim_school1=st.text_input("输入你目标院校")
    aim_major1=st.text_input("输入你的目标专业")
    ai_text=ai_explain(major1,score1,aim_school1,aim_major1)

    st.subheader("建议：")
    st.write(ai_text)
