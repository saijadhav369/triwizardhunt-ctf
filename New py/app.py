import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
from wordcloud import WordCloud
import os
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Triwizard Hunt CTF Dashboard",
    page_icon="🏆",
    layout="wide",
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #000000;
        color: #cdd6f4;
    }
    .stApp {
        background-color: #000000;
    }
    .st-bq {
        background-color: #111111;
    }
    h1, h2, h3 {
        color: #cba6f7;
    }
    .highlight {
        background-color: #111111;
        padding: 20px;
        border-radius: 10px;
    }
    .metric-card {
        background-color: #111111;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("TriWizard Hunt-scoreboard.csv")
    return df

df = load_data()

# Title & Metrics
st.title("🧙‍♂️ Triwizard Hunt - CTF Competition Dashboard")
st.markdown("*A magical competition of cybersecurity skills and challenges*")

total_participants = len(df)
top_score = df['score'].max()
avg_score = int(df['score'].mean())

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Teams", total_participants)
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Highest Score", top_score)
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Average Score", avg_score)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["Leaderboard 🏆", "Score Distribution 📊", "Team Analysis 🔍"])

# ------------------ Tab 1: Leaderboard ------------------
with tab1:
    st.header("Leaderboard")

    top_teams = df.head(3).copy()
    colors = ["gold", "silver", "#cd7f32"]
    fig_top3 = go.Figure()

    for i, (_, row) in enumerate(top_teams.iterrows()):
        fig_top3.add_trace(go.Bar(
            x=[row['user name']],
            y=[row['score']],
            marker_color=colors[i],
            text=row['score'],
            textposition='auto',
            hovertemplate=f"<b>{row['user name']}</b><br>Score: {row['score']}<extra></extra>"
        ))

    fig_top3.update_layout(
        title="🏆 Top 3 Teams",
        xaxis_title="Team Name",
        yaxis_title="Score",
        showlegend=False,
        height=300,
        template="plotly_dark",
    )
    st.plotly_chart(fig_top3, use_container_width=True)

    st.subheader("Complete Leaderboard")
    display_df = df[['place', 'user name', 'score']].copy()
    display_df.columns = ['Rank', 'Team Name', 'Score']

    def highlight_top_teams(row):
        if row['Rank'] == 1:
            return ['background-color: gold; color: black'] * len(row)
        elif row['Rank'] == 2:
            return ['background-color: silver; color: black'] * len(row)
        elif row['Rank'] == 3:
            return ['background-color: #cd7f32; color: black'] * len(row)
        else:
            return [''] * len(row)

    styled_df = display_df.style.apply(highlight_top_teams, axis=1)
    st.dataframe(styled_df, use_container_width=True, height=400)

# ------------------ Tab 2: Score Distribution ------------------
with tab2:
    st.header("Score Distribution Analysis")
    col1, col2 = st.columns([3, 2])

    with col1:
        fig_dist = px.histogram(df, x='score', nbins=10, color_discrete_sequence=['#cba6f7'], opacity=0.8, marginal='box')
        fig_dist.update_layout(
            title="Score Distribution",
            xaxis_title="Score",
            yaxis_title="Number of Teams",
            bargap=0.1,
            template="plotly_dark"
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col2:
        st.markdown('<div class="highlight">', unsafe_allow_html=True)
        st.subheader("Score Statistics")
        stats = {
            "Min Score": int(df['score'].min()),
            "Max Score": int(df['score'].max()),
            "Median Score": int(df['score'].median()),
            "Mean Score": int(df['score'].mean()),
            "Standard Deviation": int(df['score'].std())
        }
        for stat, value in stats.items():
            st.markdown(f"**{stat}:** {value}")
        st.markdown("</div>", unsafe_allow_html=True)

        df['score_bracket'] = pd.cut(df['score'], bins=[400, 800, 1200, 1600, 2000],
                                     labels=['400-800', '801-1200', '1201-1600', '1601-2000'])
        bracket_counts = df['score_bracket'].value_counts().reset_index()
        bracket_counts.columns = ['Score Range', 'Count']

        fig_pie = px.pie(
            bracket_counts,
            values='Count',
            names='Score Range',
            title='Teams by Score Range',
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            hole=0.4
        )
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

# ------------------ Tab 3: Team Analysis ------------------
with tab3:
    st.header("Team Analysis")

    top10 = df.head(10).sort_values('score', ascending=True)
    fig_top10 = px.bar(
        top10,
        y='user name',
        x='score',
        orientation='h',
        color='score',
        color_continuous_scale='Viridis',
        title='Top 10 Teams by Score',
    )
    fig_top10.update_layout(template="plotly_dark")
    st.plotly_chart(fig_top10, use_container_width=True)

    st.subheader("Team Name Analysis")
    colA, colB = st.columns([2, 1])

    with colA:
        team_names_text = ' '.join(df['user name'])
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='#000000',
            colormap='viridis',
            max_words=100,
            contour_width=1,
            contour_color='#cba6f7'
        ).generate(team_names_text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

    with colB:
        themes = {
            'Cyber': len([name for name in df['user name'] if 'cyber' in name.lower()]),
            'Hack': len([name for name in df['user name'] if 'hack' in name.lower()]),
            'Code': len([name for name in df['user name'] if 'code' in name.lower()]),
            '404': len([name for name in df['user name'] if '404' in name.lower()]),
            'Team': len([name for name in df['user name'] if 'team' in name.lower()])
        }

        st.markdown('<div class="highlight">', unsafe_allow_html=True)
        st.write("🔍 **Common Team Name Themes:**")
        for theme, count in themes.items():
            st.markdown(f"**{theme}:** {count}")
        st.markdown('</div>', unsafe_allow_html=True)
