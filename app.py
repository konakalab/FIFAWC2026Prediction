import streamlit as st
import pandas as pd
import plotly.express as px
import os
import plotly.graph_objects as go

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
    st.caption(f"Developed by [@konakalab](https://x.com/konakalab)")

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
    st.subheader("グループステージ")
    st.write("※列名をクリックするとソートできます。")

    # 1. 表示する変数をユーザー提示のリストに完全一致させる
    display_columns = [
        'Team', 'Code', 'Group', 'isHome', 
        'Rating', 
        'StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'
    ]

    # 2. 描画用の一次変数として抽出
    df_display = df[display_columns].copy()

    # 3. スタイリング（formatのキーをdisplay_columnsにあるものだけに修正）
    styled_df = df_display.style.background_gradient(
        cmap='RdYlGn', 
        subset=['Rating'],
        low=0.2, 
        high=0.2
    ).background_gradient(
        cmap='Blues',      # 確率は青系のスケールなど、色を変えると見やすいです
        subset=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
        vmin=0.0,          # 最小値を0に固定
        vmax=1.0           # 最大値を1に固定
    ).format({
        'Rating': '{:.2f}',
        'StInGS_1': '{:.3f}',
        'StInGS_2': '{:.3f}',
        'StInGS_3': '{:.3f}',
        'StInGS_4': '{:.3f}'
    })
        
    # 4. ソート可能なテーブルとして描画
    st.dataframe(
        styled_df,
        use_container_width=True,
        column_config={
            "Team": "チーム名",
            "Code": "コード",
            "Group": "グループ",
            "isHome": "開催国",
            "Rating": "評価値",
            "StInGS_1": "GS1位確率",
            "StInGS_2": "GS2位確率",
            "StInGS_3": "GS3位確率",
            "StInGS_4": "GS4位確率",
        },
        hide_index=True
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

def show_h2h_visuals():
    file_h2h = 'table_prediction_h2h.csv'
    if not os.path.exists(file_h2h):
        st.error(f"{file_h2h} が見つかりません。")
        return

    df_h2h = pd.read_csv(file_h2h)
    
    st.write("---")
    st.subheader("📊 グループステージ各試合の勝率予測")

    groups = sorted(df_h2h['Group'].unique())
    tabs = st.tabs([f"Group {g}" for g in groups])

    for i, group_name in enumerate(groups):
        with tabs[i]:
            group_matches = df_h2h[df_h2h['Group'] == group_name]
            
            for idx, row in group_matches.iterrows():
                # --- ヘッダー部分（日付と外部リンク） ---
                # カラムを使って日付の横にリンクを配置
                col_date, col_link = st.columns([0.85, 0.15])
                with col_date:
                    # グラフの上部に余白を作るためのスペーサー
                    st.write("") 
                
                # --- Plotly 帯グラフの作成 ---
                fig = go.Figure()

                # Team A 勝率 (緑)
                fig.add_trace(go.Bar(
                    x=[row['pWin']], y=["Match"],
                    orientation='h',
                    marker=dict(color='#2E7D32'),
                    text=f"{row['pWin']:.1%}", textposition='inside',
                    name=f"{row['CodeA']} 勝"
                ))

                # 引き分け (グレー)
                fig.add_trace(go.Bar(
                    x=[row['pDraw']], y=["Match"],
                    orientation='h',
                    marker=dict(color='#BDBDBD'),
                    text=f"{row['pDraw']:.1%}", textposition='inside',
                    name="引分"
                ))

                # Team B 勝率 (赤)
                fig.add_trace(go.Bar(
                    x=[row['pLose']], y=["Match"],
                    orientation='h',
                    marker=dict(color='#C62828'),
                    text=f"{row['pLose']:.1%}", textposition='inside',
                    name=f"{row['CodeB']} 勝"
                ))

                fig.update_layout(
                    barmode='stack',
                    height=120,
                    margin=dict(l=70, r=70, t=30, b=20),
                    showlegend=False,
                    xaxis=dict(showticklabels=False, range=[0, 1], fixedrange=True),
                    yaxis=dict(showticklabels=False, fixedrange=True),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    annotations=[
                        # 左側：国名コード
                        dict(
                            x=0, y=0.5, xref="x", yref="paper",
                            text=f"<b>{row['CodeA']}</b>", showarrow=False,
                            xanchor="right", xshift=-10, font=dict(size=20)
                        ),
                        # 右側：国名コード
                        dict(
                            x=1, y=0.5, xref="x", yref="paper",
                            text=f"<b>{row['CodeB']}</b>", showarrow=False,
                            xanchor="left", xshift=10, font=dict(size=20)
                        ),
                        # 日付とリンクのアイコン（テキストとして埋め込み）
                        dict(
                            x=0.5, y=1.35, xref="paper", yref="paper",
                            text=f"📅 {row['Date']} <a href='{row['matchURL']}' target='_blank'>↗</a>",
                            showarrow=False,
                            font=dict(size=14, color="#555555")
                        )
                    ]
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"h2h_{idx}")

# アプリのメイン処理の中で呼び出し
if df is not None:
    # (既存のテーブルやグラフ表示)
    show_h2h_visuals()
