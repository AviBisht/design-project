document.addEventListener("DOMContentLoaded", () => {
    let benchmarkData = [];
    let summaryData = null;
    let currentBenchmarkFilter = "all";

    const queryInput = document.getElementById("query-input");
    const executeBtn = document.getElementById("execute-btn");
    const auditDrawer = document.getElementById("audit-drawer");
    const closeDrawerBtn = document.getElementById("close-drawer-btn");
    const drawerTitle = document.getElementById("drawer-title");
    const drawerContent = document.getElementById("drawer-content");

    initTabNavigation();
    loadBenchmarkData();
    loadSummaryData();
    setupPresetChips();
    setupGraphVisualizer();

    function initTabNavigation() {
        const tabBtns = document.querySelectorAll(".tab-btn");

        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                window.switchToTab(btn.dataset.view);
            });
        });

        const initialHash = window.location.hash ? window.location.hash.substring(1) : "";
        if (initialHash && document.getElementById(initialHash)) {
            window.switchToTab(initialHash);
        }
    }

    function setupPresetChips() {
        document.querySelectorAll(".preset-chip-pill").forEach(chip => {
            chip.addEventListener("click", () => {
                const queryText = chip.dataset.query;
                if (queryText) {
                    queryInput.value = queryText;
                    executeComparison(queryText);
                }
            });
        });

        if (executeBtn) {
            executeBtn.addEventListener("click", () => {
                const q = queryInput.value.trim();
                if (q) executeComparison(q);
            });
        }

        if (queryInput) {
            queryInput.addEventListener("keypress", (e) => {
                if (e.key === "Enter") {
                    const q = queryInput.value.trim();
                    if (q) executeComparison(q);
                }
            });
        }
    }

    function executeComparison(queryText) {
        document.getElementById("pipe-a-latency").innerText = "Executing...";
        document.getElementById("pipe-b-latency").innerText = "Executing...";

        fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query_text: queryText, target_pipeline: "both" })
        })
        .then(res => res.json())
        .then(data => {
            renderPipelineA(data.pipeline_a);
            renderPipelineB(data.pipeline_b);
        })
        .catch(err => {
            console.error("Execution failed:", err);
            document.getElementById("pipe-a-latency").innerText = "Error";
            document.getElementById("pipe-b-latency").innerText = "Error";
        });
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function renderPipelineA(res) {
        document.getElementById("pipe-a-latency").innerText = `${res.metrics.total_latency_ms} ms (Single-Pass)`;
        document.getElementById("pipe-a-answer").innerText = res.answer;

        const chunksContainer = document.getElementById("pipe-a-chunks");
        chunksContainer.innerHTML = "";

        const chunks = res.retrieved_chunk_metadata || [];
        if (!Array.isArray(chunks) || chunks.length === 0) {
            chunksContainer.innerHTML = `<div style="color:var(--text-muted); font-size:11.5px; padding:8px 0;">No chunks retrieved yet.</div>`;
            return;
        }

        const listWrap = document.createElement("div");
        listWrap.className = "pipeline-a-chunks-list";

        chunks.forEach((m, idx) => {
            const card = document.createElement("div");
            card.className = "evidence-passage-card";

            const rank = m.rank || (idx + 1);
            const chunkShort = m.chunk_id && m.chunk_id.includes("_") ? m.chunk_id.split("_").slice(-1)[0] : (m.chunk_id || `C00${idx}`);
            const scoreVal = typeof m.score === "number" ? m.score.toFixed(4) : m.score;
            const passageText = m.content || (res.retrieved_contexts && res.retrieved_contexts[idx]) || "No text passage available.";

            card.innerHTML = `
                <div class="evidence-card-header">
                    <div class="evidence-card-meta-left">
                        <span class="evidence-card-rank-badge">Passage ${rank}</span>
                        <span class="evidence-card-doc-info">
                            <span class="evidence-card-doc-btn" onclick="window.inspectProvenance('${m.doc_id}')" title="Click to view source document">${m.doc_id} · Page ${m.page_number}</span>
                        </span>
                        <span class="evidence-card-chunk-tag" title="Full Chunk ID: ${m.chunk_id}">Chunk ${chunkShort}</span>
                    </div>
                    <div class="evidence-card-score-pill">
                        <span class="evidence-score-label">Cosine similarity:</span>
                        <span class="evidence-score-val">${scoreVal}</span>
                    </div>
                </div>
                <div class="evidence-passage-text">${escapeHtml(passageText)}</div>
            `;
            listWrap.appendChild(card);
        });

        chunksContainer.appendChild(listWrap);
    }

    function parseGraphTriple(item) {
        if (!item) return null;
        let s = null, p = null, o = null, raw = null;

        if (typeof item === "object") {
            if (Array.isArray(item) && item.length >= 3) {
                s = item[0];
                p = item[1];
                o = item[2];
            } else {
                s = item.subject || item.source || item.from || null;
                p = item.predicate || item.relation || item.relationship || null;
                o = item.object || item.target || item.to || item.connected_fact || null;
            }
        } else if (typeof item === "string") {
            raw = item.trim();
            const match = raw.match(/^\(?\s*(?:[A-Za-z0-9_]+:)?([^\)]+?)\s*\)?\s*-\[:?([A-Za-z0-9_\-]+)\]->\s*\(?\s*(?:[A-Za-z0-9_]+:)?([^\)]+?)\s*\)?$/);
            if (match) {
                s = match[1].trim();
                p = match[2].trim();
                o = match[3].trim();
            } else {
                const arrowMatch = raw.match(/^(.*?)\s*(?:-\[:?([A-Za-z0-9_\-]+)\]->|->)\s*(.*?)$/);
                if (arrowMatch) {
                    s = arrowMatch[1].replace(/[()]/g, "").trim();
                    p = arrowMatch[2] ? arrowMatch[2].trim() : "CONNECTED_TO";
                    o = arrowMatch[3].replace(/[()]/g, "").trim();
                }
            }
        }

        if (!s || !p || !o || s === "undefined" || p === "undefined" || o === "undefined") {
            return null;
        }

        const predReadable = String(p).toLowerCase().replace(/_/g, " ");
        let subjectFormatted = String(s);
        if (/^P-\d+$/.test(subjectFormatted)) {
            subjectFormatted = `Patient ${subjectFormatted}`;
        }

        return {
            subject: subjectFormatted,
            predicate: String(p),
            predicateReadable: predReadable,
            object: String(o),
            rawCypher: raw || `(${s})-[:${p}]->(${o})`
        };
    }

    function renderPipelineB(res) {
        document.getElementById("pipe-b-latency").innerText = `${res.metrics.total_latency_ms} ms (Agent Verified)`;

        const answerEl = document.getElementById("pipe-b-answer");
        let htmlAns = res.answer;
        htmlAns = htmlAns.replace(/\[(DOC-EHR-[^\]]+)\]/g, (match, p1) => {
            return `<span class="citation-action-badge" onclick="window.inspectProvenance('${p1}')">📄 ${match}</span>`;
        });
        answerEl.innerHTML = htmlAns;

        const pathContainer = document.getElementById("pipe-b-path");
        if (res.state_trace && res.state_trace.execution_path) {
            pathContainer.innerHTML = res.state_trace.execution_path.map((node, idx) => {
                const isRetry = node.includes("reformulat");
                const pillClass = isRetry ? "stepper-pill pill-retry" : "stepper-pill";
                const sep = idx < res.state_trace.execution_path.length - 1 ? `<span class="stepper-sep">→</span>` : "";
                return `<span class="${pillClass}">${node}</span>${sep}`;
            }).join("");
        }

        const graphContainer = document.getElementById("pipe-b-graph");
        graphContainer.innerHTML = "";

        const validTriples = [];
        if (Array.isArray(res.graph_evidence)) {
            res.graph_evidence.forEach(rawItem => {
                const parsed = parseGraphTriple(rawItem);
                if (parsed) {
                    validTriples.push(parsed);
                }
            });
        }

        if (validTriples.length > 0) {
            const table = document.createElement("table");
            table.className = "graph-triples-table";
            table.innerHTML = `
                <thead>
                    <tr>
                        <th style="width:30%;">Subject</th>
                        <th style="width:34%;">Relationship</th>
                        <th style="width:36%;">Connected Fact</th>
                    </tr>
                </thead>
                <tbody>
                    ${validTriples.map(t => `
                        <tr>
                            <td class="triple-subject" title="${t.rawCypher}">${t.subject}</td>
                            <td class="triple-rel"><span class="triple-rel-pill">${t.predicateReadable}</span></td>
                            <td class="triple-object">${t.object}</td>
                        </tr>
                    `).join("")}
                </tbody>
            `;
            graphContainer.appendChild(table);
        } else {
            graphContainer.innerHTML = `<div class="graph-triples-empty">No connected facts were retrieved for this query.</div>`;
        }
    }

    function loadSummaryData() {
        fetch("/api/summary")
            .then(res => res.json())
            .then(data => {
                summaryData = data.summary;
                renderAnalyticsSummary();
            })
            .catch(err => console.error("Error loading summary:", err));
    }

    function renderAnalyticsSummary() {
        if (!summaryData) return;

        const ov = summaryData.overall;
        document.getElementById("kpi-faithfulness-val").innerText = `${(ov.pipeline_b.faithfulness * 100).toFixed(1)}%`;
        document.getElementById("kpi-faithfulness-base").innerText = `Baseline: ${(ov.pipeline_a.faithfulness * 100).toFixed(1)}% | Pipeline B Heuristic`;
        document.getElementById("bar-faithfulness-b").style.width = `${ov.pipeline_b.faithfulness * 100}%`;

        document.getElementById("kpi-recall-val").innerText = `${(ov.pipeline_b.context_recall * 100).toFixed(1)}%`;
        document.getElementById("kpi-recall-base").innerText = `Baseline: ${(ov.pipeline_a.context_recall * 100).toFixed(1)}% | Connecting Related Facts`;
        document.getElementById("bar-recall-b").style.width = `${ov.pipeline_b.context_recall * 100}%`;

        document.getElementById("kpi-precision-val").innerText = `${(ov.pipeline_b.context_precision * 100).toFixed(1)}%`;
        document.getElementById("kpi-precision-base").innerText = `Baseline: ${(ov.pipeline_a.context_precision * 100).toFixed(1)}% | Relevant Pieces in Top Results`;

        document.getElementById("kpi-relevancy-val").innerText = `${ov.pipeline_b.answer_relevancy.toFixed(3)}`;
        document.getElementById("kpi-relevancy-base").innerText = `Baseline: ${ov.pipeline_a.answer_relevancy.toFixed(3)} | Small Difference Observed`;

        const tbody = document.getElementById("analytics-breakdown-body");
        if (!tbody) return;
        tbody.innerHTML = "";

        const tiers = [
            {
                name: "Single-Fact Questions (20 questions)",
                a_f: summaryData.by_category["single-hop"].pipeline_a.faithfulness,
                b_f: summaryData.by_category["single-hop"].pipeline_b.faithfulness,
                a_r: summaryData.by_category["single-hop"].pipeline_a.context_recall,
                b_r: summaryData.by_category["single-hop"].pipeline_b.context_recall,
                finding: "Both pipelines retrieve direct passages, but Pipeline B attaches document and page citations."
            },
            {
                name: "Connected-Fact Questions (20 questions)",
                a_f: summaryData.by_category["multi-hop"].pipeline_a.faithfulness,
                b_f: summaryData.by_category["multi-hop"].pipeline_b.faithfulness,
                a_r: summaryData.by_category["multi-hop"].pipeline_a.context_recall,
                b_r: summaryData.by_category["multi-hop"].pipeline_b.context_recall,
                finding: "Pipeline A misses connections between separated text pieces; Pipeline B connects facts using the knowledge graph."
            },
            {
                name: "Table & Lab Value Questions (10 questions)",
                a_f: summaryData.by_category["table-extraction"].pipeline_a.faithfulness,
                b_f: summaryData.by_category["table-extraction"].pipeline_b.faithfulness,
                a_r: summaryData.by_category["table-extraction"].pipeline_a.context_recall,
                b_r: summaryData.by_category["table-extraction"].pipeline_b.context_recall,
                finding: "Pipeline B preserves table columns and units, preventing numbers from becoming separated from their headers."
            }
        ];

        tiers.forEach(t => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="font-weight:600; color:var(--text-primary);">${t.name}</td>
                <td style="font-family:var(--font-mono); color:var(--text-muted);">${(t.a_f * 100).toFixed(1)}%</td>
                <td style="font-family:var(--font-mono); font-weight:700; color:var(--emerald);">${(t.b_f * 100).toFixed(1)}%</td>
                <td style="font-family:var(--font-mono); color:var(--text-muted);">${(t.a_r * 100).toFixed(1)}%</td>
                <td style="font-family:var(--font-mono); font-weight:700; color:var(--blue);">${(t.b_r * 100).toFixed(1)}%</td>
                <td style="font-size:11px; color:var(--text-secondary);">${t.finding}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function loadBenchmarkData() {
        fetch("/api/queries")
            .then(res => res.json())
            .then(data => {
                benchmarkData = data.queries || [];
                renderBenchmarkTable();
            })
            .catch(err => console.error("Error loading queries:", err));
    }

    function renderBenchmarkTable() {
        const tbody = document.getElementById("dataset-table-body");
        const searchVal = (document.getElementById("dataset-search-input")?.value || "").toLowerCase();
        if (!tbody) return;

        tbody.innerHTML = "";
        const filtered = benchmarkData.filter(q => {
            const matchesFilter = (currentBenchmarkFilter === "all" || q.query_type === currentBenchmarkFilter);
            const matchesSearch = (!searchVal || q.query_text.toLowerCase().includes(searchVal) || q.query_id.toLowerCase().includes(searchVal));
            return matchesFilter && matchesSearch;
        });

        filtered.forEach(q => {
            const tr = document.createElement("tr");
            const badgeClass = q.query_type === "single-hop" ? "badge-single" :
                               q.query_type === "multi-hop" ? "badge-multi" : "badge-table";

            tr.innerHTML = `
                <td style="font-family:var(--font-mono); font-weight:700; color:var(--gold);">${q.query_id}</td>
                <td><span class="query-badge ${badgeClass}">${q.query_type}</span></td>
                <td style="color:var(--text-primary); font-size:12px;">${q.query_text}</td>
                <td style="font-family:var(--font-mono); font-size:11px; color:var(--text-muted);">${q.provenance.doc_id}</td>
                <td>
                    <button class="filter-btn-pill" onclick="window.runQueryInWorkbench('${q.query_id}')">Run</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    document.querySelectorAll(".dataset-filter-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".dataset-filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentBenchmarkFilter = btn.dataset.filter;
            renderBenchmarkTable();
        });
    });

    document.getElementById("dataset-search-input")?.addEventListener("input", renderBenchmarkTable);

    function setupGraphVisualizer() {
        const svg = document.getElementById("interactive-graph-svg");
        const inspector = document.getElementById("graph-node-details");
        if (!svg) return;

        const nodes = [
            { id: "P-101", label: "Patient", x: 120, y: 150, color: "#5c1d27", detail: "58 y/o Female, T2DM, Hypertension, CKD Stage 3a" },
            { id: "T2DM", label: "Diagnosis", x: 120, y: 50, color: "#8c3f4e", detail: "Type 2 Diabetes Mellitus (E11.9)" },
            { id: "Lisinopril", label: "Medication", x: 260, y: 150, color: "#7a2232", detail: "10 mg PO daily for Diabetic Nephropathy" },
            { id: "Hyperkalemia", label: "Diagnosis", x: 420, y: 100, color: "#8c3f4e", detail: "Critical Potassium 5.7 mEq/L with peaked T-waves" },
            { id: "Lokelma", label: "Medication", x: 560, y: 100, color: "#7a2232", detail: "10 g PO TID Potassium Binder" },
            { id: "Nifedipine ER", label: "Medication", x: 420, y: 220, color: "#7a2232", detail: "30 mg PO daily (ACE-inhibitor replacement)" },
            
            { id: "P-102", label: "Patient", x: 120, y: 350, color: "#5c1d27", detail: "66 y/o Male, Ischemic Cardiomyopathy, HFrEF" },
            { id: "HFrEF LVEF 28%", label: "Diagnosis", x: 280, y: 350, color: "#8c3f4e", detail: "Severely reduced LVEF 28%, NYHA Class III" },
            { id: "Sacubitril/Valsartan", label: "Medication", x: 460, y: 320, color: "#7a2232", detail: "24/26 mg PO BID after 36-hr washout" },
            { id: "Carvedilol", label: "Medication", x: 460, y: 400, color: "#7a2232", detail: "Titrated from 3.125 to 6.25 mg PO BID" },
            { id: "NT-proBNP 4850", label: "LabTest", x: 280, y: 460, color: "#5c1d27", detail: "Decreased from 4850 to 1140 pg/mL with therapy" },

            { id: "P-104", label: "Patient", x: 120, y: 560, color: "#5c1d27", detail: "71 y/o Male, Septic Shock secondary to Pyelonephritis" },
            { id: "ESBL E. coli", label: "Diagnosis", x: 280, y: 560, color: "#8c3f4e", detail: "Extended Spectrum Beta-Lactamase Producer" },
            { id: "Ceftriaxone Resistant", label: "Pathogen", x: 440, y: 520, color: "#8c3f4e", detail: "MIC >= 64 ug/mL (Ineffective)" },
            { id: "Meropenem Susceptible", label: "Medication", x: 440, y: 600, color: "#7a2232", detail: "1 g IV q8h via PICC line for 14 days" }
        ];

        const edges = [
            { source: "P-101", target: "T2DM", label: "DIAGNOSED_WITH" },
            { source: "P-101", target: "Lisinopril", label: "PRESCRIBED" },
            { source: "Lisinopril", target: "Hyperkalemia", label: "CAUSED_ADVERSE_EVENT" },
            { source: "Hyperkalemia", target: "Lokelma", label: "TREATED_WITH" },
            { source: "P-101", target: "Nifedipine ER", label: "SWITCHED_TO" },

            { source: "P-102", target: "HFrEF LVEF 28%", label: "DIAGNOSED_WITH" },
            { source: "HFrEF LVEF 28%", target: "Sacubitril/Valsartan", label: "INDICATED_REGIMEN" },
            { source: "HFrEF LVEF 28%", target: "Carvedilol", label: "INDICATED_REGIMEN" },
            { source: "P-102", target: "NT-proBNP 4850", label: "MEASURED" },

            { source: "P-104", target: "ESBL E. coli", label: "INFECTED_WITH" },
            { source: "ESBL E. coli", target: "Ceftriaxone Resistant", label: "RESISTANT_TO" },
            { source: "ESBL E. coli", target: "Meropenem Susceptible", label: "SUSCEPTIBLE_TO" }
        ];

        let svgHtml = "";
        edges.forEach(e => {
            const s = nodes.find(n => n.id === e.source);
            const t = nodes.find(n => n.id === e.target);
            if (s && t) {
                const midX = (s.x + t.x) / 2;
                const midY = (s.y + t.y) / 2;
                svgHtml += `
                    <line x1="${s.x}" y1="${s.y}" x2="${t.x}" y2="${t.y}" stroke="var(--border-default)" stroke-width="1.5" />
                    <text x="${midX}" y="${midY - 4}" fill="var(--text-dim)" font-size="9" font-family="ui-monospace, monospace" text-anchor="middle">${e.label}</text>
                `;
            }
        });

        nodes.forEach(n => {
            svgHtml += `
                <g class="graph-node-group" onclick="window.selectGraphNode('${n.id}')" style="cursor:pointer;">
                    <circle cx="${n.x}" cy="${n.y}" r="15" fill="${n.color}" fill-opacity="0.18" stroke="${n.color}" stroke-width="1.5" />
                    <circle cx="${n.x}" cy="${n.y}" r="4" fill="${n.color}" />
                    <text x="${n.x}" y="${n.y + 24}" fill="var(--text-primary)" font-size="11" font-weight="600" text-anchor="middle">${n.id}</text>
                    <text x="${n.x}" y="${n.y + 36}" fill="var(--text-muted)" font-size="9" text-anchor="middle">${n.label}</text>
                </g>
            `;
        });

        svg.innerHTML = svgHtml;

        window.selectGraphNode = function(nodeId) {
            const node = nodes.find(n => n.id === nodeId);
            if (!node || !inspector) return;

            const connectedEdges = edges.filter(e => e.source === nodeId || e.target === nodeId);
            let edgesHtml = connectedEdges.map(e => {
                const predReadable = e.label.toLowerCase().replace(/_/g, " ");
                return `
                    <div style="font-size:11px; margin-bottom:6px; line-height:1.4;">
                        <span style="color:var(--text-primary); font-weight:600;">${e.source}</span> →
                        <span style="color:var(--emerald); font-style:italic;">${predReadable}</span> →
                        <span style="color:var(--text-primary); font-weight:600;">${e.target}</span><br>
                        <span style="font-family:var(--font-mono); font-size:10px; color:var(--text-muted);">(${e.source})-[:${e.label}]->(${e.target})</span>
                    </div>
                `;
            }).join("");

            const patientNote = node.label === "Patient" ? " (Fictional Patient)" : "";
            inspector.innerHTML = `
                <div style="font-size:10px; font-weight:700; text-transform:uppercase; color:var(--gold); margin-bottom:4px;">Node Inspector</div>
                <div style="font-size:15px; font-weight:700; color:${node.color}; margin-bottom:6px;">${node.id} (${node.label})${patientNote}</div>
                <div style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin-bottom:14px;">${node.detail}</div>
                <div style="font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text-muted); margin-bottom:6px;">Connected Relationships</div>
                ${edgesHtml}
            `;
        };
    }

    window.switchToTab = function(targetViewId) {
        document.querySelectorAll(".tab-btn").forEach(b => {
            if (b.dataset.view === targetViewId) {
                b.classList.add("active");
            } else {
                b.classList.remove("active");
            }
        });
        document.querySelectorAll(".tab-view").forEach(v => {
            if (v.id === targetViewId) {
                v.classList.add("active-tab");
            } else {
                v.classList.remove("active-tab");
            }
        });
        const activeView = document.getElementById(targetViewId);
        if (activeView) activeView.scrollTop = 0;
    };

    const landingQueryData = [
        {
            title: "Test Case 1: Initial Medication Dose (Patient P-101)",
            pipeA: {
                retrieval: "Splits records into fixed 500-character pieces and searches them using keyword matching (TF-IDF).",
                context: "[Patient Record 1 (DOC-EHR-001), Piece 2]: \"...decreased exercise tolerance. Home medications included Metformin 1000 mg BID and Amlodipine 10 mg daily. Physical Examination: BP 162/94 mmHg...\"",
                answer: "\"Based on the retrieved baseline context, insufficient evidence was found to answer this question.\"",
                failure: "✕ Problem: Splitting text at fixed boundaries missed the diagnosis and prescription on Page 2."
            },
            pipeB: {
                retrieval: "Preserves sections and tables intact; uses a manually created knowledge graph to follow connections between medical facts.",
                context: "Patient P-101 → diagnosed with → Diabetic Nephropathy<br>Lisinopril → prescribed for → Diabetic Nephropathy [Patient Record 1 (DOC-EHR-001), p.2]<br><span style=\"font-family:var(--font-mono); font-size:10px; color:var(--text-muted);\">Technical graph notation: (Patient:P-101)-[:DIAGNOSED_WITH]->(Diabetic Nephropathy)</span>",
                answer: "Patient P-101 was prescribed an initial dose of Lisinopril 10 mg PO daily to protect kidney function in diabetic nephropathy.",
                citations: ["Patient Record 1 (DOC-EHR-001), p.2", "Patient Record 1 (DOC-EHR-001), Table 1, p.3"]
            }
        },
        {
            title: "Test Case 2: Day 7 Lab Test Values (Table 1)",
            pipeA: {
                retrieval: "Splitting text at fixed 500 characters sliced Table 1 into two separate pieces.",
                context: "[Patient Record 1 (DOC-EHR-001), Piece 6]: \"| 2026-03-19 | Serum Potassium | 5.7 | 3.5 - 5.0 | CRITICAL_HIGH | mEq/L |\" (Table header row was left in previous piece)",
                answer: "\"On 2026-03-19, potassium was 5.7, but column headers and patient context were missing from this piece.\"",
                failure: "✕ Problem: Severed table header leaves test flags separated from test names."
            },
            pipeB: {
                retrieval: "Structure-aware table reader kept Table 1 intact with all column headers attached.",
                context: "Table 1: Longitudinal Renal and Electrolyte Panel (Patient Record 1, Patient P-101): Date: 2026-03-19, Test Name: Serum Potassium, Result: 5.7, Normal Range: 3.5 - 5.0, Flag: CRITICAL_HIGH, Unit: mEq/L",
                answer: "On 2026-03-19, patient P-101 had a Serum Potassium level of 5.7 mEq/L flagged as CRITICAL_HIGH (normal reference range: 3.5 - 5.0 mEq/L).",
                citations: ["Patient Record 1 (DOC-EHR-001), Table 1, p.3", "Patient Record 1 (DOC-EHR-001), p.4"]
            }
        },
        {
            title: "Test Case 3: Linking Medication to Reaction (Multi-Step)",
            pipeA: {
                retrieval: "Basic keyword search retrieved the Day 1 note and Day 7 note as two unconnected text pieces.",
                context: "[Patient Record 1 (DOC-EHR-001), Piece 3] & [Piece 8] retrieved with no link between Day 1 medication and Day 7 reaction.",
                answer: "\"Patient P-101 had kidney injury and high potassium on Day 7, but the connection to Day 1 Lisinopril was not recognized.\"",
                failure: "✕ Problem: Splitting text at fixed boundaries missed the 7-day connection between Day 1 medication and Day 7 injury."
            },
            pipeB: {
                retrieval: "Knowledge graph followed connected facts from Day 1 Lisinopril to Day 7 kidney complications.",
                context: "Patient P-101 → prescribed Lisinopril → caused adverse event → High Potassium & Acute Kidney Injury (AKI) [Patient Record 1 (DOC-EHR-001), p.4]<br><span style=\"font-family:var(--font-mono); font-size:10px; color:var(--text-muted);\">Technical graph path: (Patient:P-101)-[:PRESCRIBED]->(Lisinopril)-[:CAUSED_ADVERSE_EVENT]->(Acute Kidney Injury)</span>",
                answer: "Patient P-101 developed Acute Kidney Injury and medication-induced high potassium (hyperkalemia) after starting Lisinopril, which was stopped and treated with Lokelma.",
                citations: ["Patient Record 1 (DOC-EHR-001), p.2", "Patient Record 1 (DOC-EHR-001), p.4"]
            }
        }
    ];

    window.selectLandingQuery = function(index, btnElem) {
        document.querySelectorAll(".contrast-query-pill").forEach(p => p.classList.remove("active"));
        if (btnElem) btnElem.classList.add("active");

        const data = landingQueryData[index];
        if (!data) return;

        document.getElementById("landing-pipe-a-retrieval").innerText = data.pipeA.retrieval;
        document.getElementById("landing-pipe-a-context").innerText = data.pipeA.context;
        document.getElementById("landing-pipe-a-answer").innerText = data.pipeA.answer;
        const failElem = document.getElementById("landing-pipe-a-failure");
        if (failElem) failElem.innerText = data.pipeA.failure;

        document.getElementById("landing-pipe-b-retrieval").innerText = data.pipeB.retrieval;
        document.getElementById("landing-pipe-b-context").innerHTML = data.pipeB.context;
        document.getElementById("landing-pipe-b-answer").innerText = data.pipeB.answer;

        const citBox = document.getElementById("landing-pipe-b-citations");
        if (citBox) {
            citBox.innerHTML = data.pipeB.citations.map(c => `
                <span class="citation-chip" onclick="window.inspectProvenance('${c}')">${c}</span>
            `).join("");
        }
    };

    window.runQueryInWorkbench = function(queryId) {
        const item = benchmarkData.find(q => q.query_id === queryId);
        if (!item) return;

        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-view").forEach(v => v.classList.remove("active-tab"));

        document.querySelector(".tab-btn[data-view='view-workbench']").classList.add("active");
        document.getElementById("view-workbench").classList.add("active-tab");

        queryInput.value = item.query_text;
        executeComparison(item.query_text);
    };

    window.inspectProvenance = function(citationStr) {
        const docMatch = citationStr.match(/DOC-EHR-\d+/);
        if (!docMatch) return;
        const docId = docMatch[0];

        fetch(`/api/document/${docId}`)
            .then(res => res.json())
            .then(data => {
                drawerTitle.innerText = `PROVENANCE AUDIT: ${docId}`;
                drawerContent.innerHTML = `<div class="source-document-viewer">${data.content}</div>`;
                auditDrawer.classList.add("open");
            })
            .catch(err => console.error("Document fetch failed:", err));
    };

    closeDrawerBtn.addEventListener("click", () => {
        auditDrawer.classList.remove("open");
    });
});
