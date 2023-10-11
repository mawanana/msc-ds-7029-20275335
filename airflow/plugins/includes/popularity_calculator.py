import pandas as pd

def calculate_popularity(df):
    primary_coloum_df = ['source', 'url', 'submission_time']
    primary_coloum_df = df[primary_coloum_df]

    
    # List of column names you want in the new DataFrame
    new_df_column_names = ['title', 'views', 'likes', 'num_comments']
    
    # Create a new DataFrame by selecting the desired columns
    df = df[new_df_column_names]
    
    # Calculate total views, likes, and comments
    total_views = df['views'].sum()
    total_likes = df['likes'].sum()
    total_comments = df['num_comments'].sum()
    
    # Calculate percentage values
    df['PercentageViews'] = (df['views'] / total_views) * 100
    df['PercentageLikes'] = (df['likes'] / total_likes) * 100
    df['PercentageComments'] = (df['num_comments'] / total_comments) * 100
    
    # Define weights as the complement of the percentage values
    df['WeightViews'] = 100 - df['PercentageViews']
    df['WeightLikes'] = 100 - df['PercentageLikes']
    df['WeightComments'] = 100 - df['PercentageComments']
    
    # Calculate popularity score for each row
    df['PopularityScore'] = (df['WeightViews'] * df['views']) + (df['WeightLikes'] * df['likes']) + (df['WeightComments'] * df['num_comments'])
    
    # Normalize the popularity scores (optional)
    min_score = df['PopularityScore'].min()
    max_score = df['PopularityScore'].max()
    df['NormalizedScore'] = (df['PopularityScore'] - min_score) / (max_score - min_score)
    
    # Sort rows by popularity score in descending order
    df = df.sort_values(by='PopularityScore', ascending=False)

    # Concatenate vertically (stack rows)
    combined_df = pd.concat([primary_coloum_df, df], axis=0)
    
    # Reset the index if needed
    combined_df.reset_index(drop=True, inplace=True)
    
    # Print the sorted DataFrame
    print(df)
    
    return df