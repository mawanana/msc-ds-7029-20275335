import mysql.connector

class ModelYoutubeChannel:
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
        query = "SELECT * FROM social_media_db.youtube_channel_data WHERE batch_id = (SELECT MAX(batch_id) FROM social_media_db.youtube_channel_data)"
        cursor.execute(query)
        
        # Fetch the data
        data = cursor.fetchall()
        
        # Close the cursor and connection
        cursor.close()
        self.db.close()
        print(data)
        return data
