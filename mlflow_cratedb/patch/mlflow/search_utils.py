def patch_search_utils():
    """
    Patch MLflow's `SearchUtils` to return a comparison function for CrateDB.
    """
    from mlflow.utils.search_utils import SearchUtils

    get_sql_comparison_func_dist = SearchUtils.get_sql_comparison_func

    def get_sql_comparison_func(comparator, dialect):
        try:
            return get_sql_comparison_func_dist(comparator, dialect)
        except KeyError:

            def comparison_func(column, value):
                if comparator == "LIKE":
                    return column.like(value)
                elif comparator == "ILIKE":  # noqa: RET505
                    return column.ilike(value)
                elif comparator == "IN":
                    return column.in_(value)
                elif comparator == "NOT IN":
                    return ~column.in_(value)
                return SearchUtils.get_comparison_func(comparator)(column, value)

            return comparison_func

    SearchUtils.get_sql_comparison_func = get_sql_comparison_func
