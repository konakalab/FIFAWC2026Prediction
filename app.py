import streamlit as st
import pandas as pd
import plotly.express as px
import os

@st.cache_data
def load_data():
    file_name = 'table_predInGS.csv'
    if not os.path.exists(file_name):
        return None
    return pd.read_csv(file_name)

df = load_data()

if df is not None:
    st.set_page_config(page_title="FIFA Predictions", layout="wide")
    st.title("⚽ FIFA グループステージ順位予測")

    # グループ名のリストを取得
    groups = sorted(df['Group'].unique())

    # カラーマップの定義（前回同様のカスタムカラー）
    custom_colors = {
        '1位': '#003f5c', 
        '2位': '#7a5195', 
        '3位': '#ef5675', 
        '4位': '#ffa600'
    }

    for group_name in groups:
        st.subheader(f"Group {group_name}")
        
        # 該当グループのデータを抽出
        group_df = df[df['Group'] == group_name].copy()
        
        # 確率データを可視化用に整形（TeamではなくCodeを軸にするためCodeを保持）
        plot_df = group_df.melt(
            id_vars=['Code'], 
            value_vars=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
            var_name='Rank', 
            value_name='Probability'
        )

        # ランクの表示名を変換
        rank_labels = {'StInGS_1': '1位', 'StInGS_2': '2位', 'StInGS_3': '3位', 'StInGS_4': '4位'}
        plot_df['Rank'] = plot_df['Rank'].map(rank_labels)

        # 帯グラフの作成（y軸をCodeに変更）
        fig = px.bar(
            plot_df, 
            y='Code', 
            x='Probability', 
            color='Rank',
            orientation='h',
            height=300, 
            color_discrete_map=custom_colors,
            category_orders={"Rank": ["1位", "2位", "3位", "4位"]}
        )

        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            # 文字サイズをさらに大きく設定
            font=dict(size=18), 
            margin=dict(l=10, r=10, t=10, b=10),
            legend_title=None,
            barmode='stack',
            # Y軸（3文字コード）の順序を逆転させ、上が1番目になるように設定
            yaxis=dict(autorange="reversed") 
        )
        
        # グラフの表示
        st.plotly_chart(fig, use_container_width=True)
        st.divider()
