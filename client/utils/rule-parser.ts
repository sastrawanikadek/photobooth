const OPERATORS = {
  "=": "equal",
  "==": "equal",
  "!=": "notEqual",
  "<": "lowerThan",
  "<=": "lowerThanEqual",
  ">": "greaterThan",
  ">=": "greaterThanEqual",
  "&&": "logicalAnd",
  "||": "logicalOr",
} as const;

type IdentifierNode = {
  type: "identifier";
  value: string;
};

type RawNode = {
  type: "raw";
  value: string | number | boolean;
};

type ExpressionNode = {
  type: "expression";
  operator: (typeof OPERATORS)[keyof typeof OPERATORS];
  left: ExpressionNode | IdentifierNode | RawNode;
  right: ExpressionNode | IdentifierNode | RawNode;
};

type RuleNodes = IdentifierNode | RawNode | ExpressionNode;
type RuleContext = Record<string, string | number | boolean>;

const parseRule = (rule: string) => {
  const parser = new RuleParser(rule);
  const ast = parser.parse();

  return new Rule(ast);
};

class RuleParser {
  private _rule: string;

  constructor(rule: string) {
    this._rule = rule;
  }

  parse(): ExpressionNode | null {
    const tokens = this._tokenize();

    if (!tokens || tokens.length === 0) {
      return null;
    }

    try {
      return this._parseTokens(tokens);
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  private _tokenize() {
    return this._rule.match(/\w+|(["']).*\1|==|!=|<=|>=|<|>|=|&&|\|\||\(|\)/g);
  }

  private _parseTokens(tokens: string[]): ExpressionNode {
    const result: Partial<ExpressionNode> = {
      type: "expression",
    };

    while (tokens.length > 0) {
      const token = tokens.shift();

      if (token === "(") {
        const groupTokens = tokens.splice(0, this._getGroupLength(tokens));
        const subResult = this._parseTokens(groupTokens);

        if (result.left) {
          result.right = subResult;
        } else {
          result.left = subResult;
        }
      } else if (token === ")") {
        break;
      } else if (token === "&&" || token === "||") {
        result.operator = OPERATORS[token];
      } else {
        const leftOperand = token || "";
        const operator = tokens.shift();
        const rightOperand = tokens.shift() || "";

        if (!operator || !Object.keys(OPERATORS).includes(operator)) {
          throw new Error(`Unknown operator: ${operator}`);
        }

        const node: ExpressionNode = {
          type: "expression",
          left: this._parseOperand(leftOperand),
          operator: OPERATORS[operator as keyof typeof OPERATORS],
          right: this._parseOperand(rightOperand),
        };

        if (result.left) {
          if (tokens.length > 3) {
            tokens.unshift(leftOperand, operator, rightOperand);
            result.right = this._parseTokens(tokens);
          } else {
            result.right = node;
          }
        } else {
          result.left = node;
        }
      }
    }

    return (result.right ? result : result.left) as ExpressionNode;
  }

  private _getGroupLength(tokens: string[]) {
    let innerGroupCount = 0;
    let groupEndIndex = -1;

    for (let i = 0; i < tokens.length; i++) {
      if (tokens[i] === "(") {
        innerGroupCount++;
      } else if (tokens[i] === ")") {
        if (innerGroupCount === 0) {
          groupEndIndex = i;
          break;
        } else {
          innerGroupCount--;
        }
      }
    }

    return groupEndIndex + 1;
  }

  private _isString(value: string) {
    return /^(["']).*\1$/.test(value);
  }

  private _parseOperand(operand: string): IdentifierNode | RawNode {
    if (this._isString(operand)) {
      return {
        type: "raw",
        value: operand.slice(1, -1),
      };
    }

    try {
      return {
        type: "raw",
        value: JSON.parse(operand),
      };
    } catch (e) {
      return {
        type: "identifier",
        value: operand,
      };
    }
  }
}

class Rule {
  private _ast: ExpressionNode | null;

  constructor(ast: ExpressionNode | null = null) {
    this._ast = ast;
  }

  evaluate(context: RuleContext) {
    if (!this._ast) {
      return true;
    }

    return this._evaluateNode(this._ast, context);
  }

  private _evaluateExpression(node: ExpressionNode, context: RuleContext) {
    const left = this._evaluateNode(node.left, context);
    const right = this._evaluateNode(node.right, context);

    switch (node.operator) {
      case "equal":
        return left == right;
      case "notEqual":
        return left != right;
      case "lowerThan":
        return left < right;
      case "lowerThanEqual":
        return left <= right;
      case "greaterThan":
        return left > right;
      case "greaterThanEqual":
        return left >= right;
      case "logicalAnd":
        return Boolean(left && right);
      case "logicalOr":
        return Boolean(left || right);
      default:
        throw new Error(`Unknown operator: ${node.operator}`);
    }
  }

  private _evaluateNode(
    node: RuleNodes,
    context: RuleContext,
  ): string | number | boolean {
    if (node.type === "expression") {
      return this._evaluateExpression(node, context);
    } else if (node.type === "identifier") {
      return context[node.value] ?? node.value;
    } else if (node.type === "raw") {
      return node.value;
    }

    throw new Error("Unknown node type");
  }
}

export default parseRule;
