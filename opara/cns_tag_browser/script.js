document.addEventListener('DOMContentLoaded', function() {
    const randomTagBtn = document.getElementById('randomTagBtn');
    const randomTagSection = document.getElementById('randomTagSection');
    let randomTagInterval = null;
    const searchBar = document.getElementById('searchBar');
    const tagsList = document.getElementById('tagsList');
    const pagination = document.getElementById('pagination');
    const beatFilter = document.getElementById('beatFilter');
    const tagsDatalist = document.getElementById('tagsDatalist');
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
        // Populate datalist for search dropdown
        tagsDatalist.innerHTML = '';
        tags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag.name;
            tagsDatalist.appendChild(option);
        });
        allStories = storiesData;
        filteredTags = tags;
        renderTags();
        renderPagination();

        // --- Tag Comparison Feature ---
        const compareTag1 = document.getElementById('compareTag1');
        const compareTag2 = document.getElementById('compareTag2');
        const compareBtn = document.getElementById('compareBtn');
        const compareTagsSection = document.getElementById('compareTagsSection');

        // Populate tag dropdowns for comparison
        function populateCompareDropdowns() {
            if (!compareTag1 || !compareTag2) return;
            compareTag1.innerHTML = '<option value="">Select Tag 1</option>';
            compareTag2.innerHTML = '<option value="">Select Tag 2</option>';
            tags.forEach(tag => {
                const opt1 = document.createElement('option');
                opt1.value = tag.name;
                opt1.textContent = tag.name;
                compareTag1.appendChild(opt1);
                const opt2 = document.createElement('option');
                opt2.value = tag.name;
                opt2.textContent = tag.name;
                compareTag2.appendChild(opt2);
            });
        }

        // Show comparison of two tags
        function showTagComparison(tagName1, tagName2) {
            if (!tagName1 || !tagName2) return;
            compareTagsSection.style.display = 'flex';
            compareTagsSection.style.gap = '32px';
            compareTagsSection.innerHTML = '';
            [tagName1, tagName2].forEach((tagName, idx) => {
                const tag = tags.find(t => t.name === tagName);
                if (!tag) return;
                const tagDiv = document.createElement('div');
                tagDiv.className = 'tag-item';
                tagDiv.style.flex = '1 1 0';
                tagDiv.innerHTML = `<span class="tag-name">${tag.name}</span><span class="tag-count">${tag.count}</span>`;
                // Find stories for this tag
                const stories = allStories.filter(story => story.tags && story.tags.some(t => t.toLowerCase() === tag.name.toLowerCase()));
                const previewDiv = document.createElement('div');
                previewDiv.className = 'story-previews';
                if (stories.length > 0) {
                    for (let i = 0; i < Math.min(2, stories.length); i++) {
                        const story = stories[i];
                        const storyDiv = document.createElement('div');
                        storyDiv.className = 'story-preview';
                        storyDiv.innerHTML = `<a href="${story.link}" target="_blank" class="story-title">${story.title}</a><div class="story-summary">${story.summary}</div>`;
                        previewDiv.appendChild(storyDiv);
                    }
                }
                if (stories.length < 2) {
                    const missingCount = 2 - stories.length;
                    for (let i = 0; i < missingCount; i++) {
                        const placeholder = document.createElement('div');
                        placeholder.className = 'story-preview';
                        placeholder.innerHTML = '<span class="preview-placeholder">Preview to be updated soon</span>';
                        previewDiv.appendChild(placeholder);
                    }
                }
                tagDiv.appendChild(previewDiv);
                compareTagsSection.appendChild(tagDiv);
            });
        }

        if (compareBtn) {
            compareBtn.addEventListener('click', () => {
                const tag1 = compareTag1.value;
                const tag2 = compareTag2.value;
                if (tag1 && tag2 && tag1 !== tag2) {
                    showTagComparison(tag1, tag2);
                }
            });
        }

        // Populate dropdowns after tags are loaded
        populateCompareDropdowns();
        // --- END Tag Comparison Feature ---

        // --- Updated Similar Tags Feature ---
        // Helper: get all stories for a tag
        function getStoriesForTag(tagName) {
            return allStories.filter(story => story.tags && story.tags.some(t => t.toLowerCase() === tagName.toLowerCase()));
        }
        // Helper: get all topics for a tag
        function getTopicsForTag(tagName) {
            const stories = getStoriesForTag(tagName);
            return Array.from(new Set(stories.map(story => story.topic).filter(Boolean)));
        }
        // Helper: get all summaries for a tag
        function getSummariesForTag(tagName) {
            return getStoriesForTag(tagName).map(story => story.summary).filter(Boolean);
        }
        // Helper: simple summary similarity (shared words, ignoring stopwords)
        function summarySimilarity(summariesA, summariesB) {
            if (!summariesA.length || !summariesB.length) return 0;
            const stopwords = new Set(['the','a','an','and','or','of','to','in','for','on','with','at','by','from','as','is','are','was','were','be','been','it','that','this','which','but','not','so','if','then','than','such','has','have','had','will','would','can','could','should','may','might','do','does','did','about','into','over','after','before','between','during','out','up','down','off','above','below','under','again','further','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','no','nor','only','own','same','too','very','s','t','just','don','now']);
            function tokenize(text) {
                return text.toLowerCase().replace(/[^a-z0-9 ]/g, '').split(/\s+/).filter(w => w && !stopwords.has(w));
            }
            const wordsA = new Set(summariesA.flatMap(tokenize));
            const wordsB = new Set(summariesB.flatMap(tokenize));
            const intersection = new Set([...wordsA].filter(x => wordsB.has(x)));
            return intersection.size / Math.max(1, Math.min(wordsA.size, wordsB.size));
        }
        // Helper: topic similarity
        function topicSimilarity(topicsA, topicsB) {
            if (!topicsA.length || !topicsB.length) return 0;
            const setA = new Set(topicsA);
            const setB = new Set(topicsB);
            const intersection = new Set([...setA].filter(x => setB.has(x)));
            return intersection.size / Math.max(1, Math.min(setA.size, setB.size));
        }
        // Find similar tags by summary or topic
        function findSimilarTagsSmart(selectedName) {
            if (!selectedName) return [];
            const selectedSummaries = getSummariesForTag(selectedName);
            const selectedTopics = getTopicsForTag(selectedName);
            return tags.filter(tag => {
                if (tag.name === selectedName) return false;
                const summaries = getSummariesForTag(tag.name);
                const topics = getTopicsForTag(tag.name);
                if (selectedSummaries.length && summaries.length) {
                    // Use summary similarity
                    return summarySimilarity(selectedSummaries, summaries) > 0.15;
                } else if (!selectedSummaries.length && !summaries.length && selectedTopics.length && topics.length) {
                    // Use topic similarity if both have no summaries
                    return topicSimilarity(selectedTopics, topics) > 0;
                }
                return false;
            });
        }
        if (findSimilarBtn) {
            findSimilarBtn.addEventListener('click', () => {
                const selected = similarTagSelect.value;
                if (!selected) return;
                const similars = findSimilarTagsSmart(selected);
                similarTagsSection.innerHTML = '';
                if (similars.length === 0) {
                    similarTagsSection.innerHTML = '<div>No similar tags found.</div>';
                } else {
                    const ul = document.createElement('ul');
                    ul.style.listStyle = 'none';
                    ul.style.padding = '0';
                    similars.forEach(tag => {
                        const li = document.createElement('li');
                        li.textContent = tag.name;
                        li.style.padding = '6px 0';
                        ul.appendChild(li);
                    });
                    similarTagsSection.appendChild(ul);
                }
            });
        }
        // Populate similar tag dropdown and ensure it matches the tag list
        function populateSimilarDropdown() {
            if (!similarTagSelect) return;
            similarTagSelect.innerHTML = '<option value="">Select a Tag</option>';
            tags.forEach(tag => {
                const hasSummaries = getSummariesForTag(tag.name).length > 0;
                const hasTopics = getTopicsForTag(tag.name).length > 0;
                if (hasSummaries || hasTopics) {
                    const opt = document.createElement('option');
                    opt.value = tag.name;
                    opt.textContent = tag.name;
                    similarTagSelect.appendChild(opt);
                }
            });
        }
        // Ensure random tag button uses the tags array for random selection (already implemented)
        // Ensure all dropdowns are updated after tags are loaded
        populateCompareDropdowns();
        populateSimilarDropdown();
        // --- END Updated Similar Tags Feature ---

        // Random tag button logic
        if (randomTagBtn) {
            randomTagBtn.addEventListener('click', () => {
                showRandomTag();
                if (randomTagInterval) clearInterval(randomTagInterval);
                randomTagInterval = setInterval(showRandomTag, 60 * 1000); // 1 minute
            });
        }

        function showRandomTag() {
            if (!tags.length) return;
            const tag = tags[Math.floor(Math.random() * tags.length)];
            randomTagSection.style.display = 'block';
            randomTagSection.innerHTML = `<div class="tag-item"><span class="tag-name">${tag.name}</span><span class="tag-count">${tag.count}</span></div>`;
            // Find stories for this tag
            const stories = allStories.filter(story => story.tags && story.tags.some(t => t.toLowerCase() === tag.name.toLowerCase()));
            const previewDiv = document.createElement('div');
            previewDiv.className = 'story-previews';
            if (stories.length > 0) {
                for (let i = 0; i < Math.min(2, stories.length); i++) {
                    const story = stories[i];
                    const storyDiv = document.createElement('div');
                    storyDiv.className = 'story-preview';
                    storyDiv.innerHTML = `<a href="${story.link}" target="_blank" class="story-title">${story.title}</a><div class="story-summary">${story.summary}</div>`;
                    previewDiv.appendChild(storyDiv);
                }
            }
            if (stories.length < 2) {
                const missingCount = 2 - stories.length;
                for (let i = 0; i < missingCount; i++) {
                    const placeholder = document.createElement('div');
                    placeholder.className = 'story-preview';
                    placeholder.innerHTML = '<span class="preview-placeholder">Preview to be updated soon</span>';
                    previewDiv.appendChild(placeholder);
                }
            }
            randomTagSection.querySelector('.tag-item').appendChild(previewDiv);
        }
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
            const previewDiv = document.createElement('div');
            previewDiv.className = 'story-previews';
            if (stories.length > 0) {
                for (let i = 0; i < Math.min(2, stories.length); i++) {
                    const story = stories[i];
                    const storyDiv = document.createElement('div');
                    storyDiv.className = 'story-preview';
                    storyDiv.innerHTML = `<a href="${story.link}" target="_blank" class="story-title">${story.title}</a><div class="story-summary">${story.summary}</div>`;
                    previewDiv.appendChild(storyDiv);
                }
            }
            if (stories.length < 2) {
                const missingCount = 2 - stories.length;
                for (let i = 0; i < missingCount; i++) {
                    const placeholder = document.createElement('div');
                    placeholder.className = 'story-preview';
                    placeholder.innerHTML = '<span class="preview-placeholder">Preview to be updated soon</span>';
                    previewDiv.appendChild(placeholder);
                }
            }
            if (stories.length > 0 || stories.length < 2) {
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
