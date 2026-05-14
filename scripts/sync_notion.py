#!/usr/bin/env python3
"""Writeup을 Notion DB에 동기화하는 스크립트.

변경된 writeup 파일의 frontmatter를 파싱하여 Notion DB에 생성/업데이트합니다.

Usage:
    python scripts/sync_notion.py writeups/.../README.md [...]

Environment:
    NOTION_API_KEY       - Notion Internal Integration Token
    NOTION_DATABASE_ID   - 대상 Notion Database ID
    GITHUB_REPOSITORY    - GitHub 레포 (owner/repo 형식, Actions에서 자동 설정)
    GITHUB_SERVER_URL    - GitHub 서버 URL (Actions에서 자동 설정)
"""

import os
import re
import sys
from pathlib import Path
from typing import Any

import frontmatter
from notion_client import Client

_DATA_SOURCE_IDS: dict[str, str] = {}
NOTION_CODE_LANGUAGES = {
    "abap", "abc", "agda", "arduino", "ascii art", "assembly", "bash", "basic",
    "bnf", "c", "c#", "c++", "clojure", "coffeescript", "coq", "css", "dart",
    "dhall", "diff", "docker", "ebnf", "elixir", "elm", "erlang", "f#",
    "flow", "fortran", "gherkin", "glsl", "go", "graphql", "groovy", "haskell",
    "hcl", "html", "idris", "java", "javascript", "json", "julia", "kotlin",
    "latex", "less", "lisp", "livescript", "llvm ir", "lua", "makefile",
    "markdown", "markup", "matlab", "mathematica", "mermaid", "nix",
    "notion formula", "objective-c", "ocaml", "pascal", "perl", "php",
    "plain text", "powershell", "prolog", "protobuf", "purescript", "python",
    "r", "racket", "reason", "ruby", "rust", "sass", "scala", "scheme",
    "scss", "shell", "smalltalk", "solidity", "sql", "swift", "toml",
    "typescript", "vb.net", "verilog", "vhdl", "visual basic", "webassembly",
    "xml", "yaml", "java/c/c++/c#",
}
CODE_LANGUAGE_ALIASES = {
    "plaintext": "plain text",
    "text": "plain text",
    "txt": "plain text",
    "console": "shell",
    "shell script": "shell",
    "sh": "shell",
    "zsh": "shell",
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "yml": "yaml",
}


