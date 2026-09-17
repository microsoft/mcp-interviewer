"""Todo list tool for agent task tracking."""

from openai.types.responses import FunctionToolParam


class TodoTool:
    """Tool for managing a todo list to track agent tasks."""

    def __init__(self):
        """Initialize the todo tool."""
        self.todos: list[dict[str, str]] = []

    @staticmethod
    def get_add_todo_definition() -> FunctionToolParam:
        """Get the add_todo tool definition for the LLM."""
        return {
            "type": "function",
            "name": "add_todo",
            "description": "Add a task to your todo list. Use this to track what needs to be done.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Description of the task to add",
                    },
                },
                "required": ["task"],
            },
            "strict": None,
        }

    @staticmethod
    def get_complete_todo_definition() -> FunctionToolParam:
        """Get the complete_todo tool definition for the LLM."""
        return {
            "type": "function",
            "name": "complete_todo",
            "description": "Mark a task as completed. Provide the task description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Description of the task to mark as completed",
                    },
                },
                "required": ["task"],
            },
            "strict": None,
        }

    @staticmethod
    def get_remove_todo_definition() -> FunctionToolParam:
        """Get the remove_todo tool definition for the LLM."""
        return {
            "type": "function",
            "name": "remove_todo",
            "description": "Remove a task from the todo list. Use when a task is no longer relevant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Description of the task to remove",
                    },
                },
                "required": ["task"],
            },
            "strict": None,
        }

    @staticmethod
    def get_clear_todos_definition() -> FunctionToolParam:
        """Get the clear_todos tool definition for the LLM."""
        return {
            "type": "function",
            "name": "clear_todos",
            "description": "Clear all tasks from the todo list. Use when starting fresh.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "strict": None,
        }

    @staticmethod
    def get_list_todos_definition() -> FunctionToolParam:
        """Get the list_todos tool definition for the LLM."""
        return {
            "type": "function",
            "name": "list_todos",
            "description": "List all todos with their status (pending or completed).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "strict": None,
        }

    def add_todo(self, task: str) -> str:
        """Add a task to the todo list.

        Args:
            task: Task description

        Returns:
            Confirmation message
        """
        self.todos.append({"task": task, "status": "pending"})
        return f"Added todo: {task}\nTotal todos: {len(self.todos)}"

    def complete_todo(self, task: str) -> str:
        """Mark a task as completed.

        Args:
            task: Task description

        Returns:
            Confirmation message or error if not found
        """
        for todo in self.todos:
            if todo["task"] == task and todo["status"] == "pending":
                todo["status"] = "completed"
                pending_count = sum(1 for t in self.todos if t["status"] == "pending")
                return f"Completed todo: {task}\nRemaining todos: {pending_count}"

        return f"Error: Todo not found or already completed: {task}"

    def remove_todo(self, task: str) -> str:
        """Remove a task from the todo list.

        Args:
            task: Task description

        Returns:
            Confirmation message or error if not found
        """
        for i, todo in enumerate(self.todos):
            if todo["task"] == task:
                self.todos.pop(i)
                return f"Removed todo: {task}\nTotal todos: {len(self.todos)}"

        return f"Error: Todo not found: {task}"

    def clear_todos(self) -> str:
        """Clear all todos.

        Returns:
            Confirmation message
        """
        count = len(self.todos)
        self.todos.clear()
        return f"Cleared {count} todos. List is now empty."

    def list_todos(self) -> str:
        """List all todos with their status.

        Returns:
            Formatted todo list
        """
        return self.get_status()

    def get_status(self) -> str:
        """Get current todo list status.

        Returns:
            Formatted todo list
        """
        if not self.todos:
            return "Todo list is empty."

        pending = [t for t in self.todos if t["status"] == "pending"]
        completed = [t for t in self.todos if t["status"] == "completed"]

        result = f"Total: {len(self.todos)} | Pending: {len(pending)} | Completed: {len(completed)}\n\n"

        if pending:
            result += "Pending:\n"
            for i, todo in enumerate(pending, 1):
                result += f"  {i}. {todo['task']}\n"

        if completed:
            result += "\nCompleted:\n"
            for i, todo in enumerate(completed, 1):
                result += f"  ✓ {todo['task']}\n"

        return result
