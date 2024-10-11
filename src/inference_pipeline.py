import os

import yaml
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from openai import OpenAI

# Load project settings
with open("setup.yaml", "r") as file:
    config = yaml.load(file, yaml.Loader)

# Load environment variables
load_dotenv("secret.env")
openai_api_key = os.environ["OPENAI_API_KEY"]


class GPT4Ouro:
    def __init__(self):
        self.inference_prompt = self._create_inference_prompt()

    def _create_inference_prompt(self):
        """
        Create prompt template for inference
        """
        # Integrate memory component
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        return prompt

    def run(
            self, *,
            query: str,
            chat_history: list[tuple[str, str]],
            system_prompt: str,
            llm_base_url: str,
            model_name: str,
            temperature: float = 0.2
    ) -> str:
        # Prepare chat history input
        chat_history_window = ChatMessageHistory()
        if config["CHAT_HISTORY_WINDOW"] > 0:
            for message in chat_history[-config["CHAT_HISTORY_WINDOW"]:]:
                chat_history_window.add_user_message(message[0])
                chat_history_window.add_ai_message(message[1])

        # Define openai client
        client = OpenAI(
            base_url=llm_base_url,
            api_key=os.environ["OPENAI_API_KEY"],
        )

        # Create prompt
        prompt = self.inference_prompt.invoke(
            input={"input": query, "chat_history": chat_history_window.messages, "system_prompt": system_prompt}
        ).to_string()

        # Inference
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

        return completion.choices[0].message.content
