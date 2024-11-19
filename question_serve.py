from db import *
import discord
from discord import ui
from discord.ui import Modal, TextInput, Select
import random

def get_topic_options():
    topics = [
        "Array",
        "Hash Table",
        "Linked List",
        "Math",
        "Recursion",
        "Two Pointers",
        "String",
        "Sliding Window",
        "Binary Search",
        "Divide and Conquer",
        "Dynamic Programming",
        "Backtracking",
        "Depth-first Search",
        "Stack",
        "Heap",
        "Greedy",
        "Sort",
        "Bit Manipulation",
        "Tree",
        "Breadth-first Search",
        "Union Find",
        "Graph",
        "Design",
        "Queue",
    ]
    topics.sort()
    options = []
    for topic in topics:
        options.append(discord.SelectOption(label=topic))
    return options

def get_difficulty_options():
    difficulties = [
        "Easy",
        "Medium", 
        "Hard"
    ]
    options = []
    for difficulty in difficulties:
        options.append(discord.SelectOption(label=difficulty))
    return options

def get_problems_with_topic(topic):
    problems_with_topic = []
    
    # Iterate through all problems to find the topic in their related_topics list
    for problem_id in r.keys("problem_*"):  # Assuming your problem keys follow the pattern "problem_*"
        list_key = f"{problem_id}:related_topics"
        
        # Get all topics in the related_topics list
        related_topics = r.lrange(list_key, 0, -1)  
        related_topics = list(set(related_topics))  # Remove duplicates
        
        if topic in related_topics:
            problem_details = r.hgetall(problem_id)  # Get the problem's details
            problems_with_topic.append(problem_details)  # Append the problem details to the list
    
    return problems_with_topic

def get_problem(topic: str, difficulty: str):
    # Fetch problems filtered by topic
    problem_topic_list = get_problems_with_topic(topic)
    if not problem_topic_list:
        print(f"No problems found for the topic '{topic}'.")
        return None

    # Filter problems by difficulty
    filtered_problems = [
        problem for problem in problem_topic_list
        if problem.get("difficulty", "").lower() == difficulty.lower()
    ]
    if not filtered_problems:
        print(f"No problems found for topic '{topic}' with difficulty '{difficulty}'.")
        return None

    problem = random.choice(filtered_problems)
    return problem

def get_md_text(problem: dict):
    title = problem['title']
    url = problem['url']
    difficulty = problem['difficulty']
    solution_link = f"https://leetcode.com{problem['solution_link']}"
    description = problem['description']

    # Markdown payload without indent and with centered title
    message = f"""
    # {title}
    Difficulty: {difficulty}
    \n
    Description: {description}
    \n
    [View Problem]({url})
    [View Solution]({solution_link})
    """
    return message
