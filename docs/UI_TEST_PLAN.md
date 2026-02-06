# Agentic Platform - Consolidated UI Test Plan

> **Scope**: Covers Agent Tab, OCR Demo, Workflow Editor, and MCP Tools.

## 1. Master Test Strategy

### Core Philosophy
- **Automated Verification**: Use `browser_subagent` to click through critical paths.
- **Visual Confirmation**: Use screenshots/video to verify UI states (loading, results).
- **Backend Validation**: Verify side-effects (file creation, API responses) where possible.

---

## 2. Integration Test Suites

### Suite A: Agent Tab (Language Model Integ.)
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| **AGT-001** | **Happy Path (Mock)** | 1. Nav to Agent.<br>2. Select "Mock LLM".<br>3. Input "Hello".<br>4. Exe. | "Executing" -> Reasoning -> "MOCK ANSWER". |
| **AGT-002** | **Complex Prompt** | 1. Input "Explain quantum".<br>2. Exe. | Handling of long text/multi-step reasoning. |
| **AGT-004** | **Model Switch** | 1. Switch to "Gemini".<br>2. Exe. | Backend receives correct model param. |

### Suite B: OCR Demo (Feature & Fetch)
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| **OCR-001** | **Fetch 100 Samples** | 1. Click "Fetch".<br>2. Wait 40s. | **Backdrop** blocks UI. List populates with 100 items. |
| **OCR-002** | **Diversity Check** | 1. Click Sample 1.<br>2. Click Sample 2. | Preview images MUST be different. |
| **OCR-003** | **Extraction** | 1. Click "Run OCR". | Result box appears with text. |
| **OCR-004** | **Preview Pane** | 1. Select item used in MCP tab. | Image matches what was selected. |

### Suite C: MCP Test (Tools)
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| **MCP-001** | **Available Tools** | 1. Check dropdown. | Contains `google_vision_ocr`. |
| **MCP-002** | **Shared Samples** | 1. Look for "Internet Sample 1". | Present (Synced with OCR tab). |
| **MCP-003** | **Fetch Parity** | 1. Click "Fetch" in MCP. | Triggers same Backdrop/Process as OCR tab. |

### Suite D: Workflow (Graph Visualization)
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| **WF-001** | **Render Graph** | 1. Default load. | Nodes/Edges visible. |
| **WF-002** | **Execution** | 1. Click "Run". | Logs stream in console. |

---

## 3. QA Checklist (Manual or Automated)

### Layout & Branding
- [ ] Header: "Agentic Platform" with Pacific background.
- [ ] Tabs: Navigation works (Home, Agent, OCR, MCP).

### Functional Integrity
- [ ] **Sample List**: Scrollable, no 404s.
- [ ] **Backdrop**: Gray overlay prevents clicking "Fetch" twice.
- [ ] **Preview**: Image loads correctly (no broken icons).
- [ ] **OCR**: Returns text (mock or real).

### Negative Testing
- [ ] **Network Fail**: Disconnect internet -> Fetch -> Should fallback/alert.
- [ ] **Double Click**: "Fetch" button disabled or blocked during load.

---

## 4. Automation Evidence (Latest Run)
See `OCR_RECOVERY_REPORT.md` for the latest specific evidence of the OCR/Fetch suite.
