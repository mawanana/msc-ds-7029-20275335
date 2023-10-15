import re
import os
import time
import praw
import pandas as pd
from datetime import datetime
from datetime import timedelta
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from includes.scraper_operator import get_unique_elements
from includes.mysql_query_executor import insert_post_data
from includes.mysql_query_executor import insert_comment_data
from includes.mysql_query_executor import insert_popularity_data
from includes.popularity_calculator import calculate_popularity
from includes.selenium_webdriver import get_selenium_webdriver


# Set your API key obtained from the Google Cloud Console
api_key = "AIzaSyD-uO1hyk2x-gzoWrdByiwFqaCZuS1wwF8"  

# Create a YouTube Data API client
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)


# Define default arguments for the DAG
default_args = {
    'owner': 'MSc DS-7029-20275335',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 5),
    'retries': 1,
}

# Create the Airflow DAG
dag = DAG(
    'youtube_data_pipeline',
    default_args=default_args,
    description='DAG for youtube pipeline',
    schedule_interval='0 0 * * 1',  # Set your desired schedule interval or None
    catchup=False,
    max_active_runs=1,
    concurrency=1,
    dagrun_timeout=None,
    tags=['data', 'pipeline'],
)


# Task 1: scraping video list on chennel
def scrape_video_list():
    # Replace with the URL of the YouTube channel you want to scrape
    channel_urls = [['youtube-CANADA', 'https://www.youtube.com/channel/UCyw_PoEkfj0kA_2t_gOjtOQ'], ['youtube-India', 'https://www.youtube.com/channel/UCOBjFMnb_0rfwV0plAYXsfQ'], ['youtube-SriLanka', 'https://www.youtube.com/channel/UCixnmEcCoeqdrwyh9B3NkQw'],['youtube-SouthAfrica','https://www.youtube.com/channel/UCWvzJ3CnkDukCcEfg4rfnyg']]
    # channel_urls = [['youtube-USA', 'https://www.youtube.com/@pizzahut'], ['youtube-UK', 'https://www.youtube.com/user/pizzahutdeliveryuk']]

    
    # Initialize a 2D list to store the unique URLs
    unique_url_list = []

    # for index, channel_url in enumerate(channel_urls):
    for channel_url in channel_urls:
        print(channel_url[0], '-----', channel_url[1])
        
        # Initialize the Chrome WebDriver (you may need to specify the path to chromedriver.exe)
        driver = get_selenium_webdriver(channel_url[1])
        
        # Open the channel URL
        driver.get(channel_url[1])
        driver.implicitly_wait(5)
        
        # Find the element with the specified attributes
        element = driver.find_element(By.XPATH, '//*[@id="tabsContent"]/tp-yt-paper-tab[2]')
        
        # Click the element
        element.click()
        
        # Scroll down to load comments (you may need to adjust the number of scrolls)
        for _ in range(10):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)  # Adjust the sleep duration as needed
        
        # Find elements with id="thumbnail" and class="yt-simple-endpoint inline-block style-scope ytd-thumbnail"
        video_elements = driver.find_elements(By.XPATH, '//a[@id="thumbnail" and contains(@class, "yt-simple-endpoint inline-block style-scope ytd-thumbnail")]')
        
        # Extract the video URLs
        video_urls = [element.get_attribute("href") for element in video_elements]

        # Iterate through the video URLs and add them to the unique_url_list
        for url in video_urls:
            # Check if the URL is not None and not already in the list
            if url is not None and url not in [item[0] for item in unique_url_list]:
                unique_url_list.append([channel_url[0], url])
        
        # Close the WebDriver
        driver.quit()
#     unique_url_list = [['youtube-USA', 'https://www.youtube.com/watch?v=Ti2tgvSP-g8'], ['youtube-USA', 'https://www.youtube.com/watch?v=M2ZYL1XnvRE'], ['youtube-USA', 'https://www.youtube.com/watch?v=PpzaYg_ABQ0'], ['youtube-USA', 'https://www.youtube.com/watch?v=0OaU_Wf_q7s'], ['youtube-USA', 'https://www.youtube.com/watch?v=1E4t2kK3Q68']]
    print(unique_url_list)

    return unique_url_list

# Task 2: Data scraping (Function to extract video information for a given URL and source)
from googleapiclient.errors import HttpError

