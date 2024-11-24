from typing import List
import requests

def get_user_data(username: str):
    url = f"https://leetcode-api-faisalshohag.vercel.app/{username}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        print("API request failed with status:", response.status_code)
        return

    if 'errors' in data:
        print(f"User {username} not found.")
        return

    # Standardize the keys
    summary = {
        "username": username,
        "easySolved": data['easySolved'],
        "mediumSolved": data['mediumSolved'],
        "hardSolved": data['hardSolved'],
    }

    return summary

def get_leetcode_leaderboard(users: List[str]):
    user_data_list = []

    # Collect user data
    for user in users:
        user_data = get_user_data(user)
        if user_data:  # Skip None results
            user_data_list.append(user_data)

    # Check if we have valid user data to display
    if not user_data_list:
        return "No valid user data available to display."

    # Sort user data based on the weighted sum
    sorted_data = sorted(
        user_data_list,
        key=lambda d: d['easySolved'] * 1 + d['mediumSolved'] * 2 + d['hardSolved'] * 3,
        reverse=True
    )

    # Print sorted leaderboard
    leaderboard_message = ""
    for i, user in enumerate(sorted_data, 1):
        leaderboard_message += f"{i}. {user['username']} - Easy: {user['easySolved']}, Medium: {user['mediumSolved']}, Hard: {user['hardSolved']}\n"

    return leaderboard_message


