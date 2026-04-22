import json
from unittest import mock

from mlflow.entities import TraceInfo, TraceLocation, TraceState
from mlflow.entities.span import Span, create_mlflow_span
from mlflow.entities.trace_metrics import AggregationType, MetricAggregation, MetricDataPoint, MetricViewType
from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore
from mlflow.tracing.constant import CostKey, SpanAttributeKey
from mlflow.tracing.utils import TraceJSONEncoder
from mlflow.tracking._tracking_service.utils import _use_tracking_uri
from opentelemetry import trace as trace_api
from opentelemetry.sdk.resources import Resource as _OTelResource
from opentelemetry.sdk.trace import ReadableSpan as OTelReadableSpan


def _create_trace(
    store: SqlAlchemyStore,
    trace_id: str,
    experiment_id=0,
    request_time=0,
    execution_duration=0,
    state=TraceState.OK,
    trace_metadata=None,
    tags=None,
    client_request_id=None,
) -> TraceInfo:
    """Helper function to create a test trace in the database."""
    if not store.get_experiment(experiment_id):
        store.create_experiment(store, experiment_id)

    trace_info = TraceInfo(
        trace_id=trace_id,
        trace_location=TraceLocation.from_experiment_id(str(experiment_id)),
        request_time=request_time,
        execution_duration=execution_duration,
        state=state,
        tags=tags or {},
        trace_metadata=trace_metadata or {},
        client_request_id=client_request_id,
    )
    return store.start_trace(trace_info)


# Helper functions for span tests
def create_mock_span_context(trace_id_num=12345, span_id_num=111) -> trace_api.SpanContext:
    """Create a mock span context for testing."""
    context = mock.Mock()
    context.trace_id = trace_id_num
    context.span_id = span_id_num
    context.is_remote = False
    context.trace_flags = trace_api.TraceFlags(1)
    context.trace_state = trace_api.TraceState()
    return context


def create_test_span(
    trace_id,
    name="test_span",
    span_id=111,
    parent_id=None,
    status=trace_api.StatusCode.UNSET,
    status_desc=None,
    start_ns=1000000000,
    end_ns=2000000000,
    span_type="LLM",
    trace_num=12345,
    attributes=None,
) -> Span:
    """
    Create an MLflow span for testing with minimal boilerplate.

    Args:
        trace_id: The trace ID string
        name: Span name
        span_id: Span ID number (default: 111)
        parent_id: Parent span ID number, or None for root span
        status: StatusCode enum value (default: UNSET)
        status_desc: Status description string
        start_ns: Start time in nanoseconds
        end_ns: End time in nanoseconds
        span_type: Span type (default: "LLM")
        trace_num: Trace ID number for context (default: 12345)
        attributes: Attributes dictionary

    Returns:
        MLflow Span object ready for use in tests
    """
    context = create_mock_span_context(trace_num, span_id)
    parent_context = create_mock_span_context(trace_num, parent_id) if parent_id else None

    attributes = attributes or {}
    otel_span = OTelReadableSpan(
        name=name,
        context=context,
        parent=parent_context,
        attributes={
            "mlflow.traceRequestId": json.dumps(trace_id, cls=TraceJSONEncoder),
            "mlflow.spanType": json.dumps(span_type, cls=TraceJSONEncoder),
            **{k: json.dumps(v, cls=TraceJSONEncoder) for k, v in attributes.items()},
        },
        start_time=start_ns,
        end_time=end_ns,
        status=trace_api.Status(status, status_desc),
        resource=_OTelResource.get_empty(),
    )
    return create_mlflow_span(otel_span, trace_id, span_type)


def test_query_trace_metrics_sum(db_uri, reset_database, tracking_store):
    """
    Validate tracing and querying.

    This uses a custom implementation with CrateDB.
    https://github.com/crate/crate/issues/19207
    """

    # Create trace with span.
    experiment_id = 0
    trace_id = "trace1"
    span_id = 111
    _create_trace(tracking_store, trace_id, experiment_id)
    span1 = create_test_span(
        trace_id,
        name="database_query",
        span_id=span_id,
        span_type="FUNCTION",
        attributes={
            SpanAttributeKey.LLM_COST: json.dumps(
                {
                    CostKey.INPUT_COST: 0.01,
                    CostKey.OUTPUT_COST: 0.02,
                    CostKey.TOTAL_COST: 0.03,
                }
            )
        },
    )
    tracking_store.log_spans(str(experiment_id), [span1])

    results = tracking_store.query_trace_metrics(
        experiment_ids=["0"],
        metric_name="total_cost",
        aggregations=[MetricAggregation(AggregationType.SUM)],
        view_type=MetricViewType.SPANS,
        max_results=20,
    )
    assert results == [MetricDataPoint(metric_name="total_cost", dimensions={}, values={"SUM": 0.03})]


def test_query_trace_metrics_percentile(db_uri):
    """
    Validate tracing and querying.

    This uses a custom implementation with CrateDB.
    https://github.com/crate/crate/issues/19207
    """
    with _use_tracking_uri(db_uri):
        from mlflow.server.handlers import _get_tracking_store

        results = _get_tracking_store().query_trace_metrics(
            experiment_ids=["0"],
            metric_name="total_tokens",
            aggregations=[MetricAggregation(AggregationType.PERCENTILE, 50)],
            view_type=MetricViewType.TRACES,
            max_results=20,
        )
        assert results == []
