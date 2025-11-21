import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  
class Planner:
    def __init__(self):
        self.openai = OpenAI()

    def detect_math(self, msg):
        return any(op in msg for op in ["+", "-", "*", "/", "calc", "calculate"])

    def plan(self, user_msg: str,  conv_history):
        """
        if self.detect_math(user_msg):
            return {
                "action": "call_calculator",
                "reasoning": "Arithmetic detected",
                "missing_info": None,
                "payload": {"expression": user_msg}
            }
        else:
        """
        prompt = f"""
            You are an AI Planner that decides what the chatbot should do next. 

            You have access to:
            - conv_history: previous conversation as context
            - user_msg: the latest message from the user

            Your goal is to analyze the user's message and choose ONE action. The bot should clarify ambiguous requests before calling endpoints. For example, if the user asks about an outlet in a city but doesn't specify which outlet, ask for clarification first instead of querying all outlets.

            Available actions:
            1. call_products        → For product-related questions (tumbler, drinkware, merch)
            2. call_outlets         → For outlet-related questions (only if a specific outlet is identified)
            3. call_calculator      → If the message contains arithmetic or math expression
            4. ask_followup         → If intent is unclear or key information is missing (e.g., which outlet, product)
            5. chitchat             → For greetings or unrelated messages
            6. reset                → For deleting the conv history

            Constraints:
            - Use conv_history to determine if user has already provided missing info.
            - If user asks for information not available in the data (e.g., opening/closing time), include a note in reasoning.
            - Always ask follow-up questions if essential info is missing.
            - If action = ask_followup or chitchat, generate a friendly, concise sentence in natural language that the bot can say to the user. This should be in `response_text`.

            Return a JSON object with:
            - action: the selected action
            - reasoning: explanation of why you selected this action
            - missing_info: if action = ask_followup, specify what info is missing (e.g., "specific_outlet" or "product")
            - payload: "query": user_msg, unless action = call_calculator, then use "expression": math expression
            - response_text: a friendly, human-readable sentence for follow-up or chitchat; if action is call_products, call_outlets, or call_calculator, this can be null

            User message: "{user_msg}"
            conv_history: {conv_history}

            Think step by step and return JSON ONLY.
            """
        
        res = self.openai.chat.completions.create(
            model="gpt-5-mini-2025-08-07",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return res.choices[0].message.content
        