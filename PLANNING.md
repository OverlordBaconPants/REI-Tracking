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
Keep a concise project summary in your README.md that you can paste at the start of new conversations:

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
- Maintain a consistent project structure. The following is an example that should work as we start developing the project and will likely need to be extended as we implement more requirements per TASKS.md.

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

## 12. 🖥️ MCP Integration & File System Workflow

### File Access Boundaries
To maintain project integrity, MCP filesystem access follows these guidelines:
- **Read access**: All project files under `/home/python/rei-tracking/`
- **Write access**: Limited to:
  - Source code (`/home/python/rei-tracking/src/`)
  - Tests (`/home/python/rei-tracking/tests/`)
  - Documentation files (`/home/python/rei-tracking/*.md`)
- **No access**: 
  - Configuration files with secrets (`.env`)
  - User data files
  - Virtual environment directories

### Version Control Workflow
When working with Git through MCP or directly:

1. **Before committing:**
   - Ensure the newly implemented feature is complete
   - Documentation and unit tests are written
   - Run formatter (black) on modified code
   - Run all unit tests with pytest
   - Verify all tests pass

2. **Commit message format:**
   ```
   [TYPE]: Brief description of what changed

   Task: #task-reference
   ```
   Where TYPE is one of: FEAT (new feature), FIX (bug fix), DOCS (documentation), TEST (test addition), REFACTOR, or CHORE

3. **When to create branches:**
   - For complex changes that might take multiple days to complete
   - For experimental features you're unsure about
   - For major refactoring that could temporarily break functionality

4. **When to commit:**
   - After implementing a complete requirement with tests
   - When taking a break from coding
   - Before making major changes to existing code

## 13. 🗣️ AI-Specific Communication Patterns

### Code Context Handling
- **MCP advantage**: With MCP filesystem access, the AI can find relevant surrounding code to provide proper context for modifications
- **When MCP isn't available**: Include:
  - The full function/method being discussed
  - Any directly related functions it calls or depends on
  - Relevant imports
  - Class definition (if method is part of a class)

### Alternative Approaches
For complex implementations, request multiple options before deciding:
```
Please provide 2-3 alternative approaches for implementing [feature], including:
- Pros and cons of each approach
- Implementation complexity estimate
- Your recommendation with rationale
```

Example response format:
```
# Approach 1: [Brief description]
Pros:
- [List of advantages]
Cons:
- [List of disadvantages]
Implementation complexity: [Low/Medium/High]

# Approach 2: [Brief description]
...

Recommendation: Approach [X] because [rationale]
```

## 14. 🔍 Technical Debt Management

### Technical Debt in TASKS.md
For each task group in TASKS.md, a "Technical Debt" section will be added:
```
### Technical Debt - [Component Name]
- [ ] TD-1: [Description of technical debt item]
  - Impact: [Low/Medium/High]
  - Effort: [Low/Medium/High]
  - Added: [Date]
```

### Refactoring Schedule
Best practices for refactoring as a solo developer:

1. **When to refactor:**
   - After completing each major task group in TASKS.md
   - When technical debt impacts development velocity
   - Before adding new features to an existing component
   - When test coverage drops below 80%

2. **How to refactor:**
   - Write tests before refactoring if coverage is lacking
   - Refactor in small, testable increments
   - Run tests after each increment
   - Document changes in commit messages

### Code Smell Identification
The AI will proactively flag potential code issues using this format:

```
Code Smell Alert: [Type of smell]
File: [File path]
Line(s): [Line numbers]
Description: [Brief description of the issue]
Recommendation: [Suggested fix]
Impact: [Low/Medium/High]
```

Common code smells to watch for:
- Long methods (>50 lines)
- Duplicate code
- Complex conditionals
- Deep nesting
- Large classes with multiple responsibilities
- Excessive comments (might indicate unclear code)
- Poor naming

### Pattern Refinement
When effective coding patterns are identified:
1. Document the pattern in the Decision Log
2. Create Technical Debt items to apply the pattern to existing code
3. Use the pattern consistently in new development
4. Implement changes incrementally rather than making wholesale changes

## 15. 📝 Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-04-24 | Added MCP integration guidelines to PLANNING.md | To establish clear workflow for AI-assisted development with filesystem access and version control integration |

## 16. 📋 Conversation Summaries

At the end of each development session, the conversation will conclude with:

1. **Summary of decisions made**: Key design and implementation choices
2. **Code implemented/modified**: Brief overview of changes
3. **Documentation updated**: Which docs were modified and how
4. **Next steps**: Clear action items for the next session
5. **Open questions**: Any unresolved issues

If approved, this summary will be used to update PLANNING.md, TASKS.md, and other documentation as appropriate.

---

By following these guidelines, our collaboration will be more effective, resulting in higher quality code and a more efficient development process.