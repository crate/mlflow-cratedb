-- Synchronize with MLflow
-- `mlflow/store/tracking/dbmodels/models.py`
-- `tests/resources/db/latest_schema.sql`
-- `tests/db/schemas/postgresql.sql`

CREATE TABLE IF NOT EXISTS "datasets" (
   "dataset_uuid" TEXT NOT NULL,
   "experiment_id" BIGINT NOT NULL,
   "name" TEXT NOT NULL,
   "digest" TEXT NOT NULL,
   "dataset_source_type" TEXT NOT NULL,
   "dataset_source" TEXT NOT NULL,
   "dataset_schema" TEXT,
   "dataset_profile" TEXT,
   PRIMARY KEY ("experiment_id", "name", "digest")
);

CREATE TABLE IF NOT EXISTS "entity_associations" (
	association_id VARCHAR(36) NOT NULL,
	source_type VARCHAR(36) NOT NULL,
	source_id VARCHAR(36) NOT NULL,
	destination_type VARCHAR(36) NOT NULL,
	destination_id VARCHAR(36) NOT NULL,
	created_time BIGINT,
	PRIMARY KEY (source_type, source_id, destination_type, destination_id)
);

CREATE TABLE IF NOT EXISTS "evaluation_datasets" (
	dataset_id VARCHAR(36) NOT NULL,
	name VARCHAR(255) NOT NULL,
	schema TEXT,
	profile TEXT,
	digest VARCHAR(64),
	created_time BIGINT,
	last_update_time BIGINT,
	created_by VARCHAR(255),
	last_updated_by VARCHAR(255),
    workspace VARCHAR(63) DEFAULT 'default' NOT NULL,
	PRIMARY KEY (dataset_id)
);

CREATE TABLE IF NOT EXISTS "evaluation_dataset_records" (
	dataset_record_id VARCHAR(36) NOT NULL,
	dataset_id VARCHAR(36) NOT NULL,
	inputs OBJECT(DYNAMIC) NOT NULL,
	expectations OBJECT(DYNAMIC),
	tags OBJECT(DYNAMIC),
	source OBJECT(DYNAMIC),
	source_id VARCHAR(36),
	source_type VARCHAR(255),
	created_time BIGINT,
	last_update_time BIGINT,
	created_by VARCHAR(255),
	last_updated_by VARCHAR(255),
	input_hash VARCHAR(64) NOT NULL,
	outputs OBJECT(DYNAMIC),
    PRIMARY KEY ("dataset_record_id")
);

CREATE TABLE IF NOT EXISTS "evaluation_dataset_tags" (
	dataset_id VARCHAR(36) NOT NULL,
	key VARCHAR(255) NOT NULL,
	value VARCHAR(5000),
    PRIMARY KEY ("dataset_id", "key")
);

CREATE TABLE IF NOT EXISTS "experiment_tags" (
   "key" TEXT NOT NULL,
   "value" TEXT,
   "experiment_id" BIGINT NOT NULL,
   PRIMARY KEY ("key", "experiment_id")
);

CREATE TABLE IF NOT EXISTS "experiments" (
   "experiment_id" BIGINT NOT NULL,  -- default=autoincrement
   "name" TEXT NOT NULL,
   "artifact_location" TEXT,
   "lifecycle_stage" TEXT,
   "creation_time" BIGINT,  -- default=get_current_time_millis
   "last_update_time" BIGINT,  -- default=get_current_time_millis
   "workspace" VARCHAR(63) DEFAULT 'default' NOT NULL,
   PRIMARY KEY ("experiment_id")
);

CREATE TABLE IF NOT EXISTS "inputs" (
   "input_uuid" TEXT NOT NULL,
   "source_type" TEXT NOT NULL,
   "source_id" TEXT NOT NULL,
   "destination_type" TEXT NOT NULL,
   "destination_id" TEXT NOT NULL,
   "step" BIGINT DEFAULT '0' NOT NULL,
   PRIMARY KEY ("source_type", "source_id", "destination_type", "destination_id")
);

CREATE TABLE IF NOT EXISTS "input_tags" (
   "input_uuid" TEXT NOT NULL,
   "name" TEXT NOT NULL,
   "value" TEXT NOT NULL,
   PRIMARY KEY ("input_uuid", "name")
);

CREATE TABLE IF NOT EXISTS "jobs" (
	id VARCHAR(36) NOT NULL,
	creation_time BIGINT NOT NULL,
	job_name VARCHAR(500) NOT NULL,
	params TEXT NOT NULL,
	timeout DOUBLE PRECISION,
	status INTEGER NOT NULL,
	result TEXT,
	retry_count INTEGER NOT NULL,
	last_update_time BIGINT NOT NULL,
	workspace VARCHAR(63) DEFAULT 'default' NOT NULL,
	status_details OBJECT(DYNAMIC),
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "latest_metrics" (
   "key" TEXT NOT NULL,
   "value" DOUBLE NOT NULL,
   "timestamp" BIGINT NOT NULL,
   "step" BIGINT NOT NULL,
   "is_nan" BOOLEAN NOT NULL,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "run_uuid")
);

