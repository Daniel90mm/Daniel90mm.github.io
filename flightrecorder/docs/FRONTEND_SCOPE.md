# Frontend scope

v1 frontend surfaces from the spec. The first dogfood target is plain static HTML/CSS/JS -- no framework -- until
dogfooding proves the API shape.

Static frontend files live in `src/frontend/` and are served by the backend
at `GET /` and `GET /assets/*`.

## Available backend routes for v1 dogfood frontend

- `GET /health`
- `POST /api/sessions` - create a session
- `GET /api/sessions` - list sessions (newest first, paginated)
- `GET /api/sessions/{id}` - session detail with transcript
- `POST /api/sessions/{id}/upload` - image upload
- `POST /api/sessions/{id}/messages` - chat SSE endpoint
- `POST /api/sessions/{id}/extract` - run idea capture
- `GET /api/budget` - monthly spend and hard-stop status
- `GET /api/projects` - active project registry entries
- `GET /api/documents` - document list
- `GET /api/documents/{ref}` - document body
- `GET /api/spaghetti` - spaghetti idea list
- `GET /api/spaghetti/{idea_id}` - spaghetti body
- `POST /api/matchmaker/run` - run matchmaker

## First dogfood frontend target

Create/list sessions, chat over SSE, run extraction, watch budget status, and
inspect returned session transcript plus extracted documents/spaghetti.
The frontend should call `GET /api/runtime` on page load and display
provider readiness before enabling chat/extract.

**Status: implemented.** Static shell (`src/frontend/index.html`) served
by the backend at `GET /` with session CRUD, chat SSE streaming, extraction
trigger, budget status, and read panels for project documents and spaghetti
ideas.

## Still missing from backend

Match decision routes, voice, budget mutation endpoints, publisher controls.

## Full v1 surfaces (post-dogfood)

### Chat UI
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
