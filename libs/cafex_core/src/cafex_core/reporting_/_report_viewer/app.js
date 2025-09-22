document.addEventListener("DOMContentLoaded", () => {
    renderSummary(reportData);
    setupTabs(reportData);
    setupLogs(reportData);
});

function renderSummary(data) {
// Format Date-Time
const formatDate = (isoDate) => {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'  // Added seconds
    };
    return new Date(isoDate).toLocaleDateString('en-US', options);
};

    // Populate Collection Info
    document.getElementById("testCount").textContent = data.collectionInfo.testCount;
    document.getElementById("pytestCount").textContent = data.collectionInfo.pytestCount;
    document.getElementById("pytestBddCount").textContent = data.collectionInfo.pytestBddCount;
    document.getElementById("unittestCount").textContent = data.collectionInfo.unittestCount;

    // Populate Execution Info
    const executionInfo = data.executionInfo;
    document.getElementById("executionId").textContent = executionInfo.executionId;
    const statusElement = document.getElementById("executionStatus");
    statusElement.textContent = executionInfo.executionStatus === "P" ? "Pass" : "Fail";
    statusElement.classList.add(executionInfo.executionStatus === "P" ? "pass" : "fail");
    document.getElementById("executionStartTime").textContent = formatDate(executionInfo.executionStartTime);
    document.getElementById("executionEndTime").textContent = formatDate(executionInfo.executionEndTime);
    document.getElementById("executionDuration").textContent = executionInfo.executionDuration;
    document.getElementById("totalPassed").textContent = executionInfo.totalPassed;
    document.getElementById("totalFailed").textContent = executionInfo.totalFailed;
    document.getElementById("isParallel").textContent = executionInfo.isParallel ? "True" : "False";

    // Populate Framework Versions
    const frameworkVersions = executionInfo.frameworkVersions;
    document.getElementById("cafex").textContent = frameworkVersions["cafex"];
    document.getElementById("cafexCore").textContent = frameworkVersions["cafex-core"];
    document.getElementById("cafexApi").textContent = frameworkVersions["cafex-api"];
    document.getElementById("cafexDb").textContent = frameworkVersions["cafex-db"];
    document.getElementById("cafexUi").textContent = frameworkVersions["cafex-ui"];

    // Populate Environment Details
    document.getElementById("browser").textContent = executionInfo.browser;
    document.getElementById("executionTags").textContent = executionInfo.executionTags;
    document.getElementById("environment").textContent = executionInfo.environment;
    document.getElementById("user").textContent = executionInfo.user;
}

function setupTabs(data) {
    const testDetailsContainer = document.getElementById("test-details-container");

    // Get all buttons
    const pytestBddBtn = document.getElementById("btn-pytestBdd");
    const pytestBtn = document.getElementById("btn-pytest");
    const unittestBtn = document.getElementById("btn-unittest");

    // Update button text with counts
    if (pytestBddBtn) pytestBddBtn.textContent = `Pytest-BDD (${data.collectionInfo.pytestBddCount})`;
    if (pytestBtn) pytestBtn.textContent = `Pytest (${data.collectionInfo.pytestCount})`;
    if (unittestBtn) unittestBtn.textContent = `Unittest (${data.collectionInfo.unittestCount})`;

    // Disable buttons for empty test types
    ["pytestBdd", "pytest", "unittest"].forEach((testType) => {
        const button = document.getElementById(`btn-${testType}`);
        if (button && data.collectionInfo[`${testType}Count`] === 0) {
            button.disabled = true;
        }
    });

    // Add click handlers
    function showTests(testType) {
        if (!data.tests[testType]) return;

        testDetailsContainer.innerHTML = data.tests[testType]
            .map((test) => renderTest(test, testType))
            .join("");

        setupCollapsible();
    }

    // Attach click handlers
    if (pytestBddBtn) pytestBddBtn.onclick = () => showTests('pytestBdd');
    if (pytestBtn) pytestBtn.onclick = () => showTests('pytest');
    if (unittestBtn) unittestBtn.onclick = () => showTests('unittest');

    // Show first non-empty test type by default
    ['pytestBdd', 'pytest', 'unittest'].forEach(testType => {
        if (data.tests[testType] && data.tests[testType].length > 0) {
            showTests(testType);
            return;
        }
    });
}

