import ollama # type: ignore

def get_practice_question(topic: str) -> str:

    prompt = (
                f"Provide a {topic} practice question in a leetcode style. " 
                f"Give test cases in bullet points and format the question using markdown. Do NOT write any code or ask if the user wants a hint. "
                f"If there are things such as nodes or other objects that are needed to be create, define what the attributes of those objects are for the given problem. "
                f"Make the question structured in a way that would be language agnostic (no language specifics). "
                f"The message should contain the problem statement, definition of objects involved (such as nodes, etc.), test cases, and the result to be returned. "
                f"Your response must be less that 2000 characters total. "
            )
    try:
        result = ollama.generate(model='llama3.2', prompt=prompt)
        return result['response']
    except Exception as e:
        return f"An error occurred: {e}"


def main():
    ollama.create(model='llama3.2', modelfile=modelfile)

modelfile='''
    FROM llama3.2
    PARAMETER temperature 0
    SYSTEM You are a Data Sructures and Algorithms Tutor named AL_G_RITHM.
    '''

