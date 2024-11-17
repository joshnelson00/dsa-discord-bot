from db import *
import discord
from discord import ui
from discord.ui import Modal, TextInput, Select

def get_options():
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

def get_problems_with_topic(topic):
    problems_with_topic = []
    
    # Iterate through all problems to find the topic in their related_topics list
    for problem_id in r.keys("problem_*"):  # Assuming your problem keys follow the pattern "problem_*"
        list_key = f"{problem_id}:related_topics"
        
        # Get all topics in the related_topics list
        related_topics = r.lrange(list_key, 0, -1)  
        related_topics = list(set(related_topics))  # Remove duplicates
        print(f"Checking {problem_id}: Found related topics: {related_topics}")  # Debugging
        
        if topic in related_topics:
            problem_details = r.hgetall(problem_id)  # Get the problem's details
            print(f"Found {problem_id} with topic '{topic}': {problem_details}")  # Debugging
            problems_with_topic.append(problem_details)  # Append the problem details to the list
    
    return problems_with_topic

def get_problem(topic: str):
    problem_id_list = get_problems_with_topic(topic)


    print(problem_id_list)
get_problem('Array')
