"""Tests for incident service."""
import pytest
from app.models import IncidentStatus

class TestIncidentTransitions:
    def test_valid_transition_detected_to_investigating(self):
        valid = {
            IncidentStatus.DETECTED: [IncidentStatus.ACKNOWLEDGED, IncidentStatus.INVESTIGATING],
        }
        assert IncidentStatus.INVESTIGATING in valid[IncidentStatus.DETECTED]

    def test_cannot_skip_states(self):
        valid = {
            IncidentStatus.DETECTED: [IncidentStatus.ACKNOWLEDGED, IncidentStatus.INVESTIGATING],
        }
        assert IncidentStatus.RESOLVED not in valid[IncidentStatus.DETECTED]

    def test_closed_is_terminal(self):
        valid = {IncidentStatus.CLOSED: []}
        assert len(valid[IncidentStatus.CLOSED]) == 0


class TestSeverity:
    def test_severity_ordering(self):
        from app.models import Severity
        assert Severity.SEV1 == "sev-1"
        assert Severity.SEV2 == "sev-2"
        assert Severity.SEV3 == "sev-3"
        assert Severity.SEV4 == "sev-4"
