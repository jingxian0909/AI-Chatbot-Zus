import ast
import operator

# Allowed operators mapping
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.Pow: operator.pow
}

class SafeCalculator:

    def eval_expr(self, expression: str):
        try:
            tree = ast.parse(expression, mode='eval')
            return self._eval(tree.body)
        except ZeroDivisionError:
            return {
                "success": False,
                "error": "Division by zero is not allowed."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid expression: {str(e)}"
            }

    def _eval(self, node):
        # Number: 10, 3.5, etc.
        if isinstance(node, ast.Num):
            return node.n

        # Unary operator: -5
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](self._eval(node.operand))

        # Binary operators: + - * / **
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = self._eval(node.left)
            right = self._eval(node.right)
            return OPERATORS[type(node.op)](left, right)

        raise ValueError("Unsupported expression or characters.")
