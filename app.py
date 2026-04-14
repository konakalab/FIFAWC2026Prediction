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

    groups = sorted(df['Group'].unique())

    # --- カラーマップの定義 ---
    # 使用しているのは特定のプリセットではなく、視認性の高いカスタムカラーです
    custom_colors = {
        '1位': '#003f5c', # 濃紺（信頼感・通過確実）
        '2位': '#7a5195', # 紫
        '3位': '#ef5675', # ピンク・赤系
        '4位': '#ffa600'  # オレンジ（警告・敗退）
    }

    for group_name in groups:
        st.subheader(f"Group {group_name}")
        
        group_df = df[df['Group'] == group_name].copy()
        
        # チームの並び順を「元データの順（上が1番目）」に固定するための処理
        # Plotlyはデフォルトで下から描画するため、y軸の設定で逆にします
        
        plot_df = group_df.melt(
            id_vars=['Team'], 
            value_vars=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
            var_name='Rank', 
            value_name='Probability'
        )

        rank_labels = {'StInGS_1': '1位', 'StInGS_2': '2位', 'StInGS_3': '3位', 'StInGS_4': '4位'}
        plot_df['Rank'] = plot_df['Rank'].map(rank_labels)

        fig = px.bar(
            plot_df, 
            y='Team', 
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
            # 文字サイズを大きく設定 (デフォルトは約12)
            font=dict(size=16), 
            margin=dict(l=10, r=10, t=10, b=10),
            legend_title=None,
            barmode='stack',
            # Y軸（チーム名）の順序を逆にする（上を1番目に）
            yaxis=dict(autorange="reversed") 
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.divider()
