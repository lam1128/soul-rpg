#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "runtime" / "registry.json"
COMMON_UI = "ui/UI_统一规范_日常恢复与菜单.md"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def source_sections(route: dict, filename: str) -> list[str]:
    sections: list[str] = []
    for source in route.get("sources", []):
        if source.get("file") == filename:
            sections.extend(source.get("sections", []))
    return sections


def require_ui_section(routes: dict, route_name: str, needle: str) -> None:
    route = routes.get(route_name)
    if not route:
        fail(f"missing route: {route_name}")
    sections = source_sections(route, COMMON_UI)
    if not any(needle in section for section in sections):
        fail(f"{route_name} missing common UI source for {needle}")


def main() -> None:
    registry = load_registry()
    routes = registry.get("topic_routes", {})

    expected_ui = {
        "ordinary_gameplay_startup": ["§7"],
        "new_game": ["§15"],
        "real_activity": ["§13"],
        "hunting": ["§14"],
        "companion_episode": ["§12"],
        "readonly_query": ["§5", "§6", "§8", "§9", "§10", "§11"],
        "recovery": ["§2", "§4"],
        "economy_transaction": ["§1", "§3"],
    }
    for route_name, needles in expected_ui.items():
        for needle in needles:
            require_ui_section(routes, route_name, needle)

    readonly_sources = routes["readonly_query"].get("sources", [])
    cg_lookups = [
        source
        for source in readonly_sources
        if source.get("lookup") == "manifest.companion_episode_files[CHAPTER_ID]"
    ]
    if len(cg_lookups) != 1:
        fail("readonly_query must have exactly one scoped companion CG lookup")
    cg_lookup = cg_lookups[0]
    joined_sections = " ".join(cg_lookup.get("sections", []))
    if "基础CG画面" not in joined_sections or "高好感CG画面" not in joined_sections:
        fail("readonly CG lookup must be limited to explicit base/high CG fields")
    hard_limit = cg_lookup.get("hard_limit", "")
    if "never_scan_all_45" not in hard_limit or "at_most_five" not in hard_limit:
        fail("readonly CG lookup must enforce requested-companion-only hard limit")

    chapter_map = registry.get("companion_episode_files", {})
    if len(chapter_map) != 45:
        fail(f"expected 45 chapter mappings, got {len(chapter_map)}")
    if len(set(chapter_map.values())) != 45:
        fail("chapter mappings are not one-to-one")

    required_markers = [
        "OPTION_ORDER_SEED",
        "固定四场",
        "高理解专属回报",
        "基础CG画面",
        "高好感CG画面",
        "低分仍有戏",
        "标题回收",
    ]

    for chapter_id, rel_path in sorted(chapter_map.items()):
        path = ROOT / rel_path
        if not path.is_file():
            fail(f"missing chapter file for {chapter_id}: {rel_path}")
        text = path.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in text:
                fail(f"{chapter_id} missing marker: {marker}")
        if "记忆画面锚点（CG）" in text:
            fail(f"{chapter_id} still uses legacy single CG anchor")
        if chapter_id.endswith("_C04"):
            if "关系确认" not in text and "第4章关系门" not in text:
                fail(f"{chapter_id} is not marked as relationship-confirmation chapter")
        if chapter_id.endswith("_C05"):
            for marker in ("关系后续章", "关系分流", "ROMANCE_ACTIVE=true", "ROMANCE_ACTIVE=false"):
                if marker not in text:
                    fail(f"{chapter_id} missing relationship follow-up contract: {marker}")

    c00 = (ROOT / "data/companions/DM_ONLY_C00_伙伴篇章库.md").read_text(encoding="utf-8")
    if "既有单章若仍使用单字段" in c00:
        fail("C00 still contains legacy single-CG compatibility fallback")
    for marker in ("基础CG画面", "高好感CG画面", "第5章一律是**关系后续章**"):
        if marker not in c00:
            fail(f"C00 missing global contract marker: {marker}")

    interaction = (ROOT / "rules/13_交互协议.md").read_text(encoding="utf-8")
    if "未收录条目只显示“未解锁”" in interaction:
        fail("interaction protocol still contains stale single-slot CG lock wording")

    print(json.dumps({
        "status": "PASS",
        "routes_checked": len(expected_ui),
        "chapters_checked": len(chapter_map),
        "relationship_confirm_chapters": sum(key.endswith("_C04") for key in chapter_map),
        "relationship_followup_chapters": sum(key.endswith("_C05") for key in chapter_map),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
