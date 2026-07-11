// ======================================
// DOCUMENTATION SEARCH
// ======================================

document.addEventListener(

    "DOMContentLoaded",

    () => {

        initializeAPISearch();
    }
);


// ======================================
// INITIALIZE SEARCH
// ======================================

function initializeAPISearch() {

    const searchInput = document.getElementById(

        "apiSearch"
    );

    if (!searchInput) return;

    searchInput.addEventListener(

        "input",

        handleSearch
    );
}


// ======================================
// HANDLE SEARCH
// ======================================

function handleSearch(event) {

    const searchValue = event.target.value

        .toLowerCase()

        .trim();

    // ==================================
    // ALL DOC SECTIONS
    // ==================================

    const sections = document.querySelectorAll(

        ".doc-section"
    );

    const categoryHeadings = document.querySelectorAll(

        ".category-heading"
    );

    // ==================================
    // ALL SIDEBAR LINKS
    // ==================================

    const sidebarLinks = document.querySelectorAll(

        ".sidebar-link"
    );

    // ==================================
    // FILTER DOC SECTIONS
    // ==================================

    let visibleSections = 0;

    const visibleCategories = new Set();

    sections.forEach(section => {

        const sectionText = section.innerText

            .toLowerCase();

        const sectionCategory = (

            section.dataset.category || ""

        ).toLowerCase();

        const isVisible = sectionText.includes(

            searchValue

        ) || sectionCategory.includes(

            searchValue
        );

        section.style.display = isVisible

            ? "block"

            : "none";

        if (isVisible) {

            visibleSections++;

            visibleCategories.add(

                section.dataset.category
            );
        }
    });

    categoryHeadings.forEach(heading => {

        heading.style.display = visibleCategories.has(

            heading.dataset.category

        ) || searchValue === ""

            ? "block"

            : "none";
    });

    // ==================================
    // FILTER SIDEBAR LINKS
    // ==================================

    sidebarLinks.forEach(link => {

        const linkText = link.innerText

            .toLowerCase();

        const isVisible = linkText.includes(

            searchValue
        );

        link.style.display = isVisible

            ? "block"

            : "none";
    });

    // ==================================
    // HANDLE EMPTY STATE
    // ==================================

    handleEmptyState(visibleSections);

    // ==================================
    // HANDLE CATEGORY VISIBILITY
    // ==================================

    handleCategoryVisibility();
}


// ======================================
// CATEGORY VISIBILITY
// ======================================

function handleCategoryVisibility() {

    const categories = document.querySelectorAll(

        ".sidebar-category"
    );

    categories.forEach(category => {

        const visibleLinks = category.querySelectorAll(

            '.sidebar-link[style*="block"]'
        );

        category.style.display = visibleLinks.length > 0

            ? "block"

            : "none";
    });
}


// ======================================
// EMPTY STATE
// ======================================

function handleEmptyState(count) {

    let emptyState = document.getElementById(

        "search-empty-state"
    );

    // ==================================
    // CREATE EMPTY STATE
    // ==================================

    if (!emptyState) {

        emptyState = document.createElement("div");

        emptyState.id = "search-empty-state";

        emptyState.className = "search-empty-state";

        emptyState.innerHTML = `

<div class="empty-state-content">

    <i class="bi bi-search"></i>

    <h3>

        No APIs Found

    </h3>

    <p>

        Try searching with another keyword.

    </p>

</div>

        `;

        const content = document.querySelector(

            ".documentation-content"
        );

        if (content) {

            content.appendChild(emptyState);
        }
    }

    // ==================================
    // SHOW/HIDE EMPTY STATE
    // ==================================

    emptyState.style.display = count === 0

        ? "flex"

        : "none";
}
