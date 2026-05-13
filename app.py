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
            f"**モデル学習期間:** {start_date} ～ {end_date}.  "
            f"データは [International football results from 1872 to 2026]"
            f"(https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) "
            f"を利用しています。 "
        )
         st.info(info_text)

    st.divider()
    
    # --- 1. 予測データ一覧 (最上部に配置) ---
    st.subheader("予測データ一覧")
    st.subheader("大会予測")

    file_overall = 'table_overallPrediction.csv'
    if os.path.exists(file_overall):
        df_overall = pd.read_csv(file_overall)
        
        # 表示する列の定義
        overall_cols = [
            'Team', 'Code', 'Group', 'isHome', 'Rating', 
            'PredStanding_1', 'PredStanding_2', 'PredStanding_3', 'PredStanding_4', 
            'PredStanding_5', 'PredStanding_6', 'PredStanding_7', 'PredStanding_8'
        ]
        
        # 優勝確率順にソート
        df_overall_display = df_overall[overall_cols].sort_values('PredStanding_1', ascending=False)

        # 確率列（PredStanding_1〜8）のリスト
        prob_cols = [f'PredStanding_{i}' for i in range(1, 9)]

        # スタイル適用：Ratingは既存設定、順位確率はBlues（青系）を適用
        styled_overall = df_overall_display.style.background_gradient(
            cmap='RdYlGn', subset=['Rating'], low=0.2, high=0.2
        ).background_gradient(
            cmap='Blues',  # グループステージと同じ青系に統一
            subset=prob_cols,
            vmin=0.0, vmax=1.0
        ).format({
            'Rating': '{:.2f}',
            **{col: '{:.3f}' for col in prob_cols}
        })

        st.dataframe(
            styled_overall,
            use_container_width=True,
            column_config={
                "Team": "チーム名",
                "Code": "コード",
                "Group": "グループ",
                "isHome": "開催国",
                "Rating": "評価値",
                "PredStanding_1": "優勝",
                "PredStanding_2": "準優勝",
                "PredStanding_3": "3位",
                "PredStanding_4": "4位",
                "PredStanding_5": "ベスト8",
                "PredStanding_6": "ベスト16",
                "PredStanding_7": "ベスト32",
                "PredStanding_8": "GS敗退",
            },
            hide_index=True
        )
    else:
        st.write("大会予測データが見つかりません。")
        
    st.divider()

    st.subheader("グループステージ")
    st.write("※列名をクリックするとソートできます。")

    display_columns = [
        'Team', 'Code', 'Group', 'isHome', 
        'Rating', 
        'StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'
    ]

    df_display = df[display_columns].copy()

    styled_df = df_display.style.background_gradient(
        cmap='RdYlGn', 
        subset=['Rating'],
        low=0.2, 
        high=0.2
    ).background_gradient(
        cmap='Blues',      
        subset=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
        vmin=0.0,          
        vmax=1.0           
    ).format({
        'Rating': '{:.2f}',
        'StInGS_1': '{:.3f}',
        'StInGS_2': '{:.3f}',
        'StInGS_3': '{:.3f}',
        'StInGS_4': '{:.3f}'
    })
        
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

    # --- 2. 各グループのタブ構成 ---
    file_h2h = 'table_prediction_h2h.csv'
    df_h2h = None
    if os.path.exists(file_h2h):
        df_h2h = pd.read_csv(file_h2h)

    groups = sorted(df['Group'].unique())
    tabs = st.tabs([f"Group {g}" for g in groups])

    custom_colors = {
        '1位': '#003f5c', 
        '2位': '#7a5195', 
        '3位': '#ef5675', 
        '4位': '#ffa600'
    }

    for i, group_name in enumerate(groups):
        with tabs[i]:
           # --- タブ内上部：グループステージ順位予測の帯グラフ ---
            group_df = df[df['Group'] == group_name].copy()
            # チームのCodeをリスト化して "/" で結合
            team_codes = "/".join(group_df['Code'].tolist())
            st.subheader(f"Group {group_name} 順位予測 ({team_codes})")
            
            plot_df = group_df.melt(
                id_vars=['Code'], 
                value_vars=['StInGS_1', 'StInGS_2', 'StInGS_3', 'StInGS_4'],
                var_name='Rank', 
                value_name='Probability'
            )
            rank_labels = {'StInGS_1': '1位', 'StInGS_2': '2位', 'StInGS_3': '3位', 'StInGS_4': '4位'}
            plot_df['Rank'] = plot_df['Rank'].map(rank_labels)

            fig_rank = px.bar(
                plot_df, 
                y='Code', 
                x='Probability', 
                color='Rank',
                orientation='h',
                height=300, 
                color_discrete_map=custom_colors,
                category_orders={"Rank": ["1位", "2位", "3位", "4位"]}
            )

            fig_rank.update_layout(
                font=dict(size=18), 
                xaxis_title=None,
                yaxis_title=None,
                margin=dict(l=10, r=10, t=10, b=10),
                # 凡例をグラフ上部に水平配置
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                legend_title=None,
                barmode='stack',
                xaxis=dict(tickfont=dict(size=20)),
                yaxis=dict(autorange="reversed", tickfont=dict(size=22))
            )
            st.plotly_chart(fig_rank, use_container_width=True, key=f"rank_{group_name}")

            st.divider()

            # --- タブ内下部：各試合の勝率予測 (H2H) ---
            if df_h2h is not None:
                st.subheader(f"Group {group_name} 各試合の勝率予測")
                group_matches = df_h2h[df_h2h['Group'] == group_name]
                
                for idx, row in group_matches.iterrows():
                    st.write(f"**{row['Date']} {row['TeamA']} vs {row['TeamB']}**")
                    
                    fig_h2h = go.Figure()
                    fig_h2h.add_trace(go.Bar(
                        x=[row['pWin']], y=["Match"],
                        orientation='h',
                        marker=dict(color='#2222EE'),
                        text=f"{row['CodeA']} {row['pWin']:.1%}",
                        textposition='inside',
                        insidetextanchor='middle',
                        textfont=dict(size=20),
                        hoverinfo="skip",
                        name=f"{row['CodeA']} 勝"
                    ))
                    fig_h2h.add_trace(go.Bar(
                        x=[row['pDraw']], y=["Match"],
                        orientation='h',
                        marker=dict(color='#BDBDBD'),
                        text=f"Draw {row['pDraw']:.1%}",
                        textposition='inside',
                        insidetextanchor='middle',
                        textfont=dict(size=20),
                        hoverinfo="skip",
                        name="引分"
                    ))
                    fig_h2h.add_trace(go.Bar(
                        x=[row['pLose']], y=["Match"],
                        orientation='h',
                        marker=dict(color='#C62828'),
                        text=f"{row['CodeB']} {row['pLose']:.1%}",
                        textposition='inside',
                        insidetextanchor='middle',
                        textfont=dict(size=20),
                        hoverinfo="skip",
                        name=f"{row['CodeB']} 勝"
                    ))

                    fig_h2h.update_layout(
                        barmode='stack',
                        height=90,
                        margin=dict(l=70, r=70, t=00, b=0),
                        showlegend=False,
                        xaxis=dict(showticklabels=False, range=[0, 1], fixedrange=True),
                        yaxis=dict(showticklabels=False, fixedrange=True),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        annotations=[
                            dict(
                                x=0, y=0.5, xref="x", yref="paper",
                                text=f"<b>{row['CodeA']}</b>", showarrow=False,
                                xanchor="right", xshift=-10, font=dict(size=20)
                            ),
                            dict(
                                x=1, y=0.5, xref="x", yref="paper",
                                text=f"<b>{row['CodeB']}</b>", showarrow=False,
                                xanchor="left", xshift=10, font=dict(size=20)
                            ),
                        ]
                    )
                    st.plotly_chart(fig_h2h, use_container_width=True, key=f"h2h_{group_name}_{idx}")
            else:
                st.write("H2Hデータがありません。")

else:
    st.error("データが読み込めません。")
