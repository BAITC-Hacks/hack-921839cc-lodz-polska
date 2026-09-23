# AGENTS.md

## Track

Education

## Project structure

Use this repository structure unless the existing code requires otherwise:

- `frontend/` — user interface for students, teachers, and admins.
- `backend/` — API, authentication, business logic, and database access.
- `ml/` — optional AI/ML features such as recommendations, tutoring, grading assistance, or analytics.
- `docs/` — API contracts, architecture notes, product requirements, and setup documentation.
- `.env` — local environment variables only. Never commit secrets.
- `docker-compose.yml` — local multi-service setup when Docker is used.

## General rules

- Read the existing code and documentation before making changes.
- Keep changes focused on the requested task.
- Follow the existing project structure and coding conventions.
- Do not remove or rewrite working code unless necessary.
- Reuse existing components and utilities before creating duplicates.
- Update documentation when behavior, setup, or API contracts change.
- Never commit API keys, passwords, access tokens, private keys, or student personal data.

## Education product rules

- Design for clear and simple student and teacher workflows.
- Keep learning content readable and accessible.
- Do not invent grades, attendance, progress, or student records.
- Treat student and teacher data as sensitive.
- AI-generated educational content should be clearly distinguishable when relevant.
- For quizzes, grading, recommendations, or tutoring features, keep the logic explainable and testable.

## Frontend

If a `frontend/` directory exists, keep frontend work inside it.

Recommended structure:

- `src/api/` — API client functions. Base URLs must come from environment variables.
- `src/components/` — reusable UI components.
- `src/pages/` — application screens/pages.
- `src/features/` — larger education features such as courses, lessons, quizzes, assignments, or progress.
- `src/hooks/` — reusable frontend hooks.
- `src/utils/` — shared frontend utilities.

Rules:

- Do not modify `backend/` or `ml/` when the task is frontend-only.
- Keep components small and reusable.
- Handle loading, empty, success, and error states.
- Do not hardcode backend URLs or secrets.
- Requests must follow the API contract in `docs/API_CONTRACT.md` if that file exists.

## Backend

If a `backend/` directory exists, keep backend work inside it.

Recommended responsibilities:

- API endpoints and validation.
- Authentication and authorization.
- Courses, lessons, assignments, quizzes, submissions, progress, and user roles.
- Database access and migrations.
- Integration with ML services when required.

Rules:

- Do not modify `frontend/` or `ml/` when the task is backend-only.
- Validate all client input.
- Enforce authorization on protected education data.
- Never expose secrets or sensitive student information in logs or API responses.
- Keep API changes synchronized with `docs/API_CONTRACT.md`.

## ML / AI

If an `ml/` directory exists, use it for AI and machine-learning functionality.

Examples:

- Personalized learning recommendations.
- Educational content generation.
- Question generation.
- Tutoring or explanation features.
- Learning analytics.

Rules:

- Keep ML code separate from API and UI code.
- Document model inputs and outputs.
- Do not silently make high-impact education decisions for users.
- Backend code should communicate with ML through a clear interface/API.
- Include a non-ML fallback when practical.

## API sync

Before writing or changing code that communicates between frontend, backend, or ML services, read `docs/API_CONTRACT.md` first if it exists.

The API contract is the source of truth for:

- Endpoint paths.
- HTTP methods.
- Request fields.
- Response fields.
- Error formats.
- Authentication requirements.

If the needed contract is missing or ambiguous, update or clarify the contract before implementing incompatible assumptions.

## Validation

Before considering a change complete:

1. Run the available tests, linting, type checks, or build commands.
2. Verify that the changed functionality works as expected.
3. Check that frontend/backend/ML interfaces still match.
4. Report any checks that could not be run and why.

## Git

- Use clear, descriptive commit messages.
- Keep unrelated changes out of commits.
- Do not force-push or rewrite shared history unless explicitly requested.
