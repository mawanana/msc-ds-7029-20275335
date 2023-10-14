import mysql.connector

class ModelPostCleaned:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="rootpassword",
            database="social_media_db"
        )

    def get_data_for_max_batch_id(self):
        cursor = self.db.cursor()

        query = """
            SELECT * FROM post_cleaned_data
            WHERE batch_id = (SELECT MAX(batch_id) FROM post_cleaned_data)
        """
        cursor.execute(query)
        data = cursor.fetchall()

        cursor.close()
        self.db.close()

        return data





# import mysql.connector

# class Model2:
#     def __init__(self):
#         self.db = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="rootpassword",
#             database="your_database"  # Replace with the actual database name
#         )

#     def get_data(self):
#         try:
#             cursor = self.db.cursor()

#             # Perform a database query to retrieve data for Model 2
#             cursor.execute("SELECT * FROM model2_table")
#             data = cursor.fetchall()

#             # Process and return the data
#             processed_data = self.process_data(data)

#             return processed_data

#         finally:
#             cursor.close()
#             self.db.close()

#     def process_data(self, data):
#         # Perform any data processing or formatting specific to Model 2
#         # For example, create a list of dictionaries

#         processed_data = []
#         for row in data:
#             processed_data.append({
#                 "field1": row[0],
#                 "field2": row[1],
#                 # ...
#             })

#         return processed_data
