// =====================================
// API TESTER LOGIC
// =====================================


// =====================================
// LOAD API DOCS
// =====================================

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

        renderApiDocs(result.data);
    }

    catch (error) {

        console.error(
            "Failed to load API docs:",
            error
        );
    }
}


// =====================================
// RENDER API DOCS
// =====================================

function renderApiDocs(apiDocs) {

    const container = document.getElementById(
        "api-docs-container"
    );

    if (!container) {

        return;
    }

    container.innerHTML = "";

    // =================================
    // LOOP THROUGH CATEGORIES
    // =================================

    Object.keys(apiDocs).forEach(category => {

        const categoryApis = apiDocs[category];

        // =============================
        // CATEGORY TITLE
        // =============================

        const categoryTitle = document.createElement(
            "div"
        );

        categoryTitle.className = "api-category";

        categoryTitle.innerHTML = `

            <h2 class="api-category-title">

                ${category.toUpperCase()}

            </h2>

        `;

        container.appendChild(categoryTitle);

        // =============================
        // LOOP APIS
        // =============================

        categoryApis.forEach(api => {

            const card = document.createElement(
                "div"
            );

            card.className = "api-card";

            // =========================
            // QUERY PARAMS HTML
            // =========================

            let queryInputs = "";

            if (
                api.query_params &&
                api.query_params.length > 0
            ) {

                api.query_params.forEach(param => {

                    queryInputs += `

<div class="mb-3">

    <label class="form-label">

        ${param.name}

    </label>

    <input
        type="text"
        class="form-control api-input"
        id="${api.id}-${param.name}"
        placeholder="${param.example || ''}"
    >

</div>

                    `;
                });
            }

            // =========================
            // CARD HTML
            // =========================

            card.innerHTML = `

<div class="api-card-header">

    <span class="api-method">

        ${api.method}

    </span>

    <code class="api-route">

        ${api.route}

    </code>

</div>

<h3 class="api-title">

    ${api.title}

</h3>

<p class="api-description">

    ${api.description}

</p>

<div class="api-inputs">

    ${queryInputs}

</div>

<div class="api-actions">

    <button
        class="btn btn-primary run-api-btn"
        onclick="runAPI(
            '${api.route}',
            '${api.id}'
        )"
    >

        Run API

    </button>

</div>

<div
    id="response-${api.id}"
    class="api-response-box"
    style="display:none;"
></div>

            `;

            container.appendChild(card);
        });
    });
}


// =====================================
// LIVE API TESTER
// =====================================

async function runAPI(route, apiId) {

    // =================================
    // RESPONSE BOX
    // =================================

    const responseBox = document.getElementById(
        `response-${apiId}`
    );

    if (!responseBox) {

        return;
    }

    responseBox.style.display = "block";

    // =================================
    // LOADING STATE
    // =================================

    responseBox.innerHTML = `

<div class="loading-box">

    <div class="spinner-border text-light"></div>

    <p class="mt-3 mb-0">

        Loading API response...

    </p>

</div>

    `;

    // =================================
    // BUILD QUERY PARAMETERS
    // =================================

    const params = new URLSearchParams();

    let finalURL = route;

    const inputs = document.querySelectorAll(
        `[id^="${apiId}-"]`
    );

    inputs.forEach(input => {

        const value = input.value.trim();

        if (value) {

            const paramName = input.id.replace(
                `${apiId}-`,
                ""
            );

            const anglePlaceholder = `<${paramName}>`;

            const bracePlaceholder = `{${paramName}}`;

            if (finalURL.includes(anglePlaceholder)) {

                finalURL = finalURL.replaceAll(
                    anglePlaceholder,
                    encodeURIComponent(value)
                );
            }

            else if (finalURL.includes(bracePlaceholder)) {

                finalURL = finalURL.replaceAll(
                    bracePlaceholder,
                    encodeURIComponent(value)
                );
            }

            else {

                params.append(
                    paramName,
                    value
                );
            }
        }
    });

    // =================================
    // BUILD FINAL URL
    // =================================

    if ([...params].length > 0) {

        finalURL += `?${params.toString()}`;
    }

    // =================================
    // FETCH API
    // =================================

    try {

        // =============================
        // START TIMER
        // =============================

        const startTime = performance.now();

        const response = await fetch(
            finalURL
        );

        // =============================
        // END TIMER
        // =============================

        const endTime = performance.now();

        const responseTime =
            Math.round(endTime - startTime);

        const data = await response.json();

        // =============================
        // SUCCESS RESPONSE
        // =============================

        responseBox.innerHTML = `

<div class="response-top">

    <div class="response-actions">

        <span class="success-badge">

            ${response.status}
            ${response.statusText}

        </span>

        <span class="response-time-badge">

            ${responseTime} ms

        </span>

    </div>

    <div class="response-buttons">

        <button
            class="clear-response-btn"
            onclick="clearResponse('${apiId}')"
        >

            <i class="bi bi-trash"></i>

            Clear

        </button>

        <button
            class="response-copy-btn"
            onclick='copyText(
                JSON.stringify(
                    ${JSON.stringify(data)},
                    null,
                    4
                )
            )'
        >

            <i class="bi bi-copy"></i>

            Copy Response

        </button>

    </div>

</div>

<div class="response-url-box">

    <span class="response-url-label">

        Request URL

    </span>

    <div class="response-url-content">

        <code>

            ${window.location.origin}${finalURL}

        </code>

        <button
            class="mini-copy-btn"
            onclick="copyText(
                '${window.location.origin}${finalURL}'
            )"
        >

            <i class="bi bi-copy"></i>

        </button>

    </div>

</div>

<pre class="response-json">

${JSON.stringify(data, null, 4)}

</pre>

        `;
    }

    // =================================
    // ERROR HANDLING
    // =================================

    catch (error) {

        responseBox.innerHTML = `

<div class="error-box">

    <span class="error-status">

        ERROR

    </span>

    <pre class="error-response">

${error}

    </pre>

</div>

        `;
    }
}


// =====================================
// CLEAR RESPONSE
// =====================================

function clearResponse(apiId) {

    const responseBox = document.getElementById(
        `response-${apiId}`
    );

    if (!responseBox) return;

    responseBox.innerHTML = `

<pre class="response-json">
{
    "message": "Response cleared"
}
</pre>

    `;
}


// =====================================
// INITIALIZE
// =====================================

document.addEventListener(

    "DOMContentLoaded",

    () => {

        loadApiDocs();
    }
);
