# Author: Ainsley Baker
# Version: Python 3.11.5
# Description: An application that scrapes the comments of any YouTube video and stores within an SQL database

# Importing Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import re
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import html
import sqlite3

root = tk.Tk()
root.title("Youtube Comment Scraper")
# Connecting to SQLite database
conn = sqlite3.connect("comments.db")
URL_STATE = False
AMOUNT_STATE = False

# YouTube API setup
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = ""
youtube = build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

# Function for collection of comments
def comment_collection(videoID, maxResults):
    request = youtube.commentThreads().list(
    part="snippet",
    videoId=videoID,
    maxResults=maxResults)

    response = request.execute()
    comments = []

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']

        published_at = datetime.strptime(comment['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")

        # Format the time as YYYY/MM/DD
        formatted_time = published_at.strftime("%Y/%m/%d")

        text = html.unescape(comment['textDisplay'])

        comments.append([comment['authorDisplayName'], formatted_time, text])

        df = pd.DataFrame(comments, columns=['User', 'Time', 'Comment'])

    # Store the Dataframe in the SQLite database
    df.to_sql('comments', conn, if_exists='replace', index=False)

# Function for validating user input and initiating comment scraping
def validation():
    global AMOUNT_STATE, URL_STATE
    url = url_entry.get()
    max_results = max_results_entry.get()
    try:
        max_results = int(max_results)
        if max_results <= 0:
            raise ValueError("Max results must be a positive integer.")
        elif max_results > 100:
            max_results = 100
            max_results_entry.delete(0, tk.END)
            max_results_entry.insert(0, str(max_results))
        AMOUNT_STATE = True
    except ValueError as e:
        AMOUNT_STATE = False
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(e))
        return
    
    video_id_match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
    if video_id_match:
        URL_STATE = True
        videoID = video_id_match.group(1)
        comment_collection(videoID, max_results)
        result_text.delete(1.0, tk.END)
    else:
        URL_STATE = False
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Invalid YouTube URL")

# Function for fetching comments from SQL database
def display_comments():
    global AMOUNT_STATE, URL_STATE
    conn = sqlite3.connect('comments.db')

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments")
    comments = cursor.fetchall()
    result_text.delete(1.0, tk.END)

    # Display comments
    if URL_STATE and AMOUNT_STATE:   
        for comment in comments:
            user, time, text = comment
            result_text.insert(tk.END, f"User: {user}\nTime: {time}\nComment: {text}\n\n")
    else:
        print("Invalid Entries")

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

# Function for exporting comments
def export_data():
    try:
        conn = sqlite3.connect('comments.db')
        query = "SELECT * FROM comments"
        df = pd.read_sql_query(query, conn)

        # Ask the user for the file path and name
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            df.to_csv(file_path, index=False)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"Data exported to {file_path}")
        else:
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "Export cancelled.")
    except Exception as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error exporting data: {str(e)}")
    finally:
        conn.close()

# Label and Entry for URL
url_label = ttk.Label(root, text="Enter YouTube URL:")
url_label.pack()
url_entry = ttk.Entry(root, width=100)
url_entry.pack()

# Label and Entry for amount of comments
max_results_label = ttk.Label(root, text="Enter amount of comments:")
max_results_label.pack()
max_results_entry = ttk.Entry(root, width=5)
max_results_entry.pack()

# Button to trigger data collection
collect_button = ttk.Button(root, text="Collect Data", command=show_data)
collect_button.pack()

# Button to trigger viewing comments
view_comments_button = ttk.Button(root, text="View Comments", command=display_comments)
view_comments_button.pack()

# Button for exporting comments
export_button = ttk.Button(root, text="Export Data", command=export_data)
export_button.pack()

# Displaying comments
result_text = tk.Text(root, height=55, width=235)
result_text.pack()

# Button to clear screen
clear_button = ttk.Button(root, text="Clear", command=lambda: result_text.delete(1.0, tk.END))
clear_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()
conn.close()