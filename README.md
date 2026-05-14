# ASC Writeup DB

ASC 보안 동아리 CTF Writeup 관리 시스템

멤버가 Git PR로 writeup을 제출하면, 관리자 리뷰 후 merge 시 자동으로 Notion DB에 동기화됩니다.

## 마감

- **매주 화요일 23:59** 까지 PR merge 완료 시 해당 주차 제출로 인정
- 주간 기준: 화요일 ~ 월요일

## 구조

```
writeups/
└── {YYYY-CTF이름}/
    └── {카테고리}/
        └── {문제명}/
            ├── {github_username}.md   # writeup 본문 (frontmatter 포함)
            ├── solve.py               # 풀이 스크립트 (선택)
            └── images/                # 스크린샷 (선택)
```

> **같은 문제를 여러 멤버가 풀어도 각자 자신의 GitHub username으로 파일을 생성하므로 충돌 없이 구분됩니다.**
>
> 예: `writeups/2026-DiceCTF/web/baby-xss/alice.md`, `writeups/2026-DiceCTF/web/baby-xss/bob.md`

## 빠른 시작

### 1. 레포 Fork & Clone

```bash
# 본인 GitHub 계정으로 Fork 후
git clone https://github.com/<your-username>/WriteupDB.git
cd WriteupDB
```

### 2. Writeup 작성

```bash
# 디렉토리 생성
mkdir -p writeups/2026-Example-CTF/web/example-challenge

# 템플릿 복사 (파일명을 본인 GitHub username으로 지정)
cp templates/writeup-template.md writeups/2026-Example-CTF/web/example-challenge/<your-github-username>.md

# writeup 작성 (frontmatter의 author 필드도 동일한 GitHub username으로 기입)
```

### 3. 로컬 검증

```bash
pip install -r scripts/requirements.txt
python scripts/validate_frontmatter.py
```

### 4. PR 제출

```bash
git checkout -b writeup/2026-Example-CTF/web/example-challenge
git add .
git commit -m "Add writeup: 2026-Example-CTF/web/example-challenge"
git push origin writeup/2026-Example-CTF/web/example-challenge
# GitHub에서 PR 생성
```

자세한 제출 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 파이프라인

```
[멤버] -> fork/branch -> [PR 제출] -> 리뷰 -> [merge] -> [GitHub Actions] -> [Notion DB]
                              |                              |
                        CI: frontmatter 검증         변경된 .md 파싱 -> 동기화
                                                     + 제출 현황 체크박스 업데이트
```

## 설정 (관리자)

### GitHub Secrets

| Secret | 설명 |
|--------|------|
| `NOTION_API_KEY` | Notion Internal Integration Token |
| `NOTION_DATABASE_ID` | Writeup Notion DB ID |
| `NOTION_TRACKING_DB_ID` | 제출 현황 DB ID |
| `NOTION_MEMBERS_DB_ID` | 부원 명단 DB ID |

### Notion DB 스키마

| 속성명 | 타입 | 비고 |
|--------|------|------|
| 문제명 | Title | |
| 대회명 | Select | CTF 대회명 |
| 분야 | Multi-select | WEB/PWN/REV/CRYPTO/MISC |
| 난이도 | Select | easy/medium/hard/insane |
| 닉네임 | Rich Text | GitHub username |
| 날짜 | Date | |
| 취약점 태그 | Multi-select | 사용 기술/취약점 |
| Git 링크 | URL | writeup 원문 링크 |

### 브랜치 보호 규칙 (권장)

- `main` 브랜치 직접 push 금지
- PR 필수, CI 통과 필수
- 최소 1명 리뷰 승인 필수
