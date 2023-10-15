from flask import Flask, jsonify
from controllers.controller_comments_cleaned_data import process_api_request_comments_cleaned_data
from controllers.controller_post_cleaned_data import process_api_request_post_cleaned_data
from controllers.controller_youtube_channel_data import process_api_request_youtube_channel_data

app = Flask(__name)

@app.route('/api/comments_cleaned_data')
def api_comments_cleaned_data():
    data = process_api_request_comments_cleaned_data()
    return jsonify(data)

@app.route('/api/post_cleaned_data')
def api_post_cleaned_data():
    data = process_api_request_post_cleaned_data()
    return jsonify(data)

@app.route('/api/youtube_channel_data')
def api_youtube_channel_data():
    data = process_api_request_youtube_channel_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
