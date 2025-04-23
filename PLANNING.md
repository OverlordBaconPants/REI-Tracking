# 🧠 Enhanced AI Coding Assistant Workflow for Claude

This guide provides a structured process for working with Claude to build production-quality software. The workflow is designed to maximize the effectiveness of our interactions and ensure consistent, high-quality results.

## 1. 🔑 Golden Rules for Claude Collaboration

These high-level principles will guide our interactions:

- **Use markdown files to manage the project** (README.md, PLANNING.md, TASK.md)
- **Keep files under 500 lines** and split into modules when needed
- **Start fresh conversations often** with sufficient context
- **One task per message** for clearer responses
- **Test early, test often** with unit tests for each new function
- **Be specific and detailed** in your requests
- **Write docs and comments as you go**
- **Handle sensitive information yourself** (API keys, credentials)
- **Request clarification when needed** - If my requests are unclear, vague, or making too many assumptions, Claude will ask for clarification rather than guessing
- **Accept feedback gracefully** - Be open to Claude pointing out when requirements are inconsistent or approaches might be problematic
- **Provide the "why" behind requests** - Explain reasoning behind requirements to help Claude provide better solutions
- **Acknowledge context limitations** - Recognize when Claude might be missing important context and proactively provide it

## 2. 🔄 Project Awareness & Context

- **Always read `README.md` and `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints
- **Check `TASK.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`
- **Upload relevant files** at the beginning of new conversations
- **Summarize previous conclusions** when starting a new thread
- **Reference specific file paths** when discussing code

### Project Summaries
Keep a concise project summary in your PLANNING.md that you can paste at the start of new conversations:

```
Project: [Name]
Tech Stack: [Languages, frameworks, libraries]
Current Status: [Brief status update]
Key Components:
- [Component 1]: [Brief description]
- [Component 2]: [Brief description]
```

## 3. 🗣️ Effective Communication Patterns

### Starting New Conversations
When starting a new conversation, include:

```
Context: [Brief project description]
Current task: [What we're working on]
Relevant files: [List key files/modules]
Goals for this conversation: [What you want to accomplish]
```

Example:
```
Context: Building a FastAPI backend for a task management app
Current task: Implementing user authentication
Relevant files: auth.py, models/user.py, routes/auth_routes.py
Goals: Complete JWT token validation function and test cases
```

### Request Templates

#### For Code Implementation:
```
Please implement [feature/function] with the following requirements:
- Requirement 1
- Requirement 2

Input: [describe inputs]
Output: [describe expected outputs]
Edge cases to handle: [list edge cases]

Related code: [paste relevant existing code if applicable]
```

#### For Code Review/Debugging:

Please review this code for [specific concerns/bugs]:

```
 Code here
```

The issue I'm seeing is: [describe problem]
Expected behavior: [what should happen]
Actual behavior: [what's actually happening]


#### For Architecture/Design Decisions:

I need guidance on [specific design challenge].

```
Current approach: [describe current implementation]
Constraints: [list any constraints]
Options I'm considering:
1. [Option 1]
2. [Option 2]

What would you recommend and why?
```

## 4. 🧱 Code Structure & Modularity

- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files
- **Organize code into clearly separated modules**, grouped by feature or responsibility
- **Use clear, consistent imports** (prefer relative imports within packages)
- Maintain a consistent project structure:

```
project_name/
├── README.md
├── PLANNING.md
├── TASK.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── tests/
│   ├── __init__.py
│   ├── test_models/
│   ├── test_routes/
│   ├── test_services/
│   └── test_utils/
└── docs/
```

## 5. 📋 Planning & Task Management

### ✅ Task Completion Requirements

For any task to be considered complete, it must meet these criteria:
- Core functionality is implemented and working
- Documentation is complete:
  - Code-level documentation (docstrings, comments)
  - User documentation (if applicable)
  - README updates (if applicable)
- Unit tests are written and passing:
  - Happy path tests
  - Edge case tests
  - Error handling tests
- Code has been reviewed against our quality guidelines

### Task Management

- **Mark completed tasks in `TASK.md`** immediately after finishing them
- Add new tasks or sub-tasks discovered during development to `TASK.md` in the appropriate sections, noting the items as "Discovered During Work" section along with the date of discovery

### Project Overview
[Project description and goals]

### Architecture
[High-level architecture description]

### Tech Stack
- [Language]
- [Framework]
- [Database]
- [Other tools]

### Data Models
[Describe key data models]

### API Endpoints
[List planned endpoints]

### Components
[Describe main components/modules]

## 6. 🧪 Testing & Reliability

- **Always create Pytest unit tests for new features** (functions, classes, routes, etc)
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it
- **Tests should live in a `/tests` folder** mirroring the main app structure
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case
- For each new feature, include tests for:
  - Happy path (expected use case)
  - Edge cases (boundary conditions)
  - Failure cases (error handling)

## 7. 📚 Documentation & Explainability

- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what
- **Write docs and comments as you go**, not after the fact

### Documentation Requirements
- Google-style docstrings for all functions:
  ```python
  def function(param1: type, param2: type) -> return_type:
      """Brief description of function.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
          
      Raises:
          ExceptionType: When and why exception is raised
      """
  ```
- Inline comments for complex logic with `# Reason:` prefix
- README.md updates for all new features

## 8. 📎 Style & Conventions

- **Use Python** as the primary language
- **Follow PEP8**, use type hints, and format with `black`
- **Use `pydantic` for data validation**
- Use consistent naming conventions:
  - `snake_case` for variables and functions
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- Include type hints for all function parameters and return values

## 9. 📊 Feedback Loop

### Getting Better Results
When my responses don't meet your expectations:

1. **Be specific about what's missing**: "This is good, but I also need X included"
2. **Show examples** of the format or style you prefer
3. **Request incremental improvements**: "Let's improve the error handling by..."

### Iteration Prompts
```
This looks good, but let's refine:
- Change A to improve B
- Add more detail to section C
- Simplify the approach to D
```

## 10. 🔄 Working With Claude Effectively

### DO:
- **Upload code files** directly rather than pasting large blocks
- **Break complex features** into smaller, manageable tasks
- **Provide clear requirements** with examples when possible
- **Ask for explanations** when you don't understand something
- **Be explicit about priorities** (readability, performance, etc.)

### DON'T:
- **Overload with multiple questions** in a single message
- **Assume I remember details** from far back in conversation
- **Ask for complete applications** in one go
- **Skip providing context** when switching topics

### 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain**
- **Never hallucinate libraries or functions** – only use known, verified Python packages
- **Always confirm file paths and module names** exist before referencing them in code or tests
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`

### When Things Go Wrong
If I misunderstand or produce incorrect code:
1. **Identify the specific issue**: "The database connection isn't being closed properly"
2. **Provide error messages** if available
3. **Ask for focused correction**: "Please fix the connection handling in this function"

## 11. 🔍 Code Review Checklist

When requesting code review, specify what to focus on:

- [ ] Overall architecture and design patterns
- [ ] Function and variable naming
- [ ] Error handling approach
- [ ] Performance considerations
- [ ] Security considerations
- [ ] Test coverage
- [ ] Documentation completeness

---

By following these guidelines, our collaboration will be more effective, resulting in higher quality code and a more efficient development process.