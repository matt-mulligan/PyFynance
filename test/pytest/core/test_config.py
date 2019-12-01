from core.config import Configuration


class TestConfiguration:

    # ---- Test Fixtures ------------------------------

    # ---- Test Data Objects --------------------------

    # ---- Test Methods ------------------------------

    def test_when_init_then_config_object_returned(self):
        config = Configuration()
        assert isinstance(config, Configuration)
        assert hasattr(config, "paths")
        assert hasattr(config.paths, "repo_path")
        assert hasattr(config.paths, "code_path")
        assert hasattr(config, "version")