def scrape_data(**kwargs):
    unique_url_list = kwargs['task_instance'].xcom_pull(task_ids='scrape_video_list')
    video_data = []
    comment_data = []

    for video_info in unique_url_list:
        print(unique_url_list)
        video_source, video_url = video_info
        video_id = video_url.split("v=")[1]

        try:
            # Retrieve video details
            video_response = youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()

            video_info = video_response["items"][0]

            # Extract desired information
            video_title = video_info["snippet"]["title"]
            video_description = video_info["snippet"]["description"]
            video_views = video_info["statistics"]["viewCount"]

            # Check if the "likeCount" field exists
            if "likeCount" in video_info["statistics"]:
                video_likes = video_info["statistics"]["likeCount"]
            else:
                video_likes = 0  # Set to 0 if the field does not exist

            # Check if the "dislikeCount" field exists
            if "dislikeCount" in video_info["statistics"]:
                video_dislikes = video_info["statistics"]["dislikeCount"]
            else:
                video_dislikes = 0  # Set to 0 if the field does not exist

            # Extract number of comments
            video_comment_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText"
            ).execute()

            num_comments = video_comment_response["pageInfo"]["totalResults"]

            # Extract submission time and author name
            video_submission_date = video_info["snippet"]["publishedAt"]
            author_name = video_info["snippet"]["channelTitle"]

            # Extract comments and append them to comment_data
            for comment in video_comment_response["items"]:
                comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comment_data.append([video_source, video_url, comment_text])

            # Append video data to video_data
            video_data.append([
                video_source,
                video_url,
                video_title,
                video_views,
                video_likes,
                video_dislikes,
                num_comments,
                video_description,
                video_submission_date,
                author_name
            ])
        except HttpError as e:
            if e.resp.status == 403 and "commentsDisabled" in str(e):
                print(f"Skipping video with disabled comments: {video_url}")
                # Optionally, you can log this information or take additional actions.
                continue  # Skip to the next URL
            else:
                # Handle other HTTP errors or raise an exception for unexpected errors
                raise e
                
    return video_data, comment_data


# Define the post_data_preparation function
def post_data_preparation(**kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='scrape_data')
    
    # Initialize video_data list with column names
    video_data = [['source', 'url', 'title', 'views', 'likes', 'dislikes', 'num_comments', 'description', 'submission_time', 'author_name']]
    
    for video_data_element in data[0]:  # Iterate through each video data element
        source = video_data_element[0]
        url = video_data_element[1]  # Get the URL from the element
        title = video_data_element[2]  # Get the title from the element
        
        # Initialize views, likes, dislikes, and num_comments to 0
        views = int(video_data_element[3]) if isinstance(video_data_element[3], str) and video_data_element[3].isdigit() else 0
        likes = int(video_data_element[4]) if isinstance(video_data_element[4], str) and video_data_element[4].isdigit() else 0
        dislikes = int(video_data_element[5]) if isinstance(video_data_element[5], str) and video_data_element[5].isdigit() else 0
        num_comments = int(video_data_element[6])
        
        description = video_data_element[7]
        
        # Initialize submission_time to a default value (e.g., current datetime)
        submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Attempt datetime parsing only if the element can be a datetime
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', video_data_element[8]):
            input_datetime = datetime.strptime(video_data_element[8], "%Y-%m-%dT%H:%M:%SZ")
            submission_time = input_datetime.strftime("%Y-%m-%d %H:%M:%S")

        author_name = video_data_element[9]

        video_data.append([source, url, title, views, likes, dislikes, num_comments, description, submission_time, author_name])
    # Create a Pandas DataFrame using the video_data
    video_df = pd.DataFrame(video_data[1:], columns=video_data[0])
    return video_df
    pass

# Define the comment_data_preparation function
def comment_data_preparation(**kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='scrape_data')
    print(data[1])
    column_prepared_data = []
    for element in data[1]:
        # Use a list comprehension to replace 'None' with ''
        element = ['' if item == 'None' else item for item in element]

        source = element[0]
        url = element[1]
        comment = element[2]
        author = ''
        likes = 0
        dislikes = 0
        replies = 0
        extra = ''

        column_prepared_data.append([source, url, comment, author, likes, dislikes, replies, extra])

    # Define column names for your DataFrame
    column_names = ['source', 'url', 'comment', 'author', 'likes', 'dislikes', 'replies', 'extra']
    
    # Create a Pandas DataFrame
    column_prepared_data_df = pd.DataFrame(column_prepared_data, columns=column_names)
    return column_prepared_data_df
    pass

