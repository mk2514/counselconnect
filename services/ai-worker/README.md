# AI Worker

The API runs asynchronous document jobs through the locally configured Ollama
service for:

- PDF text extraction and scanned-page OCR through a local vision model
- Review-only metadata/entity extraction for FIR, absence proof, investigation,
  judgment, and withdrawal documents
- Case summaries based on recorded case data

**AI control model**: outputs are candidate information only. Police must review
and confirm extracted FIR details before the case record is finalized. AI does
not make judicial or other official decisions. See
[Architecture Rules](../../docs/rules/01-architecture.md).

## Configuration

Configure `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `OLLAMA_TIMEOUT_SECONDS` for
the API. The model must be available to that Ollama instance; scanned documents
require a vision-capable model. With the default settings, install it locally
using `ollama pull llama3.2-vision`, or in the Docker Compose service with
`docker compose exec ollama ollama pull llama3.2-vision`. If processing fails
or Ollama is offline, the job is marked `FAILED`, a retry is available, and the
case workflow remains available for manual review.

Speech transcription, case categorization, administrative prioritization, and
conflict detection are not part of this processing layer.
