from core.config import Configuration

def test_when_init_then_config_object_returned():
    config = Configuration()
    assert hasattr(config, "paths")
    assert hasattr(config.paths, "repo_path")
    assert hasattr(config.paths, "code_path")
    assert hasattr(config, "version")
