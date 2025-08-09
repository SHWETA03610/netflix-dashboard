import pandas as pd
import plotly.express as px
import streamlit as st
import requests
from config import TMDB_API_KEY
# TMDB API Key
TMDB_API_KEY = "259a0fe1ea08bbe830fee282174c4e42"

# Page Config
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# Custom CSS for Netflix-style dark theme + scrolling carousel
st.markdown("""
    <style>
        body {
            background-color: #141414;
            color: white;
        }
        .stApp {
            background-color: #141414;
            color: white;
        }
        h1, h2, h3, h4, h5 {
            color: #E50914;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: bold;
        }
        .stTextInput > div > div > input {
            background-color: #333;
            color: white;
        }
        .stSelectbox > div > div {
            background-color: #333;
            color: white;
        }
        img {
            border-radius: 8px;
        }
        /* Horizontal scrolling style */
        .scroll-container {
            display: flex;
            overflow-x: auto;
            gap: 12px;
            padding: 10px;
            scroll-behavior: smooth;
        }
        .scroll-container::-webkit-scrollbar {
            height: 8px;
        }
        .scroll-container::-webkit-scrollbar-thumb {
            background: #E50914;
            border-radius: 4px;
        }
        .scroll-item {
            flex: 0 0 auto;
            width: 150px;
            text-align: center;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("netflix_titles.csv")

df = load_data()

# Function to get poster from TMDB
def get_poster(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url).json()
    if response.get('results'):
        poster_path = response['results'][0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w200{poster_path}"
    return None

# Function to get trending titles from TMDB
def get_trending():
    url = f"https://api.themoviedb.org/3/trending/all/day?api_key={TMDB_API_KEY}"
    response = requests.get(url).json()
    trending_data = []
    if response.get('results'):
        for item in response['results'][:15]:  # Top 15 trending
            title = item.get('title') or item.get('name')
            poster_path = item.get('poster_path')
            full_poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None
            trending_data.append({"title": title, "poster": full_poster_url})
    return trending_data

# Title
st.markdown("<h1>📺 Netflix Data Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>Explore Netflix Movies and TV Shows</p>", unsafe_allow_html=True)

# Trending Now Section (Horizontal Scroll)
st.subheader("🔥 Trending Now")
trending_items = get_trending()
if trending_items:
    html_code = "<div class='scroll-container'>"
    for item in trending_items:
        poster_html = f"<img src='{item['poster']}' width='150'>" if item['poster'] else ""
        html_code += f"<div class='scroll-item'>{poster_html}<br>{item['title']}</div>"
    html_code += "</div>"
    st.markdown(html_code, unsafe_allow_html=True)

# Search Box with Poster Display
search_query = st.text_input("🔍 Search for a Movie/TV Show")
if search_query:
    results = df[df['title'].str.contains(search_query, case=False, na=False)]
    if not results.empty:
        st.subheader("Search Results")
        for _, row in results.iterrows():
            col1, col2 = st.columns([1, 3])
            poster_url = get_poster(row['title'])
            with col1:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.write("No poster available")
            with col2:
                st.write(f"**Title:** {row['title']}")
                st.write(f"**Type:** {row['type']}")
                st.write(f"**Country:** {row['country']}")
                st.write(f"**Release Year:** {row['release_year']}")
                st.write(f"**Genre:** {row['listed_in']}")
                st.write(f"**Description:** {row['description']}")
    else:
        st.warning("No results found.")

# Filters
st.subheader("Filters")
col1, col2 = st.columns(2)
with col1:
    type_filter = st.selectbox("Select Content Type", ["All"] + sorted(df['type'].dropna().unique().tolist()))
with col2:
    country_filter = st.selectbox("Select Country", ["All"] + sorted(df['country'].dropna().unique().tolist()))

filtered_df = df.copy()
if type_filter != "All":
    filtered_df = filtered_df[filtered_df['type'] == type_filter]
if country_filter != "All":
    filtered_df = filtered_df[filtered_df['country'] == country_filter]

# Charts
st.subheader("Release Year Distribution")
fig_year = px.histogram(filtered_df, x="release_year", nbins=30,
                        title="Content Releases Over the Years",
                        template="plotly_dark")
st.plotly_chart(fig_year, use_container_width=True)

st.subheader("Top Genres")
filtered_df['main_genre'] = filtered_df['listed_in'].apply(lambda x: x.split(",")[0] if pd.notnull(x) else "Unknown")
genre_counts = filtered_df['main_genre'].value_counts().reset_index()
genre_counts.columns = ['Genre', 'Count']
fig_genre = px.bar(genre_counts.head(10), x='Genre', y='Count', title="Top 10 Genres",
                   template="plotly_dark", color='Count', color_continuous_scale="reds")
st.plotly_chart(fig_genre, use_container_width=True)

st.subheader("Content by Country")
country_counts = filtered_df['country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']
fig_country = px.choropleth(country_counts, locations="Country",
                             locationmode="country names", color="Count",
                             title="Content Count by Country",
                             color_continuous_scale="reds", template="plotly_dark")
st.plotly_chart(fig_country, use_container_width=True)
