import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from llama_index.core.base.llms.types import ChatMessage

from ai_agents.agents import RecommendationAgent
from ai_agents.serializers import ChatRequestSerializer

log = logging.getLogger(__name__)


class RecommendationAgentConsumer(AsyncWebsocketConsumer):
    """
    Async websocket consumer for the recommendation agent.
    """

    async def connect(self):
        """Connect to the websocket and initialize the AI agent."""
        user = self.scope.get("user", None)
        session = self.scope.get("session", None)

        if user and user.username:
            self.user_id = user.username
        elif session:
            if not session.session_key:
                session.save()
            self.user_id = session.session_key
        else:
            self.user_id = None

        self.agent = RecommendationAgent(self.user_id)
        await super().connect()

    async def receive(self, text_data: str) -> str:
        """Send the message to the AI agent and return its response."""

        try:
            text_data_json = json.loads(text_data)
            serializer = ChatRequestSerializer(data=text_data_json)
            serializer.is_valid(raise_exception=True)
            message_text = serializer.validated_data.pop("message", "")
            clear_history = serializer.validated_data.pop("clear_history", False)
            temperature = serializer.validated_data.pop("temperature", None)
            instructions = serializer.validated_data.pop("instructions", None)
            model = serializer.validated_data.pop("model", None)

            if clear_history:
                self.agent.clear_chat_history()
            if model:
                self.agent.agent.agent_worker._llm.model = model  # noqa: SLF001
            if temperature:
                self.agent.agent.agent_worker._llm.temperature = temperature  # noqa: SLF001
            if instructions:
                self.agent.agent.agent_worker.prefix_messages = [
                    ChatMessage(content=instructions, role="system")
                ]

            for chunk in self.agent.get_completion(message_text):
                await self.send(text_data=chunk)
        except:  # noqa: E722
            log.exception("Error in RecommendationAgentConsumer")
        finally:
            # This is a bit hacky, but it works for now
            await self.send(text_data="!endResponse")
