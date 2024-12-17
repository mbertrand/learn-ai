"""Test factory classes for ai_agents tests"""

import factory
from factory.fuzzy import FuzzyChoice
from llama_cloud import ChatMessage
from llama_index.core.base.llms.types import MessageRole


class ChatMessageFactory(factory.Factory):
    """Factory for generating llamaindex ChatMessage instances."""

    role = FuzzyChoice(MessageRole.USER, MessageRole.ASSISTANT)
    content = factory.Faker("sentence")
    id = name = factory.Sequence(lambda n: "%d" % n)
    index = factory.Sequence(lambda n: "%d" % n)

    class Meta:
        model = ChatMessage
