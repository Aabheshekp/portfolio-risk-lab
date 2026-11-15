from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Portfolio Risk Lab",page_icon="📈",layout="wide")
st.title("Portfolio Risk Lab")
st.caption("Explore historical risk metrics from sample asset prices. This is educational software, not financial advice.")
prices=pd.read_csv(Path(__file__).parent/"data"/"prices.csv",parse_dates=["date"]).pivot(index="date",columns="asset",values="close").sort_index()
assets=st.sidebar.multiselect("Assets",list(prices.columns),default=list(prices.columns))
if not assets: st.warning("Select one or more assets."); st.stop()
ret=prices[assets].pct_change().dropna()
weights={asset:st.sidebar.slider(f"Weight: {asset}",0,100,max(0,(100//len(assets)//5)*5),5)/100 for asset in assets}
total=sum(weights.values())
if total==0: st.error("Combined weight must be greater than zero."); st.stop()
w=pd.Series(weights)/total
portfolio=(ret*w).sum(axis=1)
vol=portfolio.std()*252**0.5; ann=portfolio.mean()*252; wealth=(1+portfolio).cumprod(); dd=wealth/wealth.cummax()-1
a,b,c,d=st.columns(4)
a.metric("Annualized return",f"{ann:.1%}")
b.metric("Annualized volatility",f"{vol:.1%}")
c.metric("Sharpe (rf=0)",f"{ann/vol:.2f}" if vol else "n/a")
d.metric("Maximum drawdown",f"{dd.min():.1%}")
st.subheader("Normalized asset prices"); st.line_chart(prices[assets]/prices[assets].iloc[0]*100)
left,right=st.columns(2)
with left: st.subheader("Portfolio growth of $1"); st.line_chart(wealth)
with right: st.subheader("Daily return correlation"); st.dataframe(ret.corr().style.format("{:.2f}"),use_container_width=True)
st.subheader("Daily returns"); st.line_chart(ret)
st.download_button("Download returns",ret.to_csv(),"daily-returns.csv","text/csv")
st.info("Metrics use sample daily closes and 252 trading days. Past returns do not predict future results; taxes, fees, and market impact are omitted.")
