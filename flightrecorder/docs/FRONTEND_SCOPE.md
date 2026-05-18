# Frontend scope

v1 frontend surfaces from the spec. All are not started.

## Surfaces

### chat UI
The primary interaction surface. Responsive, mobile-first. Message input,
streaming SSE display, image paste, session context. Installable as PWA on
phone home screen.

### Session list
List of past sessions, newest first. Shows session slug, date, tag preview,
project annotation.

### Document view
Read-only view of project documents (`/projects/<name>`). Shows sections
(Problem, TODOs, etc.) with their status. Links to spaghetti ideas for TODOs
that came from the wall.

### Match approval queue
Pending matchmaker proposals displayed as checklists. Daniel ticks approve
or reject per proposed match. Approval triggers document append and spaghetti
frontmatter update.

### Wall view
The public `/wall/` and `/wall/<idea-id>/` pages rendered by Hugo. Frontend
only needs to display these, not manage them.

## Available backend routes today

- `POST /api/sessions` - create
- `GET /api/sessions` - list
- `GET /api/sessions/{id}` - detail with transcript
- `POST /api/sessions/{id}/upload` - image upload

## Draft/missing

- Chat endpoint (SSE) - contract draft exists, not implemented
- Session close - no contract draft, not implemented
- Voice input - not implemented
- All document, spaghetti, match, project, journey, budget, audit routes -
  not implemented
