import pytest
from unittest.mock import patch, MagicMock
from src.sources.github_trending import GitHubTrendingSource

SAMPLE_HTML = """
<html><body>
<article class="Box-row">
  <h2><a href="/owner/repo-one">owner / repo-one</a></h2>
  <p>A great Python project</p>
  <span itemprop="programmingLanguage">Python</span>
  <a href="/owner/repo-one/stargazers">1,234</a>
</article>
<article class="Box-row">
  <h2><a href="/owner/repo-two">owner / repo-two</a></h2>
  <p>Another project</p>
  <span itemprop="programmingLanguage">Go</span>
  <a href="/owner/repo-two/stargazers">567</a>
</article>
</body></html>
"""


def _mock_response(html: str, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.text = html
    return resp


def test_fetch_returns_repos():
    source = GitHubTrendingSource()
    with patch("src.sources.github_trending.requests.get", return_value=_mock_response(SAMPLE_HTML)):
        records = source.fetch()
    assert len(records) == 2
    assert records[0]["rank"] == 1
    assert "repo-one" in records[0]["repo"]
    assert records[0]["stars"] == "1,234"
    assert records[0]["language"] == "Python"


def test_fetch_respects_limit():
    source = GitHubTrendingSource(limit=1)
    with patch("src.sources.github_trending.requests.get", return_value=_mock_response(SAMPLE_HTML)):
        records = source.fetch()
    assert len(records) == 1


def test_fetch_raises_on_non_200():
    source = GitHubTrendingSource()
    with patch("src.sources.github_trending.requests.get", return_value=_mock_response("", 403)):
        with pytest.raises(RuntimeError, match="403"):
            source.fetch()


def test_fetch_returns_empty_list_when_no_articles():
    source = GitHubTrendingSource()
    with patch("src.sources.github_trending.requests.get", return_value=_mock_response("<html></html>")):
        records = source.fetch()
    assert records == []


def test_fetch_uses_language_in_url():
    source = GitHubTrendingSource(language="python")
    with patch("src.sources.github_trending.requests.get", return_value=_mock_response(SAMPLE_HTML)) as mock_get:
        source.fetch()
    called_url = mock_get.call_args[0][0]
    assert "python" in called_url


def test_format_shows_header_and_repos():
    source = GitHubTrendingSource()
    records = [
        {"rank": 1, "repo": "owner/repo-one", "description": "Cool project", "language": "Python", "stars": "1,234"},
    ]
    msg = source.format(records)
    assert "<b>GitHub Trending</b>" in msg
    assert "<b>owner/repo-one</b>" in msg
    assert "⭐" in msg
    assert "1,234" in msg
    assert "Python" in msg
    assert "github.com" in msg


def test_format_hides_language_when_empty():
    source = GitHubTrendingSource()
    records = [
        {"rank": 1, "repo": "user/repo", "description": "", "language": "", "stars": "500"},
    ]
    msg = source.format(records)
    assert "<b>user/repo</b>" in msg
    assert "🔤" not in msg


def test_format_returns_empty_string_for_empty_records():
    source = GitHubTrendingSource()
    assert source.format([]) == ""


def test_name_and_default_schedule():
    source = GitHubTrendingSource()
    assert source.name == "github-trending"
    assert source.default_schedule == "0 9 * * *"
