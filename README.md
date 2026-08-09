# Ajiteu (아지트)

함께 나누는 이야기를 위한 **Flask 기반 커뮤니티/SNS** 프로젝트입니다.  
회원가입 후 게시글 작성, 댓글, 좋아요, 북마크, 알림, 프로필 관리 등을 사용할 수 있습니다.

- **GitHub:** https://github.com/Ajiteu/Ajiteu000.git

---

## 기술 스택

| 구분 | 사용 기술 |
|------|-----------|
| 백엔드 | Python, Flask 3 |
| DB | SQLite, SQLAlchemy, Flask-Migrate (Alembic) |
| 폼/인증 | Flask-WTF, 세션 로그인, PyJWT (API) |
| 프론트 | Jinja2, Bootstrap 5, CSS |

---

## 실행 방법

### 1. 저장소 clone

```bash
git clone https://github.com/Ajiteu/Ajiteu000.git
cd Ajiteu000
```

### 2. 가상환경 및 패키지 설치

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> PowerShell 실행 정책 오류가 나면:  
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 3. DB 마이그레이션

```powershell
$env:FLASK_APP = "ajiteu"
flask db upgrade
```

### 4. 서버 실행

```powershell
flask run
```

브라우저에서 **http://127.0.0.1:5000** 접속 → 로그인 페이지로 이동합니다.

---

## 화면 구성

로그인 후 메인 화면은 **3단 레이아웃**입니다.

| 영역 | 설명 |
|------|------|
| **좌측 사이드바** | 내 프로필, 글쓰기, 프로필 설정, 내가 쓴 글, 북마크, 로그아웃 |
| **중앙 피드** | 게시글 카드 목록, 검색, 정렬(최신/인기), 페이지네이션 |
| **우측 사이드바** | 카테고리 필터, 주간 트렌드 |

---

## 기능 및 사용법

### 회원가입 / 로그인

1. 첫 접속 시 **로그인** 페이지가 표시됩니다.
2. **회원가입** 버튼 → 아이디, 비밀번호, 이메일 입력 후 가입
3. 가입 완료 시 자동 로그인되어 메인 피드로 이동합니다.
4. **로그아웃**은 좌측 사이드바 하단에서 가능합니다.

| URL | 설명 |
|-----|------|
| `/auth/login/` | 로그인 |
| `/auth/signup/` | 회원가입 |
| `/auth/logout` | 로그아웃 |

---

### 게시글

#### 글 목록 보기

- 로그인 후 메인 피드(`/post/list/<내 user id>`)에서 전체 게시글을 볼 수 있습니다.
- 상단 **최신글 / 인기글** 버튼으로 정렬을 바꿀 수 있습니다.
- **검색창**에 키워드를 입력하면 제목·내용·작성자·댓글에서 검색합니다.
- 우측 **카테고리**(전체 / 여행 / 운동 / 음식)로 필터링할 수 있습니다.

#### 글 작성

1. 좌측 **글쓰기** 클릭
2. 본문 입력 (이미지 여러 장 첨부 가능)
3. **등록하기** 클릭

> 글 내용의 키워드에 따라 카테고리가 자동 분류됩니다.  
> (예: "여행", "맛집", "운동" 등)

#### 글 상세 / 수정 / 삭제

- 카드 클릭 → 게시글 상세 모달
- **⋯** 메뉴 → 수정 / 삭제 (본인 글 또는 관리자만 가능)
- **◀ ▶** 버튼으로 이전·다음 글 이동

#### 좋아요 (추천)

- 목록 또는 상세에서 👍 클릭
- 본인 글은 추천할 수 없습니다.
- 다시 클릭하면 추천 취소됩니다.

#### 조회수

- 게시글 **상세 페이지를 처음 열 때** 조회수 +1
- 같은 브라우저 세션에서 새로고침해도 중복 증가하지 않습니다.

| URL | 설명 |
|-----|------|
| `/post/list/<user_id>` | 게시글 목록 |
| `/post/create/<user_id>` | 글 작성 |
| `/post/detail/<post_id>/` | 글 상세 |
| `/post/user/<user_id>` | 특정 사용자 글만 보기 |
| `/post/like/<post_id>/` | 좋아요 |

