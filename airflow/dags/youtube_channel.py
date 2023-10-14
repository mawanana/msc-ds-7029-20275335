import os
import pandas as pd
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from includes.mysql_query_executor import insert_channel_data

# Define your API key
api_key = "AIzaSyD-uO1hyk2x-gzoWrdByiwFqaCZuS1wwF8"  


# Define default arguments for the DAG
default_args = {
    'owner': 'MSc DS-7029-20275335',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 11),
    'retries': 1,
}

# Create the Airflow DAG
dag = DAG(
    'youtube_channel_data_pipeline',
    default_args=default_args,
    description='DAG for youtube pipeline',
    schedule_interval='0 0 * * *',  # Run daily at midnight
    catchup=False,
    max_active_runs=1,
    concurrency=1,
    dagrun_timeout=None,
    tags=['data', 'pipeline'],
)


def scrape_channel_data():
    # Define the channel URLs here
    channel_urls = [['Canada', 'https://www.youtube.com/channel/UCyw_PoEkfj0kA_2t_gOjtOQ'],
                    ['India', 'https://www.youtube.com/channel/UCOBjFMnb_0rfwV0plAYXsfQ'],
                    ['Sri Lanka', 'https://www.youtube.com/channel/UCixnmEcCoeqdrwyh9B3NkQw'],
                    ['South Africa', 'https://www.youtube.com/channel/UCWvzJ3CnkDukCcEfg4rfnyg']]

    # Create a list to store the data for all channels
    all_channel_data = []

    for channel_name, channel_url in channel_urls:
        # Extract the channel ID from the URL
        channel_id = channel_url.split('/')[-1]

        # Initialize the YouTube Data API
        youtube = build("youtube", "v3", developerKey=api_key)

        subscribers = 0
        video_count = 0
        total_likes = 0
        total_dislikes = 0
        total_shares = 0
        total_comments = 0
        total_views = 0
        join_date = ""

        try:
            # Get channel statistics
            channel_response = youtube.channels().list(
                part="statistics,snippet",
                id=channel_id
            ).execute()

            if 'items' in channel_response:
                channel_data = channel_response['items'][0]
                subscribers = channel_data['statistics'].get('subscriberCount', 0)
                video_count = channel_data['statistics'].get('videoCount', 0)
                total_views = channel_data['statistics'].get('viewCount', 0)
                join_date = channel_data['snippet'].get('publishedAt', "")

            # Get playlist data to retrieve video statistics
            playlist_response = youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()

            if 'items' in playlist_response:
                # Get the upload playlist ID
                upload_playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

                # Get the videos in the upload playlist
                videos_response = youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=upload_playlist_id,
                    maxResults=50  # You can increase this number if needed
                ).execute()

                # Iterate over videos to get likes, dislikes, shares, and comments
                for item in videos_response.get('items', []):
                    video_id = item['contentDetails']['videoId']
                    video_response = youtube.videos().list(
                        part="statistics",
                        id=video_id
                    ).execute()
                    video_data = video_response['items'][0]['statistics']
                    total_likes += int(video_data.get('likeCount', 0))
                    total_dislikes += int(video_data.get('dislikeCount', 0))
                    total_shares += int(video_data.get('shareCount', 0))

                    try:
                        # Get comments count (if comments are enabled)
                        comments_response = youtube.commentThreads().list(
                            part="snippet",
                            videoId=video_id
                        ).execute()
                        total_comments += int(comments_response.get('pageInfo', {}).get('totalResults', 0))
                    except HttpError as e:
                        if 'commentsDisabled' in str(e):
                            # Comments are disabled for this video
                            pass

        except HttpError as e:
            if 'channelNotFound' in str(e):
                print(f"Channel not found for URL: {channel_url}")

        # Create a list containing all the data elements for this channel
        channel_data_list = [channel_name, subscribers, video_count, total_likes, total_dislikes, total_shares, total_comments, total_views, join_date]
        all_channel_data.append(channel_data_list)

    return all_channel_data
    pass

def channel_data_preparation(**kwargs):
    channel_data = kwargs['task_instance'].xcom_pull(task_ids='scrape_channel_data')
    # Define column names for the DataFrame
    columns = ['country', 'subscribers', 'videos', 'likes', 'dislikes', 'shares', 'comments', 'views', 'join_date']
    
    # Create the DataFrame
    channel_data_df = pd.DataFrame(channel_data, columns=columns)
    
    # Convert the "Join Date" column to the desired strftime format
    channel_data_df['join_date'] = channel_data_df['join_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'))

    return channel_data_df
    pass

# Define the channel_data_preparation function
def channel_data_injection(**kwargs):
    channel_data_df = kwargs['task_instance'].xcom_pull(task_ids='channel_data_preparation')
    insert_channel_data(channel_data_df, "youtube_channel_data")
    pass


# Define the tasks

scrape_channel_data_task = PythonOperator(
    task_id='scrape_channel_data',
    python_callable=scrape_channel_data,
    provide_context=True,
    dag=dag,
)

channel_data_preparation_task = PythonOperator(
    task_id='channel_data_preparation',
    python_callable=channel_data_preparation,
    provide_context=True,
    dag=dag,
)

channel_data_injection_task = PythonOperator(
    task_id='channel_data_injection',
    python_callable=channel_data_injection,
    provide_context=True,
    dag=dag,
)

# Define the task dependencies
scrape_channel_data_task >> channel_data_preparation_task >> channel_data_injection_task
