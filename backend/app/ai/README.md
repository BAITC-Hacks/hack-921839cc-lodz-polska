# Meeting analysis

This package converts an existing transcript into an evidence-linked summary,
decisions, action items, and open questions. Speech recognition and speaker
diarization belong to the local ML pipeline; this package accepts their
transcript output.

## Privacy and model boundary

Meeting audio and transcripts can contain sensitive information. The router
requires an injected local JSON generator; there is no external cloud provider
or cloud fallback. Connect it only to a self-hosted model/service on the
approved on-premise network. Keep model loading and inference in the ML service.

The generator interface is:

    local_generate_json(system_prompt: str, payload: dict) -> dict

Its output is validated as MeetingAnalysis. The prompt requires evidence
segment IDs and represents missing people or deadlines as null. It does not
invent assignments.

## Proposed endpoint

POST /api/meetings/analyze

Request: AnalysisRequest with meeting ID, language (ru, kk, or ru_kk),
and timestamped/speaker-labeled transcript segments.

Response: MeetingAnalysis with summary, key points, decisions, action items,
and open questions. Each extracted item includes transcript segment evidence.

The repository has no application entry point or shared API contract yet.
Mount create_ai_router(local_generate_json) only after aligning this proposed
shape with docs/API_CONTRACT.md.