CREATE TABLE IF NOT EXISTS "logged_models" (
	model_id VARCHAR(36) NOT NULL,
	experiment_id BIGINT NOT NULL,
	name VARCHAR(500) NOT NULL,
	artifact_location VARCHAR(1000) NOT NULL,
	creation_timestamp_ms BIGINT NOT NULL,
	last_updated_timestamp_ms BIGINT NOT NULL,
	status INTEGER NOT NULL,
	lifecycle_stage VARCHAR(32),
	model_type VARCHAR(500),
	source_run_id VARCHAR(32),
	status_message VARCHAR(1000),
    PRIMARY KEY ("model_id")
);

CREATE TABLE IF NOT EXISTS "logged_model_metrics" (
	model_id VARCHAR(36) NOT NULL,
	metric_name VARCHAR(500) NOT NULL,
	metric_timestamp_ms BIGINT NOT NULL,
	metric_step BIGINT NOT NULL,
	metric_value FLOAT,
	experiment_id BIGINT NOT NULL,
	run_id VARCHAR(32) NOT NULL,
	dataset_uuid VARCHAR(36),
	dataset_name VARCHAR(500),
	dataset_digest VARCHAR(36),
    PRIMARY KEY ("model_id", "metric_name", "metric_timestamp_ms", "metric_step", "run_id")
);

CREATE TABLE IF NOT EXISTS "logged_model_params" (
	model_id VARCHAR(36) NOT NULL,
	experiment_id BIGINT NOT NULL,
	param_key VARCHAR(255) NOT NULL,
	param_value TEXT NOT NULL,
    PRIMARY KEY ("model_id", "param_key")
);


CREATE TABLE IF NOT EXISTS "logged_model_tags" (
	model_id VARCHAR(36) NOT NULL,
	experiment_id BIGINT NOT NULL,
	tag_key VARCHAR(255) NOT NULL,
	tag_value TEXT NOT NULL,
    PRIMARY KEY ("model_id", "tag_key")
);

CREATE TABLE IF NOT EXISTS "online_scoring_configs" (
	online_scoring_config_id VARCHAR(36) NOT NULL,
	scorer_id VARCHAR(36) NOT NULL,
	sample_rate DOUBLE PRECISION NOT NULL,
	experiment_id BIGINT NOT NULL,
	filter_string TEXT,
	PRIMARY KEY (online_scoring_config_id)
);

CREATE TABLE IF NOT EXISTS "metrics" (
   "key" TEXT NOT NULL,
   "value" DOUBLE NOT NULL,
   "timestamp" BIGINT NOT NULL,
   "step" BIGINT NOT NULL,
   "is_nan" BOOLEAN NOT NULL,
   "run_uuid" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "model_versions" (
   "name" TEXT NOT NULL,
   "version" INTEGER NOT NULL,
   "creation_time" BIGINT,  -- default=get_current_time_millis
   "last_updated_time" BIGINT,  -- default=get_current_time_millis
   "description" TEXT,
   "user_id" TEXT,
   "current_stage" TEXT,
   "source" TEXT,
   "storage_location" TEXT,
   "run_id" TEXT,
   "run_link" TEXT,
   "status" TEXT,
   "status_message" TEXT,
   "workspace" VARCHAR(63) DEFAULT 'default' NOT NULL,
   PRIMARY KEY ("workspace", "name", "version")
);

CREATE TABLE IF NOT EXISTS "model_version_tags" (
   "name" TEXT NOT NULL,
   "version" INTEGER NOT NULL,
   "key" TEXT NOT NULL,
   "value" TEXT,
   "workspace" VARCHAR(63) DEFAULT 'default' NOT NULL,
   PRIMARY KEY ("workspace", "key", "name", "version")
);

CREATE TABLE IF NOT EXISTS "params" (
   "key" TEXT NOT NULL,
   "value" TEXT NOT NULL,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "run_uuid")
);

CREATE TABLE IF NOT EXISTS "registered_models" (
   "name" TEXT NOT NULL,
   "key" TEXT DEFAULT GEN_RANDOM_TEXT_UUID() NOT NULL,
   "value" TEXT,
   "creation_time" BIGINT,
   "last_updated_time" BIGINT,
   "description" TEXT,
   "workspace" VARCHAR(63) DEFAULT 'default' NOT NULL,
   PRIMARY KEY ("workspace", "name")
);

CREATE TABLE IF NOT EXISTS "registered_model_aliases" (
   "name" TEXT NOT NULL,
   "alias" TEXT NOT NULL,
   "version" TEXT NOT NULL,
   "workspace" VARCHAR(63) DEFAULT 'default' NOT NULL,
   PRIMARY KEY ("workspace", "name", "alias")
);

