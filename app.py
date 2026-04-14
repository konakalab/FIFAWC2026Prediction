import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. データの読み込み
@st.cache_data
def load_data():
    # ファイル名を直接指定
    file_name = 'table_predInGS.csv'
    
    if not os.path.exists(file_name):
        st.error(f"エラー: '{file_name}' が見つかりません。GitHubリポジトリの直下にファイルを配置してください。")
        return None
    
    return pd.read_csv(file_name)

df = load_data()

if df is not None:
    # ページ設定
    st.set_page_config(page_title="FIFA Predictions", layout="wide")
    st.title("⚽ FIFA グループステージ順位予測")

    # 2. 全グループをループして表示
    # Group列が存在することを確認し、ソートしてループ
    groups = sorted(df['Group'].unique())

    for group_name in groups:
        st.subheader(f"Group {group_name}")
        
        # 該当グループのデータ抽出
        group_df = df[df['Group'] == group_name].copy()
        
        # 確率データを可視化用に整形（Wide to Long）
        plot_df = group_df.melt(
            id_vars=['Team'], 
            value_vars=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
            var_name='Rank', 
            value_name='Probability'
        )

        # ラベルの日本語化
        rank_labels = {
            'StInGS_1': '1位', 'StInGS_2': '2位', 
            'StInGS_3': '3位', 'StInGS_4': '4位'
        }
        plot_df['Rank'] = plot_df['Rank'].map(rank_labels)

        # 3. 帯グラフの作成
        fig = px.bar(
            plot_df, 
            y='Team', 
            x='Probability', 
            color='Rank',
            orientation='h',
            height=250, # 4チーム表示に最適な高さ
            color_discrete_map={
                '1位': '#003f5c', 
                '2位': '#7a5195', 
                '3位': '#ef5675', 
                '4位': '#ffa600'
            },
            category_orders={"Rank": ["1位", "2位", "3位", "4位"]}
        )

        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=10, r=10, t=10, b=10),
            legend_title=None,
            barmode='stack'
        )
        
        # グラフを表示
        st.plotly_chart(fig, use_container_width=True)
        st.divider()
