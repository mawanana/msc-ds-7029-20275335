import pandas as pd
import mysql.connector

from airflow.hooks.mysql_hook import MySqlHook


def insert_popularity_data(dataframe, table_name):

    # Replace NaN values in numeric columns with 0
    dataframe.fillna({'views': 0, 'likes': 0, 'num_comments': 0, 'PercentageViews': 0, 'PercentageLikes': 0, 'PercentageComments': 0, 'WeightViews': 0, 'WeightLikes': 0, 'WeightComments': 0, 'PopularityScore': 0, 'NormalizedScore': 0}, inplace=True)

    # Create a MySqlHook instance to get the MySQL connection
    mysql_hook = MySqlHook("mysql_conn_id")
    mysql_connection = mysql_hook.get_conn()

    try:
        # Create a cursor for database operations
        cursor = mysql_connection.cursor()

        # Define the SQL query to retrieve the maximum batch_id
        sql_query = "SELECT MAX(batch_id) AS max_batch_id FROM social_media_db.popularity_data;"
    
        # Execute the query
        cursor.execute(sql_query)

        # Fetch the result (maximum batch_id)
        max_batch_id = cursor.fetchone()[0]
        if max_batch_id is None:
            max_batch_id = 1
        else:
            max_batch_id += 1  # Increment the max_batch_id by 1

        # Iterate over DataFrame rows and insert data into the MySQL table
        for _, row in dataframe.iterrows():
            insert_query = f"""
                INSERT INTO {table_name} (
                    batch_id, source, url, submission_time, title, views, likes, num_comments,
                    PercentageViews, PercentageLikes, PercentageComments, WeightViews,
                    WeightLikes, WeightComments, PopularityScore, NormalizedScore
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            values = (
                max_batch_id, row['source'], row['url'], row['submission_time'], row['title'],
                row['views'], row['likes'], row['num_comments'], row['PercentageViews'],
                row['PercentageLikes'], row['PercentageComments'], row['WeightViews'],
                row['WeightLikes'], row['WeightComments'], row['PopularityScore'],
                row['NormalizedScore']
            )

            cursor.execute(insert_query, values)

        # Commit the changes to the database
        mysql_connection.commit()

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close cursor and database connection
        cursor.close()
        mysql_connection.close()

        
def insert_comment_data(dataframe, table_name):
    # Create a MySqlHook instance to get the MySQL connection
    mysql_hook = MySqlHook("mysql_conn_id")
    mysql_connection = mysql_hook.get_conn()

    try:
        # Create a cursor for database operations
        cursor = mysql_connection.cursor()

        # Define the SQL query to retrieve the maximum batch_id
        sql_query = "SELECT MAX(batch_id) AS max_batch_id FROM social_media_db.comments_cleaned_data;"
    
        # Execute the query
        cursor.execute(sql_query)

        # Fetch the result (maximum batch_id)
        max_batch_id = cursor.fetchone()[0]
        if max_batch_id is None:
            max_batch_id = 1
        else:
            max_batch_id += 1  # Increment the max_batch_id by 1
            
        # Iterate over DataFrame rows and insert data into the MySQL table
        for _, row in dataframe.iterrows():
            insert_query = """
                INSERT INTO comments_cleaned_data (
                    batch_id, source, url, comment, author, likes, dislikes, replies, extra
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            values = (
                max_batch_id, row['source'], row['url'], row['comment'], row['author'], row['likes'],
                row['dislikes'], row['replies'], row['extra'],
            )
                    
            cursor.execute(insert_query, values)

        # Commit the changes to the database
        mysql_connection.commit()

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close cursor and database connection
        cursor.close()
        mysql_connection.close()


def insert_post_data(dataframe, table_name):
  
    # Create a MySqlHook instance to get the MySQL connection
    mysql_hook = MySqlHook("mysql_conn_id")
    mysql_connection = mysql_hook.get_conn()

    try:
        # Create a cursor for database operations
        cursor = mysql_connection.cursor()

        # Define the SQL query to retrieve the maximum batch_id
        sql_query = "SELECT MAX(batch_id) AS max_batch_id FROM social_media_db.post_cleaned_data;"
    
        # Execute the query
        cursor.execute(sql_query)

        # Fetch the result (maximum batch_id)
        max_batch_id = cursor.fetchone()[0]
        if max_batch_id is None:
            max_batch_id = 1
        else:
            max_batch_id += 1  # Increment the max_batch_id by 1

        # Iterate over DataFrame rows and insert data into the MySQL table
        for _, row in dataframe.iterrows():
            insert_query = """
                INSERT INTO post_cleaned_data (
                    batch_id, source, url, title, views, likes, dislikes, num_comments,
                    description, submission_time, author_name
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
            values = (
                max_batch_id, row['source'], row['url'], row['title'], row['views'], row['likes'],
                row['dislikes'], row['num_comments'], row['description'], row['submission_time'], row['author_name'],
            )
            
            cursor.execute(insert_query, values)

        # Commit the changes to the database
        mysql_connection.commit()

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close cursor and database connection
        cursor.close()
        mysql_connection.close()
