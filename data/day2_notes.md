# Day 2 — LLM APIs, Structured Output, Tool Calling

## Setting up API access
Anthropic or OpenAI both give an API key after signup. Never hardcode the key in your code. Store it in a `.env` file and load it with `python-dotenv`. Always add `.env` to `.gitignore` before writing any code, so the key never gets pushed to GitHub by mistake.

## Basic API call
```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=200,
    messages=[{"role": "user", "content": "Say hello"}]
)
print(response.content[0].text)
```
The model does not remember past messages on its own — every call is independent. To have a conversation, you must resend the full message history each time.

## Structured output
Instead of letting the model reply in free text, you can instruct it to return only JSON, then parse it in Python with `json.loads()`. This is important because real applications need to use the model's output in code, not just display it as text.

**Weakness:** the model can sometimes add extra text around the JSON, or return invalid JSON if the question is ambiguous. This needs to be handled with error checking (`try/except` around `json.loads()`).

## Tool calling (function calling)
Tool calling lets the model decide WHEN and WITH WHAT ARGUMENTS to call a function, but the model itself does NOT execute the function. The actual code must:

1. Define a tool with a name, description, and input schema (what arguments it needs)
2. Send the tool definition along with the user's message
3. If the model decides a tool is needed, it returns a `tool_use` block with the function name and arguments, instead of a normal text answer
4. The developer's code runs the real function using those arguments
5. The result is sent back to the model in a second API call, and the model uses it to generate the final answer

### Example flow
- User asks: *"What's the weather in Bengaluru?"*
- Model replies: wants to call `get_weather(city="Bengaluru")`
- Code runs the real `get_weather()` function, gets a result
- Code sends that result back to the model
- Model replies with the final natural language answer

**Why this matters:** tool calling is the foundation of AI agents. An agent is basically an LLM that can repeatedly call tools, read their results, and decide the next action, instead of just answering once.

## Key takeaway
The model is the "brain" that decides what to do, but all actual actions (calling APIs, running functions, fetching data) are code that I write and control. The model never directly touches the real world.