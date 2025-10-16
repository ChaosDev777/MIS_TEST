import streamlit as st
import pandas as pd
import sqlite3

from numpy.f2py.crackfortran import updatevars

st.set_page_config(page_title="个人信息管理系统", page_icon="👩🏻‍🦱", layout="wide")
st.title("😺个人信息管理系统")
conn=sqlite3.connect("PIMS.db")
print("open database successfully")
conn.execute("PRAGMA foreign_keys=ON;")
conn.execute("""
CREATE TABLE IF NOT EXISTS personal_message(
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_name TEXT, gender CHAR(2), phone CHAR(11),age INT UNSIGNED
);
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS personal_schedule(
ps_id INTEGER PRIMARY KEY AUTOINCREMENT,
PS_name TEXT,PS_category TEXT,PS_note TEXT,PS_created_at TEXT,status TEXT, user_id INT,
FOREIGN KEY (user_id) REFERENCES personal_message(user_id)
);
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS personal_honor(
ph_id INTEGER PRIMARY KEY AUTOINCREMENT,
PH_name TEXT,PH_category TEXT,time TEXT,PH_note TEXT,user_id INT,
FOREIGN KEY (user_id) REFERENCES personal_message(user_id)
);
"""
)
st.markdown("个人基础信息表")
with st.form("add_form_message",clear_on_submit=True):
    name=st.text_input("name")
    gender=st.selectbox("cate",["男","女"])
    phone=st.text_input("phone_number")
    age=st.text_input("age")
    submit=st.form_submit_button("提交",type="primary",use_container_width=True)
    if submit:
        conn.execute(f"""
        INSERT INTO personal_message(user_name,gender,phone,age)
        VALUES("{name}","{gender}","{phone}","{age}");
        """)
        conn.commit()
        st.success("提交成功✅")

st.markdown("个人日程信息表")
with st.form("add_form_schedule",clear_on_submit=True):
    name=st.text_input("name")
    cate=st.selectbox("cate",["工作","学习","社交","生活"])
    note=st.text_area("note")
    statue=st.radio("状态",["已完成","待处理","进行中"])
    user_id=st.number_input("user_id")
    submit=st.form_submit_button("提交",type="primary",use_container_width=True)
    if submit:
        conn.execute(f"""
        INSERT INTO personal_schedule(PS_name,PS_category,PS_note,PS_created_at,status,user_id)
        VALUES("{name}","{cate}","{note}",datetime('now'),"{statue}","{user_id}");
        """)
        conn.commit()
        st.success("提交成功✅")

st.markdown("个人荣誉信息表")
with st.form("add_form_honor",clear_on_submit=True):
    name=st.text_input("name")
    cate=st.selectbox("cate",["荣誉","奖项","证书"])
    time=st.text_input("time")
    note=st.text_area("note")
    user_id=st.number_input("user_id")
    submit=st.form_submit_button("提交",type="primary",use_container_width=True)
    if submit:
        conn.execute(f"""
        INSERT INTO personal_honor(PH_name,PH_category,time,PH_note,user_id)
        VALUES("{name}","{cate}","{time}","{note}","{user_id}");
        """)
        conn.commit()
        st.success("提交成功✅")

st.markdown("数据更新")
with st.form ("update_form",clear_on_submit=True) :
    t_name=st.text_input("table_name")
    row=st.text_input("update_row")
    updatevar=st.text_input("value")
    cond=st.text_input("condition")
    submit = st.form_submit_button("提交", type="primary", use_container_width=True)
    if  submit:
        conn.execute(f"""
        UPDATE {t_name}
        SET {row}={updatevar}
        WHERE {cond};
        """)
        conn.commit()
        st.success("提交成功✅")
st.markdown("数据删除")
with st.form("delete_form",clear_on_submit=True):
    t_name = st.text_input("table_name")
    cond = st.text_input("condition")
    submit = st.form_submit_button("提交", type="primary", use_container_width=True)
    if submit:
        conn.execute(f"""
        DELETE FROM {t_name}
        WHERE {cond};
        """)
        conn.commit()
        st.success("提交成功✅")


sql3="SELECT personal_schedule.user_id,user_name,gender,PS_name,PS_category,PS_note,PS_created_at,status FROM personal_schedule,personal_message WHERE personal_schedule.user_id=personal_message.user_id;"
sql2="SELECT *FROM personal_message;"
sql='SELECT personal_honor.user_id,user_name,gender,PH_name,PH_category,time,PH_note FROM personal_honor,personal_message WHERE personal_honor.user_id=personal_message.user_id;'
d=pd.read_sql(sql,conn)
d2=pd.read_sql(sql2,conn)
d3=pd.read_sql(sql3,conn)
st.markdown("个人基本信息表查询")
st.write(d2)
st.markdown("个人信息及荣誉查询")
st.write(d)
st.markdown("个人信息及日程安排查询")
st.write(d3)