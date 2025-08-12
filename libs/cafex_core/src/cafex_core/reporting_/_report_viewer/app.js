document.addEventListener("DOMContentLoaded", () => {
    renderSummary(reportData);
    setupTabs(reportData);
    setupLogs(reportData);
});

function renderSummary(data) {
    // Format Date-Time
    const formatDate = (isoDate) => {
        const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
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

function setupLogs(data) {
    if (!data.logs || data.logs.length === 0) {
        document.querySelector('.logs-section').style.display = 'none';
        return;
    }

    const select = document.getElementById('log-file-select');
    const logContent = document.getElementById('log-content');

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
        }
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