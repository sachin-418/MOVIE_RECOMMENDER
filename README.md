# 🎬 Movie Recommender System

An end-to-end, content-based Movie Recommendation Web Application built using **Python**, **Machine Learning**, and **Streamlit**. The application processes metadata from over 4,800 movies to compute pairwise cosine similarity scores, recommending the top 5 most similar titles alongside high-resolution poster artwork dynamically fetched across multiple API endpoints.

---

## 📸 Overview & Demo

The application provides a modern, dark-themed dashboard where users can search or select any movie from the TMDB 5000 dataset. Upon clicking **"Show Recommendation"**, the system executes a real-time vector search, retrieves top recommendations, and fetches artwork in parallel using multi-threaded execution.

---

## ✨ Features

- **Content-Based Filtering Pipeline**: Computes similarities based on metadata tags derived from genres, plot keywords, top billed cast, and key crew members (directors).
- **Multi-Threaded Poster Engine**: Utilizes Python's `ThreadPoolExecutor` to fetch poster URLs concurrently across 5 threads, significantly reducing UI blocking times.
- **Multi-Source Poster Fallback**: 
  1. Primary: **TMDB API** (using dynamic movie IDs).
  2. Secondary: **OMDb API** (title-based search fallback).
  3. Tertiary: **Wikipedia Media API** (image parsing).
  4. Final: Custom SVG card generator (guarantees no broken image icons).
- **Compressed Model Storage**: Bypasses GitHub's 100 MB file limit by serializing the high-dimensional similarity matrix into a `bz2`-compressed stream (`similarity.pbz2`), reducing disk footprint by ~70%.
- **Responsive Dark-Mode UI**: Styled using custom CSS with flexible HTML card layouts, hover elevation, and proper vertical text wrapping for complete title visibility.

---

## 🛠️ Tech Stack & Dependencies

| Category | Tools & Libraries |
| :--- | :--- |
| **Language** | Python 3.8+ |
| **Frontend Framework** | Streamlit |
| **Data Processing** | Pandas, NumPy, Ast |
| **Machine Learning** | Scikit-learn (`CountVectorizer`, `cosine_similarity`) |
| **Concurrency & Web** | Requests, `concurrent.futures.ThreadPoolExecutor`, `urllib.parse` |
| **Serialization** | Pickle, BZ2 |

---

## 📐 Machine Learning Pipeline & Mathematics

### 1. Feature Extraction & Engineering
Metadata fields from `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` are merged on `title` and preprocessed as follows:

- **Genres & Keywords**: Parsed from stringified JSON objects to extract name arrays.
- **Cast**: Extracted the top 3 lead actors per movie.
- **Crew**: Extracted the `Director` name from the crew list.
- **Normalization**: Spaces within entity names are removed (e.g., `"Johnny Depp"` $\rightarrow$ `"JohnnyDepp"`) to ensure single-token representation during vectorization.

All features are concatenated into a single unified text string called `tags`.

### 2. Bag of Words Vectorization
Text tokens are vectorized using Scikit-learn's `CountVectorizer`:
- `max_features = 5000` (selects the top 5,000 most frequent tokens across the corpus).
- `stop_words = 'english'` (filters out common English stop words).

This transforms the text corpus into a sparse matrix $V \in \mathbb{R}^{N \times 5000}$, where $N$ is the number of movies ($N \approx 4806$).

### 3. Cosine Similarity Computation
Similarity between two movie vectors $\mathbf{A}$ and $\mathbf{B}$ is computed using the dot product of normalized vectors:

$$\text{Similarity}(\mathbf{A}, \mathbf{B}) = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\Vert{}\mathbf{A}\Vert{} \Vert{}\mathbf{B}\Vert{}} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

The resulting $N \times N$ matrix contains pairwise distance values bounded in $[0, 1]$, where $1.0$ indicates identical feature tags.

---

## 📁 Repository Structure

```text
📂 MOVIE_RECOMMENDER
 ├── 📜 MOVIE_RECOMMENDATION.ipynb  # Preprocessing, Feature Engineering & Export Notebook
 ├── 📜 app.py                      # Streamlit Application & Multi-source Poster Engine
 ├── 📦 similarity.pbz2             # Compressed Pairwise Cosine Similarity Matrix
 ├── 📦 movie_list.pkl              # Pickled DataFrame (Movie Titles, IDs, and Indices)
 ├── 📊 tmdb_5000_movies.csv        # Raw Movies Dataset from Kaggle
 ├── 📊 tmdb_5000_credits.csv       # Raw Credits Dataset from Kaggle
 ├── 📄 requirements.txt            # Python Dependencies List
 └── 📄 README.md                   # System Documentation

##🤝 Contributor
Sachin C — Data Pipeline, System Architecture, & UI Implementation — GitHub Profile

##📜 Acknowledgments
Dataset: TMDB 5000 Movie Dataset hosted on Kaggle.

Poster Artwork: Delivered via TMDB & OMDb Open APIs.
