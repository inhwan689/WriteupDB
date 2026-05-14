# Writeup 제출 가이드

## 파일 네이밍 규칙

> **중요: writeup 파일명은 반드시 본인의 GitHub username으로 작성합니다.**
>
> 같은 문제를 여러 멤버가 풀어도 각자의 파일로 구분되므로 충돌이 발생하지 않습니다.

```
writeups/{YYYY-CTF이름}/{카테고리}/{문제명}/{github_username}.md
```

예시:
```
writeups/2026-DiceCTF/web/baby-xss/alice.md    # alice의 풀이
writeups/2026-DiceCTF/web/baby-xss/bob.md      # bob의 풀이
writeups/2026-DiceCTF/pwn/heap-note/alice.md   # alice의 다른 문제 풀이
```

**주의**: 파일명(`alice.md`)과 frontmatter의 `author` 필드(`alice`)가 반드시 일치해야 합니다. 불일치 시 CI 검증에서 실패합니다.

## 제출 절차

### 1. Fork & Clone

이 레포를 본인 GitHub 계정으로 Fork한 뒤 Clone합니다.

```bash
git clone https://github.com/<your-username>/WriteupDB.git
cd WriteupDB
```

### 2. 브랜치 생성

```bash
git checkout -b writeup/<CTF이름>/<카테고리>/<문제명>
# 예: git checkout -b writeup/2026-DiceCTF/web/baby-xss
```

### 3. 디렉토리 및 파일 생성

디렉토리 네이밍 규칙:

- **CTF이름**: `YYYY-CTF이름` 형식 (예: `2026-DiceCTF`, `2026-DEFCON-Quals`)
- **카테고리**: 소문자 (`web`, `pwn`, `rev`, `crypto`, `misc`)
- **문제명**: 소문자, 공백은 하이픈으로 (예: `baby-xss`, `heap-note`)
- **파일명**: `{본인 GitHub username}.md` (예: `alice.md`)

```bash
# 디렉토리 생성
mkdir -p writeups/2026-DiceCTF/web/baby-xss

# 템플릿 복사 (파일명을 본인 GitHub username으로!)
cp templates/writeup-template.md writeups/2026-DiceCTF/web/baby-xss/alice.md
```

### 4. Writeup 작성

복사한 `.md` 파일의 YAML frontmatter를 반드시 작성합니다.

#### 필수 필드

| 필드 | 설명 | 예시 |
|------|------|------|
| `ctf_name` | CTF 대회명 | `DiceCTF 2026` |
| `challenge_name` | 문제명 | `baby-xss` |
| `category` | 카테고리 | `web` |
| `difficulty` | 난이도 | `easy` |
| `author` | 작성자 (GitHub username, **파일명과 동일해야 함**) | `alice` |
| `date` | 대회 날짜 | `2026-01-15` |

#### 선택 필드

| 필드 | 설명 | 예시 |
|------|------|------|
| `points` | 문제 배점 | `500` |
| `tags` | 관련 기술/툴 | `[XSS, CSP bypass]` |

#### 카테고리 유효값

`web`, `pwn`, `rev`, `crypto`, `misc`

#### 난이도 유효값

`easy`, `medium`, `hard`, `insane`

### 5. 로컬 검증

```bash
pip install -r scripts/requirements.txt
python scripts/validate_frontmatter.py
```

### 6. Commit & Push

```bash
git add writeups/2026-DiceCTF/web/baby-xss/alice.md
git commit -m "Add writeup: DiceCTF 2026 - baby-xss (web) by alice"
git push origin writeup/2026-DiceCTF/web/baby-xss
```

### 7. Pull Request

GitHub에서 PR을 생성합니다. PR 템플릿을 채워주세요.

## 추가 파일

- `solve.py`, `exploit.py` 등 풀이 스크립트 첨부 가능
- 스크린샷은 `images/` 디렉토리에 저장
- writeup 본문에서 상대 경로로 참조: `![screenshot](images/step1.png)`
- 상대 경로 이미지는 Notion 동기화 시 GitHub raw URL로 자동 변환되므로, 외부 URL을 직접 쓸 필요 없음

## 주의사항

- **파일명 = GitHub username** (예: `alice.md`) — frontmatter의 `author` 필드와 반드시 일치
- 실제 CTF 플래그는 가급적 마스킹 처리 (예: `flag{REDACTED}`)
- 대용량 바이너리 파일은 가급적 첨부하지 않기
- frontmatter 검증 CI가 통과해야 merge 가능
