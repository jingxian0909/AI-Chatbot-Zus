from planner import Planner
from calculator import SafeCalculator
import requests
import json
import os

conv_history = []

class Orchestrator:
    def __init__(self):
        self.planner = Planner()
        self.calculator = SafeCalculator()
        self.api_base = os.getenv("API_BASE_URL")

    @staticmethod
    def formatConvHistory(messages):
        return (
            "\n".join(
                f"Human: {message}" if i%2==0 else f"AI: {message}"
                for i, message in enumerate(messages)
            )
        )

    def handle(self, user_msg: str):
        history = Orchestrator.formatConvHistory(conv_history)
        print(history)
        plan = json.loads(self.planner.plan(user_msg, history))
        print(plan)
        
        action = plan.get("action", {})
        payload = plan.get("payload", {})
        conv_history.append(user_msg)

        # Developer logs for UI
        debug = {
            "planner_action": action,
            "reasoning": plan.get("reasoning", {}),
            "missing_info": plan.get("missing_info", {})
        }

        # ---------------- Routing ----------------
        if action == "call_calculator":
            result  = self.calculator.eval_expr(plan["payload"]["expression"])
            if isinstance(result, dict):
                if result.get("success") == False:
                    conv_history.append(result.get("error"))
                    return {
                        "message": result.get("error"),
                    }
                conv_history.append(result)
                return {"message": result, "debug": debug}

            # Otherwise, result is a normal number
            conv_history.append(result)
            return {
                "message": result,
                "debug": debug
            }
    
        if action == "call_products":
            res = requests.get(
                f"{self.api_base}/products",
                params={"query": payload["query"]}
            )
            conv_history.append(res.json())
            return {"message": res.json(), "debug": debug}

        if action == "call_outlets":
            res = requests.get(
                f"{self.api_base}/outlets",
                params={"query": payload["query"]}
            )
            if res.ok:
                conv_history.append(res.json())
                return {"message": res.json(), "debug": debug}
            else:
                conv_history.append("Failed to get answer.")
                return {"message": "Failed to get answer."}

        if action == "ask_followup":
            conv_history.append(plan["response_text"])
            return {
                "message": plan["response_text"],                
                "debug": debug
            }
        if action == "reset":
            conv_history.clear()
            return

        conv_history.append(plan["response_text"])
        return {
            "message": plan["response_text"],
            "debug": debug
        }             

if __name__ == "__main__":
    user_msg = "Which outlets open in PJ?"
    client = Orchestrator()
    client.handle(user_msg)