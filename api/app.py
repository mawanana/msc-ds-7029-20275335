from flask import Flask
from controllers.controller_youtube_channel import controller_youtube_channel_api
from controllers.controller_post_cleaned_reddit import controller_post_cleaned_reddit_api
from controllers.controller_post_cleaned_youtube import controller_post_cleaned_youtube_api

app = Flask(__name__)

app.register_blueprint(controller_youtube_channel_api, url_prefix='/controller_youtube_channel')
app.register_blueprint(controller_post_cleaned_reddit_api, url_prefix='/controller_post_cleaned_reddit')
app.register_blueprint(controller_post_cleaned_youtube_api, url_prefix='/controller_post_cleaned_youtube')

if __name__ == '__main__':
    app.run(debug=True)