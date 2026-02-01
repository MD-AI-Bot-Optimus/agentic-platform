# ADR-009: Google Vision OCR Integration

**Date:** 2026-02-01  
**Status:** ACCEPTED  
**Context:** Proof of Concept (POC) for the Agentic Platform requires optical character recognition (OCR) capability to extract text from images for document processing workflows.

## Problem
The platform needs a reliable, production-grade OCR solution that:
1. Integrates seamlessly with the workflow engine
2. Supports multiple image formats (JPEG, PNG, etc.)
3. Provides confidence scores and structured output
4. Works locally in development environments
5. Scales for enterprise use cases

## Decision
We integrate **Google Cloud Vision API** for OCR via:
1. **GoogleVisionOCR adapter** in the tool registry
2. **Dedicated `/run-ocr/` FastAPI endpoint** for image uploads
3. **Application Default Credentials (ADC)** for authentication (local dev) and workload identity (production)
4. **YAML-based workflow definition** (ocr_mvp.yaml) using nodes/edges format
5. **React UI component** for testing and demonstration

## Rationale

### Why Google Vision?
- **Industry-leading accuracy:** State-of-the-art ML models trained on billions of images
- **Multi-format support:** JPEG, PNG, GIF, WebP, TIFF, HEIF, HEIC
- **Structured output:** Full text blocks, paragraphs, words with confidence scores
- **Scalable:** Handles millions of requests; built on Google's infrastructure
- **Cost-effective:** Pay-per-use pricing, no upfront fees or minimum commitments

### Why ADC + Organization Policy Workaround?
- **ADC for local dev:** Eliminates need for service account keys in source control; uses local gcloud auth
- **Org policy constraint:** Organization disables `iam.disableServiceAccountKeyCreation`, blocking traditional key-based auth
- **Solution:** Use ADC with `gcloud auth application-default login` for development; for production, use **Workload Identity** on GKE or **Service Account Impersonation** via short-lived tokens
- **Security benefit:** No long-lived credentials stored anywhere; rotated automatically by Google

### Why Separate `/run-ocr/` Endpoint?
- **Simplicity:** Dedicated endpoint for image processing separate from general workflow execution
- **Optimization:** Can handle multipart form-data efficiently without YAML overhead
- **User experience:** Easier for UI to implement image upload + preview
- **Future extension:** Can add OCR-specific features (batch processing, document splitting) without affecting workflow engine

### Why Nodes/Edges Workflow Format?
- **Graph-native:** Natural representation of conditional branching and parallelism
- **Explicit routing:** Clear edges define workflow topology; easier to validate and visualize
- **Future-ready:** Supports complex routing logic and dynamic node generation

## Implementation

### Files
- `src/agentic_platform/tools/google_vision_ocr.py` — GoogleVisionOCR adapter
- `src/agentic_platform/api.py` — `/run-ocr/` endpoint implementation
- `src/workflows/ocr_mvp.yaml` — Example OCR workflow
- `ui/src/App.jsx` — React OCR demo component
- `.gitignore` — Exclude credentials and sensitive files

### API Endpoint
```
POST /run-ocr/
Content-Type: multipart/form-data

image: <binary image file>
credentials_json: <optional Google credentials JSON>
```

**Response:**
```json
{
  "result": {
    "job_id": "job-1",
    "status": "completed",
    "tool_results": [
      {
        "node_id": "ocr_step",
        "result": {
          "text": "Extracted full text",
          "confidence": 0.95,
          "formatted_text_lines": ["Line 1", "Line 2", ...]
        }
      }
    ]
  },
  "audit_log": [...]
}
```

### Authentication Setup
```bash
# Local development
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
gcloud auth application-default set-quota-project <PROJECT_ID>

# Enable API
gcloud services enable vision.googleapis.com
```

### Workflow YAML Format
```yaml
nodes:
  - id: start
    type: start
  - id: ocr_step
    type: tool
    tool: google_vision_ocr
  - id: end
    type: end
edges:
  - from: start
    to: ocr_step
  - from: ocr_step
    to: end
```

## Trade-offs

### Pros
- ✅ Best-in-class accuracy and support
- ✅ No self-hosted infrastructure needed
- ✅ Easy to integrate with existing tool registry
- ✅ Scales automatically with demand
- ✅ Rich output (confidence, text blocks, tables, etc.)

### Cons
- ⚠️ External dependency on Google Cloud
- ⚠️ Network latency for each request (~200-500ms)
- ⚠️ Requires active Google Cloud project and billing
- ⚠️ Not suitable for fully offline workflows

## Alternatives Considered

### 1. Tesseract OCR (Open Source)
- **Pros:** No external dependency, free, open source
- **Cons:** Lower accuracy, slower, requires local installation, poor handling of skewed/rotated text
- **Decision:** Not chosen due to accuracy requirements

### 2. AWS Textract
- **Pros:** Good accuracy, document-specific features
- **Cons:** Adds AWS dependency, higher latency, more complex pricing
- **Decision:** Chose Google Vision for consistency with GCP setup

### 3. Azure Computer Vision
- **Pros:** Good integration if using Azure stack
- **Cons:** Not ideal for our architecture; GCP already in use
- **Decision:** Chose Google Vision for ecosystem alignment

## Future Enhancements

1. **Batch OCR:** Add endpoint for processing multiple images in parallel
2. **Document parsing:** Extract structured data (tables, forms) from documents
3. **Handwriting recognition:** Support for handwritten text
4. **Language detection:** Auto-detect and handle multiple languages
5. **Post-processing:** Spell-check, grammar correction via LLM
6. **Caching:** Cache OCR results for identical images (content-addressed)
7. **Async OCR:** Support long-running OCR jobs with polling/webhooks

## Testing

### Unit Tests
- Mock Google Vision API responses
- Validate error handling (invalid image, API failures)
- Check formatted text line output

### Integration Tests
- Real Google Vision API calls (with test images)
- End-to-end workflow execution
- Audit log verification

### UI Testing
- Image upload and preview
- Result display and formatting
- Error message handling

## Monitoring & Observability

- **Audit logs:** All OCR requests logged with inputs, outputs, confidence scores, timing
- **Metrics:** Request count, average latency, error rate, API quota usage
- **Alerts:** Set up alerts for quota exhaustion, high error rates, API outages

## Security Considerations

1. **Credentials:** Use ADC (local) or Workload Identity (production); never commit credentials
2. **Image data:** Images are sent to Google Cloud servers; ensure compliance with data privacy policies
3. **Output storage:** OCR results can be cached in artifact store; apply encryption at rest
4. **Rate limiting:** Implement rate limiting on `/run-ocr/` to prevent abuse/quota exhaustion
5. **Access control:** Use IAM roles to restrict who can enable Vision API and run OCR

## References

- [Google Cloud Vision API Documentation](https://cloud.google.com/vision/docs)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [OCR MVP Workflow](../../workflows/ocr_mvp.yaml)

## Sign-off

- **Author:** Agentic Platform Team
- **Reviewers:** TBD
- **Date:** 2026-02-01
