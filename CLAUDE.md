# CLAUDE.md - EHR Evaluation System Project Context

## Project Overview
This is an Employee Performance Evaluation System that integrates features from the Elevate Growth System. It provides comprehensive evaluation capabilities with AI-powered feedback generation.

## Key Features Implemented
- **Contribution Evaluation System** at `/evaluations/contribution/`
- Multi-dimensional evaluation criteria (Technical, Contribution, Growth)
- AI-powered feedback using OpenAI API
- Task management and tracking
- Goal setting and progress monitoring
- Real-time notification system (WebSocket ready)
- Role-based access control (Employee, Evaluator, HR, Admin)
- **Organization Chart System** at `/organization/chart/` (NEW - 2025.01.18)
  - Interactive org tree with drag-and-drop reorganization
  - What-if analysis and scenario management
  - Snapshot A/B comparison
  - Excel import/export functionality
  - Function × Leader matrix view

## Tech Stack
- **Backend**: Django 5.2, Django REST Framework, PostgreSQL/SQLite
- **Frontend**: React 18, TypeScript, Material-UI
- **AI**: OpenAI API for feedback generation
- **Real-time**: Django Channels, WebSocket

## Project Structure
```
EHR_project/
├── ehr_evaluation/     # Django settings
├── users/              # User management
├── evaluations/        # Core evaluation system
├── notifications/      # Notification system
├── frontend/          # React application
│   └── src/pages/ContributionEvaluation.tsx  # Main evaluation page
├── manage.py
├── setup_initial_data.py
├── run_server.bat
└── run_frontend.bat
```

## Quick Start Commands
```bash
# Backend
python manage.py runserver
# or
run_server.bat

# Frontend
cd frontend && npm start
# or
run_frontend.bat
```

## Login Credentials
- Admin: admin / admin123
- Evaluator: evaluator1 / password123
- Employee: employee1 / password123

## Important URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

### Main Pages
- Home Dashboard: http://localhost:8000/
- Employee Management: http://localhost:8000/employees/

### Organization Charts
- Basic Organization Chart: http://localhost:8000/employees/org-chart/
- Advanced Organization Management: http://localhost:8000/organization/chart/
- Hierarchical Organization: http://localhost:8000/employees/hierarchy-org/

### Performance Evaluation
- Evaluation Dashboard: http://localhost:8000/evaluations/
- Contribution Evaluation Guide: http://localhost:8000/evaluations/contribution/guide/
- Contribution Employee List: http://localhost:8000/evaluations/contribution/employees/
- Expertise Evaluation Guide: http://localhost:8000/evaluations/expertise/guide/
- Expertise Employee List: http://localhost:8000/evaluations/expertise/employees/
- Impact Evaluation Guide: http://localhost:8000/evaluations/impact/guide/
- Impact Employee List: http://localhost:8000/evaluations/impact/employees/
- Comprehensive Evaluation: http://localhost:8000/evaluations/comprehensive/
- Calibration: http://localhost:8000/evaluations/calibration/
- My Evaluations: http://localhost:8000/evaluations/my/
- Evaluator Dashboard: http://localhost:8000/evaluations/evaluator/
- HR Admin Dashboard: http://localhost:8000/evaluations/hr-admin/

### AI Services
- AI QuickWin Hub: http://localhost:8000/ai-quickwin/
- AIRISS Dashboard: http://localhost:8000/airiss/
- AI Coaching: http://localhost:8000/ai-coaching/
- Team Optimizer: http://localhost:8000/ai-team-optimizer/
- Executive Insights: http://localhost:8000/ai-insights/
- Prediction Analytics: http://localhost:8000/ai-predictions/
- AI Interviewer: http://localhost:8000/ai-interviewer/
- AI Chatbot: http://localhost:8000/ai-quickwin/chatbot/
- Leader Assistant: http://localhost:8000/ai-quickwin/leader-assistant/

## Environment Variables (.env)
- `SECRET_KEY`: Django secret key
- `OPENAI_API_KEY`: Required for AI feedback generation
- `DEBUG`: Set to False in production
- `DATABASE_URL`: PostgreSQL connection (optional)

## Key Models
- `User`: Extended Django user with roles and departments
- `Evaluation`: Main evaluation record with status workflow
- `Task`: Task assignments and tracking
- `Score`: Individual scoring for criteria
- `Feedback`: AI and manual feedback
- `Goal`: Employee goals and progress

## API Endpoints
- `/api/evaluations/` - Evaluation CRUD
- `/api/evaluations/{id}/submit/` - Submit evaluation
- `/api/evaluations/feedbacks/generate_ai/` - Generate AI feedback
- `/api/tasks/` - Task management
- `/api/notifications/` - Notification system
- `/api/organization/org/units/` - Organization units CRUD (NEW)
- `/api/organization/org/units/tree/` - Organization tree structure (NEW)
- `/api/organization/org/units/group/matrix/` - Function × Leader matrix (NEW)
- `/api/organization/org/scenarios/` - Scenario management (NEW)
- `/api/organization/org/whatif/reassign/` - What-if analysis (NEW)
- `/api/organization/org/io/import/` - Excel import (NEW)
- `/api/organization/org/io/export/` - Excel export (NEW)

