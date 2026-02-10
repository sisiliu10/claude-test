import pytest

from social.models import Platform
from social.platforms import PLATFORMS, get_platform_config, list_platforms


def test_all_platforms_defined():
    for p in Platform:
        assert p in PLATFORMS


def test_max_length_positive():
    for config in PLATFORMS.values():
        assert config.max_length > 0


def test_twitter_constraints():
    config = get_platform_config(Platform.TWITTER)
    assert config.max_length == 280
    assert config.hashtag_style == "inline"
    assert config.name == "Twitter / X"


def test_instagram_constraints():
    config = get_platform_config(Platform.INSTAGRAM)
    assert config.max_length == 2200
    assert config.hashtag_style == "footer"


def test_linkedin_constraints():
    config = get_platform_config(Platform.LINKEDIN)
    assert config.max_length == 3000
    assert config.tone == "professional, insightful, thought-leadership"


def test_list_platforms_returns_all():
    result = list_platforms()
    assert len(result) == 3


def test_platform_config_is_frozen():
    config = get_platform_config(Platform.TWITTER)
    with pytest.raises(AttributeError):
        config.max_length = 500
