document.addEventListener('DOMContentLoaded', function() {
    const searchBar = document.getElementById('searchBar');
    const tagsList = document.getElementById('tagsList');
    const pagination = document.getElementById('pagination');
    const beatFilter = document.getElementById('beatFilter');
    let tags = [];
    let filteredTags = [];
    let allStories = [];
    let currentPage = 1;
    const tagsPerPage = 30;

    // Map of beats to example tags (should be replaced with real mapping if available)
    const beatTagMap = {
        'Politics': ['Elections', 'Maryland Government and Politics', 'Federal Government and Politics'],
        'Health': ['Health', 'Cancer Research', 'NIH'],
        'Crime': ['Crime', 'Public Safety', 'FBI'],
        'Community': ['Community', 'Baltimore', 'Neighborhood', 'Remington'],
        'Lifestyle': ['Lifestyle', 'Arts & Culture', 'Songwriters Festival', 'Emmy Awards']
    };

    // Fetch tags and stories
    Promise.all([
        fetch('../../data/tags.json').then(r => r.json()),
        fetch('../../data/story_summaries.json').then(r => r.json())
    ]).then(([tagsData, storiesData]) => {
        tags = tagsData.map(tag => ({
            name: tag.name,
            count: tag.count
        }));
        tags.sort((a, b) => a.name.localeCompare(b.name));
        allStories = storiesData;
        filteredTags = tags;
        renderTags();
        renderPagination();
    });

    searchBar.addEventListener('input', filterAndRender);
    beatFilter.addEventListener('change', filterAndRender);

    function filterAndRender() {
        const query = searchBar.value.toLowerCase();
        const beat = beatFilter.value;
        filteredTags = tags.filter(tag => {
            const matchesSearch = tag.name.toLowerCase().includes(query);
            if (!beat) return matchesSearch;
            // Check if tag is in the beat's tag list (case-insensitive)
            return matchesSearch && beatTagMap[beat].some(bt => tag.name.toLowerCase().includes(bt.toLowerCase()));
        });
        currentPage = 1;
        renderTags();
        renderPagination();
    }

    function renderTags() {
        tagsList.innerHTML = '';
        const start = (currentPage - 1) * tagsPerPage;
        const end = start + tagsPerPage;
        const pageTags = filteredTags.slice(start, end);
        for (const tag of pageTags) {
            const li = document.createElement('li');
            li.className = 'tag-item';
            li.innerHTML = `<span class="tag-name">${tag.name}</span><span class="tag-count">${tag.count}</span>`;

            // Add story previews
            const stories = allStories.filter(story => story.tags && story.tags.some(t => t.toLowerCase() === tag.name.toLowerCase()));
            if (stories.length > 0) {
                const previewDiv = document.createElement('div');
                previewDiv.className = 'story-previews';
                for (let i = 0; i < Math.min(2, stories.length); i++) {
                    const story = stories[i];
                    const storyDiv = document.createElement('div');
                    storyDiv.className = 'story-preview';
                    storyDiv.innerHTML = `<a href="${story.link}" target="_blank" class="story-title">${story.title}</a><div class="story-summary">${story.summary}</div>`;
                    previewDiv.appendChild(storyDiv);
                }
                li.appendChild(previewDiv);
            }
            tagsList.appendChild(li);
        }
        if (pageTags.length === 0) {
            tagsList.innerHTML = '<li class="tag-item">No tags found.</li>';
        }
    }

    function renderPagination() {
        pagination.innerHTML = '';
        const totalPages = Math.ceil(filteredTags.length / tagsPerPage);
        const leftArrow = document.createElement('button');
        leftArrow.className = 'page-arrow';
        leftArrow.innerHTML = '&#8592;';
        leftArrow.disabled = currentPage === 1;
        leftArrow.onclick = () => {
            if (currentPage > 1) {
                currentPage--;
                renderTags();
                renderPagination();
            }
        };
        pagination.appendChild(leftArrow);

        // Show up to 7 page numbers, centered on current page
        let startPage = Math.max(1, currentPage - 3);
        let endPage = Math.min(totalPages, currentPage + 3);
        if (currentPage <= 4) endPage = Math.min(7, totalPages);
        if (currentPage > totalPages - 4) startPage = Math.max(1, totalPages - 6);
        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement('button');
            btn.className = 'page-btn' + (i === currentPage ? ' active' : '');
            btn.textContent = i;
            btn.onclick = () => {
                currentPage = i;
                renderTags();
                renderPagination();
            };
            pagination.appendChild(btn);
        }

        const rightArrow = document.createElement('button');
        rightArrow.className = 'page-arrow';
        rightArrow.innerHTML = '&#8594;';
        rightArrow.disabled = currentPage === totalPages || totalPages === 0;
        rightArrow.onclick = () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderTags();
                renderPagination();
            }
        };
        pagination.appendChild(rightArrow);
    }
});
