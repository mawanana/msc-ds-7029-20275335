import praw
import pandas as pd
from datetime import datetime
from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator

from includes.scraper_operator import get_unique_elements
from includes.mysql_query_executor import insert_post_data
from includes.mysql_query_executor import insert_comment_data
from includes.mysql_query_executor import insert_popularity_data
from includes.popularity_calculator import calculate_popularity

# Define default arguments for the DAG
default_args = {
    'owner': 'MSc DS-7029-20275335',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 5),
    'retries': 1,
}

# Create the Airflow DAG
dag = DAG(
    'raddit_data_pipeline',
    default_args=default_args,
    description='DAG for raddit pipeline',
    schedule_interval='0 0 * * 1',  # Set your desired schedule interval or None
    catchup=False,
    max_active_runs=1,
    concurrency=1,
    dagrun_timeout=None,
    tags=['data', 'pipeline'],
)

# Define the scrape_data function
def scrape_data():
    post_data = []
    comment_data = []
    # Reddit API credentials
    client_id = 'rXf-0NseUho9HifbbYVD-Q'
    client_secret = '5eNKToLc7Kqon0aPajHsK5sBytZOgQ'
    user_agent = 'https://www.reddit.com/r/FormerPizzaHuts/'
    
    # Initialize the Reddit API client
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    
    # Subreddit to scrape
    subreddit_name = 'FormerPizzaHuts'
    
    # Number of posts to scrape
    num_posts = 5000  # Adjust as needed
    
    # Post ID to start from (from the URL you provided)
    after_post_id = 't3_10qoih0'  # Replace with the actual post ID
    
    # Scrape the subreddit starting from the specified post
    subreddit = reddit.subreddit(subreddit_name)
    latest_posts = subreddit.new(limit=num_posts)  # Use to get the latest posts
    # top_posts = subreddit.top(limit=num_posts, params={'after': after_post_id})   # Use to get the top posts
    
    # Print post details and comments
    for post in latest_posts:
        url =  post.url
        title = post.title
        if hasattr(post, 'view_count'):
            views = post.view_count
        else:
            views = ""
        likes = post.score
        dislikes = post.downs
        num_comments = post.num_comments
        description = post.selftext
        submission_time = post.created_utc
        if post.author:
            author_name = post.author.name
        else:
            author_name = ""
        
        # Append post data to the post_data list
        post_data.append([url, title, views, likes, dislikes, num_comments, description, submission_time, author_name])
        
        # Iterate through the comments of the post
        for comment in post.comments:
            url = post.url
            comment = comment.body
            # Append comment data to the comment_data list
            comment_data.append([url, comment])
    return post_data, comment_data
    pass

# Define the post_data_preparation function
def post_data_preparation(**kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='scrape_data')
    post_prepared_data = []
    for element in data[0]:
        # Use a list comprehension to replace 'None' with ''
        element = ['' if item == 'None' else item for item in element]

        source = "Reddit"
        url = element[0]
        title = element[1]

        if element[2] is not None:
            try:
                views = int(element[2])
            except ValueError:
                views = 0
        else:
            views = 0
        if element[3] is not None:
            try:
                likes = int(element[3])
            except ValueError:
                likes = 0
        else:
            views = 0
        if element[4] is not None:
            try:
                dislikes = int(element[4])
            except ValueError:
                dislikes = 0
        else:
            views = 0
        if element[5] is not None: 
            try:
                num_comments = int(element[5])
            except ValueError:
                num_comments = 0
        else:
            views = 0
        
        description = element[6]
        # Convert UTC timestamp to a datetime object
        utc_datetime = datetime.utcfromtimestamp(element[7])
        # Format the datetime object as a string (in a specific format, if desired)
        submission_time = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        author_name = element[8]
        # print(source, "|" ,url, "|" , title, "|" , views, "|" , likes, "|" ,dislikes, "|" , num_comments, "|" ,description, "|" ,submission_time, "|" , author_name)
        post_prepared_data.append([source, url, title, views, likes, dislikes, num_comments, description, submission_time, author_name])
    # post_prepared_data = get_unique_elements(post_prepared_data)

    # Define column names for your DataFrame
    column_names = ['source', 'url', 'title', 'views', 'likes', 'dislikes', 'num_comments', 'description', 'submission_time', 'author_name']
    
    # Create a Pandas DataFrame
    post_prepared_data_df = pd.DataFrame(post_prepared_data, columns=column_names)

    return post_prepared_data_df    
    pass

# Define the comment_data_preparation function
def comment_data_preparation(**kwargs):
    data = kwargs['task_instance'].xcom_pull(task_ids='scrape_data')
    column_prepared_data = []
    for element in data[1]:
        # Use a list comprehension to replace 'None' with ''
        element = ['' if item == 'None' else item for item in element]

        source = "Reddit"
        url = element[0]
        comment = element[1]
        author = ''
        likes = 0
        dislikes = 0
        replies = 0
        extra = ''

        column_prepared_data.append([source, url, comment, author, likes, dislikes, replies, extra])
    # post_prepared_data = get_unique_elements(post_prepared_data)

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

# Create tasks using PythonOperators
scrape_data_task = PythonOperator(
    task_id='scrape_data',
    python_callable=scrape_data,
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
scrape_data_task >> post_data_preparation_task >> post_data_injection_task
scrape_data_task >> comment_data_preparation_task >> comment_data_injection_task
scrape_data_task >> post_data_preparation_task >> calculate_popularity_task >> popularity_data_injection_task

if __name__ == "__main__":
    dag.cli()