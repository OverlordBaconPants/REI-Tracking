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
11. [Development Practices](#11--development-practices)
12. [UI/UX Guidelines](#12--uiux-guidelines)
13. [API Contract Standards](#13--api-contract-standards)
14. [Project Constraints](#14--project-constraints)
15. [Decision Log](#15--decision-log)

## 1. 🔑 Golden Rules for Collaboration

- **Use markdown files** for project management (README.md, PLANNING.md, TASK.md)
- **Keep development and test files under 500 lines** and split into modules when needed
- **Markdown files can be more than 500 lines** since this is just documentation
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

### User Story Format for Task Requests
When providing tasks, use this format for clarity:

```
As a [property owner/investor/user],
I want to [specific capability],
So that [tangible benefit].

Technical Details:
- [Implementation specifics]
- [API endpoints affected]
- [Data models involved]

Any relevant constraints or considerations?
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

### Standard Acceptance Criteria
All development tasks must meet the following criteria:

- Functionality implements all specified requirements
- Code coverage meets minimum 80% threshold
- All unit tests pass (new and existing)
- UI testing passes with testing persona
- Documentation updated (README.md, PLANNING.md, TASKS.md)
- Mobile-first implementation verified
- Cross-browser compatibility (Chrome, Safari, Edge)

### Task Tracking
- **Mark completed tasks** in `TASK.md` immediately
- **Add new tasks** discovered during development to `TASK.md` as Technical Debt

### Task Prioritization Framework
All tasks should be prioritized using the following framework:

- **Priority Levels**:
  - **P0**: Critical - Blocking or major functionality issue
  - **P1**: High - Important feature or improvement
  - **P2**: Medium - Desired enhancement
  - **P3**: Low - Nice to have

- **Effort Estimation**:
  - **Small**: 1-4 hours
  - **Medium**: 4-8 hours
  - **Large**: 8+ hours

- **Format in TASKS.md**:
  ```
  - [P1][Medium] Implement transaction filtering system
  ```

## 6. 🧪 Testing & Reliability

### Test Implementation Strategy

1. **Write Tests First**: Following Test-Driven Development (TDD) principles, write tests before implementing features to ensure requirements are met and code is testable.
   - Define expected behavior before writing implementation
   - Use tests to guide the design of interfaces and APIs
   - Ensure all requirements are covered by test cases

2. **Automate Testing**: All tests should be automated and integrated into the development workflow.
   - Use pytest for backend testing
   - Use Selenium WebDriver for UI testing
   - Run tests automatically before commits
   - Maintain a CI/CD pipeline for continuous testing

3. **Test in Isolation**: Unit tests should test components in isolation with mocked dependencies.
   - Mock external services and APIs
   - Test individual functions and methods independently
   - Use dependency injection to facilitate testing
   - Avoid testing implementation details

4. **Integration Testing**: Verify that components work together correctly.
   - Test API endpoints with real database connections
   - Test interactions between modules
   - Verify correct data flow between components
   - Test error handling across component boundaries

5. **UI Testing**: Verify the end-to-end functionality from the user's perspective.
   - Test critical user flows
   - Verify UI elements and interactions
   - Test responsive design and mobile compatibility
   - Test accessibility features

### Testing Guidelines

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

## 11. 🛠️ Development Practices

### Code Reuse & Simplicity
- **Always look for existing code to iterate on** instead of creating new code
- **Adhere to variable names as set forth in DATA_STRUCTURES.md**
  - Consult before extending DATA_STRUCTURES.md with clear justification
- **Prefer simple solutions** over complex ones
- **Avoid duplication of code** by checking for similar functionality elsewhere in the codebase
- **Do not store calculated or derived values in JSON objects** if such values can be calculated at run-time
  - This maintains a single source of truth for calculations
  - Prevents data inconsistency issues
  - All calculations performed at run-time should be consistent with calculations performed elsewhere. For example, all calculations to determine cash-on-cash return should follow the same logic and yield the same results.
  - Reduces storage requirements
  - Improves maintainability by centralizing calculation logic
  - **Implement calculation functions in a centralized utility library**
    - Create named, testable functions (e.g., `calculateCashOnCashReturn`) in dedicated modules
    - Reference these functions whenever the calculation is needed in the UI
    - This ensures consistency and makes future formula changes easier to implement
  - **Use computed properties in view models/components**
    - Create getter methods that derive values from base properties dynamically
    - This maintains reactivity while preventing stale calculated data
  - **Document calculation formulas in comments and documentation**
    - Each formula should include a clear explanation of its purpose and methodology
    - Include business context when applicable (e.g., "Industry standard formula for property ROI")
  - **For API responses, transform server data at the boundary**
    - Strip any derived values received from APIs before storing
    - Recalculate these values using client-side logic when needed

### Debugging Methodology
When debugging an issue:
1. **Identify and rank potential root causes** by likelihood
2. **Create a clear action plan** for each cause, listing specific changes to make
3. **Try solutions in order** of highest likelihood
4. **If a solution doesn't work**, clearly state why and revert all changes before trying the next approach
5. **Document the successful solution** and explain why it worked

### Code Organization
- **Keep the codebase very clean and organized**
- When encountering a non-Markdown file exceeding 600 lines of code:
  1. Analyze the file structure and identify logical separation points
  2. Present a refactoring plan that includes:
     - Proposed file names and their responsibilities
     - Which functions/classes belong in each new file
     - Any shared interfaces or dependencies between files
     - Estimated complexity of the refactoring (low/medium/high)
  3. Wait for approval before proceeding with the refactoring

### Strategic Logging
Add strategic logging statements throughout the codebase:
1. **Log function entry points** with parameters for key functions
2. **Use different console methods appropriately**:
   - `console.log()` for general flow information
   - `console.warn()` for potential issues
   - `console.error()` for caught exceptions
3. **Format logs with clear prefixes** (e.g., "[ComponentName]") to make them easily identifiable
4. **Include relevant state values** in logs to provide context
5. **For async operations**, log both the start and completion/failure

### Additional Guidelines
- **Mocking data is only needed for tests**; never mock data for code intended for production
- **Focus on the areas of code relevant to the task**
- **Do not touch code that is unrelated to the task**
- **Always think about what other methods and areas of code** might be affected by code changes

## 12. 🎨 UI/UX Guidelines

### Visual Elements

#### Color Palette
- **Primary**: #3498db (Blue)
- **Secondary**: #2ecc71 (Green)
- **Accent**: #f39c12 (Orange)
- **Warning**: #f1c40f (Yellow)
- **Error**: #e74c3c (Red)
- **Text**: #2c3e50 (Dark Blue/Gray)
- **Background**: #ecf0f1 (Light Gray)
- **Card Background**: #ffffff (White)

#### Typography
- **Font Family**: 
  - Primary: "Roboto", sans-serif
  - Secondary: "Open Sans", sans-serif
  - Monospace: "Roboto Mono", monospace
- **Font Sizes**:
  - Heading 1: 2.5rem
  - Heading 2: 2rem
  - Heading 3: 1.75rem
  - Heading 4: 1.5rem
  - Body: 1rem
  - Small: 0.875rem
- **Font Weights**:
  - Light: 300
  - Regular: 400
  - Medium: 500
  - Bold: 700

#### Spacing System
- **Base Unit**: 4px
- **Spacing Scale**: 
  - xs: 4px
  - sm: 8px
  - md: 16px
  - lg: 24px
  - xl: 32px
  - xxl: 48px
- **Grid**: 12-column system with 24px gutters

#### Shadows & Elevation
- **Level 1**: 0 2px 5px rgba(0,0,0,0.1)
- **Level 2**: 0 4px 10px rgba(0,0,0,0.15)
- **Level 3**: 0 8px 20px rgba(0,0,0,0.2)

### Components Library

#### Buttons
- **Primary**: Filled blue button with white text
- **Secondary**: Outlined button with colored text
- **Destructive**: Red button for delete/remove actions
- **Text**: No background, just colored text
- **Button Sizes**: Small, Medium (default), Large
- **States**: Normal, Hover, Active, Disabled

#### Form Elements
- **Text Inputs**: Floating label design with validation feedback
- **Dropdowns**: Custom styled with search functionality for long lists
- **Checkboxes**: Custom styled with animation
- **Radio Buttons**: Custom styled with animation
- **Toggle Switches**: For boolean settings
- **Date Pickers**: Calendar popup with range selection
- **Form Layout**: Consistent spacing and alignment

#### Cards & Containers
- **Standard Card**: White background with shadow
- **Feature Card**: With header, icon, and call-to-action
- **Data Card**: For displaying metrics and statistics
- **Container Types**: Fixed-width, fluid, and sectioned

#### Tables & Data Displays
- **Data Tables**: Responsive with sortable columns
- **Pagination**: With customizable items per page
- **Filters**: Inline and expandable filter panels
- **Empty States**: With helpful messages and actions
- **Mobile Adaptation**: Card view for narrow screens

#### Navigation Elements
- **Navbar**: Fixed top with dropdown menus
- **Sidebar**: Collapsible with icons and labels
- **Tabs**: Underlined style with sliding indicator
- **Breadcrumbs**: For hierarchy navigation
- **Pagination**: For multi-page content

#### Modals & Dialogs
- **Standard Modal**: For forms and confirmation
- **Alert Dialog**: For important notifications
- **Drawer**: Side panel for additional content
- **Toast Notifications**: For transient messages

#### Notifications & Alerts
- **Success**: Green with check icon
- **Info**: Blue with info icon
- **Warning**: Yellow with exclamation icon
- **Error**: Red with error icon
- **Toast Duration**: 4 seconds by default

### Interaction Patterns

#### Form Validation Feedback
- **Real-time Validation**: Validate as user types
- **Error Messages**: Display below the field
- **Success Indicators**: Green check for valid fields
- **Form Submit**: Disable until valid, show loading state

#### Loading States
- **Button Loading**: Replace text with spinner
- **Page Loading**: Full-page loading overlay
- **Content Loading**: Skeleton screens for progressive loading
- **Infinite Scroll**: Load more content as user scrolls

#### Empty States
- **Friendly Message**: Explain why content is empty
- **Helpful Action**: Suggest next steps
- **Illustrations**: Use consistent visual style

#### Error States
- **User Errors**: Clear guidance on how to fix
- **System Errors**: Apologize and offer solutions
- **Offline State**: Handle gracefully with recovery

#### Mobile-specific Interactions
- **Touch Targets**: Minimum 44x44px
- **Swipe Actions**: For common actions like delete
- **Bottom Navigation**: For primary actions on mobile
- **Pull to Refresh**: For content updates

### Responsive Breakpoints
- **Mobile**: < 576px
- **Tablet**: 576px - 992px
- **Desktop**: > 992px
- **Large Desktop**: > 1200px

### Accessibility Guidelines
- **Color Contrast**: Minimum ratio of 4.5:1 for normal text
- **Focus States**: Visible focus indicator for keyboard navigation
- **ARIA Attributes**: For complex interactive components
- **Keyboard Navigation**: All interactive elements must be accessible
- **Screen Reader Support**: Meaningful alt text and ARIA labels
- **Reduced Motion**: Support prefers-reduced-motion media query

## 13. 📋 API Contract Standards

Each API endpoint should be documented using the following template:

```markdown
# API Contract: [Endpoint Group]

## Endpoint: [HTTP Method] [Path]

**Purpose**: [Brief description of what this endpoint does]

**Authentication**: [Required/Optional/None]

**Request Parameters**:
- `parameter1` (type): Description [Required/Optional]
- `parameter2` (type): Description [Required/Optional]

**Request Body**:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Response**:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Status Codes**:
- 200: Success
- 400: Bad Request [Error details]
- 401: Unauthorized [Error details]
- 404: Not Found [Error details]
- 500: Server Error [Error details]

**Example**:
```curl
curl -X POST https://api.example.com/endpoint \
  -H "Content-Type: application/json" \
  -d '{"field1": "value1"}'
```
```

### API Documentation Guidelines

1. **Consistency**: Use consistent naming, parameter styles, and response formats across endpoints

2. **Completeness**: Document all possible parameters, responses, and error states

3. **Examples**: Provide working examples of requests and responses

4. **Versioning**: Include API version information in documentation

5. **Status Codes**: Use standard HTTP status codes consistently

6. **Error Handling**: Document error response format and possible error codes

7. **Authentication**: Clearly document authentication requirements

## 14. 🚧 Project Constraints

### Technical Constraints
- **Browser Compatibility**: Chrome, Safari, and Microsoft Edge
- **Mobile-First Implementation**: All features must work well on mobile devices
- **Test Coverage**: Minimum 80% code coverage required
- **Accessibility**: WCAG 2.1 AA compliance

### Performance Constraints
- **Page Load Time**: < 3 seconds on desktop, < 5 seconds on mobile
- **API Response Time**: < 500ms for non-complex operations
- **Bundle Size**: < 500KB initial load (compressed)
- **Time-to-Interactive**: < 4 seconds

### Maintenance Constraints
- **Solo Developer Workflow**: Documentation must be sufficient for future reference
- **Code Organization**: Follow established patterns in PLANNING.md
- **Technical Debt**: Address high-impact debt items promptly
- **Dependency Management**: Keep dependencies updated and minimal

## 15. 📝 Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-05-02 | Added UI/UX Guidelines section | To establish consistent visual design principles, component standards, and interaction patterns across the application |
| 2025-05-02 | Added API Contract Standards section | To ensure consistent API documentation and interface patterns |
| 2025-05-02 | Added Project Constraints section | To clearly define technical, performance, and maintenance boundaries |
| 2025-05-02 | Enhanced Task Management section | To add prioritization framework with P0-P3 levels and effort estimation |
| 2025-04-30 | Added Test Implementation Strategy | To establish clear guidelines for comprehensive testing including writing tests first, automating testing, testing in isolation, integration testing, and UI testing |
| 2025-04-24 | Added MCP integration guidelines | To establish clear workflow for AI-assisted development with filesystem access and version control integration |
| 2025-04-26 | Reorganized PLANNING.md | To improve clarity, conciseness, and organization of the development workflow documentation |
| 2025-04-26 | Implemented user authentication system | To provide secure user management with login/registration, session handling, and role-based access control |
| 2025-04-26 | Implemented property access controls | To enable fine-grained property access management with owner, manager, and viewer roles, supporting partner equity-based permissions |
| 2025-04-26 | Implemented core calculation components | To provide a robust foundation for financial calculations with proper decimal handling, validation, and support for various loan types |
| 2025-04-26 | Implemented analysis system | To enable comprehensive property investment analysis with specialized support for different investment strategies (LTR, BRRRR, Lease Option, Multi-Family, PadSplit) |
| 2025-04-26 | Implemented investment metrics calculator | To provide specialized calculators for ROI, equity tracking with appreciation projections, and other investment-specific metrics |
| 2025-04-26 | Implemented analysis CRUD operations | To provide complete API for creating, reading, updating, and deleting analyses with specialized validation and normalization for different analysis types |
| 2025-04-26 | Refactored Loan model to use Pydantic V2 | To improve validation robustness, separate data models from validation models, and implement custom validators for Money and Percentage types |
| 2025-04-26 | Implemented property comps functionality | To provide accurate property valuation with correlation scoring, range indicators, and market statistics integration |
| 2025-04-26 | Implemented financial calculations | To provide comprehensive financial analysis capabilities including detailed cash flow breakdowns, balloon payment analysis, lease option calculations, and refinance impact analysis |
| 2025-04-26 | Implemented transaction operations | To enable comprehensive transaction management with property association, categorization, reimbursement tracking, and property-specific permissions |
| 2025-04-26 | Implemented transaction filtering system | To provide robust filtering capabilities including property, date range, category, type, and description search, with multi-property views and user-specific visibility |
| 2025-04-26 | Implemented reimbursement system | To provide equity-based reimbursement tracking with automatic handling for single-owner properties, status tracking, and documentation support |
| 2025-04-27 | Implemented transaction reporting | To enable comprehensive transaction reporting with PDF generation, financial summaries with visualizations, and documentation bundling in ZIP archives |
| 2025-04-27 | Implemented bulk transaction import | To provide a robust system for importing transactions from CSV and Excel files with flexible column mapping, data validation, duplicate detection, and detailed import reporting |
| 2025-04-27 | Implemented property management operations | To enable comprehensive property management with add/edit/remove functionality, property listing with filtering and sorting, address standardization, and permission-based access |
| 2025-04-27 | Implemented partner equity management | To provide comprehensive partner management with equity share assignment, property manager designation, visibility settings, and contribution/distribution tracking |
| 2025-04-27 | Implemented equity tracking and cash flow calculations | To provide property owners with detailed equity tracking based on loan paydown and appreciation, comprehensive cash flow metrics based on actual transaction data, and comparison of actual performance to analysis projections |
| 2025-04-27 | Implemented KPI comparison reports | To enable property owners to generate detailed PDF reports comparing planned vs. actual metrics, with property details, performance summaries, and visualizations |
| 2025-04-27 | Implemented portfolio dashboard | To provide property owners with a comprehensive view of their portfolio, including equity distribution, cash flow by property, income and expense breakdowns, and key metrics in a mobile-responsive design with time period filtering |
| 2025-04-27 | Implemented loan tracking and management | To provide comprehensive loan management with support for primary and secondary financing, loan details tracking, remaining balance and equity calculations, and monthly equity gain tracking |
| 2025-04-27 | Implemented dashboard routing system with authentication | To create a secure dashboard system with login requirements, property-based access control, and mobile-responsive layouts |
| 2025-04-27 | Built portfolio dashboard | To provide users with comprehensive portfolio overview including equity distribution, cash flow visualizations, and property metrics in a mobile-responsive design |
| 2025-04-27 | Implemented amortization dashboard | To provide property owners with detailed loan amortization tracking including property selector, loan overview with equity gained calculation, interactive amortization visualization with current position indicator, and responsive amortization schedule table with principal/interest breakdown |
| 2025-04-27 | Implemented transactions dashboard | To provide users with a comprehensive interface for viewing, filtering, and reporting on property transactions, with mobile-responsive design, advanced filtering capabilities, PDF report generation, document bundling, and visual indicators for transaction types and status |
| 2025-04-27 | Implemented User Interface & Frontend Architecture | To create a responsive, accessible, and modular frontend architecture with Bootstrap Spacelab theme, enhanced UI components including form validation, notification system, data visualization, and mobile optimizations |
| 2025-04-27 | Implemented Frontend Testing Framework | To establish a comprehensive testing framework for JavaScript components using pytest, Selenium WebDriver, and Chrome headless browser, with minimal tests for core modules (base.js, notifications.js, form_validator.js, data_formatter.js, main.js) |
| 2025-04-27 | Implemented KPI dashboard | To provide property owners with a comprehensive view of their property KPIs including NOI, cap rate, cash-on-cash return, and DSCR, with data quality assessment, analysis comparison functionality, and mobile-responsive design |
| 2025-04-27 | Implemented KPI comparison tool | To enable property owners to compare planned vs. actual metrics with side-by-side comparison tables, variance calculation, performance status indicators, and PDF report generation |
| 2025-04-27 | Created MAO calculator | To provide a comprehensive tool for calculating maximum allowable offers based on different investment strategies, with support for BRRRR-specific calculations and integration with property comps data |
| 2025-04-27 | Implemented welcome and landing page modules | To create an intuitive onboarding experience for new users with clear navigation to key features and getting started guidance |
| 2025-04-27 | Built loan term toggle functionality | To allow users to easily switch between years and months when entering loan terms, improving usability and flexibility |
| 2025-04-27 | Enhanced print-specific styling and layouts | To provide optimized printing capabilities for reports, calculators, and dashboards with proper page breaks, headers, and formatting |
| 2025-04-27 | Implemented occupancy rate calculator | To enable multi-family property owners to analyze occupancy rates, calculate revenue impact, compare to market averages, and determine breakeven occupancy |
| 2025-04-28 | Refactored utility functions into centralized modules | To eliminate code duplication, improve maintainability, and ensure consistent behavior by centralizing common functions in dedicated utility modules (common.py, dash_helpers.py, financial_helpers.py) |
| 2025-04-29 | Updated Property model to use flat structure for monthly income and expenses | To align implementation with documented data structures, improve maintainability, and simplify property financial service interactions |
| 2025-04-29 | Standardized property_taxes field naming | To ensure consistent use of "property_taxes" (plural) throughout the codebase, aligning with DATA_STRUCTURES.md documentation |
| 2025-04-29 | Added Development Practices section to PLANNING.md | To establish clear guidelines for code reuse, debugging methodology, code organization, strategic logging, and general development practices that ensure maintainable, clean, and well-structured code |
| 2025-04-29 | Established rule against storing calculated values | To improve data integrity, reduce storage needs, and maintain a single source of truth for calculations by computing derived values at runtime rather than storing them |
| 2025-04-29 | Standardized Transaction model ID field and simplified Reimbursement structure | To align implementation with documented data structures, ensuring ID field is explicitly defined in Transaction class and simplifying the Reimbursement structure while maintaining validation logic |
| 2025-04-29 | Documented property_access field in User model | To align implementation with documented data structures, adding the property_access field to DATA_STRUCTURES.md with comprehensive documentation of access levels and equity shares, and creating unit tests to validate functionality |
| 2025-04-29 | Enhanced landing page for unauthenticated users | To provide a more informative and engaging experience for new users, created a comprehensive landing page that showcases the application's features and capabilities, with proper authentication flow to redirect unauthenticated users to this page |
| 2025-04-30 | Fixed circular import between money.py and validators.py | To resolve an import error that was preventing the application from starting, restructured the imports by moving utility functions to validators.py and removing the circular dependency |
| 2025-04-30 | Implemented alphanumeric sorting for property dropdowns | To improve user experience by displaying properties in a consistent, predictable order in all dropdown menus throughout the application, modified the _format_property_addresses function to sort properties by address in ascending alphanumeric order |
| 2025-04-30 | Implemented comprehensive test persona for UI testing | To provide consistent test data for UI testing, created a test persona with dedicated user credentials, diverse property portfolio, comprehensive analyses, various loan scenarios, transaction history with reimbursements, and MAO calculation defaults |
| 2025-04-30 | Relocated MAO button from Purchase Details to Comparable Properties card | To improve UI organization and consolidate related functionality, removed the "Calculate MAO" button from the Purchase Details card header and renamed the "Comparable Properties" card to "Comparable Properties and MAO" to better reflect its combined functionality |
| 2025-04-30 | Fixed "Run Comps" button for new analyses | To ensure consistent functionality between new and existing analyses, fixed the "Run Comps" button to properly display property values when creating a new analysis by correcting field name references in the API response handling |
| 2025-04-30 | Added "Change MAO Default Values" feature | To allow users to customize their MAO calculation parameters by setting default values for LTV percentage, monthly holding costs, and max cash left in deal, with values stored in the user's profile and applied to all MAO calculations |

---

By following these guidelines, our collaboration will be more effective, resulting in higher quality code and a more efficient development process.