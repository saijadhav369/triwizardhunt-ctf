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

# Set page configuration
st.set_page_config(
    page_title="Triwizard Hunt CTF Dashboard",
    page_icon="🏆",
    layout="wide",
)

# Apply custom CSS with pitch black background and improved styling
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
    .st-cb, .st-cd, .st-cj {
        color: #cdd6f4;
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
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    .organizers {
        text-align: center;
        margin: 20px 0;
        padding: 15px;
        background-color: #111111;
        border-radius: 10px;
    }
    .organizers h3 {
        color: #cba6f7;
        margin-bottom: 10px;
    }
    .organizers p {
        margin: 5px 0;
        color: #cdd6f4;
    }
    </style>
""", unsafe_allow_html=True)

# Read the CSV file
@st.cache_data
def load_data():
    df = pd.read_csv("TriWizard Hunt-scoreboard.csv")
    return df

# Load the data
df = load_data()

# Main header
st.title("🧙‍♂️ Triwizard Hunt - CTF Competition Dashboard")
st.markdown("*A magical competition of cybersecurity skills and challenges*")

# Create metrics for the dashboard
total_participants = len(df)
top_score = df['score'].max()
avg_score = int(df['score'].mean())

# Display metrics in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="Total Teams", value=total_participants)
    st.markdown('</div>', unsafe_allow_html=True)
    
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="Highest Score", value=top_score)
    st.markdown('</div>', unsafe_allow_html=True)
    
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="Average Score", value=avg_score)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Leaderboard 🏆", "Score Distribution 📊", "Team Analysis 🔍"])

with tab1:
    st.header("Leaderboard")
    
    # Highlight top three teams
    top_teams = df.head(3).copy()
    rest_teams = df.iloc[3:].copy()
    
    # Create a colored leaderboard for top 3
    fig_top3 = go.Figure()
    
    colors = ["gold", "silver", "#cd7f32"]  # Gold, Silver, Bronze
    
    for i, (_, row) in enumerate(top_teams.iterrows()):
        fig_top3.add_trace(go.Bar(
            x=[row['user name']],
            y=[row['score']],
            name=f"{row['place']}. {row['user name']}",
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
        margin=dict(l=20, r=20, t=60, b=20),
        height=300,
        template="plotly_dark",
        xaxis=dict(tickangle=-45),
    )
    
    st.plotly_chart(fig_top3, use_container_width=True)
    
    # Display the complete leaderboard as a table
    st.subheader("Complete Leaderboard")
    
    # Create a filtered dataframe for display
    display_df = df[['place', 'user name', 'score']].copy()
    display_df.columns = ['Rank', 'Team Name', 'Score']
    
    # Highlight rows based on ranking
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

with tab2:
    st.header("Score Distribution Analysis")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create a histogram of scores with a more beautiful design
        fig_dist = px.histogram(
            df, 
            x='score',
            nbins=10,
            color_discrete_sequence=['#cba6f7'],
            opacity=0.8,
            marginal='box',
            title="Score Distribution"
        )
        
        fig_dist.update_layout(
            xaxis_title="Score",
            yaxis_title="Number of Teams",
            bargap=0.1,
            template="plotly_dark",
            margin=dict(l=20, r=20, t=60, b=20),
            height=400
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Score statistics
        st.markdown('<div class="highlight">', unsafe_allow_html=True)
        st.subheader("Score Statistics")
        
        score_stats = {
            "Min Score": int(df['score'].min()),
            "Max Score": int(df['score'].max()),
            "Median Score": int(df['score'].median()),
            "Mean Score": int(df['score'].mean()),
            "Standard Deviation": int(df['score'].std())
        }
        
        for stat, value in score_stats.items():
            st.markdown(f"**{stat}:** {value}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Create score brackets
        df['score_bracket'] = pd.cut(
            df['score'], 
            bins=[400, 800, 1200, 1600, 2000],
            labels=['400-800', '801-1200', '1201-1600', '1601-2000']
        )
        
        bracket_counts = df['score_bracket'].value_counts().reset_index()
        bracket_counts.columns = ['Score Range', 'Count']
        
        fig_pie = px.pie(
            bracket_counts,
            values='Count',
            names='Score Range',
            title='Teams by Score Range',
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            hole=0.4,
        )
        
        fig_pie.update_layout(
            legend_title="Score Range",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.header("Team Analysis")
    
    # Top 10 teams visualization
    top10 = df.head(10).copy()
    top10 = top10.sort_values('score', ascending=True)  # Sort for horizontal bar chart
    
    fig_top10 = px.bar(
        top10,
        y='user name',
        x='score',
        orientation='h',
        color='score',
        color_continuous_scale='Viridis',
        title='Top 10 Teams by Score',
    )
    
    fig_top10.update_layout(
        yaxis_title="Team Name",
        xaxis_title="Score",
        yaxis={'categoryorder':'total ascending'},
        height=500,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    
    st.plotly_chart(fig_top10, use_container_width=True)
    
    # Team name analysis
    st.subheader("Team Name Analysis")
    
    cols = st.columns([2, 1])
    
    with cols[0]:
        # Word cloud of team names
        
        # Join all team names into a single string
        team_names_text = ' '.join(df['user name'])
        
        # Create a word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='#000000',
            colormap='viridis',
            max_words=100,
            contour_width=1,
            contour_color='#cba6f7'
        ).generate(team_names_text)
        
        # Display the word cloud using matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_facecolor('#000000')
        fig.patch.set_facecolor('#000000')
        
        st.pyplot(fig)
    
    with cols[1]:
        # Detect popular themes in team names
        themes = {
            'Cyber': len([name for name in df['user name'] if 'cyber' in name.lower()]),
            'Hack': len([name for name in df['user name'] if 'hack' in name.lower()]),
            'Code': len([name for name in df['user name'] if 'code' in name.lower()]),
            '404': len([name for name in df['user name'] if '404' in name.lower()]),
            'Team': len([name for name in df['user name'] if 'team' in name.lower()]),
            'CTF': len([name for name in df['user name'] if 'ctf' in name.lower()]),
            'Flag': len([name for name in df['user name'] if 'flag' in name.lower()]),
        }
        
        theme_df = pd.DataFrame({
            'Theme': list(themes.keys()),
            'Count': list(themes.values())
        })
        theme_df = theme_df.sort_values('Count', ascending=False)
        
        fig_themes = px.bar(
            theme_df,
            x='Theme',
            y='Count',
            color='Count',
            color_continuous_scale='Viridis',
            title='Popular Themes in Team Names'
        )
        
        fig_themes.update_layout(
            xaxis_title="Theme",
            yaxis_title="Count",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        
        st.plotly_chart(fig_themes, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"**Triwizard Hunt CTF Competition** • Total Participants: {total_participants} • Data Visualization")

# Minimal, elegant organizers section at the end (no background, just accent bar and centered text)
st.markdown('''
    <div style="max-width: 480px; margin: 48px auto 0 auto;">
        <div style="height: 6px; width: 100px; margin: 0 auto 1.2rem auto; border-radius: 6px; background: linear-gradient(90deg, #cba6f7 0%, #f38ba8 100%);"></div>
        <div style="text-align: center;">
            <div style="font-size: 2.2rem; color: #cba6f7; font-weight: 800; margin-bottom: 10px; letter-spacing: 2px; text-shadow: 0 2px 8px #181825;">TRIWIZARD HUNT - CTF</div>
            <div style="font-size: 1.1rem; color: #f38ba8; font-weight: 700; margin-bottom: 18px; letter-spacing: 1px;">by DSUTECHFLIX</div>
            <div style="font-size: 2.3rem; font-weight: 900; margin-bottom: 28px; letter-spacing: 2px;">
                <span style="color: #fff;">DSU</span><span style="color: #e50914; margin-left: 8px;">TECHFLIX</span>
            </div>
            <div style="font-size: 1.1rem; color: #a6adc8; font-weight: 600; margin-bottom: 6px;">Organized By</div>
            <div style="font-size: 1.05rem; color: #cdd6f4; font-weight: 500; margin-bottom: 18px;">DSU ACM</div>
            <div style="font-size: 1.1rem; color: #a6adc8; font-weight: 600; margin-bottom: 6px;">Event Heads</div>
            <div style="font-size: 1.05rem; color: #cdd6f4; font-weight: 700;">
                <span style="color: #f38ba8;">Sai Jadhav</span> & <span style="color: #89b4fa;">Samrdhe</span>
            </div>
        </div>
    </div>
''', unsafe_allow_html=True)