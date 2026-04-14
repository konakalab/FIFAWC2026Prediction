import streamlit as st
import pandas as pd
import plotly.express as px

# 1. データの読み込み
@st.cache_data
def load_data():
    # データ読み込み（エンコーディングは環境に合わせて調整してください）
    df_pred = pd.read_csv('table_predInGS.csv')
    df_flags = pd.read_csv('fifa_flag_complete.csv')
    # Codeをキーに結合
    df = pd.merge(df_pred, df_flags, on='Code', how='left')
    return df

df = load_data()

# ページ設定
st.set_page_config(page_title="FIFA Group Stage Predictions", layout="wide")
st.title("⚽ FIFA グループステージ順位予測確率")
st.write("各グループの1位〜4位通過確率を比較できます。")

# 2. 全グループを順にループ
groups = sorted(df['Group'].unique())

for group_name in groups:
    st.header(f"Group {group_name}")
    
    # 該当グループのデータ抽出
    group_df = df[df['Group'] == group_name].copy()
    
    # 確率データを可視化用に整形（Wide to Long）
    plot_df = group_df.melt(
        id_vars=['Team', 'Code'], 
        value_vars=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
        var_name='Rank', 
        value_name='Probability'
    )

    # ラベル変換
    rank_labels = {
        'StInGS_1': '1位', 'StInGS_2': '2位', 
        'StInGS_3': '3位', 'StInGS_4': '4位'
    }
    plot_df['Rank'] = plot_df['Rank'].map(rank_labels)

    # 3. 帯グラフ（積層棒グラフ）の作成
    fig = px.bar(
        plot_df, 
        y='Team', 
        x='Probability', 
        color='Rank',
        orientation='h',
        height=300,  # グループごとに高さを固定
        color_discrete_map={
            '1位': '#003f5c', # 濃い青
            '2位': '#7a5195', # 紫
            '3位': '#ef5675', # ピンク
            '4位': '#ffa600'  # オレンジ
        },
        category_orders={"Rank": ["1位", "2位", "3位", "4位"]}
    )

    # グラフのデザイン調整
    fig.update_layout(
        xaxis_title="確率 (1.0 = 100%)",
        yaxis_title=None,
        margin=dict(l=20, r=20, t=30, b=20),
        legend_title="予想順位",
        barmode='stack'
    )
    
    # 表示
    st.plotly_chart(fig, use_container_width=True)
    st.divider() # グループごとの区切り線
