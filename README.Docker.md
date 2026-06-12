# Docker

Run WatchNext in a container without installing Python dependencies locally.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- A [TMDB API key](https://www.themoviedb.org/settings/api) for movie posters and trailers

## Quick start

1. Create a `.env` file in the project root (optional but recommended):

   ```bash
   TMDB_API_KEY=your_tmdb_api_key_here
   ```

2. Build and start the app:

   ```bash
   docker compose up --build
   ```

3. Open [http://localhost:8501](http://localhost:8501) in your browser.

## Commands

Build the image only:

```bash
docker compose build
```

Run in the background:

```bash
docker compose up -d
```

Stop the container:

```bash
docker compose down
```

Build and run with plain Docker:

```bash
docker build -t watchnext .
docker run --rm -p 8501:8501 -e TMDB_API_KEY=your_key_here watchnext
```