function renderTest(test, testType) {
    const featureDetails =
        testType === "pytestBdd"
            ? `<p><strong>Feature:</strong> ${test.scenario.featureName}</p>
               <p><strong>Scenario:</strong> ${test.scenario.scenarioName}</p>`
            : "";

    const testExceptions = test.evidence?.exceptions?.filter(e => e.phase === 'test') || [];

    return `
        <div class="test-details">
            <div class="collapsible-header">
                <span class="toggle-indicator">▼</span>
                <h3>Test: ${test.name}</h3>
                <span class="status-indicator ${test.testStatus === "P" ? "pass" : "fail"}">
                    ${test.testStatus === "P" ? "Pass" : "Fail"}
                </span>
            </div>
            <div class="collapsible-body">
                <p><strong>Duration:</strong> ${test.duration}</p>
                <p><strong>Tags:</strong> ${test.tags.join(", ")}</p>
                ${featureDetails}
                ${testExceptions.length > 0 ? `
                    <div class="test-exceptions">
                        <h4>Test Exceptions</h4>
                        ${testExceptions.map(renderException).join('')}
                    </div>
                ` : ''}
                ${test.steps ? renderSteps(test.steps) : ""}
            </div>
        </div>`;
}

function renderSteps(steps) {
    return steps.map(step => {
        const stepExceptions = step.evidence?.exceptions || [];

        return `
            <div class="step">
                <div class="collapsible-header">
                    <span class="toggle-indicator">▼</span>
                    <h4>Step: ${step.stepName}</h4>
                    <span class="status-indicator ${step.stepStatus === "P" ? "pass" : "fail"}">
                        ${step.stepStatus === "P" ? "Pass" : "Fail"}
                    </span>
                </div>
                <div class="collapsible-body">
                    <div class="details-and-screenshot">
                        <div class="details">
                            <p><strong>Start Time:</strong> ${step.stepStartTime}</p>
                            <p><strong>End Time:</strong> ${step.stepEndTime}</p>
                            <p><strong>Duration:</strong> ${step.stepDuration}</p>
                        </div>
                        <div class="screenshot">
                            ${step.screenshot ? renderScreenshot(step.screenshot) : ""}
                        </div>
                    </div>
                    ${stepExceptions.length > 0 ? `
                        <div class="step-exceptions">
                            <h4>Step Exceptions</h4>
                            ${stepExceptions.map(renderException).join('')}
                        </div>
                    ` : ''}
                    ${renderAssertions(step.asserts)}
                </div>
            </div>`
    }).join("");
}

function renderAssertions(asserts) {
    if (!asserts) return "";
    return asserts
        .map((assertion) => {
            let label = "Assert";
            if (assertion.type === "verify") label = "Verify";
            else if (assertion.type === "step") label = "Sub Step";

            return `
            <div class="assertion">
                <div class="collapsible-header">
                    <span class="toggle-indicator">▼</span>
                    <p><strong>${label}:</strong> ${assertion.name}</p>
                    <span class="status-indicator ${assertion.status === "P" ? "pass" : "fail"}">
                        ${assertion.status === "P" ? "Pass" : "Fail"}
                    </span>
                </div>
                <div class="collapsible-body">
                    <div class="details-and-screenshot">
                        <div class="details">
                            <p><strong>Expected:</strong> ${assertion.expected}</p>
                            <p><strong>Actual:</strong> ${assertion.actual}</p>
                        </div>
                        <div class="screenshot">
                            ${assertion.screenshot ? renderScreenshot(assertion.screenshot) : ""}
                        </div>
                    </div>
                </div>
            </div>`;
        })
        .join("");
}