## Development Notes
- Always run migrations before starting: `python manage.py migrate`
- Initial data setup: `python setup_initial_data.py`
- Frontend uses proxy to backend (configured in package.json)
- WebSocket support requires Redis installation

## Testing Checklist
- [ ] User authentication works
- [ ] Evaluation creation and submission
- [ ] AI feedback generation (requires valid OpenAI key)
- [ ] Task assignment and completion
- [ ] Score calculation
- [ ] Notification delivery

## Deployment Considerations
- Use PostgreSQL in production
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`
- Install and configure Redis for WebSocket
- Set up proper CORS configuration
- Use environment variables for sensitive data
- Configure static file serving

## Future Enhancements
- Complete dashboard implementation
- Mobile responsive improvements
- Advanced analytics and reporting
- 360-degree feedback system
- Performance prediction models
- Integration with external HR systems

## Common Issues & Solutions
1. **OpenAI API Error**: Ensure OPENAI_API_KEY is set in .env
2. **CORS Issues**: Check CORS_ALLOWED_ORIGINS in settings
3. **Static Files 404**: Run `python manage.py collectstatic`
4. **Migration Errors**: Delete migrations and re-run makemigrations

## Code Quality Standards
- Follow PEP 8 for Python code
- Use TypeScript strict mode for React
- Write meaningful commit messages
- Document API changes
- Test before pushing to production

## Contact & Support
For issues or questions about this project, refer to the README.md or contact the development team.

## Recent Updates

### 2025.01.18 - UI/UX Improvements
**Revolutionary Template & Sidebar Enhancement:**
- **Revolutionary Template Applied**
  - Applied dark theme with cyan (#00d4ff) accents across all pages
  - Organization chart pages now use Revolutionary template
  - Consistent design system throughout the application
  
- **Sidebar Navigation Overhaul**
  - Complete restructuring of sidebar menu for better organization
  - **Expandable Performance Evaluation Menu**:
    - Contribution Evaluation (Guide, Employee Evaluations)
    - Expertise Evaluation (Guide, Employee Evaluations)
    - Impact Evaluation (Guide, Employee Evaluations)
    - Comprehensive Evaluation & Calibration
    - Role-based Views (My Evaluation, Evaluator, HR Admin)
  - **Enhanced Organization Chart Menu**:
    - Basic Organization Chart
    - Advanced Organization Management (NEW badge)
    - Hierarchical Organization View
  - **AI Services Menu** with expandable submenu
  - State persistence for expanded/collapsed sections
  - Auto-highlight for current page
  - Font Awesome icons integration
  
- **API Improvements**
  - Enhanced error handling for AI feedback generation
  - Fallback feedback when AI service unavailable
  - Better null/undefined handling in evaluation APIs

**Files Modified:**
- `templates/base_revolutionary.html` - Integrated new sidebar
- `templates/sidebar_revolutionary.html` - New comprehensive sidebar component
- `employees/templates/employees/organization_chart.html` - Revolutionary theme
- `organization/templates/organization/organization_chart_revolutionary.html` - Revolutionary theme
- `evaluations/api_views.py` - Enhanced error handling

## Changelog

### 2025.01.18 - Organization Chart System Implementation
**Major Features Added:**
- **Enhanced Organization Models** (`organization/models_enhanced.py`)
  - OrgUnit: Flexible organization unit with JSONB support for members
  - OrgScenario: Save and manage organizational scenarios
  - OrgSnapshot: Capture organization state for comparison
  - OrgChangeLog: Comprehensive audit logging
  
- **RESTful API** (`organization/api_views.py`, `organization/serializers.py`)
  - Full CRUD operations for organization units
  - Tree structure API with hierarchical data
  - Matrix view API (Function × Leader)
  - What-if analysis for reorganization simulation
  - Excel import/export with validation
  - Scenario management and application
  
- **React Frontend Components** 
  - `OrganizationChart.tsx`: Main page with tabs for Tree/Matrix views
  - `OrgTree.tsx`: React Flow based interactive tree with drag-and-drop
  - `OrgNodeCard.tsx`: Rich node visualization with leader and member info
  - `OrgMatrix.tsx`: Heatmap matrix for cross-functional analysis
  - `OrgSidebar.tsx`: Control panel for filters, snapshots, scenarios
  
- **Advanced Features**
  - Drag-and-drop reorganization with circular reference prevention
  - A/B snapshot comparison for change analysis
  - Scenario save/load for planning purposes
  - Excel round-trip (import/export) with template validation
  - Redis caching for performance optimization
  - Comprehensive audit logging with IP tracking
  
**Technical Improvements:**
- Added TypeScript type definitions for organization entities
- Implemented proper error handling and validation
- Added Django admin interface for organization management
- Created migration files for database schema updates
- Integrated with existing authentication and permission system

**Files Created/Modified:**
- Backend: 7 new files (models, views, serializers, URLs, admin, migration)
- Frontend: 7 new React components and helpers
- Documentation: PROJECT_STRUCTURE.md, ORGANIZATION_CHART_IMPLEMENTATION.md