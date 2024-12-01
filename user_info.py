from typing import List
import requests

def get_user_data(username: str):
    url = f"https://leetcode-api-faisalshohag.vercel.app/{username}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        print("API request failed with status:", response.status_code)
        return False

    if 'errors' in data:
        print(f"User {username} not found.")
        return False

    # Standardize the keys
    summary = {
        "username": username,
        "easySolved": data['easySolved'],
        "mediumSolved": data['mediumSolved'],
        "hardSolved": data['hardSolved'],
    }

    return summary

def get_desktop_leetcode_leaderboard(users: List[str]):
    user_data_list = []

    # Collect user data
    for user in users:
        user_data = get_user_data(user)
        if user_data:  # Skip None results
            user_data_list.append(user_data)

    # Check if we have valid user data to display
    if not user_data_list:
        return "No valid user data available to display."

    # Sort user data based on the weighted sum (Total Score)
    sorted_data = sorted(
        user_data_list,
        key=lambda d: d['easySolved'] * 1 + d['mediumSolved'] * 2 + d['hardSolved'] * 3,
        reverse=True
    )

    # Create formatted leaderboard table with Markdown header
    trophy_emoji = ":trophy:"
    leaderboard_message =  f"# {trophy_emoji} **Leaderboard** {trophy_emoji}\n\n"
    leaderboard_message += "```"
    leaderboard_message += "+------+-----------------+-------------+---------------+-------------+-------------+\n"
    leaderboard_message += "+------+-----------------+-------------+---------------+-------------+-------------+\n"
    leaderboard_message += "| #    | Username        | Easy Solved | Medium Solved | Hard Solved | Total Score |\n"
    leaderboard_message += "+------+-----------------+-------------+---------------+-------------+-------------+\n"

    # Populate leaderboard with user data
    for i, user in enumerate(sorted_data, 1):
        easy = user['easySolved']
        medium = user['mediumSolved']
        hard = user['hardSolved']
        total_score = easy * 1 + medium * 2 + hard * 3
        leaderboard_message += f"| {i:<4} | {user['username']:<15} | {easy:<11} | {medium:<13} | {hard:<11} | {total_score:<11} |\n"

    leaderboard_message += "+------+-----------------+-------------+---------------+-------------+-------------+ ```"

    return leaderboard_message

def get_mobile_leetcode_leaderboard(users: List[str]):
    user_data_list = []

    # Collect user data
    for user in users:
        user_data = get_user_data(user)
        if user_data:  # Skip None results
            user_data_list.append(user_data)

    # Check if we have valid user data to display
    if not user_data_list:
        return "No valid user data available to display."

    # Sort user data based on the weighted sum (Total Score)
    sorted_data = sorted(
        user_data_list,
        key=lambda d: d['easySolved'] * 1 + d['mediumSolved'] * 2 + d['hardSolved'] * 3,
        reverse=True
    )

    # Create formatted leaderboard message
    trophy_emoji = ":trophy:"
    leaderboard_message =  f"{trophy_emoji} **Leaderboard** {trophy_emoji}\n\n"
    
    # Compact horizontal display for leaderboard
    leaderboard_message += "```\n"
    leaderboard_message += "Rank | Username   | Easy | Med | Hard | Total\n"
    leaderboard_message += "---------------------------------------------\n"

    # Populate leaderboard with user data
    for i, user in enumerate(sorted_data, 1):
        easy = user['easySolved']
        medium = user['mediumSolved']
        hard = user['hardSolved']
        total_score = easy * 1 + medium * 2 + hard * 3
        leaderboard_message += f"{i:<4} | {user['username'][:10]:<10} | {easy:<4} | {medium:<3} | {hard:<4} | {total_score:<5}\n"

    leaderboard_message += "```"

    return leaderboard_message


def leetcode_user_exists(username: str):
    url = f"https://leetcode-api-faisalshohag.vercel.app/{username}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        print("API request failed with status:", response.status_code)
        return

    if 'errors' in data:
        print(f"User {username} not found.")
        return False
    return True

