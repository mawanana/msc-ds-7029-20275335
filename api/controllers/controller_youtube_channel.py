import pandas as pd
from flask import Blueprint, jsonify
from models.model_youtube_channel import ModelYoutubeChannel

controller_youtube_channel_api = Blueprint('controller_youtube_channel_api', __name__)

@controller_youtube_channel_api.route('/api/youtube_channel_data', methods=['GET'])
def get_post_cleaned_youtube_data():
    try:
        model = ModelYoutubeChannel()
        data = model.get_data_for_max_batch_id()
        print("--------22222222")
        print(data)

        # Define column names
        columns = ['id', 'batch_id', 'source', 'subscribers', 'videos', 'likes', 'dislikes', 'shares', 'comments', 'views', 'join_date', 'create_date']
        
        # Create a DataFrame
        df = pd.DataFrame(data, columns=columns)
        
        # Drop the specified columns
        columns_to_drop = ['id', 'batch_id', 'dislikes', 'shares', 'join_date', 'create_date']
        df = df.drop(columns=columns_to_drop)

        data = df.to_dict(orient='records')
        print(data)
    
        
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# import pandas as pd
# from flask import Blueprint, jsonify
# from models.model_post_cleaned_youtube import ModelPostCleanedYoutube

# controller_post_cleaned_youtube_api = Blueprint('controller_post_cleaned_youtube_api', __name__)

# @controller_post_cleaned_youtube_api.route('/api/post_cleaned_youtube_data', methods=['GET'])
# def get_post_cleaned_youtube_data():
#     try:
#         model = ModelYoutubeChannel()
#         data = model.get_data_for_max_batch_id()
#         print("--------22222222")
#         print(data)

#         # Define column names
#         columns = ['id', 'batch_id', 'source', 'subscribers', 'videos', 'likes', 'dislikes', 'shares', 'comments', 'views', 'join_date', 'create_date']
        
#         # Create a DataFrame
#         df = pd.DataFrame(data, columns=columns)
        
#         # Drop the specified columns
#         columns_to_drop = ['id', 'batch_id', 'dislikes', 'shares', 'join_date', 'create_date']
#         df = df.drop(columns=columns_to_drop)

#         data = df.to_dict(orient='records')
#         print(data)
    
        
#         return jsonify(data)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
