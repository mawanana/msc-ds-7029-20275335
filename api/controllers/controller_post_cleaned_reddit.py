import pandas as pd
from flask import Blueprint, jsonify
from models.model_post_cleaned_reddit import ModelPostCleanedReddit

controller_post_cleaned_reddit_api = Blueprint('controller_post_cleaned_reddit_api', __name__)

@controller_post_cleaned_reddit_api.route('/api/post_cleaned_reddit_data', methods=['GET'])
def get_post_cleaned_reddit_data():
    try:
        model = ModelPostCleanedReddit()
        data = model.get_data_for_max_batch_id()
        print("--------22222222")
        print(data)

        # Define column names
        columns = ['likes', 'num_comments', 'submission_time']
        
        # Create a DataFrame
        df = pd.DataFrame(data, columns=columns)
        
        # # Drop the specified columns
        # columns_to_drop = ['id', 'batch_id', 'dislikes', 'shares', 'join_date', 'create_date']
        # df = df.drop(columns=columns_to_drop)

        data = df.to_dict(orient='records')
        print(data)
    
        
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
