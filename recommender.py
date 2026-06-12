import os

import pandas as pd
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import streamlit as st
import requests

# ---------------- DATA ----------------
ratings = pd.read_csv("ml-latest-small/ratings.csv")
movies = pd.read_csv("ml-latest-small/movies.csv")
links = pd.read_csv("ml-latest-small/links.csv")

movie_tmdb_map = dict(zip(links.movieId, links.tmdbId))

TMDB_KEY = os.environ.get("TMDB_API_KEY", "")


# ---------------- POSTER ----------------
def fetch_poster(movie_id):
    tmdb_id = movie_tmdb_map.get(movie_id)

    if not tmdb_id:
        return "https://via.placeholder.com/300x450?text=No+Poster"

    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_KEY}"
        data = requests.get(url, timeout=5).json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]

    except Exception as e:
        print("Poster error:", e)

    return "https://via.placeholder.com/300x450?text=Error"


# ---------------- TRAILER ----------------
def fetch_trailer(title):
    clean = title.split("(")[0].strip()

    try:
        search = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={clean}"
        ).json()

        if not search.get("results"):
            return None

        tmdb_id = search["results"][0]["id"]

        videos = requests.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key={TMDB_KEY}"
        ).json().get("results", [])

        for v in videos:
            if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                return f"https://www.youtube.com/watch?v={v['key']}"

    except Exception as e:
        print("Trailer error:", e)

    return None


# ---------------- SESSION ----------------
for k, v in {
    "watchlist": [],
    "movie_results": [],
    "genre_results": [],
    "not_interested": [],
    "previous_scores": [],
    "last_movie": "",
    "last_genres": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------- MODEL ----------------
movie_matrix = ratings.pivot(index="movieId", columns="userId", values="rating").fillna(0)
sparse_matrix = csr_matrix(movie_matrix.values)
movie_matrix = movie_matrix.reset_index()

knn = NearestNeighbors(metric="cosine", algorithm="brute")
knn.fit(sparse_matrix)


# ---------------- RECOMMEND MOVIE ----------------
def recommend_movies(name):
    match = movies[movies["title"].str.contains(name, case=False)]

    if match.empty:
        return []

    movie_id = match.iloc[0]["movieId"]
    idx = movie_matrix[movie_matrix["movieId"] == movie_id].index[0]

    dist, ind = knn.kneighbors(sparse_matrix[idx], n_neighbors=20)

    results = []

    for i in range(1, len(ind.flatten())):
        rec_id = movie_matrix.iloc[ind.flatten()[i]]["movieId"]

        if rec_id in st.session_state.not_interested:
            continue

        title = movies[movies["movieId"] == rec_id]["title"].values[0]

        score = round((1 - dist.flatten()[i]) * 100)

        results.append({
            "movieId": rec_id,
            "title": title,
            "poster": fetch_poster(rec_id),
            "trailer": fetch_trailer(title),
            "score": score
        })

        if len(results) >= 10:
            break

    return results


# ---------------- GENRE ----------------
movies["genres"] = movies["genres"].str.split("|")
all_genres = sorted(set(g for x in movies["genres"] for g in x))

for g in all_genres:
    movies[g] = movies["genres"].apply(lambda x: int(g in x))


def recommend_by_genre(selected):
    if not selected:
        return []

    df = movies.copy()

    for g in selected:
        df = df[df[g] == 1]

    results = []

    for _, row in df.iterrows():
        if row["movieId"] in st.session_state.not_interested:
            continue

        results.append({
            "movieId": row["movieId"],
            "title": row["title"],
            "poster": fetch_poster(row["movieId"]),
            "trailer": fetch_trailer(row["title"]),
            "score": 0
        })

        if len(results) >= 10:
            break

    return results


# ---------------- UI ----------------
st.title("🎬 Movie Recommender")

tab1, tab2, tab3 = st.tabs(["Movie", "Genre", "Watchlist"])


# ================= TAB 1 =================
with tab1:
    movie = st.text_input("Search movie")

    if st.button("Recommend"):
        st.session_state.last_movie = movie
        st.session_state.previous_scores = []
        st.session_state.movie_results = recommend_movies(movie)

    for idx, m in enumerate(st.session_state.movie_results):

        col1, col2 = st.columns([1, 4])

        with col1:
            st.image(m["poster"], width=120)

        with col2:
            st.write(m["title"])

            new = m["score"]

            if st.session_state.previous_scores:
                old = (
                    st.session_state.previous_scores[idx]
                    if idx < len(st.session_state.previous_scores)
                    else st.session_state.previous_scores[-1]
                )
                diff = new - old

                if diff > 0:
                    st.success(f"{new}% (+{diff})")
                else:
                    st.warning(f"{new}% ({diff})")
            else:
                st.write(f"{new}%")

            if m["trailer"]:
                st.markdown(f"[▶ Trailer]({m['trailer']})")

            if st.button("➕ Add", key=f"a{m['movieId']}"):
                st.session_state.watchlist.append(m)

            if st.button("❌ Remove", key=f"d{m['movieId']}"):
                st.session_state.not_interested.append(m["movieId"])
                st.session_state.movie_results.remove(m)
                st.rerun()

    # ================= IMPORTANT: PUT IT HERE =================
    if st.session_state.movie_results:

        st.markdown("---")

        if st.button("🔄 Regenerate"):
            st.session_state.previous_scores = [
                m["score"] for m in st.session_state.movie_results
            ]

            st.session_state.movie_results = recommend_movies(
                st.session_state.last_movie
            )

            st.rerun()


# ================= TAB 2: GENRE =================
with tab2:
    genres = st.multiselect("Genres", all_genres)

    if st.button("Search Genre"):
        st.session_state.genre_results = recommend_by_genre(genres)

    for m in st.session_state.genre_results:

        col1, col2 = st.columns([1, 4])

        with col1:
            st.image(m["poster"], width=120)

            if m["trailer"]:
                st.markdown(f"[▶ Trailer]({m['trailer']})")

            if st.button("➕ Add", key=f"g_add_{m['movieId']}"):
                st.session_state.watchlist.append(m)


                st.rerun()


# ================= TAB 3: WATCHLIST =================
with tab3:
    st.subheader("Your Watchlist")

    for m in st.session_state.watchlist:

        col1, col2 = st.columns([1, 4])

        with col1:
            st.image(m["poster"], width=120)

        with col2:
            st.write(m["title"])

            if m.get("trailer"):
                st.markdown(f"[▶ Trailer]({m['trailer']})")

            if st.button("❌ Remove", key=f"w_del_{m['movieId']}"):
                st.session_state.watchlist = [
                    x for x in st.session_state.watchlist
                    if x["movieId"] != m["movieId"]
                ]
                st.rerun()