# Define the calculate_popularity function
def calculate_popularity(**kwargs):
    df = kwargs['task_instance'].xcom_pull(task_ids='post_data_preparation')

    primary_coloum_df = ['source', 'url', 'submission_time']
    primary_coloum_df = df[primary_coloum_df]

    # List of column names you want in the new DataFrame
    new_df_column_names = ['title', 'views', 'likes', 'num_comments']
    
    # Create a new DataFrame by selecting the desired columns
    df = df[new_df_column_names]

    # Replace NaN values in numeric columns with 0
    df.fillna({'views': 0, 'likes': 0, 'num_comments': 0}, inplace=True)

    
    # Calculate total views, likes, and comments
    total_views = df['views'].sum()
    total_likes = df['likes'].sum()
    total_comments = df['num_comments'].sum()
    
    # Calculate percentage values
    df['PercentageViews'] = (df['views'] / total_views) * 100
    df['PercentageLikes'] = (df['likes'] / total_likes) * 100
    df['PercentageComments'] = (df['num_comments'] / total_comments) * 100
    
    # Define weights as the complement of the percentage values
    df['WeightViews'] = 100 - df['PercentageViews']
    df['WeightLikes'] = 100 - df['PercentageLikes']
    df['WeightComments'] = 100 - df['PercentageComments']
    
    # Calculate popularity score for each row
    df['PopularityScore'] = (df['WeightViews'] * df['views']) + (df['WeightLikes'] * df['likes']) + (df['WeightComments'] * df['num_comments'])
    
    # Normalize the popularity scores (optional)
    min_score = df['PopularityScore'].min()
    max_score = df['PopularityScore'].max()
    df['NormalizedScore'] = (df['PopularityScore'] - min_score) / (max_score - min_score)
    
    # Sort rows by popularity score in descending order
    df = df.sort_values(by='PopularityScore', ascending=False)

    # Combine the DataFrames into one
    popularity_df = pd.concat([primary_coloum_df, df], axis=1)
    
    return popularity_df
    pass

# Define the post_data_injection function
def post_data_injection(**kwargs):
    df = kwargs['task_instance'].xcom_pull(task_ids='post_data_preparation')
    insert_post_data(df, "post_cleaned_data")
    pass

# Define the comment_data_injection function
def comment_data_injection(**kwargs):
    df = kwargs['task_instance'].xcom_pull(task_ids='comment_data_preparation')
    insert_comment_data(df, "comments_cleaned_data")
    pass

# Define the comment_data_injection function
def popularity_data_injection(**kwargs):
    df = kwargs['task_instance'].xcom_pull(task_ids='calculate_popularity')
    insert_popularity_data(df, "popularity_data")
    pass


# Scrape Data Task
scrape_video_list_task = PythonOperator(
    task_id='scrape_video_list',
    python_callable=scrape_video_list,
    dag=dag,
)

scrape_data_task = PythonOperator(
    task_id='scrape_data',
    python_callable=scrape_data,
    provide_context=True,
    dag=dag,
)

post_data_preparation_task = PythonOperator(
    task_id='post_data_preparation',
    python_callable=post_data_preparation,
    provide_context=True,
    dag=dag,
)

comment_data_preparation_task = PythonOperator(
    task_id='comment_data_preparation',
    python_callable=comment_data_preparation,
    provide_context=True,
    dag=dag,
)

calculate_popularity_task = PythonOperator(
    task_id='calculate_popularity',
    python_callable=calculate_popularity,
    provide_context=True,
    dag=dag,
)

post_data_injection_task = PythonOperator(
    task_id='post_data_injection',
    python_callable=post_data_injection,
    provide_context=True,
    dag=dag,
)

comment_data_injection_task = PythonOperator(
    task_id='comment_data_injection',
    python_callable=comment_data_injection,
    provide_context=True,
    dag=dag,
)

popularity_data_injection_task = PythonOperator(
    task_id='popularity_data_injection',
    python_callable=popularity_data_injection,
    provide_context=True,
    dag=dag,
)

# Task dependencies
# scrape_video_list_task
scrape_video_list_task >> scrape_data_task >> post_data_preparation_task >> post_data_injection_task
scrape_video_list_task >> scrape_data_task >> comment_data_preparation_task >> comment_data_injection_task
scrape_video_list_task >> scrape_data_task >> post_data_preparation_task >> calculate_popularity_task >> popularity_data_injection_task

if __name__ == "__main__":
    dag.cli()