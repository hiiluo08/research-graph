from uuid import uuid4


def new_run_id() -> str:
    """ Create a new run ID with prefix `run_` for easy filtering. """
    return f"run_{uuid4().hex[:12]}"