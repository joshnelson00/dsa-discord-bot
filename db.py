import redis # "redis-server" to start redis db // "pkill redis" to stop redis db
import pandas as pd


def import_data(df):
    counter = 1
    for _, row in df.iterrows():

        problem_id = f"problem_{counter}"

        # Set simple fields (attributes)
        r.hset(problem_id, mapping = {
            "title": row['title'] if pd.notna(row['title']) else "",
            "description": row['description'] if pd.notna(row['description']) else "",
            "difficulty": row['difficulty'] if pd.notna(row['difficulty']) else "",
            "solution_link": row['solution_link'] if pd.notna(row['solution_link']) else "",
            "url": row['url'] if pd.notna(row['url']) else "",
        })
        # Add each item in related_topics to a list and assign to key
        if pd.notna(row['related_topics']):  # Check if the field is not NaN
            topics = row['related_topics'].split(',')  # Split into a list
            list_key = f"{problem_id}:related_topics"  # Use a separate key for the list
            for topic in topics:
                r.rpush(list_key, topic.strip())  # Add each topic to the Redis list
        counter+=1

# Import data
data = pd.read_csv('leetcode-dataset.csv')
df = pd.DataFrame(data)
df = df.dropna(subset=['solution_link'])
df = df.drop(columns=['id', 'is_premium', 'acceptance_rate', 'frequency', 'discuss_count', 'accepted', 'submissions', 'companies', 'likes', 'dislikes', 'rating', 'asked_by_faang', 'similar_questions'])

# Initialize DB
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
try:
    r.ping()
    print("Redis connection successful!")
except redis.ConnectionError:
    print("Redis connection failed. Is the server running?")
r.flushall()
import_data(df)



print("Data Imported!")
