CREATE TABLE IF NOT EXISTS "{schema_name}"."datasets" (
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

CREATE TABLE IF NOT EXISTS "{schema_name}"."experiment_tags" (
   "key" TEXT NOT NULL,
   "value" TEXT,
   "experiment_id" BIGINT NOT NULL,
   PRIMARY KEY ("key", "experiment_id")
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."experiments" (
   "experiment_id" BIGINT NOT NULL,  -- default=autoincrement
   "name" TEXT NOT NULL,
   "artifact_location" TEXT,
   "lifecycle_stage" TEXT,
   "creation_time" BIGINT,  -- default=get_current_time_millis
   "last_update_time" BIGINT,  -- default=get_current_time_millis
   PRIMARY KEY ("experiment_id")
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."inputs" (
   "input_uuid" TEXT NOT NULL,
   "source_type" TEXT NOT NULL,
   "source_id" TEXT NOT NULL,
   "destination_type" TEXT NOT NULL,
   "destination_id" TEXT NOT NULL,
   PRIMARY KEY ("source_type", "source_id", "destination_type", "destination_id")
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."input_tags" (
   "input_uuid" TEXT NOT NULL,
   "name" TEXT NOT NULL,
   "value" TEXT NOT NULL,
   PRIMARY KEY ("input_uuid", "name")
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."latest_metrics" (
   "key" TEXT NOT NULL,
   "value" REAL NOT NULL,
   "timestamp" BIGINT NOT NULL,
   "step" BIGINT NOT NULL,
   "is_nan" BOOLEAN NOT NULL,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "run_uuid")
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."metrics" (
   "key" TEXT NOT NULL,
   "value" REAL NOT NULL,
   "timestamp" BIGINT NOT NULL,
   "step" BIGINT NOT NULL,
   "is_nan" BOOLEAN NOT NULL,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "timestamp", "step", "run_uuid", "is_nan")
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."model_versions" (
   "name" TEXT NOT NULL,
   "version" INTEGER NOT NULL,
   "creation_time" BIGINT,  -- default=get_current_time_millis
   "last_update_time" BIGINT,  -- default=get_current_time_millis
   "description" TEXT,
   "user_id" TEXT,
   "current_stage" TEXT,
   "source" TEXT,
   "run_id" TEXT,
   "run_link" TEXT,
   "status" TEXT,
   "status_message" TEXT
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."model_version_tags" (
   "name" TEXT NOT NULL,
   "version" INTEGER NOT NULL,
   "key" TEXT NOT NULL,
   "value" TEXT
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."params" (
   "key" TEXT NOT NULL,
   "value" TEXT NOT NULL,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "run_uuid")
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."registered_models" (
   "name" TEXT NOT NULL,
   "key" TEXT NOT NULL,
   "value" TEXT
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."registered_model_aliases" (
   "name" TEXT NOT NULL,
   "alias" TEXT NOT NULL,
   "version" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."registered_model_tags" (
   "name" TEXT NOT NULL,
   "creation_time" BIGINT,  -- default=get_current_time_millis
   "last_update_time" BIGINT,  -- default=get_current_time_millis
   "description" TEXT
);

CREATE TABLE IF NOT EXISTS "{schema_name}"."runs" (
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

CREATE TABLE IF NOT EXISTS "{schema_name}"."tags" (
   "key" TEXT NOT NULL,
   "value" TEXT,
   "run_uuid" TEXT NOT NULL,
   PRIMARY KEY ("key", "run_uuid")
);
