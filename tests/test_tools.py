"""Tool behaviour against the bundled icon list. No network: downloads are stubbed."""

import json

import pytest


def call(fn, **args):
    return json.loads(fn(args))


@pytest.fixture()
def tools(plugin):
    from icon_index import tools as module

    return module


@pytest.fixture()
def catalog(plugin):
    from icon_index import catalog as module

    return module


def test_register_wires_tools_command_and_skill(plugin):
    seen = {"tools": [], "commands": [], "skills": []}

    class Ctx:
        def register_tool(self, name, **kw):
            seen["tools"].append(name)

        def register_command(self, name, handler, **kw):
            seen["commands"].append(name)

        def register_skill(self, name, path):
            seen["skills"].append(name)

    plugin.register(Ctx())
    assert seen == {"tools": ["icon_search", "icon_get", "icon_save"], "commands": ["icons"], "skills": ["add-3d-icon"]}


def test_every_icon_is_valid_and_unique(catalog):
    ids = [entry["id"] for entry in catalog.load()]
    assert len(ids) == len(set(ids)) >= 40
    assert set(catalog.categories()) == {"Tech", "Money", "Social", "Work"}


def test_search_finds_by_meaning(tools):
    result = call(tools.icon_search, query="security")
    assert result["ok"]
    assert {"lock", "shield"} <= {icon["id"] for icon in result["icons"][:3]}


def test_search_by_category_and_bad_category(tools):
    result = call(tools.icon_search, category="Money", limit=40)
    assert result["ok"] and all(icon["category"] == "Money" for icon in result["icons"])
    assert not call(tools.icon_search, category="Nope")["ok"]


def test_get_orange_has_all_files_and_embeds(tools):
    result = call(tools.icon_get, id="rocket")
    assert result["ok"]
    assert set(result["files"]) == {"glb", "glb_full", "png", "mp4"}
    assert {"iframe", "html", "react", "threejs", "img"} <= set(result["embed"])
    assert result["show_in_chat"] == '::icon-index{id="rocket"}'
    assert result["files"]["glb"]["url"].endswith("/icons/rocket/model.glb")


def test_get_preset_colour_points_at_colour_files(tools):
    result = call(tools.icon_get, id="rocket", color="Blue")
    assert set(result["files"]) == {"glb", "png"}
    assert result["files"]["glb"]["url"].endswith("/icons/rocket/colors/blue/model.glb")
    assert result["show_in_chat"] == '::icon-index{id="rocket" color="3b82f6"}'
    assert call(tools.icon_get, id="rocket", color="#3B82F6")["color"]["name"] == "blue"


def test_get_custom_hex_offers_viewer_only(tools):
    result = call(tools.icon_get, id="rocket", color="#0ea5e9")
    assert result["ok"] and result["files"] == {}
    assert "color=0ea5e9" in result["embed"]["iframe"] and "html" not in result["embed"]


def test_get_rejects_unknown_icon_and_bad_colour(tools):
    unknown = call(tools.icon_get, id="rockett")
    assert not unknown["ok"] and "rocket" in unknown["did_you_mean"]
    assert not call(tools.icon_get, id="rocket", color="not-a-colour")["ok"]


def test_save_writes_files_and_never_overwrites(tools, tmp_path, monkeypatch):
    fetched = []

    def fake_download(url, dest):
        fetched.append(url)
        dest.write_bytes(b"glTF")
        return 4

    monkeypatch.setattr(tools, "_download", fake_download)
    first = call(tools.icon_save, id="lock", folder=str(tmp_path / "icons"), color="green")
    assert first["ok"] and [f["path"].split("/")[-1] for f in first["files"]] == ["lock-green.glb", "lock-green.png"]
    assert all("/colors/green/" in url for url in fetched)
    second = call(tools.icon_save, id="lock", folder=str(tmp_path / "icons"), color="green")
    assert all("skipped" in f for f in second["files"]) and len(fetched) == 2


def test_save_refuses_custom_hex_and_missing_formats(tools, tmp_path):
    assert not call(tools.icon_save, id="lock", folder=str(tmp_path), color="#123456")["ok"]
    assert not call(tools.icon_save, id="lock", folder=str(tmp_path), color="blue", formats=["mp4"])["ok"]
    assert not call(tools.icon_save, id="lock", folder="")["ok"]


def test_real_download_never_overwrites(tools, tmp_path, monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self, n):
            return b"new"

    monkeypatch.setattr(tools.urllib.request, "urlopen", lambda *a, **k: Response())
    dest = tmp_path / "x.glb"
    assert tools._download("https://example.invalid/x", dest) == 3 and dest.read_bytes() == b"new"
    with pytest.raises(OSError):
        tools._download("https://example.invalid/x", dest)
    assert dest.read_bytes() == b"new" and len(list(tmp_path.iterdir())) == 1


def test_command_lists_matches(tools):
    assert "Padlock" in tools.icon_command("lock")
    assert "No icon matches" in tools.icon_command("zzzz")
