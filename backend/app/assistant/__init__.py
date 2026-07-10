"""
AI Assistant module — natural-language interface for expense management.
Architecture:

  assistant_routes.py       ← Blueprint with HTTP endpoints
       ↓
  assistant_controller.py   ← Request parsing, response formatting
       ↓
  assistant_service.py      ← Orchestrator: intent → entities → tool → response
       ↙       ↓        ↘
  intent_    entity_    tool_        response_
  detector   extractor  router       builder
"""

from app.assistant.assistant_routes import assistant_bp

__all__ = ["assistant_bp"]