def get_notion_client() -> Client:
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        print("Error: NOTION_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    timeout_ms = int(os.environ.get("NOTION_TIMEOUT_MS", "60000"))
    return Client(auth=api_key, timeout_ms=timeout_ms)


def get_database_id() -> str:
    db_id = os.environ.get("NOTION_DATABASE_ID")
    if not db_id:
        print("Error: NOTION_DATABASE_ID 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    return db_id


def build_github_url(filepath: Path) -> str:
    """writeup 파일의 GitHub URL을 생성합니다."""
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        return ""
    # writeups/ 이하 상대 경로 사용
    return f"{server}/{repo}/blob/main/{filepath}"


def parse_writeup(filepath: Path) -> tuple[dict, str]:
    """writeup 파일의 frontmatter와 본문을 파싱합니다."""
    post = frontmatter.loads(filepath.read_text(encoding="utf-8-sig"))
    return post.metadata, post.content


def rich_text(content: str) -> list[dict]:
    """Notion rich_text 객체를 생성합니다."""
    # Notion API는 rich_text content를 2000자로 제한
    if len(content) > 2000:
        content = content[:2000]
    return [{"type": "text", "text": {"content": content}}]


def normalize_code_language(lang: str) -> str:
    """Notion이 허용하는 코드 블록 언어로 정규화합니다."""
    normalized = CODE_LANGUAGE_ALIASES.get(lang.strip().lower(), lang.strip().lower())
    return normalized if normalized in NOTION_CODE_LANGUAGES else "plain text"


def build_raw_image_url(relative_path: str, writeup_filepath: Path) -> str:
    """상대 경로 이미지를 GitHub raw URL로 변환합니다."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        return ""
    image_path = (writeup_filepath.parent / relative_path).as_posix()
    if "writeups/" in image_path:
        idx = image_path.index("writeups/")
        image_path = image_path[idx:]
    return f"https://raw.githubusercontent.com/{repo}/main/{image_path}"


def markdown_to_notion_blocks(md: str, writeup_filepath: Path | None = None) -> list[dict]:
    """마크다운 텍스트를 Notion 블록 리스트로 변환합니다."""
    blocks = []
    lines = md.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # 빈 줄 건너뛰기
        if not line.strip():
            i += 1
            continue

        # 코드 블록
        if line.strip().startswith("```"):
            lang = line.strip().removeprefix("```").strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 닫는 ``` 건너뛰기
            code_content = "\n".join(code_lines)
            if len(code_content) > 2000:
                code_content = code_content[:2000]
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": rich_text(code_content),
                    "language": normalize_code_language(lang),
                },
            })
            continue

        # 제목
        heading_match = re.match(r"^(#{1,3})\s*(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            blocks.append({
                "object": "block",
                "type": f"heading_{level}",
                f"heading_{level}": {"rich_text": rich_text(heading_text)},
            })
            i += 1
            continue

        # 인용문
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:])
                i += 1
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {"rich_text": rich_text("\n".join(quote_lines))},
            })
            continue

        # 비순서 목록
        if re.match(r"^[-*] ", line):
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": rich_text(lines[i][2:].strip())},
                })
                i += 1
            continue

        # 순서 목록
        if re.match(r"^\d+\. ", line):
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                text = re.sub(r"^\d+\. ", "", lines[i]).strip()
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": rich_text(text)},
                })
                i += 1
            continue

        # 이미지
        img_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if img_match:
            url = img_match.group(2)
            if not url.startswith("http") and writeup_filepath:
                url = build_raw_image_url(url, writeup_filepath)
            if url.startswith("http"):
                blocks.append({
                    "object": "block",
                    "type": "image",
                    "image": {"type": "external", "external": {"url": url}},
                })
            i += 1
            continue

        # 구분선
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", line.strip()):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # 일반 텍스트 (연속된 줄을 하나의 paragraph로)
        para_lines = []
        while i < len(lines) and lines[i].strip() and not any([
            re.match(r"^(#{1,3})\s+.+$", lines[i]),
            lines[i].startswith("> "),
            lines[i].startswith("```"),
            re.match(r"^[-*] ", lines[i]),
            re.match(r"^\d+\. ", lines[i]),
            re.match(r"^(-{3,}|\*{3,}|_{3,})$", lines[i].strip()),
            re.match(r"!\[([^\]]*)\]\(([^)]+)\)", lines[i].strip()),
        ]):
            para_lines.append(lines[i])
            i += 1
        if not para_lines:
            para_lines.append(lines[i])
            i += 1
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": rich_text("\n".join(para_lines))},
        })

    # Notion API는 한 번에 최대 100개 블록
    return blocks[:100]


def find_existing_page(notion: Client, database_id: str, ctf_name: str, challenge_name: str, author: str) -> str | None:
    """대회명+문제명+작성자로 기존 Notion 페이지를 검색합니다. 있으면 page_id 반환."""
    response = notion.search(
        query=challenge_name,
        filter={"value": "page", "property": "object"},
    )
    for page in response.get("results", []):
        if page.get("parent", {}).get("database_id", "").replace("-", "") != database_id.replace("-", ""):
            continue
        props = page.get("properties", {})
        # 문제명(Title) 확인
        title_prop = props.get("문제명", {})
        title_texts = title_prop.get("title", [])
        title = title_texts[0]["plain_text"] if title_texts else ""
        # 대회명(Select) 확인
        ctf_prop = props.get("대회명", {})
        ctf_select = ctf_prop.get("select")
        ctf = ctf_select["name"] if ctf_select else ""
        # 작성자 확인
        author_prop = props.get("닉네임", {})
        author_texts = author_prop.get("rich_text", [])
        page_author = author_texts[0]["plain_text"] if author_texts else ""
        if title == challenge_name and ctf == ctf_name and page_author == author:
            return page["id"]
    return None


def resolve_query_target_id(notion: Client, database_id: str) -> str:
    """Notion DB query에 사용할 식별자를 반환합니다."""
    if hasattr(notion.databases, "query"):
        return database_id

    cached_id = _DATA_SOURCE_IDS.get(database_id)
    if cached_id:
        return cached_id

    database = notion.databases.retrieve(database_id=database_id)
    data_sources = database.get("data_sources") or []
    if not data_sources and database.get("initial_data_source"):
        data_sources = [database["initial_data_source"]]

    for data_source in data_sources:
        data_source_id = data_source.get("id") if isinstance(data_source, dict) else None
        if data_source_id:
            _DATA_SOURCE_IDS[database_id] = data_source_id
            return data_source_id

    raise RuntimeError(
        f"Database {database_id} 에 query 가능한 data source가 없습니다. "
        "Notion API 버전과 데이터베이스 접근 권한을 확인하세요."
    )


def query_database(notion: Client, database_id: str, **kwargs: Any) -> dict[str, Any]:
    """구/신 Notion SDK 모두에서 동작하도록 데이터베이스를 조회합니다."""
    if hasattr(notion.databases, "query"):
        return notion.databases.query(database_id=database_id, **kwargs)
    return notion.data_sources.query(
        data_source_id=resolve_query_target_id(notion, database_id),
        **kwargs,
    )


def build_properties(metadata: dict, github_url: str) -> dict:
    """frontmatter 메타데이터를 Notion properties로 변환합니다."""
    properties = {
        "문제명": {"title": [{"text": {"content": metadata.get("challenge_name", "")}}]},
        "대회명": {"select": {"name": metadata.get("ctf_name", "")}},
        "분야": {"multi_select": [{"name": metadata.get("category", "misc").upper()}]},
        "난이도": {"select": {"name": metadata.get("difficulty", "medium")}},
        "닉네임": {"rich_text": [{"text": {"content": metadata.get("author", "")}}]},
    }

    # 날짜
    date = metadata.get("date")
    if date:
        properties["날짜"] = {"date": {"start": str(date)}}

    # 취약점 태그
    tags = metadata.get("tags")
    if tags and isinstance(tags, list):
        properties["취약점 태그"] = {"multi_select": [{"name": str(t)} for t in tags]}

    # Git 링크
    if github_url:
        properties["Git 링크"] = {"url": github_url}

    return properties


def clear_page_content(notion: Client, page_id: str) -> None:
    """기존 페이지의 블록을 모두 삭제합니다."""
    print(f"[NOTION] 기존 블록 조회: {page_id}")
    children = notion.blocks.children.list(block_id=page_id)
    for block in children.get("results", []):
        print(f"[NOTION] 블록 삭제: {block['id']}")
        notion.blocks.delete(block_id=block["id"])


def find_member_name_by_github(notion: Client, members_db_id: str, github_username: str) -> str | None:
    """멤버 DB에서 GitHub username으로 이름을 검색합니다."""
    print(f"[NOTION] 멤버 조회: github={github_username}")
    response = query_database(
        notion,
        members_db_id,
        filter={"property": "GitHub username", "rich_text": {"equals": github_username}},
        page_size=1,
    )
    results = response.get("results", [])
    if not results:
        return None
    title_prop = results[0].get("properties", {}).get("이름", {})
    title_texts = title_prop.get("title", [])
    return title_texts[0]["plain_text"] if title_texts else None


def find_tracking_page(notion: Client, tracking_db_id: str, name: str) -> str | None:
    """제출 현황 DB에서 이름으로 페이지를 검색합니다."""
    print(f"[NOTION] 제출 현황 조회: name={name}")
    response = query_database(
        notion,
        tracking_db_id,
        filter={"property": "이름", "title": {"equals": name}},
        page_size=1,
    )
    results = response.get("results", [])
    return results[0]["id"] if results else None


def update_tracking_checkbox(notion: Client, tracking_db_id: str, name: str, week: int) -> None:
    """제출 현황 DB에서 멤버의 W{week} 체크박스를 True로 업데이트합니다."""
    prop_name = f"WW{week}"
    page_id = find_tracking_page(notion, tracking_db_id, name)
    if page_id:
        print(f"[NOTION] 제출 현황 업데이트: page={page_id} prop={prop_name}")
        notion.pages.update(
            page_id=page_id,
            properties={prop_name: {"checkbox": True}},
        )
        print(f"[TRACK] {name} → {prop_name} ✅")
    else:
        print(f"[TRACK] {name} → 제출 현황 DB에서 찾을 수 없음")


def sync_writeup(notion: Client, database_id: str, filepath: Path) -> None:
    """단일 writeup을 Notion DB에 동기화합니다."""
    print(f"[SYNC] 시작: {filepath}")
    metadata, content = parse_writeup(filepath)
    ctf_name = metadata.get("ctf_name", "")
    challenge_name = metadata.get("challenge_name", "")

    if not ctf_name or not challenge_name:
        print(f"[SKIP] {filepath}: ctf_name 또는 challenge_name 누락")
        return

    github_url = build_github_url(filepath)
    properties = build_properties(metadata, github_url)
    blocks = markdown_to_notion_blocks(content, filepath)

    author = metadata.get("author", "")
    print(f"[NOTION] 기존 페이지 검색: ctf={ctf_name} challenge={challenge_name} author={author}")
    existing_page_id = find_existing_page(notion, database_id, ctf_name, challenge_name, author)

    if existing_page_id:
        print(f"[NOTION] 페이지 업데이트: {existing_page_id}")
        notion.pages.update(page_id=existing_page_id, properties=properties)
        clear_page_content(notion, existing_page_id)
        if blocks:
            print(f"[NOTION] 블록 추가: {existing_page_id} count={len(blocks)}")
            notion.blocks.children.append(block_id=existing_page_id, children=blocks)
        print(f"[UPDATE] {ctf_name} - {challenge_name}")
    else:
        print(f"[NOTION] 페이지 생성: title={challenge_name} blocks={len(blocks)}")
        notion.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            children=blocks,
        )
        print(f"[CREATE] {ctf_name} - {challenge_name}")

    # 제출 현황 DB 체크박스 업데이트
    week_number = os.environ.get("WEEK_NUMBER", "")
    tracking_db_id = os.environ.get("NOTION_TRACKING_DB_ID", "")
    members_db_id = os.environ.get("NOTION_MEMBERS_DB_ID", "")
    if week_number and tracking_db_id and members_db_id and author:
        week = int(week_number)
        member_name = find_member_name_by_github(notion, members_db_id, author)
        if member_name:
            update_tracking_checkbox(notion, tracking_db_id, member_name, week)
        else:
            print(f"[TRACK] GitHub '{author}' → 멤버 DB에서 찾을 수 없음")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python sync_notion.py <writeup_file> [...]")
        return 1

    notion = get_notion_client()
    database_id = get_database_id()

    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if not filepath.exists():
            print(f"[SKIP] {filepath}: 파일 없음")
            continue
        try:
            sync_writeup(notion, database_id, filepath)
        except Exception as e:
            print(f"[ERROR] {filepath}: {e}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
