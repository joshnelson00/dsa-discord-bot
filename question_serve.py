import textwrap
from db import *
import discord
from discord import ui
from discord.ui import Modal, TextInput, Select
import random
import ollama  # type: ignore

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

    # Pick a problem that satisfies the length constraint
    valid_problems = [
        problem for problem in filtered_problems
        if len(get_md_text(problem)) <= 2000  # Ensure the problem length is valid
    ]
    if not valid_problems:
        print(f"No problems found under 2000 characters for topic '{topic}' with difficulty '{difficulty}'.")
        return None

    problem = random.choice(valid_problems)
    return problem

def get_md_text(problem):
    # Check if the problem is a dictionary or a string
    if isinstance(problem, dict):
        title = problem.get('title', 'Untitled Problem')
        url = problem.get('url', '#')
        difficulty = problem.get('difficulty', 'Unknown')
        solution_link = f"https://leetcode.com{problem.get('solution_link', '#')}"
        description = problem.get('description', 'No description available.')

        # Markdown payload without indent and with centered title
        message = f"""\
        # {title}
        Difficulty: {difficulty}
        Description: {description}

        **[View Problem]({url})**
        **[View Solution]({solution_link})**"""
    else:
        # If the problem is a string (likely from AI), just return it directly
        message = problem  # The problem itself is already a formatted string

    return message





def get_ai_problem(topic, difficulty, model="llama3.2"):
    # Construct the prompt dynamically using f-strings
    prompt = f"""
    You are AL_G_RITHM, a Data Structures and Algorithms Tutor.
    You are to provide a leetcode-style practice problem to help with data structures and algorithms.
    The required topic and difficulty of the question are below.
    Topic: {topic}
    Difficulty: {difficulty}
    """
    try:
        response = ollama.generate(prompt=prompt, model=model)
        if "response" in response:
            return response["response"]
        else:
            print(f"Error: Unexpected response format - {response}")
            return "Sorry, I couldn't process your request right now."
    except Exception as e:
        print(f"Error querying Ollama API: {e}")
        return "Sorry, I couldn't process your request right now."

modelfile = '''
    FROM llama3.2
    PARAMETER temperature 0.7
    SYSTEM You are a Data Structures and Algorithms Tutor named AL_G_RITHM.
'''
