document.addEventListener(

    "DOMContentLoaded",

    () => {

        initializeAvailableDataSearch();
    }
);


function initializeAvailableDataSearch() {

    const sections = document.querySelectorAll(

        "[data-available-section]"
    );

    sections.forEach(section => {

        const input = section.querySelector(

            ".data-search-input"
        );

        const pills = section.querySelectorAll(

            ".data-pill"
        );

        const count = section.querySelector(

            ".data-search-count"
        );

        if (!input || !count) {

            return;
        }

        input.addEventListener(

            "click",

            event => {

                event.stopPropagation();
            }
        );

        input.addEventListener(

            "input",

            () => {

                filterAvailableData(

                    input.value,

                    pills,

                    count
                );
            }
        );
    });
}


function filterAvailableData(searchValue, pills, count) {

    const normalizedSearch = searchValue

        .toLowerCase()

        .trim();

    let visibleCount = 0;

    pills.forEach(pill => {

        const value = pill.dataset.value || "";

        const isVisible = value.includes(

            normalizedSearch
        );

        pill.style.display = isVisible

            ? "inline-flex"

            : "none";

        if (isVisible) {

            visibleCount++;
        }
    });

    count.textContent = `${visibleCount} / ${pills.length}`;
}
