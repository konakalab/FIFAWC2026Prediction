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
            f"を利用しています。 \n\n"
            f"この予測を引用される場合は次の一行をコピーしてください．\n\n"
            f"小中英嗣 (a.k.a konakalab). FIFAワールドカップ2026予測 (https://fifawc2026prediction-konakalab.streamlit.app/), 2026"
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
            width='stretch',
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

    # =========================================================================
    # 大会全体の予測性能評価
    # =========================================================================
    file_h2h_result = 'table_prediction_h2h_withResult.csv'
    if os.path.exists(file_h2h_result):
        df_res = pd.read_csv(file_h2h_result)
        
        if not df_res.empty:
            st.subheader("📊 大会全体の予測性能評価")
            st.write("有利（勝率が高い）と予測したチームの視点から、確率ごとの実際の着地（勝・分・敗・未実施）を集計しています。")
            st.write("「予測勝率(調整値)」は(予測勝率)+(予測引き分け率)/2 の値を意味していま．")
            
            fav_probs = []
            actual_results = []
            
            for _, row in df_res.iterrows():
                p_w = float(row['pWin'])
                p_d = float(row['pDraw'])
                p_l = float(row['pLose'])
                
                # 予測勝率が高い方を判定し、基準となる確率を計算
                if p_w >= p_l:
                    p_fav = p_w + (p_d / 2.0)
                    
                    if pd.notna(row['GoalsA']):
                        if row['aWin'] == 1:
                            res = '有利側の勝利'
                        elif row['aDraw'] == 1:
                            res = '引き分け'
                        else:
                            res = '有利側の敗北 (波乱)'
                    else:
                        res = '未実施'
                else:
                    p_fav = p_l + (p_d / 2.0)
                    
                    if pd.notna(row['GoalsA']):
                        if row['aLose'] == 1:
                            res = '有利側の勝利'
                        elif row['aDraw'] == 1:
                            res = '引き分け'
                        else:
                            res = '有利側の敗北 (波乱)'
                    else:
                        res = '未実施'
                        
                fav_probs.append(p_fav)
                actual_results.append(res)
                
            df_eval = pd.DataFrame({
                'Prob': fav_probs,
                'Result': actual_results
            })
            
            bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            labels = ['50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
            df_eval['Prob_Bin'] = pd.cut(df_eval['Prob'], bins=bins, labels=labels, right=False)
            
            df_chart = df_eval.groupby(['Prob_Bin', 'Result'], observed=False).size().reset_index(name='Count')
            
            eval_colors = {
                '有利側の勝利': '#2222EE',
                '引き分け': '#BDBDBD',
                '有利側の敗北 (波乱)': '#C62828',
                '未実施': '#FAFAFA'
            }
            
            # ─────────────────────────────────────────────────────────
            # 追加: 比率（100%積み上げ）棒グラフ + 予測一致直線
            # ─────────────────────────────────────────────────────────
            fig_perf_pct = px.bar(
                df_chart,
                x='Prob_Bin',
                y='Count',
                color='Result',
                title="予測確率別の結果比率",
                labels={'Prob_Bin': '有利側の予測勝率（調整値）', 'Count': '比率', 'Result': '実際の結果'},
                color_discrete_map=eval_colors,
                category_orders={"Result": ['有利側の勝利', '引き分け', '有利側の敗北 (波乱)', '未実施']}
            )
            
            # 各階級の中央値（理想的な的中率）をプロットする直線のデータを追加
            # 横軸のラベル（Labels）の並び順と一致させます
            ideal_x = ['50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
            ideal_y = [55, 65, 75, 85, 95]  # 各階級の中央値をパーセント（0-100）で指定
            
            fig_perf_pct.add_trace(
                go.Scatter(
                    x=ideal_x,
                    y=ideal_y,
                    mode='lines+markers',
                    name='予測と結果が一致',
                    line=dict(color='#222222', width=3, dash='dash'), # 黒ベースの太い破線
                    marker=dict(size=8, color='#222222'),
                    hoverinfo='skip'
                )
            )
            
            fig_perf_pct.update_layout(
                barmode='stack',
                barnorm='percent',  # 100%積み上げ比率にする設定
                font=dict(size=14),
                margin=dict(l=40, r=40, t=40, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=None),
                xaxis=dict(tickfont=dict(size=14)),
                # 【エラー修正済】ticksuffix を使用
                yaxis=dict(tickfont=dict(size=14), ticksuffix="%")
            )
            fig_perf_pct.update_traces(
                marker=dict(line=dict(color='#777777', width=1)),
                selector=dict(type='bar') # 枠線は棒グラフ（bar）だけに適用し、直線には適用させない
            )
            
            # 比率グラフの描画
            st.plotly_chart(fig_perf_pct, width='stretch', key="overall_performance_pct")
            
            # ─────────────────────────────────────────────────────────
            # 既存: 件数（実数カウント）棒グラフ
            # ─────────────────────────────────────────────────────────
            fig_perf = px.bar(
                df_chart,
                x='Prob_Bin',
                y='Count',
                color='Result',
                title="予測確率別の試合結果件数",
                labels={'Prob_Bin': '有利側の予測勝率（調整値）', 'Count': '試合数', 'Result': '実際の結果'},
                color_discrete_map=eval_colors,
                category_orders={"Result": ['有利側の勝利', '引き分け', '有利側の敗北 (波乱)', '未実施']}
            )
            
            fig_perf.update_layout(
                font=dict(size=14),
                margin=dict(l=40, r=40, t=40, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=None),
                xaxis=dict(tickfont=dict(size=14)),
                yaxis=dict(tickfont=dict(size=14))
            )
            fig_perf.update_traces(marker=dict(line=dict(color='#777777', width=1)))
            
            # 件数グラフの描画
            st.plotly_chart(fig_perf, width='stretch', key="overall_performance_count")
    # =========================================================================
    # 
    # =========================================================================
    
    st.divider()
    st.subheader("ノックアウトステージ(決勝トーナメント)")
    st.write("※予測は90分終了時点のものなので，「引き分け」があります．")

    # =========================================================================
    # 🏅 【タブ構造 1】決勝トーナメント専用の処理と表示
    # =========================================================================
    file_h2h_result = 'table_prediction_h2h_withResult.csv'
    if os.path.exists(file_h2h_result):
        df_matches = pd.read_csv(file_h2h_result)
        all_groups_in_csv = df_matches['Group'].unique().astype(str)
        
        # 決勝トーナメントとして想定されているラウンドの定義
        tournament_rounds = ['R32', 'R16', 'QF', 'SF', '3PL', 'Final']
        # CSV内に現在存在する決勝ステージのラウンドのみを定義順に抽出
        tm_rounds = [g for g in tournament_rounds if g in all_groups_in_csv]
        
        if tm_rounds:
            # 決勝トーナメント専用の独立したタブを生成
            tm_tabs = st.tabs([r for r in tm_rounds])
            
            for r_idx, round_name in enumerate(tm_rounds):
                with tm_tabs[r_idx]:
                    # 決勝トーナメントの該当ラウンドの試合データのみを抽出してループ
                    round_matches = df_matches[df_matches['Group'] == round_name]
                    
                    for idx, row in round_matches.iterrows():
                        has_result = 'GoalsA' in row.index and pd.notna(row['GoalsA'])
                        score_str = f" {int(row['GoalsA'])}-{int(row['GoalsB'])}" if has_result else ""
                        
                        # 💡 実施・未実施に関わらず、グラフの長さ(x軸)にはCSVの予測データをそのまま利用
                        val_win  = float(row['pWin'])
                        val_draw = float(row['pDraw'])
                        val_lose = float(row['pLose'])
                        
                        if has_result:
                            st.write(f"**{row['Date']} {row['TeamA']} vs {row['TeamB']}{score_str}**")
                            a_win  = float(row['aWin'])  if ('aWin'  in row.index and pd.notna(row['aWin']))  else 0.0
                            a_draw = float(row['aDraw']) if ('aDraw' in row.index and pd.notna(row['aDraw'])) else 0.0
                            a_lose = float(row['aLose']) if ('aLose' in row.index and pd.notna(row['aLose'])) else 0.0
                        else:
                            st.write(f"**{row['Date']} {row['TeamA']} vs {row['TeamB']} (未実施)**")
                            a_win = a_draw = a_lose = 0.0
                        
                        # ★ は試合が実施済みのときだけ付与
                        text_win  = f"★ {row['CodeA']} {val_win:.1%}" if (has_result and a_win  == 1.0) else f"{row['CodeA']} {val_win:.1%}"
                        text_draw = f"★ Draw {val_draw:.1%}"           if (has_result and a_draw == 1.0) else f"Draw {val_draw:.1%}"
                        text_lose = f"★ {row['CodeB']} {val_lose:.1%}" if (has_result and a_lose == 1.0) else f"{row['CodeB']} {val_lose:.1%}"
                        
                        fig_h2h = go.Figure()
                        
                        # オリジナルの鮮やかなカラー（青、グレー、赤）を完全に維持
                        fig_h2h.add_trace(go.Bar(x=[val_win], y=["Match"], orientation='h', marker=dict(color='#2222EE'), text=text_win, textposition='inside', insidetextanchor='middle', textfont=dict(size=20), hoverinfo="skip", name=f"{row['CodeA']} 勝"))
                        fig_h2h.add_trace(go.Bar(x=[val_draw], y=["Match"], orientation='h', marker=dict(color='#BDBDBD'), text=text_draw, textposition='inside', insidetextanchor='middle', textfont=dict(size=20), hoverinfo="skip", name="引分"))
                        fig_h2h.add_trace(go.Bar(x=[val_lose], y=["Match"], orientation='h', marker=dict(color='#C62828'), text=text_lose, textposition='inside', insidetextanchor='middle', textfont=dict(size=20), hoverinfo="skip", name=f"{row['CodeB']} 勝"))
                        
                        fig_h2h.update_layout(
                            barmode='stack', height=90, margin=dict(l=70, r=70, t=0, b=0), showlegend=False,
                            xaxis=dict(showticklabels=False, range=[0, 1], fixedrange=True),
                            yaxis=dict(showticklabels=False, fixedrange=True),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            annotations=[
                                dict(x=0, y=0.5, xref="x", yref="paper", text=f"<b>{row['CodeA']}</b>", showarrow=False, xanchor="right", xshift=-10, font=dict(size=20)),
                                dict(x=1, y=0.5, xref="x", yref="paper", text=f"<b>{row['CodeB']}</b>", showarrow=False, xanchor="left", xshift=10, font=dict(size=20)),
                            ]
                        )
                        st.plotly_chart(fig_h2h, width='stretch', key=f"sep_tm_{round_name}_{idx}")
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
        width='stretch',
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
    file_h2h = 'table_prediction_h2h_withResult.csv'
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
            st.plotly_chart(fig_rank, width='stretch', key=f"rank_{group_name}")

            st.divider()

            # --- タブ内下部：各試合の勝率予測 (H2H) ---
            if df_h2h is not None:
                st.subheader(f"Group {group_name} 各試合の勝率予測")
                group_matches = df_h2h[df_h2h['Group'] == group_name]
                
                for idx, row in group_matches.iterrows():
                    # ① まず has_result を定義
                    has_result = 'GoalsA' in row.index and pd.notna(row['GoalsA'])
    
                    # ② スコアを含むタイトルを表示
                    score_str = f" {int(row['GoalsA'])}-{int(row['GoalsB'])}" if has_result else ""
                    st.write(f"**{row['Date']} {row['TeamA']} vs {row['TeamB']}{score_str}**")

                    if has_result:
                        a_win  = float(row['aWin'])  if ('aWin'  in row.index and pd.notna(row['aWin']))  else 0.0
                        a_draw = float(row['aDraw']) if ('aDraw' in row.index and pd.notna(row['aDraw'])) else 0.0
                        a_lose = float(row['aLose']) if ('aLose' in row.index and pd.notna(row['aLose'])) else 0.0
                    else:
                        a_win = a_draw = a_lose = 0.0  # 未実施は全フラグ 0

                    fig_h2h = go.Figure()

                    # ★ は試合が実施済みのときだけ付与
                    text_win  = f"★ {row['CodeA']} {row['pWin']:.1%}"  if (has_result and a_win  == 1.0) else f"{row['CodeA']} {row['pWin']:.1%}"
                    text_draw = f"★ Draw {row['pDraw']:.1%}"           if (has_result and a_draw == 1.0) else f"Draw {row['pDraw']:.1%}"
                    text_lose = f"★ {row['CodeB']} {row['pLose']:.1%}" if (has_result and a_lose == 1.0) else f"{row['CodeB']} {row['pLose']:.1%}"


                    # 3. 帯グラフの描画（オリジナル設定・カラーを100%完全維持）
                    fig_h2h.add_trace(go.Bar(
                        x=[row['pWin']], y=["Match"],
                        orientation='h',
                        marker=dict(color='#2222EE'),
                        text=text_win,
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
                        text=text_draw,
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
                        text=text_lose,
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
                    st.plotly_chart(fig_h2h, width='stretch', key=f"h2h_{group_name}_{idx}")
            else:
                st.write("H2Hデータがありません。")

else:
    st.error("データが読み込めません。")
