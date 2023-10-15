from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# Replace with your MySQL database credentials
db_config = {
    "host": "msc_ds-7029-20275335-mysql-1",
    "user": "airflow",
    "password": "rootpassword",
    "database": "social_media_db"
}

# Create a MySQL connection
db = mysql.connector.connect(**db_config)

@app.route('/get_comments_data', methods=['GET'])
def get_comments_data():
    try:
        cursor = db.cursor()
        
        # Query to retrieve data for the highest batch_id
        query = """
        SELECT comment_text, likes, shares, replies
        FROM comments_processed_data
        WHERE batch_id = (
            SELECT MAX(batch_id) FROM comments_processed_data
        )
        """
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        if result:
            data = []
            for row in result:
                comment_data = {
                    "comment_text": row[0],
                    "likes": row[1],
                    "shares": row[2],
                    "replies": row[3]
                }
                data.append(comment_data)
            
            return jsonify(data)
        else:
            return jsonify({"message": "No data found"})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
