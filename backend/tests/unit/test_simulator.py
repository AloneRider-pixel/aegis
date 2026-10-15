"""Tests for the failure simulator."""
from datetime import datetime, timedelta
from app.simulator.scenarios import list_scenarios, get_scenario, trigger_scenario
from app.simulator.telemetry import telemetry_store


class TestScenarios:
    def test_list_scenarios(self):
        scenarios = list_scenarios()
        assert len(scenarios) >= 10
        for s in scenarios:
            assert "id" in s
            assert "name" in s
            assert "severity" in s

    def test_get_scenario(self):
        s = get_scenario("db-connection-exhaustion")
        assert s is not None
        assert s["id"] == "db-connection-exhaustion"
        assert "symptoms" in s

    def test_get_invalid_scenario(self):
        s = get_scenario("nonexistent")
        assert s is None

    def test_trigger_scenario(self):
        result = trigger_scenario("db-connection-exhaustion")
        assert "scenario" in result
        assert "incident" in result
        assert result["telemetry_generated"] is True
        assert result["incident"]["severity"] == "sev-2"

    def test_trigger_invalid_scenario(self):
        result = trigger_scenario("nonexistent")
        assert "error" in result


class TestTelemetryStore:
    def test_add_and_get_metrics(self):
        telemetry_store.reset()
        telemetry_store.add_metric("test-service", "cpu", 50.0)
        metrics = telemetry_store.get_metrics("test-service")
        assert "cpu" in metrics
        assert len(metrics["cpu"]) == 1

    def test_add_and_get_logs(self):
        telemetry_store.reset()
        telemetry_store.add_log("test-service", "ERROR", "Something failed")
        logs = telemetry_store.get_logs(service_name="test-service")
        assert len(logs) == 1
        assert logs[0]["message"] == "Something failed"

    def test_log_filtering(self):
        telemetry_store.reset()
        telemetry_store.add_log("svc-a", "ERROR", "Error in A")
        telemetry_store.add_log("svc-b", "ERROR", "Error in B")
        logs = telemetry_store.get_logs(service_name="svc-a")
        assert len(logs) == 1
        assert logs[0]["service"] == "svc-a"

    def test_reset(self):
        telemetry_store.add_metric("svc", "cpu", 50)
        telemetry_store.reset()
        metrics = telemetry_store.get_metrics("svc")
        assert len(metrics) == 0
    
    def test_metrics_keep_recent_samples_when_stale_sample_was_appended_last(self):
        telemetry_store.reset()
        now = datetime.utcnow()
        telemetry_store.add_metric("svc", "cpu", 55.0, timestamp=now - timedelta(minutes=1))
        telemetry_store.add_metric("svc", "cpu", 10.0, timestamp=now - timedelta(minutes=10))

        metrics = telemetry_store.get_metrics("svc", time_range_minutes=5)

        assert [sample["value"] for sample in metrics["cpu"]] == [55.0]

    def test_logs_keep_recent_entries_when_stale_entry_was_appended_last(self):
        telemetry_store.reset()
        now = datetime.utcnow()
        telemetry_store.add_log("svc", "INFO", "recent entry", timestamp=now - timedelta(minutes=1))
        telemetry_store.add_log("svc", "INFO", "stale entry", timestamp=now - timedelta(minutes=10))

        logs = telemetry_store.get_logs(service_name="svc", time_range_minutes=5)

        assert [entry["message"] for entry in logs] == ["recent entry"]

