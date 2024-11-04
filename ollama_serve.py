import ollama

def get_response(topic: str) -> str:
    try:
        result = ollama.generate(model='llama3.2', prompt=topic)
        return result['response']
    except Exception as e:
        return f"An error occurred: {e}"


def main():
    ollama.create(model='llama3.2', modelfile=modelfile)

modelfile='''
    FROM llama3.2
    PARAMETER temperature 0.5
    SYSTEM You are a Data Sructures and Algorithms Tutor named AL_G_RITHM. You will provide 1 practice problem similar to leetcode based upon the subject input. Do not give the answer.
    '''

