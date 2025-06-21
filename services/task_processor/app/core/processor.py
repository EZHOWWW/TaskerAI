from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models import BaseChatModel

# We will get the task model from our shared library
from core_lib.models.task import Task

# --- System Prompt ---
# This is the core instruction for our AI assistant.
PROMPT_TEMPLATE = """
You are TaskerAI, an expert assistant specializing in project management and task decomposition.
Your goal is to take a user's high-level goal and break it down into a structured, actionable root task with relevant sub-tasks.

Please analyze the user's goal provided below and generate a response in the required JSON format.
Here are the rules and definitions for the fields:
- title: A concise, clear title for the main task, derived from the user's goal.
- description: A slightly more detailed description of the main task.
- subtasks: A list of smaller, concrete, and actionable steps needed to achieve the main goal. Each sub-task should be a self-contained action that can be completed in a reasonable amount of time. If the goal is simple and requires no decomposition, return an empty list.
- complexity: An estimated complexity of the main task on a scale of 0.0 (trivial) to 1.0 (very complex).
- priority: An estimated priority of the task on a scale of 0.0 (low) to 1.0 (critical), based on common sense.
- tags: A list of 1-3 relevant keywords or tags for the task (e.g., "work", "learning", "health").
- estimated_duration: The estimated time to complete the entire main task, formatted as a string like "2 days 4:00:00" or "6:00:00". Be realistic.
If the user has explicitly specified any parameter (for example, priority: 0.4), then use it.

USER'S GOAL:
{goal}

{format_instructions}
"""

class TaskProcessor:
    """
    Encapsulates the logic for processing a goal using an LLM chain.
    """
    def __init__(self, model: BaseChatModel):
        # 1. Create a Pydantic parser for our Task model
        self.parser = PydanticOutputParser(pydantic_object=Task)

        # 2. Create a prompt template with format instructions
        self.prompt = ChatPromptTemplate.from_template(
            template=PROMPT_TEMPLATE,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        # 3. Create the processing chain
        self.chain = self.prompt | model | self.parser

    async def process_goal(self, goal: str) -> Task:
        """
        Processes the user's goal and returns a structured Task object.
        """
        # The .ainvoke method runs the chain asynchronously
        return await self.chain.ainvoke({"goal": goal})
