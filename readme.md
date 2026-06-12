# WatchNext – Movie Recommendation System

WatchNext is an interactive movie recommendation web app built using Python and Streamlit. It uses a collaborative filtering approach with a K-Nearest Neighbors (KNN) model and cosine similarity to suggest movies based on user input.

The system is trained on the MovieLens dataset and converts the user–movie ratings into a sparse matrix for efficient computation. Users can search for a movie or select genres to receive personalized recommendations with similarity scores.

Unlike traditional recommendation systems that require extensive user history, WatchNext generates relevant suggestions from a single input, making it fast, simple, and user-friendly.

## Running with Docker

**1. Build and start**
```bash
docker compose up --build
```

**2. Open the app**
Visit [http://localhost:8501](http://localhost:8501).

**Other commands**
```bash
docker compose down          # stop the container
docker compose up --build -d # run in the background
```

# Running Locally

## To install dependencies please run the following command in the terminal:
`pip install -r requirements.txt`


## To run the app please run the following command in the terminal:

`streamlit run recommender.py`
