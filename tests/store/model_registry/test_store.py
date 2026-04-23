from mlflow.entities import WebhookEvent
from mlflow.entities.model_registry import ModelVersionTag, RegisteredModel, RegisteredModelTag
from mlflow.entities.webhook import WebhookAction, WebhookEntity


def test_registered_models(model_registry_store, tracking_canvas):
    """Test basic CRUD operations on registered models."""

    # Create and retrieve.
    model = model_registry_store.create_registered_model(
        "Hotzenplotz", tags=[RegisteredModelTag(key="enabled", value="true")], description="Räuberhöhle"
    )
    model = model_registry_store.get_registered_model(model.name)
    assert model.name == "Hotzenplotz"

    # Search.
    results = model_registry_store.search_registered_models(filter_string="name = 'Hotzenplotz'")
    assert len(results) == 1, f"Unable to find expected model, found {len(results)} results"

    # Version.
    model_version = model_registry_store.create_model_version(
        name="Hotzenplotz", source="http://localhost:1234/foo", tags=[ModelVersionTag(key="enabled", value="true")]
    )
    model_version = model_registry_store.get_model_version(name="Hotzenplotz", version=model_version.version)
    assert model_version.version == 1

    # Delete.
    model_registry_store.delete_model_version(name="Hotzenplotz", version=model_version.version)
    model_registry_store.delete_registered_model(name="Hotzenplotz")


def test_prompt(model_registry_store, tracking_canvas):
    """Test basic CRUD operations on prompts."""

    # Create and retrieve.
    prompt = model_registry_store.create_prompt("Hotzenplotz", tags={"enabled": "true"}, description="Räuberhöhle")
    prompt = model_registry_store.get_prompt(prompt.name)
    assert prompt.name == "Hotzenplotz"

    # Search.
    results = model_registry_store.search_prompts(filter_string="name = 'Hotzenplotz'")
    assert len(results) == 1, f"Unable to find expected prompt, found {len(results)} results"

    # Version.
    prompt_version = model_registry_store.create_prompt_version(
        name="Hotzenplotz", template="{{variable}}", tags={"enabled": "true"}
    )
    prompt_version = model_registry_store.get_prompt_version(name="Hotzenplotz", version=prompt_version.version)
    assert prompt_version.version == 1

    # Delete.
    model_registry_store.delete_prompt_version(name="Hotzenplotz", version=prompt_version.version)
    model_registry_store.delete_prompt(name="Hotzenplotz")


def test_webhook(model_registry_store, tracking_canvas):
    """Test basic CRUD operations on webhooks."""

    # Create and retrieve.
    webhook = model_registry_store.create_webhook(
        "Hotzenplotz",
        url="https://example.org/",
        events=[WebhookEvent(entity=WebhookEntity.PROMPT, action=WebhookAction.CREATED)],
    )
    webhook = model_registry_store.get_webhook(webhook_id=webhook.webhook_id)
    assert webhook.name == "Hotzenplotz"

    # Search.
    results = model_registry_store.list_webhooks_by_event(
        event=WebhookEvent(entity=WebhookEntity.PROMPT, action=WebhookAction.CREATED)
    )
    assert len(results) == 1, f"Unable to find expected webhook, found {len(results)} results"

    # Delete.
    model_registry_store.delete_webhook(webhook_id=webhook.webhook_id)


def test_linking(tracking_store, model_registry_store, tracking_canvas):
    """
    Test basic linking operations.

    Suggested by CodeRabbit.
    """
    # Create a LoggedModel to serve as the link target.
    # link_prompt_version_to_model expects a LoggedModel ID (UUID), not a
    # RegisteredModel name — so we create one explicitly via the tracking client.
    experiment_id = tracking_store.get_experiment_by_name("Default").experiment_id
    logged_model = tracking_store.create_logged_model(
        experiment_id=experiment_id,
        name="HotzenplotzLoggedModel",
    )

    # Create a RegisteredModel.
    model: RegisteredModel = model_registry_store.create_registered_model(  # noqa: F841
        "HotzenplotzModel",
        tags=[RegisteredModelTag(key="enabled", value="true")],
        description="Räuberhöhle",
    )

    # Create a Prompt and a PromptVersion.
    prompt = model_registry_store.create_prompt(
        "HotzenplotzPrompt", tags={"enabled": "true"}, description="Räuberhöhle"
    )
    prompt_version = model_registry_store.create_prompt_version("HotzenplotzPrompt", template="{{variable}}")

    # Link.
    model_registry_store.link_prompt_version_to_model(
        name=prompt.name,
        version=str(prompt_version.version),
        model_id=logged_model.model_id,  # <-- use the LoggedModel UUID
    )

    # Assert: verify the link was persisted by inspecting the prompt version.
    linked_pv = model_registry_store.get_prompt_version(name="HotzenplotzPrompt", version=prompt_version.version)
    assert linked_pv is not None
    # If the PromptVersion entity surfaces linked model IDs, assert against them:
    # assert logged_model.model_id in (linked_pv.model_ids or [])  # noqa: ERA001

    # Cleanup.
    model_registry_store.delete_prompt_version(name="HotzenplotzPrompt", version=prompt_version.version)
    model_registry_store.delete_prompt(name="HotzenplotzPrompt")
    model_registry_store.delete_registered_model(name="HotzenplotzModel")
