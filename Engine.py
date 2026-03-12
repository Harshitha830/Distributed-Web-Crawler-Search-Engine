# -------------------------------------------------------------
# Distributed Web Crawler + Mini Search Engine
#
# This program simulates how search engines crawl web pages,
# store their content, and allow users to search information.
#
# Main Concepts Demonstrated:
# 1. URL Frontier (Queue of URLs to visit)
# 2. Distributed Crawling using Threads
# 3. HTML Parsing to extract links
# 4. Inverted Index creation (word → URLs)
# 5. Simple search engine functionality
#
# This is a simplified academic model for learning purposes.
# -------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
from queue import Queue
import re

# -------------------------------------------------------------
# Global Data Structures
# -------------------------------------------------------------
MAX_PAGES = int(input("Enter maximum number of pages to crawl: "))
# Stores URLs that are already visited
visited_urls = set()

# Queue to manage URLs waiting to be crawled
url_queue = Queue()

# Inverted index dictionary
# Example: {"python": {"site1.com", "site2.com"}}
inverted_index = {}

# Lock to prevent race conditions between threads
lock = threading.Lock()


# -------------------------------------------------------------
# Function: Tokenize Text
# Converts page text into individual words
# -------------------------------------------------------------

def tokenize(text):
    # Convert text to lowercase and extract words
    words = re.findall(r'\w+', text.lower())
    return words


# -------------------------------------------------------------
# Function: Index Web Page
# Stores words and the URL where they appear
# -------------------------------------------------------------

def index_page(url, text):

    words = tokenize(text)

    # Use lock because multiple threads update the index
    with lock:
        for word in words:

            # If word not in index, create entry
            if word not in inverted_index:
                inverted_index[word] = set()

            # Add URL to word's list
            inverted_index[word].add(url)


# -------------------------------------------------------------
# Function: Crawl Worker
# Each thread runs this function
# -------------------------------------------------------------

def crawl_worker():

    while not url_queue.empty():

        # Get URL from queue
        url = url_queue.get()

        # Skip if already visited
        if url in visited_urls or len(visited_urls) >= MAX_PAGES:
            url_queue.task_done()
            continue

        try:
            # Request webpage
            response = requests.get(url, timeout=5)

            # Parse HTML content
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract visible text from webpage
            page_text = soup.get_text()

            # Index the webpage content
            index_page(url, page_text)

            print(f"[Crawler] Crawled: {url}")

            # Mark URL as visited
            with lock:
                visited_urls.add(url)

            # -------------------------------------------------
            # Extract all links from page
            # -------------------------------------------------

            for link in soup.find_all("a", href=True):

                absolute_link = urljoin(url, link["href"])

                # Add new links to queue
                if absolute_link not in visited_urls:
                    url_queue.put(absolute_link)

        except:
            # Ignore errors like connection failure
            pass

        # Mark task complete
        url_queue.task_done()


# -------------------------------------------------------------
# Function: Search Engine
# Finds pages containing query words
# -------------------------------------------------------------

def search(query):

    query_words = tokenize(query)

    results = None

    for word in query_words:

        if word in inverted_index:

            if results is None:
                results = inverted_index[word]

            else:
                # Intersection → pages containing all words
                results = results.intersection(inverted_index[word])

        else:
            return []

    return list(results) if results else []


# -------------------------------------------------------------
# MAIN PROGRAM
# -------------------------------------------------------------

if __name__ == "__main__":

    # ---------------------------------------------------------
    # Seed URLs (Starting websites)
    # ---------------------------------------------------------

    seed_urls = [
        "https://www.python.org"
    ]

    # Add seed URLs to queue
    for url in seed_urls:
        url_queue.put(url)

    # ---------------------------------------------------------
    # Create Multiple Threads (Distributed Crawlers)
    # ---------------------------------------------------------

    threads = []

    number_of_workers = 3  # Simulating 3 crawler machines

    for i in range(number_of_workers):

        thread = threading.Thread(target=crawl_worker)

        thread.start()

        threads.append(thread)

    # Wait until crawling finishes
    url_queue.join()

    print("\n----- Crawling Completed -----\n")

    # ---------------------------------------------------------
    # Search Engine Interface
    # ---------------------------------------------------------

    while True:

        user_query = input("Enter search query (type exit to quit): ")

        if user_query.lower() == "exit":
            break

        results = search(user_query)

        if results:

            print("\nPages Found:\n")

            for url in results:
                print(url)

        else:
            print("No pages found.")