import json
from openai import OpenAI

# Assume you have your OpenAI API key set as an environment variable
# export OPENAI_API_KEY='your-api-key'
client = OpenAI()

# Define the tools (functions) that the LLM can call
# This is a list of dictionaries, each describing a function.
# The 'name' is how the LLM will refer to the function.
# The 'description' helps the LLM understand when to use the function.
# 'parameters' define the expected arguments for the function.
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit, can be celsius or fahrenheit",
                    },
                },
                "required": ["location"],
            },
        }
    }
]

# This is a mock function that simulates calling an external API.
# In a real application, this would make an actual API call.
def get_current_weather(location: str, unit: str = "celsius") -> str:
    """Simulates fetching weather data."""
    print(f"--- Calling external weather API for {location} in {unit} ---")
    # In a real scenario, you'd call a weather API here.
    # For demonstration, we'll return a canned response.
    if "istanbul" in location.lower():
        return f"The weather in {location} is sunny and 25 {unit}."
    elif "ankara" in location.lower():
        return f"The weather in {location} is cloudy and 15 {unit}."
    else:
        return f"Weather data not available for {location}."

# Map function names to actual Python functions.
# This dictionary is used to execute the function called by the LLM.
available_functions = {
    "get_current_weather": get_current_weather,
}

# The user's query
user_query = "Bugün İstanbul'da hava nasıl?"
# user_query = "What's the weather like in Ankara?"

print(f"User Query: {user_query}")

# First, call the LLM to see if it wants to call a tool.
chat_completion = client.chat.completions.create(
    model="gpt-4o", # Or gpt-3.5-turbo, etc.
    messages=[{"role": "user", "content": user_query}],
    tools=tools, # Pass the defined tools to the model
    tool_choice="auto", # Let the model decide whether to call a tool
)

# Extract the response from the LLM
response_message = chat_completion.choices[0].message

# Check if the LLM decided to call a tool
if response_message.tool_calls:
    # Get the tool call details
    tool_call = response_message.tool_calls[0].function
    function_name = tool_call.name
    function_args = json.loads(tool_call.arguments)

    print(f"LLM wants to call function: {function_name}")
    print(f"With arguments: {function_args}")

    # Check if the requested function is available in our mapping
    if function_name in available_functions:
        # Get the actual Python function
        function_to_call = available_functions[function_name]

        # Call the function with the arguments provided by the LLM
        # We use **function_args to unpack the dictionary into keyword arguments.
        function_response = function_to_call(**function_args)

        print(f"Function Response: {function_response}")

        # Optionally, you can then send this function response back to the LLM
        # to generate a natural language answer based on the tool's output.
        # For this example, we'll just print the function response.

    else:
        print(f"Error: Function '{function_name}' not found.")
else:
    # If the LLM did not call a tool, it likely generated a direct text response.
    print(f"LLM Direct Response: {response_message.content}")