---

### 댓글 / 대댓글

1. 게시글 상세 하단 **댓글 입력** 후 등록
2. 댓글 수정·삭제는 작성자 본인만 가능
3. 댓글에 **대댓글(Reply)** 작성 가능

| URL | 설명 |
|-----|------|
| `POST /comment/create/<post_id>/` | 댓글 작성 |
| `/comment/modify/<comment_id>/` | 댓글 수정 |
| `/comment/delete/<comment_id>/` | 댓글 삭제 |

---

### 프로필

1. 좌측 **프로필 설정** → 닉네임, 소개, 프로필 사진 변경
2. 다른 사용자 프로필은 `/profile/view/<user_id>/` 에서 확인

| URL | 설명 |
|-----|------|
| `/profile/detail/<user_id>/` | 프로필 수정 (본인만) |
| `/profile/view/<user_id>/` | 프로필 보기 |

---

### 북마크

- 게시글 상세에서 **북마크** 버튼 클릭 → 저장
- 좌측 **북마크** 메뉴에서 저장한 글 목록 확인
- **북마크 해제**로 삭제

| URL | 설명 |
|-----|------|
| `/bookmark/add/<post_id>/` | 북마크 추가 |
| `/bookmark/remove/<post_id>/` | 북마크 해제 |
| `/bookmark/list/` | 북마크 목록 |

---

### 알림

- 다른 사용자가 내 글에 **좋아요**를 누르면 알림 생성
- `/notification/list/` 에서 알림 목록 확인
- 개별 알림 읽음 처리 가능

---

### 관리자 (role = admin 계정)

- 좌측 **관리자** 메뉴 (관리자 계정만 표시)
- 신고 처리, 게시글 삭제, 사용자 활성/비활성 관리

| URL | 설명 |
|-----|------|
| `/admin/` | 관리자 대시보드 |

---

## REST API (선택)

모바일/프론트 연동용 JSON API도 제공합니다.  
요청 시 `Authorization: Bearer <token>` 헤더가 필요합니다.

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/auth/api/signup` | 회원가입 → JWT 발급 |
| POST | `/auth/api/login` | 로그인 → JWT 발급 |
| GET | `/auth/api/me` | 내 정보 조회 |
| GET | `/api/posts` | 게시글 목록 (카테고리·검색) |
| GET | `/api/trends/weekly` | 주간 트렌드 |
| GET | `/notification/api/list` | 알림 목록 |

---

## 프로젝트 구조

```
Ajiteu000/
├── ajiteu/                 # Flask 앱
│   ├── __init__.py         # 앱 팩토리
│   ├── models.py           # DB 모델
│   ├── forms.py            # WTForms
│   ├── views/              # 라우트(Blueprint)
│   ├── templates/          # HTML
│   └── static/             # CSS, JS, 이미지
├── migrations/             # DB 마이그레이션
├── config.py               # 설정 (DB, SECRET_KEY, JWT)
├── requirements.txt
└── ajiteu.db               # SQLite DB (로컬)
```

---

## 자주 발생하는 문제

### 500 Internal Server Error (로그인 등)

1. **마이그레이션 미적용** → `flask db upgrade` 실행
2. **패키지 미설치** → `pip install -r requirements.txt` (PyJWT 포함)
3. **잘못된 실행 경로** → 프로젝트 **루트**(`Ajiteu000`)에서 `flask run`
4. **예전 세션 쿠키** → 브라우저 쿠키 삭제 후 재접속

### `flask` 명령을 찾을 수 없음

가상환경이 활성화되지 않았을 가능성이 큽니다.

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 개발 참고

- DB 스키마 변경 후: `flask db migrate -m "설명"` → `flask db upgrade`
- `config.py`의 `SECRET_KEY`, `JWT_SECRET_KEY`는 배포 시 반드시 변경하세요.
- 팔로우 기능은 제거되었습니다. (2026-08-09 기준)

---

## 라이선스 / 기여

팀 프로젝트 저장소입니다. 이슈 및 PR은 GitHub 저장소를 이용해 주세요.
