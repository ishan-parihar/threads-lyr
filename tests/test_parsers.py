"""Tests for threads_mcp_server.scraping.parsers."""

import json

from threads_mcp_server.scraping import parsers


class TestEmbeddedJson:
    def test_parse_embedded_json(self):
        html = '<script type="application/json">{"a": 1}</script>'
        blobs = parsers.parse_embedded_json(html)
        assert blobs == [{"a": 1}]

    def test_parse_embedded_json_skips_non_json(self):
        html = "<script>function foo() {}</script>"
        assert parsers.parse_embedded_json(html) == []

    def test_deep_find_nested(self):
        data = {"x": {"y": [{"z": 1}, {"w": 2}]}}
        found = parsers.deep_find(data, lambda n: isinstance(n, dict) and "z" in n)
        assert len(found) == 1
        assert found[0]["z"] == 1


class TestThreadsProfile:
    THREADS_HTML = (
        '<script type="application/json">'
        + json.dumps(
            {
                "props": {
                    "pageProps": {
                        "user": {
                            "id": "314159",
                            "username": "zuck",
                            "full_name": "Mark Zuckerberg",
                            "biography": "Building the metaverse",
                            "followers": 100,
                            "following": 50,
                            "posts": 10,
                        }
                    }
                }
            }
        )
        + "</script>"
    )

    def test_parse_threads_profile(self):
        profile = parsers.parse_threads_profile(self.THREADS_HTML, "zuck")
        assert profile["id"] == "314159"
        assert profile["name"] == "Mark Zuckerberg"
        assert profile["bio"] == "Building the metaverse"
        assert profile["followers_count"] == 100
        assert profile["following_count"] == 50
        assert profile["posts_count"] == 10
        assert profile["url"] == "https://www.threads.net/@zuck"

    def test_parse_threads_profile_empty(self):
        profile = parsers.parse_threads_profile("<html></html>", "nobody")
        assert profile["username"] == "nobody"
        assert "id" not in profile


class TestThreadsPosts:
    THREADS_HTML = (
        '<script type="application/json">'
        + json.dumps(
            {
                "props": {
                    "pageProps": {
                        "threads": [
                            {
                                "id": "post_1",
                                "text": "Hello Threads",
                                "created_at": 1700000000,
                                "like_count": 5,
                            }
                        ]
                    }
                }
            }
        )
        + "</script>"
    )

    def test_parse_threads_posts(self):
        posts = parsers.parse_threads_posts(self.THREADS_HTML, "zuck", limit=5)
        assert len(posts) == 1
        assert posts[0]["text"] == "Hello Threads"
        assert posts[0]["id"] == "post_1"
        assert posts[0]["like_count"] == 5
        assert posts[0]["url"] == "https://www.threads.net/@zuck/post/post_1"

    def test_parse_threads_posts_modern_caption_dict(self):
        html = (
            '<script type="application/json">'
            + json.dumps(
                {
                    "props": {
                        "pageProps": {
                            "threads": [
                                {
                                    "pk": "123456",
                                    "code": "abcdef",
                                    "caption": {"text": "Modern caption"},
                                    "taken_at": 1700000000,
                                }
                            ]
                        }
                    }
                }
            )
            + "</script>"
        )
        posts = parsers.parse_threads_posts(html, "zuck", limit=5)
        assert len(posts) == 1
        assert posts[0]["text"] == "Modern caption"
        assert posts[0]["code"] == "abcdef"
        assert posts[0]["url"] == "https://www.threads.net/@zuck/post/abcdef"

    def test_parse_threads_posts_limit(self):
        html = (
            '<script type="application/json">'
            + json.dumps(
                {
                    "props": {
                        "pageProps": {
                            "threads": [
                                {"id": f"p{i}", "text": f"t{i}", "created_at": i} for i in range(10)
                            ]
                        }
                    }
                }
            )
            + "</script>"
        )
        posts = parsers.parse_threads_posts(html, "zuck", limit=3)
        assert len(posts) == 3

    def test_parse_threads_posts_empty(self):
        assert parsers.parse_threads_posts("<html></html>", "zuck") == []
