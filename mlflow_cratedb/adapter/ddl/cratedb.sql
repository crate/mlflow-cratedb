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
   PRIMARY KEY ("experiment_id")
);

CREATE TABLE IF NOT EXISTS "inputs" (
   "input_uuid" TEXT NOT NULL,
   "source_type" TEXT NOT NULL,
   "source_id" TEXT NOT NULL,
   "destination_type" TEXT NOT NULL,
   "destination_id" TEXT NOT NULL,
   PRIMARY KEY ("source_type", "source_id", "destination_type", "destination_id")
);

CREATE TABLE IF NOT EXISTS "input_tags" (
   "input_uuid" TEXT NOT NULL,
   "name" TEXT NOT NULL,
   "value" TEXT NOT NULL,
   PRIMARY KEY ("input_uuid", "name")
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
   "status_message" TEXT
);

CREATE TABLE IF NOT EXISTS "model_version_tags" (
   "name" TEXT NOT NULL,
   "version" INTEGER NOT NULL,
   "key" TEXT NOT NULL,
   "value" TEXT
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
   "description" TEXT
);

CREATE TABLE IF NOT EXISTS "registered_model_aliases" (
   "name" TEXT NOT NULL,
   "alias" TEXT NOT NULL,
   "version" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "registered_model_tags" (
   "name" TEXT NOT NULL,
   "key" TEXT NOT NULL,
   "value" TEXT NOT NULL,
   "creation_time" BIGINT,  -- default=get_current_time_millis
   "last_update_time" BIGINT,  -- default=get_current_time_millis
   "description" TEXT
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

CREATE TABLE IF NOT EXISTS "tags" (
   "key" TEXT NOT NULL,
   "value" TEXT,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "run_uuid")
);

CREATE TABLE IF NOT EXISTS "trace_info" (
   "request_id" TEXT NOT NULL,
   "experiment_id" BIGINT,
   "timestamp_ms" BIGINT NOT NULL,
   "execution_time_ms" BIGINT NOT NULL,
   "status" TEXT,
   PRIMARY KEY ("request_id")
);

CREATE TABLE IF NOT EXISTS "trace_tags" (
   "key" TEXT,
   "value" TEXT NOT NULL,
   "request_id" TEXT NOT NULL,
   "trace_info" BIGINT,
   PRIMARY KEY ("request_id", "key")
);

CREATE TABLE IF NOT EXISTS "trace_request_metadata" (
   "key" TEXT,
   "value" TEXT NOT NULL,
   "request_id" TEXT NOT NULL,
   "trace_info" BIGINT,
   PRIMARY KEY ("request_id", "key")
);
