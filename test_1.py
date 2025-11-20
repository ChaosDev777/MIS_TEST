import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import sklearn as sk
from lightgbm import LGBMClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from openai import OpenAI
import json

from pyexpat.errors import messages
from statsmodels.graphics.tukeyplot import results

api_key="your key"
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


def ai_explain(task, method, ds_name, highlights):
    prompt=f"""
    你是数据科学助教。请用中文简要解读下面的模型结果，并给出3-5条面向管理者的可执行建议（使用•项目符号，不要输出代码）。
    任务：{task}；方法：{method}；数据集：{ds_name}
    关键结果：{highlights}
    请先用1-2句话说明结果意味着什么，再给出建议；尽量避免术语，聚焦业务含义。
    """
    return ask_ai(prompt,json_type=False)

def load_data(task,ds_name):
    ds=sk.datasets
    if task=="分类":
        if ds_name.startswith("Iris") :
            d = ds.load_iris()
        elif ds_name.startswith("Wine"):
            d = ds.load_wine()
        else:
            d = ds.load_breast_cancer()
    return d.data, d.target, d.feature_names, list(d.target_names)


def dss_model(task="分类", ds_name="Iris", method="DecisionTree"):

    X, y, feature_names, target_names = load_data(task, ds_name)


    X_tr, X_te, y_tr, y_te = sk.model_selection.train_test_split(
        X, y, test_size=0.2, random_state=0
    )

    if method == "DecisionTree":
        model = DecisionTreeClassifier(random_state=0)

    else:
        model=LGBMClassifier(random_state=0)

    model.fit(X_tr, y_tr)
    y_pred = model.predict(X_te)

    acc = accuracy_score(y_te, y_pred)
    cm = confusion_matrix(y_te, y_pred)
    highlights = f"准确率={acc:.3f}；混淆矩阵规模={cm.shape}"

    cm_df = pd.DataFrame(cm, index=[f"T_{t}" for t in np.unique(y)], columns=[f"P_{t}" for t in np.unique(y)])
    heat = alt.Chart(cm_df.reset_index().melt("index")).mark_rect().encode(
        x=alt.X("variable:N", title="Pred"),
        y=alt.Y("index:N", title="True"),
        color=alt.Color("value:Q", title="Count")
    ).properties(title="Confusion Matrix（SVG）")
    st.altair_chart(heat, use_container_width=True)

    ai_text = ai_explain(task, method, ds_name, highlights)
    st.subheader("AI解读与管理建议👾")
    st.write(ai_text)


dss_model()




