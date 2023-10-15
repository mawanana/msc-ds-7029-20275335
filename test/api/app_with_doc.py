# from flask import Flask, jsonify
# from flask_restplus import Api, Resource

# app = Flask(__name)
# api = Api(app, version='1.0', title='API Documentation', description='Sample API Documentation')
from flask_restplus import Api

api = Api(app, version='1.0', title='API Documentation', description='Sample API Documentation', compate=False)

# Import controllers and models
from controllers.controller_comments_cleaned_data import process_api_request_comments_cleaned_data
from controllers.controller_post_cleaned_data import process_api_request_post_cleaned_data
from controllers.controller_youtube_channel_data import process_api_request_youtube_channel_data

# Namespace for the first API
ns_comments_cleaned_data = api.namespace('api/comments_cleaned_data', description='API for Comments Cleaned Data')

@ns_comments_cleaned_data.route('/')
class CommentsCleanedData(Resource):
    def get(self):
        """Get data for Comments Cleaned Data"""
        data = process_api_request_comments_cleaned_data()
        return jsonify(data)

# Namespace for the second API
ns_post_cleaned_data = api.namespace('api/post_cleaned_data', description='API for Post Cleaned Data')

@ns_post_cleaned_data.route('/')
class PostCleanedData(Resource):
    def get(self):
        """Get data for Post Cleaned Data"""
        data = process_api_request_post_cleaned_data()
        return jsonify(data)

# Namespace for the third API
ns_youtube_channel_data = api.namespace('api/youtube_channel_data', description='API for YouTube Channel Data')

@ns_youtube_channel_data.route('/')
class YoutubeChannelData(Resource):
    def get(self):
        """Get data for YouTube Channel Data"""
        data = process_api_request_youtube_channel_data()
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
