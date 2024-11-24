import ollama # type: ignore

def query_ollama(prompt, model="llama3.2"):
    """Query the Ollama API with a prompt."""
    try:
        response = ollama.generate(prompt=prompt, model=model)
        if "response" in response:
            return response["response"]
        else:
            # Log and return a default error message if the 'response' field is missing
            print(f"Error: Unexpected response format - {response}")
            return "Sorry, I couldn't process your request right now."
    except Exception as e:
        # Handle exceptions and log the error
        print(f"Error querying Ollama API: {e}")
        return "Sorry, I couldn't process your request right now."

modelfile = '''
    FROM llama3.2
    PARAMETER temperature 0.7
    SYSTEM You are a Data Structures and Algorithms Tutor named AL_G_RITHM.
'''


def main():
    try:
        ollama.create(model="llama3.2", modelfile=modelfile)
    except Exception as e:
        print(f"Error creating Ollama model: {e}")

