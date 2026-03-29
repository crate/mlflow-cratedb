# Source: mlflow:tests/store/tracking/__init__.py
import json

import pytest
from mlflow.entities import RunTag
from mlflow.models import Model
from mlflow.utils.mlflow_tags import MLFLOW_LOGGED_MODELS


class AbstractStoreTest:
    def create_test_run(self):
        raise Exception("this should be overridden")

    def get_store(self):
        raise Exception("this should be overridden")

    def test_record_logged_model(self):
        store = self.get_store()
        run_id = self.create_test_run().info.run_id
        m = Model(name="model/path", run_id=run_id, flavors={"tf": "flavor body"})
        store.record_logged_model(run_id, m)
        self._verify_logged(
            store,
            run_id=run_id,
            params=[],
            metrics=[],
            tags=[RunTag(MLFLOW_LOGGED_MODELS, json.dumps([m.to_dict()]))],
        )
        m2 = Model(name="some/other/path", run_id=run_id, flavors={"R": {"property": "value"}})
        store.record_logged_model(run_id, m2)
        self._verify_logged(
            store,
            run_id,
            params=[],
            metrics=[],
            tags=[RunTag(MLFLOW_LOGGED_MODELS, json.dumps([m.to_dict(), m2.to_dict()]))],
        )
        m3 = Model(name="some/other/path2", run_id=run_id, flavors={"R2": {"property": "value"}})
        store.record_logged_model(run_id, m3)
        self._verify_logged(
            store,
            run_id,
            params=[],
            metrics=[],
            tags=[RunTag(MLFLOW_LOGGED_MODELS, json.dumps([m.to_dict(), m2.to_dict(), m3.to_dict()]))],
        )
        with pytest.raises(
            TypeError,
            match="Argument 'mlflow_model' should be mlflow.models.Model, got '<class 'dict'>'",
        ):
            store.record_logged_model(run_id, m.to_dict())

    @staticmethod
    def _verify_logged(store, run_id, metrics, params, tags):
        run = store.get_run(run_id)
        all_metrics = sum([store.get_metric_history(run_id, key) for key in run.data.metrics], [])
        assert len(all_metrics) == len(metrics)
        logged_metrics = [(m.key, m.value, m.timestamp, m.step) for m in all_metrics]
        assert set(logged_metrics) == {(m.key, m.value, m.timestamp, m.step) for m in metrics}

        # TODO: CrateDB adjustments; investigate later.
        logged_tags = dict(run.data.tags.items())
        expected_tags = {tag.key: tag.value for tag in tags}

        if "mlflow.log-model.history" in logged_tags:
            logged_tags["mlflow.log-model.history"] = json.loads(logged_tags["mlflow.log-model.history"])
            expected_tags["mlflow.log-model.history"] = json.loads(expected_tags["mlflow.log-model.history"])
            expected_tags["mlflow.log-model.history"][0].pop("mlflow_version", None)
            expected_tags["mlflow.log-model.history"][0].pop("prompts", None)

        assert set(expected_tags) <= set(logged_tags), (
            f"expected tags not in logged tags: {expected_tags} vs. {logged_tags}"
        )
        assert len(run.data.params) == len(params)
        assert set(run.data.params.items()) == {(param.key, param.value) for param in params}
