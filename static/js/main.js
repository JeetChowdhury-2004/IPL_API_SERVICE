// ======================================
// DOM READY
// ======================================

document.addEventListener(

    "DOMContentLoaded",

    () => {

        initializeTooltips();

        initializeNavbar();

        initializeSmoothScroll();

        initializeScrollTop();

        loadApiDocs();
    }
);


// ======================================
// LOAD API DOCS
// ======================================

async function loadApiDocs() {

    try {

        const response = await fetch(
            "/api-docs"
        );

        const result = await response.json();

        console.log(
            "API DOCS LOADED:",
            result
        );
    }

    catch (error) {

        console.error(
            "Failed to load API docs:",
            error
        );
    }
}


// ======================================
// TOOLTIPS
// ======================================

function initializeTooltips() {

    const tooltipTriggerList = [].slice.call(

        document.querySelectorAll(
            '[data-bs-toggle="tooltip"]'
        )
    );

    tooltipTriggerList.map(

        tooltipTriggerEl =>

            new bootstrap.Tooltip(
                tooltipTriggerEl
            )
    );
}


// ======================================
// NAVBAR EFFECT
// ======================================

function initializeNavbar() {

    const navbar = document.querySelector(
        ".custom-navbar"
    );

    if (!navbar) return;

    window.addEventListener(

        "scroll",

        () => {

            if (window.scrollY > 50) {

                navbar.classList.add(
                    "navbar-scrolled"
                );
            }

            else {

                navbar.classList.remove(
                    "navbar-scrolled"
                );
            }
        }
    );
}


// ======================================
// SMOOTH SCROLL
// ======================================

function initializeSmoothScroll() {

    document.querySelectorAll(
        'a[href^="#"]'
    ).forEach(anchor => {

        anchor.addEventListener(

            "click",

            function(e) {

                const targetId =
                    this.getAttribute(
                        "href"
                    );

                if (

                    targetId.length > 1 &&

                    document.querySelector(targetId)

                ) {

                    e.preventDefault();

                    document.querySelector(targetId)

                        .scrollIntoView({

                            behavior: "smooth",

                            block: "start"
                        });
                }
            }
        );
    });
}


// ======================================
// SCROLL TO TOP
// ======================================

function initializeScrollTop() {

    const scrollBtn =
        document.getElementById(
            "scrollTopBtn"
        );

    if (!scrollBtn) return;

    window.addEventListener(

        "scroll",

        () => {

            if (window.scrollY > 300) {

                scrollBtn.style.display = "flex";
            }

            else {

                scrollBtn.style.display = "none";
            }
        }
    );

    scrollBtn.addEventListener(

        "click",

        () => {

            window.scrollTo({

                top: 0,

                behavior: "smooth"
            });
        }
    );
}


// ======================================
// COPY TO CLIPBOARD
// ======================================

function copyText(text) {

    navigator.clipboard.writeText(text)

        .then(() => {

            showToast(
                "Copied Successfully"
            );
        })

        .catch(error => {

            console.error(error);

            showToast(
                "Copy Failed",
                "error"
            );
        });
}

// ======================================
// TOAST MESSAGE
// ======================================

function showToast(message, type = "success") {

    let toast = document.getElementById(
        "custom-toast"
    );

    // ==============================
    // CREATE TOAST
    // ==============================

    if (!toast) {

        toast = document.createElement("div");

        toast.id = "custom-toast";

        toast.className = "custom-toast";

        document.body.appendChild(toast);
    }

    // ==============================
    // ICONS
    // ==============================

    let icon = "";

    if (type === "success") {

        icon = `<i class="bi bi-check-circle-fill"></i>`;
    }

    else if (type === "error") {

        icon = `<i class="bi bi-x-circle-fill"></i>`;
    }

    // ==============================
    // MESSAGE
    // ==============================

    toast.innerHTML = `
        ${icon}
        <span>${message}</span>
    `;

    // ==============================
    // STYLES
    // ==============================

    toast.classList.add("show");

    // ==============================
    // REMOVE
    // ==============================

    setTimeout(() => {

        toast.classList.remove("show");

    }, 2200);
}

// ======================================
// TOGGLE API CARD
// ======================================

function toggleApiCard(apiId) {

    const body =
        document.getElementById(
            `api-body-${apiId}`
        );

    if (!body) return;

    body.classList.toggle(
        "active"
    );
}

// ======================================
// ACTIVE SIDEBAR LINK
// ======================================

const sidebarLinks = document.querySelectorAll(

    ".sidebar-link"
);

window.addEventListener(

    "scroll",

    () => {

        let currentSection = "";

        document
            .querySelectorAll(".doc-section")
            .forEach(section => {

                const sectionTop =
                    section.offsetTop - 120;

                if (

                    scrollY >= sectionTop
                ) {

                    currentSection =
                        section.getAttribute("id");
                }
            });

        sidebarLinks.forEach(link => {

            link.classList.remove("active");

            if (

                link.getAttribute("href") ===
                `#${currentSection}`
            ) {

                link.classList.add("active");
            }
        });
    }
);