function renderScreenshot(path) {
    const fileName = path.split(/[/\\]/).pop();
    return `<img src="screenshots/${fileName}" alt="Screenshot" onclick="openInNewTab('screenshots/${fileName}')">`;
}

function openInNewTab(url) {
    window.open(url, "_blank");
}

function setupCollapsible() {
    document.querySelectorAll(".collapsible-header").forEach((header) => {
        header.addEventListener("click", () => {
            const body = header.nextElementSibling;
            const indicator = header.querySelector(".toggle-indicator");

            body.classList.toggle("active");
            indicator.textContent = body.classList.contains("active") ? "▲" : "▼";
        });
    });
}

function renderException(exception) {
    return `
        <div class="exception-details">
            <div class="exception-header">
                <span class="exception-type">${exception.type}</span>
                <span class="exception-timestamp">${exception.timestamp}</span>
            </div>
            <div class="details-and-screenshot">
                <div class="details">
                    <div class="exception-message">
                        <strong>Message:</strong>
                        <pre>${exception.message}</pre>
                    </div>
                    ${exception.stackTrace ? `
                        <div class="exception-stack">
                            <strong>Stack Trace:</strong>
                            <pre>${exception.stackTrace}</pre>
                        </div>
                    ` : ''}
                </div>
                ${exception.screenshot ? `
                    <div class="screenshot">
                        <img src="./screenshots/${exception.screenshot.split('\\').pop()}"
                             alt="Exception Screenshot"
                             onclick="openInNewTab('./screenshots/${exception.screenshot.split('\\').pop()}')"
                             title="Click to expand">
                    </div>
                ` : ''}
            </div>
        </div>`;
}

// Helper functions for log searching
// Define these functions in the global scope so they're accessible everywhere
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function clearHighlights(logContent) {
    if (logContent) {
        logContent.innerHTML = logContent.textContent;
    }
}

function highlightAllInstances(term, logContent) {
    if (!term || !logContent) return;

    const content = logContent.textContent;
    const escapedTerm = escapeRegExp(term);
    const regex = new RegExp(escapedTerm, 'gi');

    let highlightedContent = content.replace(regex, match =>
        `<span class="highlight">${match}</span>`);

    logContent.innerHTML = highlightedContent;
}

