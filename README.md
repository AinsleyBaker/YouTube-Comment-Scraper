# YouTube-Comment-Scraper
An application made in python that scrapes the comments of any YouTube video via YouTube's API and stores within an SQLite database.
Implements a user-friendly GUI made with tkinter that features multiple buttons, such as clearing comment list, exporting as CSV, etc.
Works by pasting the URL of any video and specifying the desired amount of comments to scrape and then clicking collect data which stores each entry within an SQL database.
The application implements error handling for invalid URL's and comment quantity and has a max comment scraping amount of 100.
