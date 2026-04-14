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

# 試合日程データの読み込み（Wikipediaから抽出した最新版を使用）
@st.cache_data
def load_match_data():
    file_match = 'matches_WC2026_wikipedia_standardized.csv'
    if os.path.exists(file_match):
        return pd.read_csv(file_match)
    return None

df_matches = load_match_data()

if df is not None:
    st.set_page_config(page_title="FIFA Predictions", layout="wide")
    st.title("⚽ FIFAワールドカップ2026予測")
    st.caption(f"Developed by [@konakalab](https://x.com/konakalab)")

    # 学習期間の表示（app (5).py 33-40行目のロジック）
    if df_train is not None:
         df_train['date'] = pd.to_datetime(df_train['date'])
         start_date = df_train['date'].min().strftime('%Y-%m-%d')
         end_date = df_train['date'].max().strftime('%Y-%m-%d')
         info_text = (
            f"**モデル学習期間:** {start_date} ～ {end_date}\n\n"
            f"データは [International football results from 1872 to 2026]"
            f"(https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) を使用しています。"
         )
         st.info(info_text)

    # --- 1. 予測データ一覧 (app (5).py 105-108行目の要素を最上部に移動) ---
    st.subheader("📊 予測データ一覧")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # --- 2. 各グループのタブ構成 (タブの中に「順位」と「H2H」を配置) ---
    groups = sorted(df['Group'].unique())
    group_tabs = st.tabs([f"Group {g}" for g in groups])

    for i, g in enumerate(groups):
        with group_tabs[i]:
            # A. グループ内順位確率 (app (5).py 45-55行目のロジック)
            st.header(f"Group {g} 予測順位")
            group_df = df[df['Group'] == g].sort_values('StInGS_1', ascending=False)
            
            fig_rank = px.bar(
                group_df, x='Team', y=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
                labels={'value': '確率', 'variable': '順位'},
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_rank.update_layout(xaxis_title="チーム", yaxis_title="確率")
            st.plotly_chart(fig_rank, use_container_width=True, key=f"rank_plot_{g}")

            st.divider()

            # B. H2H (app (5).py 60-103行目のロジックを各タブ内に配置)
            st.subheader(f"Group {g} 対戦カード比較 (H2H)")
            if df_matches is not None:
                current_group_matches = df_matches[df_matches['Group'] == g]
                
                for idx, row in current_group_matches.iterrows():
                    tA_info = df[df['Team'] == row['TeamA']]
                    tB_info = df[df['Team'] == row['TeamB']]
                    
                    if not tA_info.empty and not tB_info.empty:
                        # app (5).py 内のRatingに基づく計算ロジックを保持
                        rA = tA_info.iloc[0]['Rating']
                        rB = tB_info.iloc[0]['Rating']
                        codeA = tA_info.iloc[0]['Code']
                        codeB = tB_info.iloc[0]['Code']
                        
                        elo_diff = rA - rB
                        pWin = 1 / (1 + 10**(-elo_diff/2))
                        pDraw = 0.22 
                        pLose = 1 - pWin - pDraw
                        total = pWin + pDraw + pLose
                        pWin, pDraw, pLose = pWin/total, pDraw/total, pLose/total

                        st.write(f"**Match {row['MatchNumber']}: {row['TeamA']} vs {row['TeamB']}** ({row['Date']})")
                        
                        # app (5).py 76-103行目のgo.Figureのデザインを完全保持
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            y=["Match"], x=[pWin], orientation='h',
                            marker=dict(color='#1E88E5'), text=f"{pWin:.1%}", textposition='inside',
                            name=f"{codeA} 勝"
                        ))
                        fig.add_trace(go.Bar(
                            y=["Match"], x=[pDraw], orientation='h',
                            marker=dict(color='#BDBDBD'), text=f"{pDraw:.1%}", textposition='inside',
                            name="引き分け"
                        ))
                        fig.add_trace(go.Bar(
                            y=["Match"], x=[pLose], orientation='h',
                            marker=dict(color='#C62828'), text=f"{pLose:.1%}", textposition='inside',
                            name=f"{codeB} 勝"
                        ))

                        fig.update_layout(
                            barmode='stack', height=120, margin=dict(l=70, r=70, t=30, b=20),
                            showlegend=False, xaxis=dict(showticklabels=False, range=[0, 1], fixedrange=True),
                            yaxis=dict(showticklabels=False, fixedrange=True),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            annotations=[
                                dict(x=0, y=0.5, xref="x", yref="paper", text=f"<b>{codeA}</b>", showarrow=False, xanchor="right", xshift=-10, font=dict(size=20)),
                                dict(x=1, y=0.5, xref="x", yref="paper", text=f"<b>{codeB}</b>", showarrow=False, xanchor="left", xshift=10, font=dict(size=20))
                            ]
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"h2h_{g}_{idx}")
else:
    st.error("データファイルが見つかりません。")
    
