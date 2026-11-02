(function () {
  const MONTH_CN = [
    "", "一月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月"
  ];

  const els = {
    title: document.getElementById("title"),
    yearLabel: document.getElementById("year-label"),
    monthlyItems: document.getElementById("monthly-items"),
    monthsWithContent: document.getElementById("months-with-content"),
    outsideItems: document.getElementById("outside-items"),
    progressText: document.getElementById("progress-text"),
    progressBar: document.getElementById("progress-bar"),
    progressFill: document.getElementById("progress-fill"),
    currentMonthBadge: document.getElementById("current-month-badge"),
    currentChips: document.getElementById("current-chips"),
    monthTable: document.getElementById("month-table"),
    monthList: document.getElementById("month-list"),
    outsideBadge: document.getElementById("outside-badge"),
    outsideList: document.getElementById("outside-list"),
    generatedAt: document.getElementById("generated-at"),
    footerYear: document.getElementById("footer-year"),
    toggleAll: document.getElementById("toggle-all"),
    error: document.getElementById("error"),
  };

  function dataUrl(year) {
    // Resolve relative to this page so project Pages (/goose-render-index/) works.
    return new URL(`./data/${year}.json`, window.location.href).toString();
  }

  function formatGeneratedAt(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    try {
      return new Intl.DateTimeFormat("zh-CN", {
        timeZone: "Asia/Shanghai",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      }).format(d) + " (Asia/Shanghai)";
    } catch (_) {
      return iso;
    }
  }

  function statusFor(month, currentMonth) {
    if (month.count > 0 && month.number === currentMonth) {
      return { cls: "status current", label: "当月" };
    }
    if (month.count > 0) return { cls: "status ok", label: "有内容" };
    return { cls: "status empty", label: "空" };
  }

  function render(data) {
    const year = data.year || 2026;
    const current = data.current_month || new Date().getMonth() + 1;
    const monthsWith = data.months_with_content ?? data.months.filter((m) => m.count > 0).length;
    const monthly = data.monthly_items ?? data.months.reduce((s, m) => s + m.count, 0);
    const outsideCount = data.outside_items ?? (data.outside || []).reduce((s, o) => s + o.count, 0);

    const rawTitle = data.title || "抓大鹅渲染图统计清单";
    // Keep yellow marker on 渲染图 when the default Chinese title is used.
    if (rawTitle.includes("渲染图")) {
      els.title.innerHTML = rawTitle.replace("渲染图", '<span class="mark">渲染图</span>');
    } else {
      els.title.textContent = rawTitle;
    }
    els.yearLabel.textContent = `${year} 年度渲染进度`;
    els.footerYear.textContent = String(year);
    els.monthlyItems.textContent = String(monthly);
    els.monthsWithContent.textContent = String(monthsWith);
    els.outsideItems.textContent = String(outsideCount);

    const pct = Math.round((monthsWith / 12) * 100);
    els.progressText.textContent = `${monthsWith}/12 · ${pct}%`;
    els.progressFill.style.width = `${pct}%`;
    els.progressBar.setAttribute("aria-valuenow", String(monthsWith));

    const currentMonth = (data.months || []).find((m) => m.number === current) || {
      number: current,
      folder: "",
      items: [],
      count: 0,
    };
    els.currentMonthBadge.textContent = `${MONTH_CN[current] || current + "月"} · ${currentMonth.folder || "—"} · ${currentMonth.count} 项`;
    els.currentChips.innerHTML = "";
    if (!currentMonth.items || currentMonth.items.length === 0) {
      const empty = document.createElement("span");
      empty.className = "chip empty";
      empty.textContent = "本月暂无条目";
      els.currentChips.appendChild(empty);
    } else {
      currentMonth.items.forEach((name) => {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = name;
        els.currentChips.appendChild(chip);
      });
    }

    els.monthTable.innerHTML = "";
    (data.months || []).forEach((m) => {
      const st = statusFor(m, current);
      const tr = document.createElement("tr");
      if (m.number === current) tr.className = "current";
      tr.innerHTML = `
        <td>${MONTH_CN[m.number] || m.number}</td>
        <td><code>${m.folder || "—"}</code></td>
        <td>${m.count}</td>
        <td><span class="${st.cls}"><span class="status-dot"></span>${st.label}</span></td>
      `;
      els.monthTable.appendChild(tr);
    });

    els.monthList.innerHTML = "";
    (data.months || []).forEach((m) => {
      const details = document.createElement("details");
      details.className = "card";
      if (m.number === current) details.open = true;
      const summary = document.createElement("summary");
      summary.innerHTML = `<span>${MONTH_CN[m.number] || m.number} · ${m.folder}</span><span class="muted">${m.count} 项</span>`;
      details.appendChild(summary);
      if (!m.items || m.items.length === 0) {
        const note = document.createElement("p");
        note.className = "empty-note";
        note.textContent = "暂无条目";
        details.appendChild(note);
      } else {
        const ul = document.createElement("ul");
        ul.className = "item-list";
        m.items.forEach((name) => {
          const li = document.createElement("li");
          li.textContent = name;
          ul.appendChild(li);
        });
        details.appendChild(ul);
      }
      els.monthList.appendChild(details);
    });

    const outside = data.outside || [];
    els.outsideBadge.textContent = `${outsideCount} 项 · ${outside.length} 分组`;
    els.outsideList.innerHTML = "";
    if (outside.length === 0) {
      const note = document.createElement("p");
      note.className = "empty-note";
      note.textContent = "暂无月度外条目";
      els.outsideList.appendChild(note);
    } else {
      outside.forEach((group) => {
        const details = document.createElement("details");
        details.className = "card";
        details.open = true;
        const summary = document.createElement("summary");
        summary.innerHTML = `<span>${group.folder}</span><span class="muted">${group.count} 项</span>`;
        details.appendChild(summary);
        const ul = document.createElement("ul");
        ul.className = "item-list";
        (group.items || []).forEach((name) => {
          const li = document.createElement("li");
          li.textContent = name;
          ul.appendChild(li);
        });
        details.appendChild(ul);
        els.outsideList.appendChild(details);
      });
    }

    els.generatedAt.textContent = formatGeneratedAt(data.generated_at);
    els.generatedAt.setAttribute("datetime", data.generated_at || "");
  }

  let allOpen = false;
  els.toggleAll.addEventListener("click", () => {
    allOpen = !allOpen;
    document.querySelectorAll("#month-list details.card").forEach((d) => {
      d.open = allOpen;
    });
    els.toggleAll.textContent = allOpen ? "全部折叠" : "全部展开";
  });

  async function boot() {
    const year = 2026;
    try {
      const res = await fetch(dataUrl(year), { cache: "no-cache" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      render(data);
    } catch (err) {
      els.error.classList.remove("hidden");
      els.error.textContent = `无法加载 data/${year}.json：${err.message}`;
    }
  }

  boot();
})();
