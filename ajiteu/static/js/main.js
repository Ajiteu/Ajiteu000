document.addEventListener('DOMContentLoaded', () => {
    let currentCategory = 'all';
    let currentSearchQuery = '';
    let globalPosts = [];

    const postGrid = document.getElementById('postGrid');
    const serverRendered = postGrid && postGrid.dataset.serverRendered === 'true';

    // 서버에서 이미 렌더링된 경우 API 재호출하지 않음
    if (!serverRendered) {
        fetchPosts();
    }

    // 1. 카테고리 클릭 이벤트 (API 모드 전용)
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (serverRendered || e.target.closest('a')) return;
            document.querySelectorAll('.category-item').forEach(el => el.classList.remove('active'));
            e.target.classList.add('active');
            currentCategory = e.target.dataset.category || 'all';
            fetchPosts();
        });
    });

    // 2. 검색 이벤트 (API 모드 전용)
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');

    if (searchBtn && !serverRendered) {
        searchBtn.addEventListener('click', (e) => {
            e.preventDefault();
            currentSearchQuery = searchInput.value.trim();
            fetchPosts();
        });
    }

    if (searchInput && !serverRendered) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                currentSearchQuery = e.target.value.trim();
                fetchPosts();
            }
        });
    }

    // 3. API 데이터 호출
    function fetchPosts() {
        const url = `/api/posts?category=${encodeURIComponent(currentCategory)}&search=${encodeURIComponent(currentSearchQuery)}`;

        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('서버 미연결');
                return response.json();
            })
            .then(data => {
                globalPosts = data.posts || [];
                renderPosts(globalPosts);
            })
            .catch(err => {
                console.warn('Backend API 호출 실패:', err);
            });
    }

    // 4. 게시글 카드 동적 렌더링 (타이틀 완전 삭제)
    function renderPosts(posts) {
        const postGrid = document.getElementById('postGrid');
        if (!postGrid) return;

        postGrid.innerHTML = '';

        if (!posts || posts.length === 0) {
            postGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">게시글이 존재하지 않습니다.</p>';
            return;
        }

        posts.forEach((post) => {
            const card = document.createElement('div');
            card.className = 'card-item';
            card.style.cursor = 'pointer';
            
            // 카드 클릭 시 닉네임 상세보기 모달만 단일 오픈
            card.addEventListener('click', (e) => {
                if (e.target.closest('.btn-more') || e.target.closest('.action-item')) return;
                openDetailModal(post);
            });

            // 타이틀 삭제 적용
            card.innerHTML = `
                <div class="card-top">
                    <div class="author-box">
                        <div class="author-avatar"></div>
                        <div class="author-meta">
                            <div class="author-name">${escapeHtml(post.author)}</div>
                            <div class="post-date">${escapeHtml(post.created_at)}</div>
                        </div>
                    </div>
                    <button class="btn-more" data-id="${post.id}">...</button>
                </div>
                <div class="card-middle">
                    <div class="thumb-box"></div>
                    <div class="text-box">
                        <div class="card-desc">${escapeHtml((post.content || '').slice(0, 100))}</div>
                    </div>
                </div>
                <div class="card-bottom">
                    <a href="${post.detail_url || `/post/detail/${post.id}/`}" class="action-item text-decoration-none text-reset">
                        <i class="icon">👍</i> ${post.like_count}
                    </a>
                    <a href="${post.detail_url || `/post/detail/${post.id}/`}" class="action-item text-decoration-none text-reset">
                        <i class="icon">💬</i> ${post.comment_count || 0}
                    </a>
                    <span class="action-item" style="display: inline-flex; align-items: center; gap: 4px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                        ${post.view_count || 0}
                    </span>
                </div>
            `;
            postGrid.appendChild(card);
        });

        // 카드 상단 더보기(...) 버튼 클릭 시 옵션 모달 오픈
        document.querySelectorAll('.btn-more').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const modal = document.getElementById('postOptionModal');
                if (modal) modal.classList.remove('hidden');
            });
        });
    }

    /* --- 5. 새글 작성 모달 제어 --- */
    const btnWriteOpen = document.getElementById('btnWriteOpen');
    if (btnWriteOpen) {
        btnWriteOpen.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('postModal').classList.add('active');
        });
    }

    const btnCancelWrite = document.getElementById('btnCancelWrite');
    if (btnCancelWrite) {
        btnCancelWrite.addEventListener('click', closeWriteModal);
    }

    function closeWriteModal() {
        document.getElementById('postModal').classList.remove('active');
        document.getElementById('postForm').reset();
        document.getElementById('imagePreview').innerHTML = '';
    }

    // 이미지 업로드 미리보기
    const imageUploadInput = document.getElementById('imageUploadInput');
    if (imageUploadInput) {
        imageUploadInput.addEventListener('change', (event) => {
            const previewContainer = document.getElementById('imagePreview');
            previewContainer.innerHTML = '';
            const files = event.target.files;

            if (files) {
                Array.from(files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'preview-img';
                        previewContainer.appendChild(img);
                    };
                    reader.readAsDataURL(file);
                });
            }
        });
    }

    const postFormEl = document.getElementById('postForm');
    if (postFormEl) {
        postFormEl.addEventListener('submit', (e) => {
            if (postFormEl.getAttribute('action')) {
                return;
            }
            e.preventDefault();
            alert('글이 성공적으로 등록되었습니다.');
            closeWriteModal();
        });
    }

    /* --- 6. 게시글 상세보기 모달 제어 --- */
    function openDetailModal(post) {
        if (post && post.id) {
            window.location.href = post.detail_url || `/post/detail/${post.id}/`;
            return;
        }
        const modal = document.getElementById('postDetailModal');
        if (!modal) return;
        modal.classList.add('active');
    }

    const btnCloseDetail = document.getElementById('btnCloseDetail');
    if (btnCloseDetail) {
        btnCloseDetail.addEventListener('click', (e) => {
            const href = btnCloseDetail.getAttribute('href');
            if (href && !href.startsWith('#')) {
                return;
            }
            e.preventDefault();
            closeDetailModal(e);
        });
    }

    function closeDetailModal(e) {
        if (e) e.preventDefault();
        const modal = document.getElementById('postDetailModal');
        const backUrl = modal?.dataset.backUrl;
        const currentPath = window.location.pathname;
        if (backUrl && backUrl !== currentPath && !currentPath.includes(backUrl)) {
            window.location.href = backUrl;
            return;
        }
        if (window.history.length > 1) {
            window.history.back();
            return;
        }
        modal?.classList.remove('active');
        document.getElementById('commentForm')?.reset();
        hideDetailDropdown();
    }

    const postDetailModalEl = document.getElementById('postDetailModal');
    if (postDetailModalEl?.classList.contains('active')) {
        postDetailModalEl.addEventListener('click', (e) => {
            if (e.target === postDetailModalEl) {
                const backUrl = postDetailModalEl.dataset.backUrl;
                if (backUrl) {
                    window.location.href = backUrl;
                }
            }
        });
    }

    // 모달 우측 상단 더보기(...) 내림 메뉴 토글
    const btnDetailMore = document.getElementById('btnDetailMore');
    const detailDropdownMenu = document.getElementById('detailDropdownMenu');

    if (btnDetailMore && detailDropdownMenu) {
        btnDetailMore.addEventListener('click', (e) => {
            e.stopPropagation();
            detailDropdownMenu.classList.toggle('hidden');
        });
    }

    function hideDetailDropdown() {
        if (detailDropdownMenu) {
            detailDropdownMenu.classList.add('hidden');
        }
    }

    // 상세보기 모달 우측 상단 팝업 메뉴 액션 버튼
    document.getElementById('btnDetailCancel')?.addEventListener('click', () => {
        hideDetailDropdown();
    });

    // 댓글 이미지 미리보기
    const commentImageUpload = document.getElementById('commentImageUpload');
    if (commentImageUpload) {
        commentImageUpload.addEventListener('change', (event) => {
            const previewContainer = document.getElementById('commentImagePreview');
            if (!previewContainer) return;
            previewContainer.innerHTML = '';
            Array.from(event.target.files || []).forEach((file) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'preview-img';
                    previewContainer.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // 댓글 등록 처리 (서버 폼은 그대로 submit)
    const commentFormEl = document.getElementById('commentForm');
    if (commentFormEl) {
        commentFormEl.addEventListener('submit', (e) => {
            if (commentFormEl.getAttribute('action')) {
                return;
            }

            e.preventDefault();
            const input = document.getElementById('commentInput');
            if (!input || input.value.trim() === '') return;

            const commentList = document.getElementById('commentList');
            const newComment = document.createElement('div');
            newComment.className = 'comment-item';
            newComment.innerHTML = `
            <div class="d-flex align-items-start gap-2">
                <div class="comment-profile-circle flex-shrink-0"></div>
                <div>
                    <div class="fw-bold small text-dark">작성자</div>
                    <div class="small text-secondary">${escapeHtml(input.value)}</div>
                </div>
            </div>
        `;
            commentList.appendChild(newComment);
            input.value = '';

            const mainCount = document.getElementById('mainCommentCount');
            const current = parseInt(mainCount.innerText) || 0;
            mainCount.innerText = current + 1;
            document.getElementById('bottomCommentCount').innerText = current + 1;
        });
    }

    // 메인 더보기(...) 옵션 팝업 닫기 처리
    const btnCloseModal = document.getElementById('btnCloseModal');
    if (btnCloseModal) {
        btnCloseModal.addEventListener('click', () => {
            document.getElementById('postOptionModal').classList.add('hidden');
        });
    }

    // 배경 클릭 시 드롭다운 및 모달 닫기 이벤트
    window.addEventListener('click', (e) => {
        hideDetailDropdown();
        
        const optionModal = document.getElementById('postOptionModal');
        if (e.target === optionModal) {
            optionModal.classList.add('hidden');
        }
    });

    // HTML 태그 이스케이프 함수
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // 더미 데이터 생성기 (제목 없는 스펙 반영)
    function getDummyPosts() {
        const dummy = [];
        for (let i = 1; i <= 10; i++) {
            dummy.push({
                id: i,
                author: 'Author Name ' + i,
                created_at: '2024.08.13',
                like_count: i * 2,
                comment_count: i,
                view_count: 156 + i
            });
        }
        return dummy;
    }
});