# 🧠 Enhanced AI Coding Assistant Workflow

This guide provides a structured process for working with Claude to build production-quality software. The workflow maximizes the effectiveness of our interactions and ensures consistent, high-quality results.

## 📋 Table of Contents

1. [Golden Rules](#1--golden-rules-for-collaboration)
2. [Project Context Management](#2--project-awareness--context)
3. [Communication Patterns](#3--effective-communication-patterns)
4. [Code Structure & Quality](#4--code-structure--quality)
5. [Task Management](#5--planning--task-management)
6. [Testing Strategy](#6--testing--reliability)
7. [Documentation Standards](#7--documentation--explainability)
8. [Working With Claude](#8--working-with-claude-effectively)
9. [File System & Version Control](#9--file-system--version-control-workflow)
10. [Technical Debt Management](#10--technical-debt-management)
11. [Decision Log](#11--decision-log)

## 1. 🔑 Golden Rules for Collaboration

- **Use markdown files** for project management (README.md, PLANNING.md, TASK.md)
- **Keep files under 500 lines** and split into modules when needed
- **Start fresh conversations** with sufficient context
- **One task per message** for clearer responses
- **Test early and often** with unit tests for each new function
- **Be specific and detailed** in your requests
- **Document as you go** with comments and documentation
- **Handle sensitive information yourself** (API keys, credentials)
- **Request clarification when needed** rather than guessing
- **Accept feedback gracefully** on requirements or approaches
- **Provide the "why"** behind requests to get better solutions
- **Acknowledge context limitations** and proactively provide missing information

## 2. 🔄 Project Awareness & Context

### Essential Practices
- **Always read `README.md` and `PLANNING.md`** at the start of new conversations
- **Check `TASK.md`** before starting new tasks
- **Use consistent naming conventions and architecture** as described in this document
- **Upload relevant files** at the beginning of new conversations
- **Summarize previous conclusions** when starting new threads
- **Reference specific file paths** when discussing code

### Project Summary Template
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
```
Context: [Brief project description]
Current task: [What we're working on]
Relevant files: [List key files/modules]
Goals: [What you want to accomplish]
```

### Request Templates

#### Code Implementation
```
Please implement [feature/function] with the following requirements:
- Requirement 1
- Requirement 2

Input: [describe inputs]
Output: [describe expected outputs]
Edge cases: [list edge cases]

Related code: [paste relevant existing code if applicable]
```

#### Code Review/Debugging
```
Please review this code for [specific concerns/bugs]:

```code here```

Issue: [describe problem]
Expected behavior: [what should happen]
Actual behavior: [what's actually happening]
```

#### Architecture/Design Decisions
```
I need guidance on [specific design challenge].

Current approach: [describe current implementation]
Constraints: [list any constraints]
Options:
1. [Option 1]
2. [Option 2]

What would you recommend and why?
```

### Feedback Loop
When responses don't meet expectations:
1. **Be specific** about what's missing
2. **Show examples** of preferred format/style
3. **Request incremental improvements**

## 4. 🧱 Code Structure & Quality

### Structure Guidelines
- **Maximum file length: 500 lines** - Split larger files into modules
- **Organize by feature or responsibility** with clear module separation
- **Use consistent imports** (prefer relative imports within packages)

### Style Conventions
- **Language**: Python
- **Style**: PEP8, formatted with `black`
- **Validation**: Use `pydantic` for data validation
- **Naming**:
  - `snake_case` for variables and functions
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- **Type hints**: Required for all function parameters and return values

### Project Structure
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

### Task Completion Criteria
- Core functionality implemented and working
- Documentation complete:
  - Code-level documentation (docstrings, comments)
  - User documentation (if applicable)
  - `README.md` updates (if applicable)
  - `PLANNING.md` updates to Decision Log (if applicable)
  - `TASKS.md` updates for Technical Debt (if applicable)
- Unit tests written and passing:
  - Happy path tests
  - Edge case tests
  - Error handling tests
- Code reviewed against quality guidelines

### Task Tracking
- **Mark completed tasks** in `TASK.md` immediately
- **Add new tasks** discovered during development to `TASK.md` as Technical Debt

## 6. 🧪 Testing & Reliability

- **Create Pytest unit tests** for all new features
- **Update existing tests** when logic changes
- **Mirror app structure** in `/tests` folder
- **Test coverage** for each feature:
  - Happy path (expected use case)
  - Edge cases (boundary conditions)
  - Failure cases (error handling)

## 7. 📚 Documentation & Explainability

### Documentation Requirements
- **Update `README.md`** for new features, dependencies, or setup changes
- **Comment non-obvious code** for mid-level developer understanding
- **Add `# Reason:` comments** for complex logic
- **Document as you go**, not after the fact

### Docstring Format (Google-style)
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

## 8. 🔄 Working With Claude Effectively

### Best Practices
- **Upload code files** directly rather than pasting large blocks
- **Break complex features** into smaller tasks
- **Provide clear requirements** with examples
- **Ask for explanations** when needed
- **Be explicit about priorities** (readability, performance, etc.)

### Avoid These Pitfalls
- **Multiple questions** in a single message
- **Assuming memory** of details from earlier in conversation
- **Requesting complete applications** in one go
- **Switching topics** without context

### AI Behavior Rules
- **Never assume missing context** - Ask questions if uncertain
- **Never hallucinate libraries/functions** - Use only verified packages
- **Always confirm file paths/module names** before referencing
- **Never delete/overwrite existing code** without explicit instruction

### Code Review Checklist
When requesting review, specify focus areas:
- [ ] Overall architecture and design patterns
- [ ] Function and variable naming
- [ ] Error handling approach
- [ ] Performance considerations
- [ ] Security considerations
- [ ] Test coverage
- [ ] Documentation completeness

### Alternative Approaches
For complex implementations, request multiple options:
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

## 9. 🖥️ File System & Version Control Workflow

### File Access Boundaries
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

#### Before Committing
1. Ensure feature is complete
2. Documentation and unit tests are written
3. Run formatter (black) on modified code
4. Run all unit tests with pytest
5. Verify all tests pass

#### Commit Message Format
```
[TYPE]: Brief description of what changed

Task: #task-reference
```
Where TYPE is: FEAT, FIX, DOCS, TEST, REFACTOR, or CHORE

#### When to Create Branches
- For complex multi-day changes
- For experimental features
- For major refactoring

#### When to Commit
- After implementing a complete requirement with tests
- Before taking breaks
- Before making major changes to existing code

## 10. 🔍 Technical Debt Management

### Technical Debt in TASKS.md
```
### Technical Debt - [Component Name]
- [ ] TD-1: [Description of technical debt item]
  - Impact: [Low/Medium/High]
  - Effort: [Low/Medium/High]
  - Added: [Date]
```

### Refactoring Schedule
1. **When to refactor:**
   - After completing major task groups
   - When debt impacts development velocity
   - Before adding features to existing components
   - When test coverage drops below 80%

2. **How to refactor:**
   - Write tests first if coverage is lacking
   - Refactor in small, testable increments
   - Run tests after each increment
   - Document changes in commit messages

### Code Smell Identification
```
Code Smell Alert: [Type of smell]
File: [File path]
Line(s): [Line numbers]
Description: [Brief description of the issue]
Recommendation: [Suggested fix]
Impact: [Low/Medium/High]
```

Common code smells:
- Long methods (>50 lines)
- Duplicate code
- Complex conditionals
- Deep nesting
- Large classes with multiple responsibilities
- Excessive comments (might indicate unclear code)
- Poor naming

### Pattern Refinement
1. Document effective patterns in Decision Log
2. Create Technical Debt items to apply patterns to existing code
3. Use patterns consistently in new development
4. Implement changes incrementally

## 11. 📝 Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-04-24 | Added MCP integration guidelines | To establish clear workflow for AI-assisted development with filesystem access and version control integration |
| 2025-04-26 | Reorganized PLANNING.md | To improve clarity, conciseness, and organization of the development workflow documentation |
| 2025-04-26 | Implemented user authentication system | To provide secure user management with login/registration, session handling, and role-based access control |
| 2025-04-26 | Implemented property access controls | To enable fine-grained property access management with owner, manager, and viewer roles, supporting partner equity-based permissions |
| 2025-04-26 | Implemented core calculation components | To provide a robust foundation for financial calculations with proper decimal handling, validation, and support for various loan types |

---

By following these guidelines, our collaboration will be more effective, resulting in higher quality code and a more efficient development process.
