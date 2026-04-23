import pytest
from mlflow import MlflowException
from mlflow.entities import Workspace


def test_workspace_basic(workspace_store, tracking_canvas):
    """Test basic CRUD operations on the workspace SqlAlchemy store."""

    workspace_name = "zwackelmann"

    # Create and retrieve.
    workspace = workspace_store.create_workspace(Workspace(name=workspace_name))
    workspace = workspace_store.get_workspace(workspace_name=workspace.name)
    assert workspace.name == workspace_name

    # Search.
    results = list(workspace_store.list_workspaces())
    assert len(results) == 1, f"Unable to find expected workspace, found {len(results)} results"

    # Update.
    workspace_store.update_workspace(Workspace(name=workspace_name, description="Räuberhöhle"))
    workspace = workspace_store.get_workspace(workspace_name=workspace.name)
    assert workspace.description == "Räuberhöhle"

    # Delete.
    workspace_store.delete_workspace(workspace_name=workspace_name)


def test_workspace_default(workspace_store, tracking_canvas):
    """By default, the default workspace does not exist."""
    with pytest.raises(MlflowException, match="Workspace 'default' not found"):
        workspace_store.get_default_workspace()


def test_workspace_resolve_artifact_root(workspace_store, tracking_canvas):
    """Test `resolve_artifact_root` method on the workspace SqlAlchemy store."""
    artifact_root, is_default = workspace_store.resolve_artifact_root(
        default_artifact_root="acme", workspace_name="zwackelmann"
    )
    assert artifact_root == "acme"
    assert is_default is True
