from .base import CompositeConstraint
from .openai import OpenAIConstraints


class AllConstraints(CompositeConstraint):
    def __init__(self):
        super().__init__(
            OpenAIConstraints(),
        )