function setupLogs(data) {
    if (!data.logs || data.logs.length === 0) {
        document.querySelector('.logs-section').style.display = 'none';
        return;
    }

    const select = document.getElementById('log-file-select');
    const logContent = document.getElementById('log-content');
    const searchInput = document.getElementById('log-search-input');
    const searchButton = document.getElementById('log-search-button');
    const clearButton = document.getElementById('clear-search-btn');
    const resultsContainer = document.getElementById('search-results-container');
    const resultsList = document.getElementById('search-results-list');
    const resultsCount = document.getElementById('search-results-count');

    // Populate select options
    data.logs.forEach(log => {
        const option = document.createElement('option');
        option.value = log.name;
        const timestamp = new Date(log.timestamp.replace(
            /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/,
            '$1-$2-$3T$4:$5:$6'
        ));
        option.text = `${log.name} (${timestamp.toLocaleString()})`;
        select.appendChild(option);
    });

    // Show first log by default
    if (data.logs.length > 0) {
        logContent.textContent = data.logs[0].content;
    }

    // Handle log selection
    select.addEventListener('change', (e) => {
        const selectedLog = data.logs.find(log => log.name === e.target.value);
        if (selectedLog) {
            logContent.textContent = selectedLog.content;
            logContent.scrollTop = logContent.scrollHeight;
            // Clear any search highlights when switching logs
            clearHighlights(logContent);
        }
    });

    // Search across all logs
    function searchInLogs(term) {
        if (!term || !data.logs || data.logs.length === 0) {
            return [];
        }

        const results = [];
        const searchRegex = new RegExp(escapeRegExp(term), 'gi');

        data.logs.forEach(log => {
            const logFileName = log.name;
            const logLines = log.content.split('\n');

            logLines.forEach((line, lineIndex) => {
                if (searchRegex.test(line)) {
                    // Get match index
                    searchRegex.lastIndex = 0;
                    const matchIndex = line.toLowerCase().indexOf(term.toLowerCase());

                    // Create context by highlighting the matched text
                    let context = line;
                    // Replace actual match with marked version
                    context = context.replace(new RegExp(escapeRegExp(term), 'gi'),
                        match => `<mark>${match}</mark>`);

                    results.push({
                        fileName: logFileName,
                        lineNumber: lineIndex + 1,
                        context: context,
                        line: line,
                        matchIndex: matchIndex
                    });
                }
            });
        });

        return results;
    }

    // Display search results
    function displayResults(results) {
        resultsList.innerHTML = '';

        if (results.length === 0) {
            resultsCount.textContent = 'No results found';
            return;
        }

        resultsCount.textContent = `${results.length} result${results.length === 1 ? '' : 's'}`;

        results.forEach((result, index) => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            resultItem.innerHTML = `
                <span class="search-result-file">${result.fileName}:${result.lineNumber}</span>
                <span class="search-result-context">${result.context}</span>
            `;

            resultItem.addEventListener('click', () => navigateToResult(result));
            resultsList.appendChild(resultItem);
        });
    }

    // Navigate to a search result
    function navigateToResult(result) {
        // Switch to the correct log file if needed
        const logOptions = Array.from(select.options);
        const targetLogOption = logOptions.find(option => option.value === result.fileName);

        if (targetLogOption) {
            select.value = result.fileName;

            // Trigger change event to load the log content
            const changeEvent = new Event('change');
            select.dispatchEvent(changeEvent);

            // Add slight delay to ensure content is loaded
            setTimeout(() => {
                // Scroll to the matched line
                const logLines = logContent.textContent.split('\n');
                let linePosition = 0;

                // Calculate position to scroll to
                for (let i = 0; i < result.lineNumber - 1; i++) {
                    if (i < logLines.length) {
                        linePosition += logLines[i].length + 1; // +1 for newline character
                    }
                }

                // Clear any existing highlights
                clearHighlights(logContent);

                // Highlight all instances of the search term in the log
                highlightAllInstances(searchInput.value, logContent);

                // Scroll to the position
                const lineHeight = parseInt(getComputedStyle(logContent).lineHeight);
                const approximateScrollPosition = (result.lineNumber - 1) * lineHeight;
                logContent.scrollTop = approximateScrollPosition;
            }, 100);
        }
    }

    // Set up search functionality
    searchButton.addEventListener('click', () => {
        const searchTerm = searchInput.value.trim();
        if (searchTerm) {
            const results = searchInLogs(searchTerm);
            displayResults(results);
            resultsContainer.style.display = 'block';
        }
    });

    // Search input enter key handler
    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            searchButton.click();
        }
    });

    // Clear search button
    clearButton.addEventListener('click', () => {
        searchInput.value = '';
        resultsContainer.style.display = 'none';
        clearHighlights(logContent);
    });
}

function openLogsInNewWindow() {
    const logSelect = document.getElementById('log-file-select');
    const selectedLog = reportData.logs.find(log => log.name === logSelect.value);

    const newWindow = window.open('', '_blank', 'width=1000,height=800');
    newWindow.document.write(`
        <html>
            <head>
                <title>Log Viewer - ${selectedLog.name}</title>
                <style>
                    body {
                        margin: 0;
                        padding: 20px;
                        font-family: monospace;
                        background: #f5f5f5;
                    }
                    pre {
                        white-space: pre-wrap;
                        margin: 0;
                        background: white;
                        padding: 20px;
                        border-radius: 4px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                </style>
            </head>
            <body>
                <pre>${selectedLog.content}</pre>
            </body>
        </html>
    `);
}