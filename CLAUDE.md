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
- Contribution Evaluation: http://localhost:3000/evaluations/contribution

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