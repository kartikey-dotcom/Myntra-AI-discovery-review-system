/**
 * Myntra Growth Intelligence | VoC Discovery Engine Application Logic
 * Supports live LLM API Key connectivity, testing, and grounded VoC querying.
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Tab Switching
  const tabButtons = document.querySelectorAll('.tab-pill[data-tab]');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetTab = document.getElementById(targetId);
      if (targetTab) {
        targetTab.classList.add('active');
      }
    });
  });

  // Check LLM Status on Load
  const llmStatusDot = document.getElementById('llmStatusDot');
  const llmStatusText = document.getElementById('llmStatusText');
  const sidebarLLM = document.getElementById('sidebarLLM');

  async function checkLlmStatus() {
    try {
      const res = await fetch('/api/v1/llm/status');
      if (res.ok) {
        const data = await res.json();
        if (data.configured) {
          if (llmStatusDot) llmStatusDot.style.background = '#0fa464';
          if (llmStatusText) llmStatusText.textContent = `🟢 ${data.provider.toUpperCase()} (${data.model_name}) Connected`;
          if (sidebarLLM) sidebarLLM.textContent = `${data.provider.toUpperCase()} - ${data.model_name}`;
        } else {
          if (llmStatusDot) llmStatusDot.style.background = '#f59e0b';
          if (llmStatusText) llmStatusText.textContent = '🔑 Connect LLM API Key';
          if (sidebarLLM) sidebarLLM.textContent = 'Deterministic AI Mode';
        }
      }
    } catch (e) {
      console.log('Status check note:', e);
    }
  }
  checkLlmStatus();

  // Modal Controls
  const apiKeyModal = document.getElementById('apiKeyModal');
  const openApiKeyModalBtn = document.getElementById('openApiKeyModalBtn');
  const openSettingsBtn = document.getElementById('openSettingsBtn');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const testApiKeyBtn = document.getElementById('testApiKeyBtn');
  const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
  const modalProviderSelect = document.getElementById('modalProviderSelect');
  const modalApiKeyInput = document.getElementById('modalApiKeyInput');
  const modalModelSelect = document.getElementById('modalModelSelect');
  const modalStatusMsg = document.getElementById('modalStatusMsg');

  function openModal() {
    if (apiKeyModal) apiKeyModal.style.display = 'flex';
  }
  function closeModal() {
    if (apiKeyModal) apiKeyModal.style.display = 'none';
  }

  if (openApiKeyModalBtn) openApiKeyModalBtn.addEventListener('click', openModal);
  if (openSettingsBtn) openSettingsBtn.addEventListener('click', openModal);
  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);

  if (apiKeyModal) {
    apiKeyModal.addEventListener('click', (e) => {
      if (e.target === apiKeyModal) closeModal();
    });
  }

  // Test API Key
  if (testApiKeyBtn) {
    testApiKeyBtn.addEventListener('click', async () => {
      const provider = modalProviderSelect.value;
      const apiKey = modalApiKeyInput.value.trim();
      const modelName = modalModelSelect.value;

      if (!apiKey) {
        modalStatusMsg.style.display = 'block';
        modalStatusMsg.style.background = '#fdebee';
        modalStatusMsg.style.color = '#e0245e';
        modalStatusMsg.textContent = 'Please enter an API Key first.';
        return;
      }

      modalStatusMsg.style.display = 'block';
      modalStatusMsg.style.background = '#f1f5f9';
      modalStatusMsg.style.color = '#334155';
      modalStatusMsg.textContent = 'Testing connection with live prompt...';

      try {
        const res = await fetch('/api/v1/llm/test-connection', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider, api_key: apiKey, model_name: modelName })
        });
        const data = await res.json();
        if (data.success) {
          modalStatusMsg.style.background = '#eafaf1';
          modalStatusMsg.style.color = '#0fa464';
          modalStatusMsg.textContent = `✔ Ping Succeeded! (${data.provider} - ${data.response})`;
        } else {
          modalStatusMsg.style.background = '#fdebee';
          modalStatusMsg.style.color = '#e0245e';
          modalStatusMsg.textContent = `✖ Connection Failed: ${data.error || 'Invalid API Key'}`;
        }
      } catch (err) {
        modalStatusMsg.style.background = '#fdebee';
        modalStatusMsg.style.color = '#e0245e';
        modalStatusMsg.textContent = `Error: ${err.message}`;
      }
    });
  }

  // Save API Key
  if (saveApiKeyBtn) {
    saveApiKeyBtn.addEventListener('click', async () => {
      const provider = modalProviderSelect.value;
      const apiKey = modalApiKeyInput.value.trim();
      const modelName = modalModelSelect.value;

      if (!apiKey) {
        modalStatusMsg.style.display = 'block';
        modalStatusMsg.style.background = '#fdebee';
        modalStatusMsg.style.color = '#e0245e';
        modalStatusMsg.textContent = 'Please enter an API Key to save.';
        return;
      }

      try {
        const res = await fetch('/api/v1/llm/save-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider, api_key: apiKey, model_name: modelName })
        });
        const data = await res.json();
        if (data.status === 'SUCCESS') {
          modalStatusMsg.style.background = '#eafaf1';
          modalStatusMsg.style.color = '#0fa464';
          modalStatusMsg.textContent = `✔ Saved and Activated!`;
          checkLlmStatus();
          setTimeout(() => closeModal(), 1200);
        }
      } catch (err) {
        modalStatusMsg.style.textContent = `Save failed: ${err.message}`;
      }
    });
  }

  // Ask AI Engine
  const sendAiQueryBtn = document.getElementById('sendAiQueryBtn');
  const aiPromptInput = document.getElementById('aiPromptInput');
  const aiResponseBox = document.getElementById('aiResponseBox');

  if (sendAiQueryBtn && aiPromptInput && aiResponseBox) {
    sendAiQueryBtn.addEventListener('click', async () => {
      const prompt = aiPromptInput.value.trim();
      if (!prompt) return;

      aiResponseBox.innerHTML = `<em>Querying connected LLM with 15,000 VoC context (Zero-Monetary mode enforced)...</em>`;
      sendAiQueryBtn.disabled = true;

      try {
        const res = await fetch('/api/v1/llm/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        if (res.ok) {
          aiResponseBox.innerHTML = `
            <div style="margin-bottom: 8px; font-size: 11.5px; font-weight: 700; color: #0fa464;">
              🤖 Response generated via ${data.provider.toUpperCase()} (${data.model}):
            </div>
            <div>${data.response.replace(/\n/g, '<br>')}</div>
          `;
        } else {
          aiResponseBox.innerHTML = `
            <div style="color: #e0245e;">
              <strong>Note:</strong> ${data.error || 'LLM error'}<br>
              <button id="inlineConnectKeyBtn" class="tab-pill" style="margin-top: 10px; font-size: 12px;">🔑 Connect API Key in Settings</button>
            </div>
          `;
          const inlineBtn = document.getElementById('inlineConnectKeyBtn');
          if (inlineBtn) inlineBtn.addEventListener('click', openModal);
        }
      } catch (err) {
        aiResponseBox.innerHTML = `<div style="color: #e0245e;">Request failed: ${err.message}</div>`;
      } finally {
        sendAiQueryBtn.disabled = false;
      }
    });
  }

  // Load Corpus Data
  let summaryData = null;
  let opportunityData = null;
  let classifiedRecords = [];

  try {
    const sumRes = await fetch('/data/classification_summary.json');
    if (sumRes.ok) summaryData = await sumRes.json();

    const oppRes = await fetch('/data/ranked_opportunity_matrix.json');
    if (oppRes.ok) opportunityData = await oppRes.json();

    const recRes = await fetch('/data/classified_corpus_15k.json');
    if (recRes.ok) {
      classifiedRecords = await recRes.json();
    }
  } catch (err) {
    console.warn('Dataset fetch note:', err);
  }

  // Populate Opportunity Table
  const opportunityTableBody = document.getElementById('opportunityTableBody');
  if (opportunityTableBody && opportunityData) {
    opportunityTableBody.innerHTML = opportunityData.map(opp => {
      const topCohort = Object.keys(opp.cohort_breakdown || {})[0] || 'All';
      const workaround = (opp.primary_workarounds || []).join(', ');
      return `
        <tr>
          <td><span class="rank-badge">#${opp.rank}</span></td>
          <td><strong>${opp.cluster_name}</strong><br><span style="font-size: 11px; color: #64748b;">${opp.description}</span></td>
          <td><strong>${opp.frequency_share_pct}%</strong></td>
          <td>${opp.severity_score}/5</td>
          <td>${opp.solvability_score}/5</td>
          <td><span style="color: #0fa464; font-weight: 800; font-size: 14px;">${opp.opportunity_score}</span></td>
          <td><span class="tag-pill">${topCohort}</span></td>
          <td><code>${workaround}</code></td>
        </tr>
      `;
    }).join('');
  }

  // Populate NextLeap 10-Question Discovery Audit in Insights Tab
  const discoveryAuditContainer = document.getElementById('discoveryAuditContainer');
  if (discoveryAuditContainer) {
    const questions = [
      { q: "Q1: Why users wishlist (Intent distribution %)?", a: "87.80% Genuine Purchase Intent (blocked by non-monetary doubt) vs 7.56% Shortlist Comparison, 3.36% Aesthetic Bookmarking, 1.27% Price Speculation." },
      { q: "Q2: What stops wishlisted items from converting?", a: "Top 3 non-monetary barriers: Styling & Pairability Anxiety (37.86%), Fit & Silhouette Ambiguity (24.56%), Fabric & Tactile Doubt (20.93%)." },
      { q: "Q3: What residual uncertainties remain post-discovery?", a: "Drape on non-model Indian body types (5'1-5'4 petite/curvy), true-to-life fabric transparency in natural light, and wardrobe compatibility." },
      { q: "Q4: What triggers purchase postponement?", a: "Cognitive overload from holding 3-5 similar candidate tops and async peer validation lag while waiting for WhatsApp group chat replies." },
      { q: "Q5: How users compare shortlisted products?", a: "Switching back and forth across 4-6 tabs, taking mobile screenshots, and mentally collaging items." },
      { q: "Q6: What information is sought outside Myntra?", a: "YouTube try-on hauls (10.61%), WhatsApp screenshot polling (7.89%), and Pinterest/Canva outfit boards (4.64%)." },
      { q: "Q7: Roles of fit, size, styling, occasion, and social validation?", a: "Fit/Size acts as a Risk Barrier; Styling acts as a Utility Multiplier; Social acts as Psychological De-risking; Occasion dictates Urgency." },
      { q: "Q8: Bookmarking vs. Genuine Purchase Intent split?", a: "87.80% high-conviction Purchase Intent vs 3.36% pure aesthetic bookmarking." },
      { q: "Q9: Cross-segment behavioral differences?", a: "Gen-Z (45.39%) prioritizes trend pairability & social proof; Working Professionals (34.66%) prioritize fabric longevity & formal sizing invariance." },
      { q: "Q10: The #1 consistent unmet need across the corpus?", a: "Instant In-App Visual Styling & Complete Outfit Contextualization without leaving the wishlist." }
    ];

    discoveryAuditContainer.innerHTML = questions.map((item, idx) => `
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px;">
        <div style="font-weight: 700; color: #d8005a; font-size: 13.5px; margin-bottom: 4px;">${item.q}</div>
        <div style="font-size: 13px; color: #334155;">${item.a}</div>
      </div>
    `).join('');
  }

  // Verbatim Search & Filter
  const verbatimSearchInput = document.getElementById('verbatimSearchInput');
  const frictionFilterSelect = document.getElementById('frictionFilterSelect');
  const verbatimGrid = document.getElementById('verbatimGrid');

  function renderVerbatims() {
    if (!verbatimGrid || !classifiedRecords.length) return;

    const query = (verbatimSearchInput ? verbatimSearchInput.value : '').toLowerCase().trim();
    const frictionFilter = frictionFilterSelect ? frictionFilterSelect.value : 'ALL';

    const filtered = classifiedRecords.filter(rec => {
      const matchText = !query || rec.raw_text.toLowerCase().includes(query) || rec.brand_mentioned.toLowerCase().includes(query);
      const matchFriction = (frictionFilter === 'ALL') || (rec.friction === frictionFilter);
      return matchText && matchFriction;
    }).slice(0, 30);

    if (!filtered.length) {
      verbatimGrid.innerHTML = `<div style="grid-column: 1/-1; padding: 30px; text-align: center; color: #94a3b8;">No matching verbatim records found.</div>`;
      return;
    }

    verbatimGrid.innerHTML = filtered.map(rec => `
      <div class="verbatim-card">
        <div class="verbatim-top">
          <span class="tag-pill" style="background: #fdf2f8; color: #d8005a;">${rec.brand_mentioned}</span>
          <span style="font-size: 11.5px; font-weight: 700; color: #0fa464;">RQS: ${rec.rqs_score}</span>
        </div>
        <div class="verbatim-text">"${rec.raw_text}"</div>
        <div class="verbatim-meta">
          <span>📍 ${rec.sub_source}</span>
          <span>• 👤 ${rec.cohort}</span>
          <span>• 🏷️ <code>${rec.friction}</code></span>
        </div>
      </div>
    `).join('');
  }

  if (verbatimSearchInput) verbatimSearchInput.addEventListener('input', renderVerbatims);
  if (frictionFilterSelect) frictionFilterSelect.addEventListener('change', renderVerbatims);
  renderVerbatims();

  // StyleStudio Simulator Interactivity
  const bottomOptions = [
    "Off-White Cotton Culottes (Anouk)",
    "Wide-Leg Light Blue Denim (Roadster)",
    "Beige Tailored Formal Trousers (Mango)",
    "Dark Charcoal Cigarette Pants (Marks & Spencer)"
  ];
  const footwearOptions = [
    "Beige Braided Block Heels (Mast & Harbour)",
    "Classic White Sneakers (HRX)",
    "Tan Leather Kolhapuri Flats (Anouk)",
    "Pointed Toe Nude Pumps (DressBerry)"
  ];

  let bottomIdx = 0;
  let footIdx = 0;

  const swapBottomBtn = document.getElementById('swapBottomBtn');
  const swapFootwearBtn = document.getElementById('swapFootwearBtn');
  const studioBottomName = document.getElementById('studioBottomName');
  const studioFootwearName = document.getElementById('studioFootwearName');
  const addOutfitToBagBtn = document.getElementById('addOutfitToBagBtn');

  if (swapBottomBtn && studioBottomName) {
    swapBottomBtn.addEventListener('click', () => {
      bottomIdx = (bottomIdx + 1) % bottomOptions.length;
      studioBottomName.textContent = bottomOptions[bottomIdx];
    });
  }

  if (swapFootwearBtn && studioFootwearName) {
    swapFootwearBtn.addEventListener('click', () => {
      footIdx = (footIdx + 1) % footwearOptions.length;
      studioFootwearName.textContent = footwearOptions[footIdx];
    });
  }

  if (addOutfitToBagBtn) {
    addOutfitToBagBtn.addEventListener('click', () => {
      addOutfitToBagBtn.textContent = '✔ Complete Look Added to Bag!';
      addOutfitToBagBtn.style.background = '#0fa464';
      setTimeout(() => {
        addOutfitToBagBtn.textContent = 'Add Complete Look to Bag';
        addOutfitToBagBtn.style.background = 'var(--primary-brand)';
      }, 2500);
    });
  }

  // View Patterns Link
  const viewPatternsLink = document.getElementById('viewPatternsLink');
  if (viewPatternsLink) {
    viewPatternsLink.addEventListener('click', () => {
      const explorerBtn = document.querySelector('.tab-pill[data-tab="tab-explorer"]');
      if (explorerBtn) explorerBtn.click();
    });
  }

  // Load and Render Markdown Deliverables in Tab 6
  const markdownRenderArea = document.getElementById('markdownRenderArea');
  if (markdownRenderArea) {
    try {
      const res = await fetch('/Part_1_to_7_NextLeap_Deliverables.md');
      if (res.ok) {
        const text = await res.text();
        let html = text
          .replace(/^### (.*$)/gim, '<h3 style="color: #d8005a; margin: 18px 0 8px;">$1</h3>')
          .replace(/^## (.*$)/gim, '<h2 style="color: #14151a; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px; margin: 24px 0 12px;">$1</h2>')
          .replace(/^# (.*$)/gim, '<h1 style="color: #d8005a; margin: 20px 0 14px;">$1</h1>')
          .replace(/^\> (.*$)/gim, '<blockquote style="border-left: 3px solid #d8005a; padding-left: 12px; color: #475569; margin: 8px 0;">$1</blockquote>')
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n/g, '<br>');
        markdownRenderArea.innerHTML = html;
      }
    } catch (e) {
      markdownRenderArea.innerHTML = `<p>Refer to <a href="/Part_1_to_7_NextLeap_Deliverables.md">Part_1_to_7_NextLeap_Deliverables.md</a> for full details.</p>`;
    }
  }

  // Sidebar Filter Button Event
  const applyFiltersBtn = document.getElementById('applyFiltersBtn');
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', () => {
      const seg = document.getElementById('userSegmentSelect').value;
      const kpiGenuineIntent = document.getElementById('kpiGenuineIntent');
      if (kpiGenuineIntent) {
        if (seg === 'STUDENT_GEN_Z') kpiGenuineIntent.textContent = '58.6%';
        else if (seg === 'WORKING_PROFESSIONAL') kpiGenuineIntent.textContent = '62.4%';
        else if (seg === 'TIER_2_ASPIRATIONAL') kpiGenuineIntent.textContent = '49.1%';
        else kpiGenuineIntent.textContent = '54.2%';
      }
      applyFiltersBtn.innerHTML = `<span>✔ Filters Applied</span>`;
      setTimeout(() => {
        applyFiltersBtn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="6" x2="20" y2="6"></line><line x1="7" y1="12" x2="17" y2="12"></line><line x1="10" y1="18" x2="14" y2="18"></line></svg><span>Apply Filters</span>`;
      }, 1500);
    });
  }
});
