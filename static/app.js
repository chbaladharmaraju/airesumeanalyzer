/* ==========================================================================
   AI Resume Analyzer — Frontend Logic
   ========================================================================== */

(function () {
    "use strict";

    // ---- DOM Elements ----
    const $ = (sel) => document.querySelector(sel);
    const dropZone = $("#dropZone");
    const fileInput = $("#fileInput");
    const fileInfo = $("#fileInfo");
    const fileName = $("#fileName");
    const fileSize = $("#fileSize");
    const fileRemove = $("#fileRemove");
    const jdInput = $("#jdInput");
    const charCount = $("#charCount");
    const analyzeBtn = $("#analyzeBtn");
    const btnText = $(".btn-text");
    const btnLoading = $(".btn-loading");
    const errorBanner = $("#errorBanner");
    const errorText = $("#errorText");
    const errorClose = $("#errorClose");
    const heroSection = $("#heroSection");
    const inputSection = $("#inputSection");
    const loadingSection = $("#loadingSection");
    const resultsSection = $("#resultsSection");
    const backBtn = $("#backBtn");
    const themeToggle = $("#themeToggle");

    let selectedFile = null;

    // ---- Theme Toggle ----
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);

    themeToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
    });

    // ---- Drag & Drop ----
    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("drag-over");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("drag-over");
        const files = e.dataTransfer.files;
        if (files.length) handleFile(files[0]);
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length) handleFile(fileInput.files[0]);
    });

    fileRemove.addEventListener("click", () => {
        selectedFile = null;
        fileInput.value = "";
        fileInfo.style.display = "none";
        dropZone.style.display = "block";
        updateAnalyzeBtn();
    });

    function handleFile(file) {
        const ext = file.name.split(".").pop().toLowerCase();
        const allowed = ["pdf", "docx", "txt"];

        if (!allowed.includes(ext)) {
            showError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.");
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            showError("File too large. Maximum size is 5 MB.");
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatSize(file.size);
        dropZone.style.display = "none";
        fileInfo.style.display = "flex";
        updateAnalyzeBtn();
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    }

    // ---- JD Textarea ----
    jdInput.addEventListener("input", () => {
        charCount.textContent = jdInput.value.length;
        updateAnalyzeBtn();
    });

    // ---- Analyze Button State ----
    function updateAnalyzeBtn() {
        analyzeBtn.disabled = !(selectedFile && jdInput.value.trim().length > 20);
    }

    // ---- Error Handling ----
    function showError(msg) {
        errorText.textContent = msg;
        errorBanner.style.display = "flex";
        setTimeout(() => {
            errorBanner.style.display = "none";
        }, 8000);
    }

    errorClose.addEventListener("click", () => {
        errorBanner.style.display = "none";
    });

    function showRateLimitError() {
        let seconds = 60;
        errorText.textContent = `⏳ API rate limit reached. Please wait ${seconds}s before trying again...`;
        errorBanner.style.display = "flex";

        const countdown = setInterval(() => {
            seconds--;
            if (seconds <= 0) {
                clearInterval(countdown);
                errorBanner.style.display = "none";
            } else {
                errorText.textContent = `⏳ API rate limit reached. Please wait ${seconds}s before trying again...`;
            }
        }, 1000);
    }

    // ---- Analyze ----
    analyzeBtn.addEventListener("click", async () => {
        if (!selectedFile || !jdInput.value.trim()) return;

        // Show loading
        btnText.style.display = "none";
        btnLoading.style.display = "inline-flex";
        analyzeBtn.disabled = true;
        errorBanner.style.display = "none";

        heroSection.style.display = "none";
        inputSection.style.display = "none";
        loadingSection.style.display = "block";
        resultsSection.style.display = "none";

        const formData = new FormData();
        formData.append("resume", selectedFile);
        formData.append("job_description", jdInput.value.trim());

        try {
            const res = await fetch("/api/analyze", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            if (!res.ok) {
                // Specific handling for rate-limit (429) errors
                if (res.status === 429) {
                    loadingSection.style.display = "none";
                    heroSection.style.display = "block";
                    inputSection.style.display = "block";
                    showRateLimitError();
                    return;
                }
                throw new Error(data.error || "Something went wrong. Please try again.");
            }

            renderResults(data);

            // Switch to results view
            loadingSection.style.display = "none";
            resultsSection.style.display = "block";
        } catch (err) {
            loadingSection.style.display = "none";
            heroSection.style.display = "block";
            inputSection.style.display = "block";
            showError(err.message || "Network error. Please check your connection.");
        } finally {
            btnText.style.display = "inline-flex";
            btnLoading.style.display = "none";
            analyzeBtn.disabled = false;
            updateAnalyzeBtn();
        }
    });

    // ---- Back Button ----
    backBtn.addEventListener("click", () => {
        resultsSection.style.display = "none";
        heroSection.style.display = "block";
        inputSection.style.display = "block";
    });

    // ---- Render Results ----
    function renderResults(data) {
        // Scores
        animateScore("atsScore", "atsCircle", data.ats_score || 0);
        animateScore("matchScore", "matchCircle", data.semantic_match || 0);

        // Summaries
        $("#resumeSummary").textContent = data.resume_summary || "N/A";
        $("#jdSummary").textContent = data.jd_summary || "N/A";

        // Matched Keywords
        const matchedContainer = $("#matchedTags");
        matchedContainer.innerHTML = "";
        (data.matched_keywords || []).forEach((kw) => {
            const tag = document.createElement("span");
            tag.className = "tag tag-matched";
            tag.textContent = kw;
            matchedContainer.appendChild(tag);
        });

        // Missing Keywords
        const missingContainer = $("#missingTags");
        missingContainer.innerHTML = "";
        (data.missing_keywords || []).forEach((kw) => {
            const tag = document.createElement("span");
            tag.className = "tag tag-missing";
            tag.textContent = kw;
            missingContainer.appendChild(tag);
        });

        // Strengths
        const strengthsList = $("#strengthsList");
        strengthsList.innerHTML = "";
        (data.strengths || []).forEach((s) => {
            const li = document.createElement("li");
            li.className = "strength-item";
            li.innerHTML = `
                <span class="strength-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                </span>
                <span>${escapeHtml(s)}</span>
            `;
            strengthsList.appendChild(li);
        });

        // Suggestions
        const suggestionsContainer = $("#suggestionsList");
        suggestionsContainer.innerHTML = "";
        const suggestions = data.suggestions || [];
        $("#suggestionCount").textContent = suggestions.length + " suggestions";

        suggestions.forEach((s, i) => {
            const item = document.createElement("div");
            item.className = "suggestion-item";

            const priorityClass =
                s.priority === "high"
                    ? "priority-high"
                    : s.priority === "medium"
                    ? "priority-medium"
                    : "priority-low";

            item.innerHTML = `
                <button class="suggestion-toggle">
                    <span class="suggestion-number">${i + 1}</span>
                    <span class="suggestion-title">${escapeHtml(s.title)}</span>
                    <span class="suggestion-priority ${priorityClass}">${escapeHtml(s.priority || "tip")}</span>
                    <svg class="suggestion-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
                </button>
                <div class="suggestion-detail">
                    <p>${escapeHtml(s.detail)}</p>
                </div>
            `;

            // Toggle collapsible
            item.querySelector(".suggestion-toggle").addEventListener("click", () => {
                item.classList.toggle("open");
            });

            suggestionsContainer.appendChild(item);
        });
    }

    // ---- Score Animation ----
    function animateScore(valueId, circleId, score) {
        const circumference = 2 * Math.PI * 52; // ~326.73
        const circle = document.getElementById(circleId);
        const valueEl = document.getElementById(valueId);

        // Reset
        circle.style.strokeDasharray = circumference;
        circle.style.strokeDashoffset = circumference;

        // Animate after a brief delay
        requestAnimationFrame(() => {
            setTimeout(() => {
                const offset = circumference - (score / 100) * circumference;
                circle.style.strokeDashoffset = offset;
            }, 100);
        });

        // Animate number
        let current = 0;
        const duration = 1200;
        const step = score / (duration / 16);

        function tick() {
            current = Math.min(current + step, score);
            valueEl.textContent = Math.round(current);
            if (current < score) requestAnimationFrame(tick);
        }
        tick();
    }

    // ---- Utility ----
    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }
})();
