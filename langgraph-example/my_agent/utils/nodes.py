from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode


@lru_cache(maxsize=4)
def _get_model(model_name: str):
    # if model_name == "openai":
        # model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    print(model_name)
    model = ChatOpenAI(
    model="claude-3-5-sonnet-latest",
    temperature=0,
    base_url="https://litellm.deriv.ai/v1",
    default_headers={"HTTP-Referer": "litellm_proxy", "x-litellm-settings": "modify_params: True"}
    )
    # elif model_name == "anthropic":
    #     model =  ChatAnthropic(temperature=0, model_name="claude-3-5-sonnet-latest")
    # else:
    #     raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


system_prompt = """You are a SQL code reviewer tasked with reviewing PR changes according to specific SQL guidelines. Your job is to ensure that the SQL code is well-aligned and follows the provided guidelines.

First, carefully read and understand the following SQL guidelines:

<sql_guidelines>
{{sql_guidelines}}
</sql_guidelines>

You are tasked with aligning SQL queries according to a specific rule. The rule states that the last character of the first word in each line should be vertically aligned across all lines. If this alignment is not possible, you should adjust the query formatting to make it compliant.

Here are examples of good and bad alignment:

Good Aligned SQL Example:
SELECT ...
  FROM ...
  JOIN ... ON ...
  LEFT JOIN ... ON ...
 RIGHT JOIN ... ON ...
 WHERE ...
   AND ...
 GROUP BY ...
HAVING ...
 ORDER BY ... DESC
 LIMIT ...
OFFSET ...

Poorly Aligned SQL Example:
SELECT ...
 FROM ...
 JOIN ... ON ...
 LEFT JOIN ... ON ...
 RIGHT JOIN ... ON ...
 WHERE ...
     AND ...
 GROUP BY ...
 HAVING ...
 ORDER BY ... DESC
 LIMIT ...
 OFFSET ...
 
Your task is to review and align the following SQL query according to the guidelines:

<sql_query>
{{SQL QUERY}}
</sql_query>

After aligning the query, review the following changes:

<changes>
{{CHANGES}}
</changes>

Provide your response in the following format:
1. If the SQL query is already well-aligned, simply state "Great alignment!".
2. If the query needs alignment, provide the aligned query within ```sql tags.
3. If only the query needed alignment, provide your review of the changes.

Write your complete answer. Do not include any explanation or commentary outside of these tags.
"""

from langchain_core.messages import BaseMessage
# Define the function that calls the model
def call_model(state, config):
    # details_message = [{"owner":state["owner"]} , {"repo": state["repo"]}, {"pr_number":state["pr_number"]}]
    # state["messages"].append(BaseMessage(content=details_message))
    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    model_name = config.get('configurable', {}).get("model_name", "openai")
    print(model_name)
    model = _get_model(model_name)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# Define the function to execute tools
tool_node = ToolNode(tools)