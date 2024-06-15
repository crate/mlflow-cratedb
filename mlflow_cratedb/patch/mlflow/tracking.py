import math
from functools import partial


def patch_tracking():
    """
    Patch the experiment tracking subsystem of MLflow.
    """
    patch_create_default_experiment()
    patch_get_orderby_clauses()
    patch_search_runs()


def patch_create_default_experiment():
    """
    The `_create_default_experiment` function runs an SQL query sidetracking
    the SQLAlchemy ORM. Thus, it needs to be explicitly patched to invoke
    a corresponding `REFRESH TABLE` statement afterwards.
    """
    import sqlalchemy as sa
    from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore

    create_default_experiment_dist = SqlAlchemyStore._create_default_experiment

    def _create_default_experiment(self, session):
        from mlflow.store.tracking.dbmodels.models import SqlExperiment

        outcome = create_default_experiment_dist(self, session)
        session.execute(sa.text(f"REFRESH TABLE {SqlExperiment.__tablename__}"))
        return outcome

    SqlAlchemyStore._create_default_experiment = _create_default_experiment


def patch_get_orderby_clauses():
    """
    MLflow's `_get_orderby_clauses` adds an `sql.case(...)` clause, which CrateDB does not understand.

    https://github.com/crate/mlflow-cratedb/issues/8
    """
    import mlflow.store.tracking.sqlalchemy_store as sqlalchemy_store

    _get_orderby_clauses_dist = sqlalchemy_store._get_orderby_clauses

    def filter_case_clauses(items):
        new_list = []
        for item in items:
            label = None
            if isinstance(item, str):
                label = item
            elif hasattr(item, "name"):
                label = item.name
            if label is None or not label.startswith("clause_"):
                new_list.append(item)
        return new_list

    def _get_orderby_clauses(order_by_list, session):
        cases_orderby, parsed_orderby, sorting_joins = _get_orderby_clauses_dist(order_by_list, session)
        cases_orderby = filter_case_clauses(cases_orderby)
        parsed_orderby = filter_case_clauses(parsed_orderby)
        return cases_orderby, parsed_orderby, sorting_joins

    sqlalchemy_store._get_orderby_clauses = _get_orderby_clauses


def patch_search_runs():
    """
    Patch MLflow's `_search_runs` function to invoke `fix_sort_order` afterwards,
    compensating the other patch to `_get_orderby_clauses`.
    """
    from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore

    search_runs_dist = SqlAlchemyStore._search_runs

    def _search_runs(self, experiment_ids, filter_string, run_view_type, max_results, order_by, page_token):
        runs_with_inputs, next_page_token = search_runs_dist(
            self, experiment_ids, filter_string, run_view_type, max_results, order_by, page_token
        )
        runs_with_inputs = fix_sort_order(order_by, runs_with_inputs)
        return runs_with_inputs, next_page_token

    SqlAlchemyStore._search_runs = _search_runs


def fix_sort_order(order_by, runs_with_inputs):
    """
    Attempts to fix the sort order of returned tracking results, trying to
    compensate the patch to MLflow's `_get_orderby_clauses`.

    Covered by test cases `test_order_by_attributes` and `test_order_by_metric_tag_param`.
    """
    import functools

    from mlflow.utils.search_utils import SearchUtils

    if order_by is None:
        return runs_with_inputs

    def attribute_getter(key, item):
        return getattr(item.info, key)

    def metrics_getter(key, item):
        return item.data.metrics.get(key)

    def tags_getter(key, item):
        return item.data.tags.get(key)

    def parameters_getter(key, item):
        return item.data.params.get(key)

    def isnan(value):
        return value is None or (isinstance(value, float) and math.isnan(value))

    def compare_special(getter, i1, i2):
        """
        Comparison function which can accept None or NaN values.

        Otherwise, Python would raise::

            TypeError: '<' not supported between instances of 'NoneType' and 'int'
        """
        #
        i1 = getter(i1)
        i2 = getter(i2)
        if isnan(i1):
            return 1
        if isnan(i2):
            return -1
        i1 = str(i1).lower()
        i2 = str(i2).lower()
        return i1 < i2

    attribute_order_count = 0
    for order_by_clause in order_by:
        # Special case: When sorting using multiple attributes, something goes south.
        # So, limit (proper) sorting to the use of a single attribute only.
        if attribute_order_count >= 1:
            continue

        (key_type, key, ascending) = SearchUtils.parse_order_by_for_search_runs(order_by_clause)
        key_translated = SearchUtils.translate_key_alias(key)

        if key_type == "attribute":
            getter = partial(attribute_getter, key_translated)
            attribute_order_count += 1
        elif key_type == "metric":
            getter = partial(metrics_getter, key_translated)
        elif key_type == "tag":
            getter = partial(tags_getter, key_translated)
        elif key_type == "parameter":
            getter = partial(parameters_getter, key_translated)
        else:
            raise NotImplementedError(f"Need to implement getter for key_type={key_type}. clause={order_by_clause}")

        runs_with_inputs = sorted(runs_with_inputs, key=functools.cmp_to_key(partial(compare_special, getter)))

    return runs_with_inputs