CREATE TABLE IF NOT EXISTS "registered_model_tags" (
   "name" TEXT NOT NULL,
   "key" TEXT NOT NULL,
   "value" TEXT NOT NULL,
   "creation_time" BIGINT,  -- default=get_current_time_millis
   "last_update_time" BIGINT,  -- default=get_current_time_millis
   "description" TEXT,
   "workspace" VARCHAR(63) DEFAULT 'default' NOT NULL,
   PRIMARY KEY ("workspace", "key", "name")
);

CREATE TABLE IF NOT EXISTS "runs" (
   "run_uuid" TEXT NOT NULL,
   "name" TEXT,
   "source_type" TEXT,
   "source_name" TEXT,
   "entry_point_name" TEXT,
   "user_id" TEXT,
   "status" TEXT,
   "start_time" BIGINT,
   "end_time" BIGINT,
   "deleted_time" BIGINT,
   "source_version" TEXT,
   "lifecycle_stage" TEXT,
   "artifact_uri" TEXT,
   "experiment_id" BIGINT,
   PRIMARY KEY ("run_uuid")
);

CREATE TABLE IF NOT EXISTS "scorers" (
	experiment_id BIGINT NOT NULL,
	scorer_name VARCHAR(256) NOT NULL,
	scorer_id VARCHAR(36) NOT NULL,
	PRIMARY KEY (scorer_id)
);

CREATE TABLE IF NOT EXISTS "scorer_versions" (
	scorer_id VARCHAR(36) NOT NULL,
	scorer_version INTEGER NOT NULL,
	serialized_scorer TEXT NOT NULL,
	creation_time BIGINT,
	PRIMARY KEY (scorer_id, scorer_version)
);

CREATE TABLE IF NOT EXISTS "spans" (
	trace_id VARCHAR(50) NOT NULL,
	experiment_id BIGINT NOT NULL,
	span_id VARCHAR(50) NOT NULL,
	parent_span_id VARCHAR(50),
	name TEXT,
	type VARCHAR(500),
	status VARCHAR(50) NOT NULL,
	start_time_unix_nano BIGINT NOT NULL,
	end_time_unix_nano BIGINT,
	duration_ns BIGINT GENERATED ALWAYS AS ((end_time_unix_nano - start_time_unix_nano)),
	content TEXT NOT NULL,
	dimension_attributes OBJECT(DYNAMIC),
	PRIMARY KEY (trace_id, span_id)
);

CREATE TABLE IF NOT EXISTS "span_metrics" (
	trace_id VARCHAR(50) NOT NULL,
	span_id VARCHAR(50) NOT NULL,
	key VARCHAR(250) NOT NULL,
	value DOUBLE PRECISION,
	PRIMARY KEY (trace_id, span_id, key)
);

CREATE TABLE IF NOT EXISTS "tags" (
   "key" TEXT NOT NULL,
   "value" TEXT,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "run_uuid")
);

CREATE TABLE IF NOT EXISTS "trace_info" (
	request_id VARCHAR(50) NOT NULL,
	experiment_id BIGINT NOT NULL,
	timestamp_ms BIGINT NOT NULL,
	execution_time_ms BIGINT,
	status VARCHAR(50) NOT NULL,
	client_request_id VARCHAR(50),
	request_preview VARCHAR(1000),
	response_preview VARCHAR(1000),
	PRIMARY KEY (request_id)
);

CREATE TABLE IF NOT EXISTS "trace_metrics" (
	request_id VARCHAR(50) NOT NULL,
	"key" VARCHAR(250) NOT NULL,
	"value" DOUBLE PRECISION,
	PRIMARY KEY (request_id, "key")
);

CREATE TABLE IF NOT EXISTS "trace_tags" (
   "key" TEXT,
   "value" TEXT NOT NULL,
   "request_id" TEXT NOT NULL,
   PRIMARY KEY ("key", "request_id")
);

CREATE TABLE IF NOT EXISTS "trace_request_metadata" (
   "key" TEXT,
   "value" TEXT NOT NULL,
   "request_id" TEXT NOT NULL,
   PRIMARY KEY ("key", "request_id")
);

CREATE TABLE IF NOT EXISTS "webhooks" (
	webhook_id VARCHAR(256) NOT NULL,
	name VARCHAR(256) NOT NULL,
	description VARCHAR(1000),
	url VARCHAR(500) NOT NULL,
	status VARCHAR(20) DEFAULT 'ACTIVE' NOT NULL,
	secret VARCHAR(1000),
	creation_timestamp BIGINT,
	last_updated_timestamp BIGINT,
	deleted_timestamp BIGINT,
    workspace VARCHAR(63) DEFAULT 'default' NOT NULL,
    PRIMARY KEY ("webhook_id")
);

CREATE TABLE IF NOT EXISTS "webhook_events" (
	webhook_id VARCHAR(256) NOT NULL,
	entity VARCHAR(50) NOT NULL,
	action VARCHAR(50) NOT NULL,
    PRIMARY KEY ("webhook_id", "entity", "action")
);

CREATE TABLE IF NOT EXISTS "workspaces" (
	name VARCHAR(63) NOT NULL,
	description TEXT,
	default_artifact_root TEXT,
	PRIMARY KEY (name)
);
