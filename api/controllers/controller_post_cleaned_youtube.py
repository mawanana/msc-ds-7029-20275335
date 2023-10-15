import pandas as pd
from flask import Blueprint, jsonify
from models.model_post_cleaned_youtube import ModelPostCleanedYoutube

controller_post_cleaned_youtube_api = Blueprint('controller_post_cleaned_youtube_api', __name__)

@controller_post_cleaned_youtube_api.route('/api/post_cleaned_youtube_data', methods=['GET'])
def get_youtube_channel_data():
    try:
        model = ModelYoutubeChannel()
        data = model.get_data_for_max_batch_id()
        print("--------22222222")
        print(data)

        # Define column names
        columns = ['likes', 'num_comments', 'submission_time']
        
        # Create a DataFrame
        df = pd.DataFrame(data, columns=columns)
        

        data = df.to_dict(orient='records')
        print(data)
        print("@@@@@@@@@@@###############gggg")
    
        
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500