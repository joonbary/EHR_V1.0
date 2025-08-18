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