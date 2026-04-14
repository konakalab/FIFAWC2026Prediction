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

def load_train_data():
     file_train = 'table_FIFAWC2026Pred_Train.csv'
     if os.path.exists(file_train):
         return pd.read_csv(file_train)
     return None
 
df_train = load_train_data()

if df is not None:
    st.set_page_config(page_title="FIFA Predictions", layout="wide")
    st.title("⚽ FIFAワールドカップ2026予測")

    # 学習期間の表示
    if df_train is not None:
         df_train['date'] = pd.to_datetime(df_train['date'])
         start_date = df_train['date'].min().strftime('%Y-%m-%d')
         end_date = df_train['date'].max().strftime('%Y-%m-%d')
         info_text = (
        f"**モデル学習期間:** {start_date} ～ {end_date}\n\n"
        f"データは [International football results from 1872 to 2026]"
        f"(https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) "
        f"を利用しています。 "
    )
    
    st.info(info_text)
    st.divider()
    st.subheader("予測データ一覧")
    st.write("※列名をクリックするとソートできます。")

    # 指定された列のみを表示し、ソート可能なテーブルとして描画
    display_columns = [
        'Team', 'Group', 'isHome', 'Serial', 'Code', 
        'Rating', 
        'StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'
    ]

    # 数値列の表示形式を整える (小数点以下3桁など)
    st.dataframe(
        df[display_columns],
        use_container_width=True,
        column_config={
            "Rating": st.column_config.NumberColumn(format="%.2f"),
            "RatingOnScore": st.column_config.NumberColumn(format="%.2f"),
            "StInGS_1": st.column_config.NumberColumn("1位確率", format="%.3f"),
            "StInGS_2": st.column_config.NumberColumn("2位確率", format="%.3f"),
            "StInGS_3": st.column_config.NumberColumn("3位確率", format="%.3f"),
            "StInGS_4": st.column_config.NumberColumn("4位確率", format="%.3f"),
        },
        hide_index=True # インデックス列を非表示にする
    )
    
    st.divider()
    st.subheader(f"グループステージ順位予測")
    
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
            # 全体の基本フォントサイズ
            font=dict(size=18), 
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=10, r=10, t=10, b=10),
            legend_title=None,
            barmode='stack',
            
            # --- 軸のフォントサイズを個別に設定 ---
            xaxis=dict(
                tickfont=dict(size=20),  # 横軸（0.0〜1.0）の数値サイズ
            ),
            yaxis=dict(
                autorange="reversed",
                tickfont=dict(size=22),  # 縦軸（国名コード）のサイズをさらに大きく
            )
        )
        
        # グラフの表示
        st.plotly_chart(fig, use_container_width=True)
        st.divider()
