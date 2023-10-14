import mysql.connector

class ModelPostCleanedReddit:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="rootpassword",
            database="social_media_db"
        )

    def get_data_for_max_batch_id(self):
        # Create a cursor
        cursor = self.db.cursor()
        
        # SQL query to retrieve data for the maximum batch_id
        query = "SELECT pcd. likes, num_comments, submission_time FROM social_media_db.post_cleaned_data pcd JOIN ( SELECT MAX(batch_id) AS max_batch_id FROM social_media_db.post_cleaned_data WHERE source = 'Reddit' ) max_batch ON pcd.batch_id = max_batch.max_batch_id WHERE pcd.source = 'Reddit';"

        cursor.execute(query)
        
        # Fetch the data
        data = cursor.fetchall()
        print("$$$$$$$$$$$$$$$$", data)

        
        # Close the cursor and connection
        cursor.close()
        self.db.close()
        print(data)
        return data
