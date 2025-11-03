import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from scipy.stats import norm
from statsmodels.tsa.holtwinters import SimpleExpSmoothing,ExponentialSmoothing

st.set_page_config(page_title="SCM简易系统（作业版）", page_icon="🐠", layout="wide")

st.title("🐠SCM简易系统（作业版）")
tab1,tab2=st.tabs(["需求预测","库存优化"])

with st.sidebar:
    st.header("数据与参数")
    use_demo=st.toggle("使用示例数据（104）周",value=True)
    up=st.file_uploader("或上传CSV（列包含：date,demand",type=["csv"])
    K=st.number_input("固定订货成本K",value=500.0,step=10.0)
    h=st.number_input("单位持有成本h（每期）",value=2.0,step=0.1)
    L=st.number_input("提前期L（期）",min_value=0,value=2,step=1)
    service_level=st.slider("目标服务水平",0.50,0.999,value=0.95)
    periods_per_year=st.number_input("一年包含期数如52",min_value=1,value=52,step=1)
    if use_demo:
        rng=pd.date_range("2023-01-01",periods=104,freq="W")
        season=20+5*np.sin(2*np.pi*(np.arange(104)/52))
        y=50+season+np.random.normal(0,2,size=104)
        df=pd.DataFrame({"date":rng,"demand":y})
    else:
        df=pd.read_csv(up)
        df["date"]=pd.to_datetime(df["date"])
        df=df.sort_values("date")

with tab1:
    st.subheader("需求预测")
    horizon=st.number_input("预测步数（期）",min_value=1,value=12,step=1)
    valid_size=st.number_input("留出评估集大小（期）",min_value=0,value=min(12,len(df)//5),step=1)
    method=st.selectbox("方法",["Naive","MA(移动平均)","SES","Holt-Winters"],index=0)

    y=df["demand"].astype(float).reset_index(drop=True)
    y_train=y.iloc[:-valid_size] if valid_size>0 else y.copy()
    y_valid=y.iloc[-valid_size:] if valid_size>0 else pd.Series(dtype=float)

    if method=="Naive":
        fcst=np.repeat(y_train.iloc[-1],horizon)
    elif method=="MA(移动平均)":
        window=st.number_input("MA窗口",min_value=2,value=4,step=1)
        ma_val=y_train.rolling(window).mean().iloc[-1]
        fcst=np.repeat(ma_val,horizon)
    elif method=="SES":
        model=SimpleExpSmoothing(y_train,initialization_method="heuristic").fit(optimized=True)
        fcst=model.forecast(horizon).values
    elif method=="Holt-Winters":
        sp=st.number_input("季节周期",min_value=2,value=12,step=1)
        model=ExponentialSmoothing(y_train,trend="add",seasonal="add",seasonal_periods=sp).fit(optimized=True)
        fcst=model.forecast(horizon).values



    if valid_size>0 and valid_size<=horizon:
        y_true=y_valid.values
        y_pred=fcst[:valid_size]
        mae=np.mean(np.abs(y_true-y_pred))
        mape=np.mean(np.abs((y_true-y_pred)/np.maximum(np.abs(y_true),1e-8)))*100
        st.write({"MAE":float(mae),"MAPE(%)":float(mape)})

    idx_train=np.arange(len(y_train))
    idx_valid=np.arange(len(y_train),len(y_train)+len(y_valid))
    idx_fcst=np.arange(len(y_train),len(y_train)+len(fcst))

    df_plot=pd.DataFrame(
        {
            "idx":list(idx_train)+list(idx_valid)+list(idx_fcst),
            "value":list(y_train.values)+list(y_valid.values)+list(fcst),
            "type":(["Train"]*len(idx_train))+(["Text"]*len(idx_valid))+(["Forecast"]*len(idx_fcst))
            }
        )
    chart=alt.Chart(df_plot).mark_line().encode(
        x=alt.X("idx:Q",title="period"),
        y=alt.Y("value:Q",title="demand"),
        color="type:N"
    ).properties(title="需求预测结果（SVG）").interactive()
    st.altair_chart(chart,use_container_width=True)

with tab2 :
    st.subheader("库存优化")
    annual_demand = np.mean(y_train) * periods_per_year
    EOQ = np.sqrt(2 * annual_demand * K / h)
    st.markdown("经济订货量EOQ：")
    st.write(EOQ)
    st.markdown("安全库存:")
    d=np.mean(y_train)
    sigma_d=np.std(y_train,ddof=1)
    z=norm.ppf(service_level)
    safety=z*sigma_d*np.sqrt(L)
    st.write(safety)
    service_levels = [0.80, 0.85, 0.90, 0.95, 0.99]
    z_values = [norm.ppf(sl) for sl in service_levels]

    df_z = pd.DataFrame({
        '服务水平': service_levels,
        'Z值': z_values,
        '安全库存': [z * sigma_d * np.sqrt(L) for z in z_values]
    })

    st.write("不同服务水平下的安全库存对比:")
    chart2 = alt.Chart(df_z).mark_line(point=True, color='#1f77b4', strokeWidth=4).encode(
        x=alt.X('服务水平:Q', title='服务水平'),
        y=alt.Y('安全库存:Q', title='安全库存')
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(chart2, use_container_width=True)



