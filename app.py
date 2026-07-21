import streamlit as st
import pandas as pd
import pickle
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------
# Page Setup & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

# Dark-mode styling optimized for full title visibility
st.markdown("""
<style>
    .movie-card {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease-in-out;
    }
    .movie-card:hover {
        transform: translateY(-4px);
        border-color: #38bdf8;
    }
    .poster-img {
        width: 100%;
        height: 290px;
        object-fit: cover;
        border-radius: 8px;
        display: block;
    }
    .movie-title {
        color: #f8fafc;
        font-weight: 700;
        font-size: 1.05rem;
        line-height: 1.35;
        margin-top: 12px;
        min-height: 2.8em;
        display: flex;
        align-items: center;
        justify-content: center;
        word-break: break-word;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Multi-Source Poster Engine
# ---------------------------------------------------------
def fetch_poster(title, movie_id=None):
    """Fetches posters dynamically across multiple endpoints to avoid broken images."""
    if movie_id:
        try:
            clean_id = str(int(movie_id))
            tmdb_url = f"https://api.themoviedb.org/3/movie/{clean_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
            res = requests.get(tmdb_url, timeout=2)
            if res.status_code == 200:
                path = res.json().get('poster_path')
                if path:
                    return f"https://image.tmdb.org/t/p/w500{path}"
        except Exception:
            pass

    try:
        omdb_url = f"http://www.omdbapi.com/?t={urllib.parse.quote(title)}&apikey=trilogy"
        res = requests.get(omdb_url, timeout=2)
        if res.status_code == 200:
            poster = res.json().get('Poster')
            if poster and poster != 'N/A':
                return poster
    except Exception:
        pass

    try:
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}_(film)&prop=pageimages&format=json&pithumbsize=500"
        res = requests.get(wiki_url, timeout=2)
        pages = res.json().get('query', {}).get('pages', {})
        for page in pages.values():
            if 'thumbnail' in page:
                return page['thumbnail']['source']
    except Exception:
        pass

    encoded_title = title.replace(' ', '+')
    return f"https://dummyimage.com/500x750/0f172a/ffffff.png&text={encoded_title}"


# ---------------------------------------------------------
# Load Pickled Data
# ---------------------------------------------------------
import bz2
import pickle

@st.cache_data
def load_data():
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    # Load compressed similarity file
    similarity = pickle.load(bz2.BZ2File('similarity.pbz2', 'rb'))
    return movies, similarity

movies, similarity = load_data()


# ---------------------------------------------------------
# Recommendation Logic
# ---------------------------------------------------------
def recommend(movie_title):
    index = movies[movies['title'] == movie_title].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_titles = []
    movie_ids = []
    
    for i in distances[1:6]:
        recommended_titles.append(movies.iloc[i[0]].title)
        m_id = getattr(movies.iloc[i[0]], 'movie_id', getattr(movies.iloc[i[0]], 'id', None))
        movie_ids.append(m_id)

    with ThreadPoolExecutor(max_workers=5) as executor:
        recommended_posters = list(executor.map(fetch_poster, recommended_titles, movie_ids))

    return recommended_titles, recommended_posters


# ---------------------------------------------------------
# Application UI
# ---------------------------------------------------------
st.title("🎬 Movie Recommender System")
st.write("Select a movie to get top recommendations along with artwork.")

selected_movie = st.selectbox(
    'Select or search a movie:',
    movies['title'].values
)

if st.button('Show Recommendation', type="primary"):
    with st.spinner('Fetching recommendations and posters...'):
        names, posters = recommend(selected_movie)
    
    st.write("---")
    st.subheader(f"Recommended for fans of '{selected_movie}':")
    
    cols = st.columns(5)
    for col, name, poster_url in zip(cols, names, posters):
        with col:
            st.markdown(
                f"""
                <div class="movie-card">
                    <img src="{poster_url}" class="poster-img" alt="{name}">
                    <div class="movie-title">{name}</div>
                </div>
                """,
                unsafe_allow_html=True
            )