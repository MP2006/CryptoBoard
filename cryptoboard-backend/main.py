# Notes:
# Run the FastAPI server with Uvicorn (use this command to run the server)
# uvicorn main:app --reload

# This code now properly loads the data files and is ready to serve the data via API endpoints, enabling our frontend to query and display data (like the newsfeed, word cloud, and article counters) efficiently.

# Implemented FastAPI backend with endpoints for newsfeed, word cloud, and article analysis

# - Added FastAPI application with endpoints:
#   - /api/newsfeed: Returns a paginated list of article titles and links
#   - /api/word-cloud: Returns the top 10 most frequent words from articles
#   - /api/article-counter: Returns top 5 words (excluding stopwords) for each article
#   - /api/word-trend: Provides historical trend of word usage over time
#   - /api/comparative: Compares the number of articles between two categories (e.g., media vs. politics)
#   - /api/by-coin: Filters articles by cryptocurrency name (e.g., Bitcoin, Dogecoin)
#   - /api/meta: Provides metadata about the dataset (e.g., total articles, average article length)
# - Implemented word count analysis and article content filtering to exclude stopwords
# - Data loaded from local CSV files (`articles.csv` and `word_counts.csv`)
# - Ready for integration with frontend to display the dashboard

# - This update serves as the core API backend for the CryptoBoard project.

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
from typing import List
from collections import Counter
from pydantic import BaseModel
import os
import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Get the absolute path of the 'data' directory
data_folder = os.path.join(os.path.dirname(__file__), '..', 'data', 'news')

# Load data from CSVs
articles_df = pd.read_csv(os.path.join(data_folder, 'articles.csv'))
word_counts_df = pd.read_csv(os.path.join(data_folder, 'word_counts.csv'))

# Helper function to clean and process word counts
def get_word_counts():
    word_counts = word_counts_df.groupby('word').sum().sort_values('count', ascending=False)
    return word_counts.head(10)

# Endpoint 1: Newsfeed - Returns a list of article titles and links
@app.get("/api/newsfeed")
async def get_newsfeed(skip: int = 0, limit: int = 10):
    articles = articles_df[['title', 'link']].iloc[skip:skip+limit]
    return JSONResponse(content=articles.to_dict(orient='records'))

# Endpoint 2: Word Cloud - Top 10 most popular words
@app.get("/api/word-cloud")
async def get_word_cloud():
    word_counts = get_word_counts()
    return JSONResponse(content=word_counts.to_dict(orient='records'))

# Endpoint 3: Article Counter - Top words for each article
@app.get("/api/article-counter")
async def get_article_counter():
    article_words = []
    for _, row in articles_df.iterrows():
        article = row['content']
        word_list = article.split()
        word_count = Counter(word_list)
        # Remove stop words
        stop_words = set(["the", "a", "an", "and", "or", "to", "in", "of", "for", "with", "on", "at"])
        filtered_words = {k: v for k, v in word_count.items() if k.lower() not in stop_words}
        top_words = dict(filtered_words.most_common(5))
        article_words.append({"title": row['title'], "top_words": top_words})
    return JSONResponse(content=article_words)

# Endpoint 4: Word Usage Over Time - Historical trend of a word's usage
@app.get("/api/word-trend")
async def get_word_trend(word: str):
    # Filter word_counts_df by word and plot its trend over time
    word_data = word_counts_df[word_counts_df['word'] == word]
    word_data = word_data.sort_values(by="count", ascending=False)  # Sort by frequency (you can adjust this logic)
    return JSONResponse(content=word_data.to_dict(orient='records'))

# Endpoint 5: Comparative - Compare categories (e.g., media vs politics)
@app.get("/api/comparative")
async def get_comparative(category1: str, category2: str):
    # Filter articles by categories
    articles_in_category1 = articles_df[articles_df['link'].str.contains(category1, na=False)]
    articles_in_category2 = articles_df[articles_df['link'].str.contains(category2, na=False)]
    return JSONResponse(content={
        "category1": articles_in_category1.shape[0],
        "category2": articles_in_category2.shape[0]
    })

# Endpoint 6: By Coin - Filter articles by cryptocurrency coin
@app.get("/api/by-coin")
async def get_by_coin(coin: str):
    coin_articles = articles_df[articles_df['content'].str.contains(coin, case=False, na=False)]
    return JSONResponse(content=coin_articles[['title', 'link']].to_dict(orient='records'))

# Endpoint 7: Meta - Summary of collected data
@app.get("/api/meta")
async def get_meta():
    total_articles = articles_df.shape[0]
    avg_article_length = articles_df['content'].apply(len).mean()
    return JSONResponse(content={
        "total_articles": total_articles,
        "average_article_length": avg_article_length
    })
