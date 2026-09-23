# AGENTS.md

## Track

Special Track: Astana Innovations

## Project

AI system for automatic meeting minutes and task tracking.

The prototype should support the core scenario defined by the Astana Innovations case:

1. Record or receive meeting audio/video.
2. Transcribe participant speech.
3. Distinguish speakers (speaker diarization).
4. Detect assignments from the transcript and extract who is responsible, what must be done, and the deadline.
5. Generate a concise meeting summary and protocol.
6. Allow the final protocol to be exported to PDF/DOCX.
7. Support reminders and task-status tracking when implemented.

The required language scope is Russian, Kazakh, and mixed Russian/Kazakh ("shala-Kazakh").

## Privacy and deployment constraints

This project handles potentially sensitive meeting information.

- The solution must be capable of running in a closed/on-premise environment.
- Do not send meeting audio, transcripts, or sensitive data to external cloud AI APIs.
- Prefer local/self-hosted speech recognition, diarization, LLM/NLP, and supporting models.
- Never commit meeting recordings, transcripts containing real sensitive information, credentials, tokens, or secrets.
- Real recordings used for demos must be anonymized.
- Synthetic or simulated meeting recordings are acceptable for development and testing.

## Project structure

Use this repository structure unless the existing implementation requires otherwise:

- `frontend/` — meeting UI, transcripts, summaries, assignments, status dashboard, and exports.
- `backend/` — API, orchestration, meeting/task logic, persistence, authentication, and export services.
- `ml/` — local speech-to-text, diarization, assignment extraction, summarization, and other AI pipelines.
- `docs/` — API contract, architecture, setup, model documentation, and demo instructions.
- `tests/` — automated and integration tests where appropriate.
- `.env` — local configuration only; never commit secrets.
- `docker-compose.yml` — reproducible local/on-premise service setup.

## General rules

- Read the existing code, README, this file, and relevant documentation before making changes.
- Keep changes focused on the requested task.
- Follow existing project conventions before introducing new ones.
- Do not remove or rewrite working code unless necessary.
- Reuse existing components and utilities before creating duplicates.
- Keep the prototype reproducible for hackathon judging.
- Update README and documentation whenever setup, architecture, commands, APIs, or user-visible behavior change.
- Never commit secrets or sensitive meeting data.

## Frontend

If a `frontend/` directory exists, keep frontend-specific work inside it.

Recommended structure:

- `src/api/` — API client functions; base URLs come from environment variables.
- `src/components/` — reusable UI components.
- `src/pages/` — application screens.
- `src/features/meetings/` — recording/upload, meeting details, transcript, and summary.
- `src/features/tasks/` — extracted assignments, deadlines, responsible people, and statuses.
- `src/hooks/` — reusable hooks.
- `src/utils/` — shared frontend utilities.

Rules:

- Do not modify `backend/` or `ml/` for frontend-only tasks unless the interface must change.
- Handle loading, processing, empty, success, and error states.
- Clearly show speaker identity, timestamps where available, extracted assignments, responsible person, and deadline.
- Do not hardcode backend URLs or secrets.
- Requests must match `docs/API_CONTRACT.md` if it exists.

## Backend

If a `backend/` directory exists, keep backend-specific work inside it.

Recommended responsibilities:

- Meeting creation and audio/video upload.
- Processing-job orchestration and status.
- Transcript and speaker-segment storage.
- Assignment extraction and task-status management.
- Meeting summary/protocol generation.
- PDF/DOCX export.
- Authentication/authorization when required.
- Interfaces to local ML services.

Rules:

- Validate all client input.
- Do not expose sensitive meeting data in logs.
- Keep long-running ML processing outside request handlers when practical.
- Use explicit processing states and useful error messages.
- Keep API changes synchronized with `docs/API_CONTRACT.md`.

## ML / AI

The `ml/` area owns the local AI pipeline.

Core capabilities:

- Speech-to-text for Russian.
- Speech-to-text for Kazakh.
- Mixed Russian/Kazakh ("shala-Kazakh") speech handling.
- Speaker diarization.
- Assignment extraction: responsible person, task/action, and deadline.
- Meeting summarization.

Rules:

- Models used on meeting content must support local/self-hosted execution.
- Keep model loading and inference separate from API/UI code.
- Document model names, versions, hardware requirements, inputs, and outputs.
- Preserve timestamps and speaker information through the pipeline when available.
- Assignment extraction should return structured, testable output rather than only free-form prose.
- Do not fabricate a responsible person or deadline when the transcript does not provide enough evidence; represent missing/uncertain fields explicitly.
- Keep intermediate formats stable and documented.
- Provide deterministic fixtures or sample recordings/transcripts for testing where practical.

## API sync

Before changing communication between frontend, backend, and ML services, read `docs/API_CONTRACT.md` first if it exists.

The contract is the source of truth for:

- Endpoint paths and methods.
- Request and response schemas.
- Processing states.
- Transcript/speaker structures.
- Assignment fields.
- Summary/protocol fields.
- Export endpoints.
- Error formats.
- Authentication requirements.

If a required contract is missing or ambiguous, define or update it before implementing incompatible assumptions.

## Hackathon priorities

Prioritize a complete, demonstrable end-to-end workflow over unnecessary breadth.

The critical demo path is:

audio/video -> local transcription -> diarization -> structured assignments -> meeting summary/protocol -> PDF/DOCX export.

After the mandatory flow works reliably, optional enhancements can include:

- Assignment status dashboard (in progress / overdue / completed).
- Deadline reminders.
- Automatic distribution of protocol excerpts to responsible people.
- Assignment urgency/category classification.
- Voice identification.
- Electronic document-management-system integration.

Do not sacrifice the mandatory workflow for optional features.

## Validation

Before considering a change complete:

1. Run available tests, linting, type checks, and builds.
2. Verify the affected user flow.
3. For ML changes, test against Russian, Kazakh, and mixed-language samples where relevant.
4. Verify frontend/backend/ML schemas still match.
5. Verify the project can run without sending meeting content to prohibited external cloud AI services.
6. Report checks that could not be run and why.

## README and reproducibility

Keep `README.md` sufficient for a judge or new developer to understand and run the prototype.

It should document:

- What problem the project solves.
- Architecture and major components.
- Technology/model choices.
- Prerequisites.
- Environment configuration.
- Exact startup commands.
- How to run the main demo scenario.
- Expected inputs and outputs.
- Known limitations.
- Local/on-premise privacy approach.

Prefer a reproducible one-command or minimal-command startup where practical.

## Git

- Use clear, descriptive commit messages.
- Keep unrelated changes out of commits.
- Do not force-push or rewrite shared history unless explicitly requested.
