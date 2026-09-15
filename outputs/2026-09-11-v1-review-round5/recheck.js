'use strict';
(() => {
  const data = JSON.parse(document.getElementById('review-data').textContent);
  const items = data.items;
  const testMode = new URLSearchParams(location.search).get('test') === '1';
  const key = data.version + (testMode ? '-test' : '');
  let storage;
  let records = {};
  let filter = items.some(item => item.confirmedRound === data.round) && !items.some(item => item.deliveryStatus === 'ready') ? 'done' : 'todo';
  const $ = id => document.getElementById(id);
  const itemById = new Map(items.map(item => [item.id, item]));
  const cards = new Map();
  const timestamp = () => new Date().toISOString();
  const escapeText = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  function error(message) { $('error').textContent = message; $('error').hidden = !message; }
  function validateRecords(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw Error('紀錄格式不正確');
    const clean = {};
    for (const [id, record] of Object.entries(value)) {
      if (!itemById.has(id) || !record || typeof record !== 'object') throw Error('項目編號不正確');
      if (record.confirmed !== undefined && typeof record.confirmed !== 'boolean') throw Error('勾選格式不正確');
      if (record.note !== undefined && (typeof record.note !== 'string' || record.note.length > 100000)) throw Error('意見格式不正確');
      if (typeof record.updatedAt !== 'string' || !Number.isFinite(Date.parse(record.updatedAt))) throw Error('紀錄時間不正確');
      clean[id] = {updatedAt: record.updatedAt, revision: String(record.revision || '')};
      if (record.confirmed !== undefined) clean[id].confirmed = record.confirmed;
      if (record.note !== undefined) clean[id].note = record.note;
    }
    return clean;
  }
  try {
    storage = testMode ? sessionStorage : localStorage;
    const saved = storage.getItem(key);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.version !== data.version) throw Error('版本不符');
      records = validateRecords(parsed.records);
    }
  } catch (e) {
    storage = null;
    error('目前無法讀取瀏覽器儲存紀錄。你的新操作仍可匯出，請先保留 JSON 檔。');
  }
  if (testMode) $('save-status').textContent = '測試模式，與正式複檢紀錄分開保存';
  function recordFor(item) {
    const record = records[item.id] || {};
    if (item.confirmedAt && Date.parse(record.updatedAt) < Date.parse(item.confirmedAt)) return {...record, confirmed: undefined};
    return record.revision === item.deliveryRevision ? record : {...record, confirmed: undefined};
  }
  function confirmed(item) {
    const record = recordFor(item);
    return typeof record.confirmed === 'boolean' ? record.confirmed : item.reviewStatus === 'accepted';
  }
  function rechecked(item) { return recordFor(item).confirmed === true || (item.confirmedRound === data.round && confirmed(item)); }
  function mergeRecords(current, incoming) {
    const merged = {...current};
    for (const [id, value] of Object.entries(incoming)) {
      if (!merged[id] || Date.parse(value.updatedAt) >= Date.parse(merged[id].updatedAt)) merged[id] = value;
    }
    return merged;
  }
  function persist() {
    try {
      if (!storage) throw Error('storage unavailable');
      const saved = storage.getItem(key);
      if (saved) records = mergeRecords(validateRecords(JSON.parse(saved).records), records);
      storage.setItem(key, JSON.stringify({version: data.version, records}));
      $('save-status').textContent = (testMode ? '測試紀錄已儲存 · ' : '已儲存於此瀏覽器 · ') + new Intl.DateTimeFormat('zh-TW', {hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date());
      return true;
    } catch (e) {
      $('save-status').textContent = '尚未存入瀏覽器，請匯出保留';
      error('瀏覽器無法儲存這次變更。請按「匯出複檢結果」保存，目前填寫內容仍在本頁。');
      return false;
    }
  }
  function save(item, patch) {
    records[item.id] = {...recordFor(item), ...patch, revision:item.deliveryRevision, updatedAt:timestamp()};
    persist();
  }
  const acceptedIds = items.filter(item => item.reviewStatus === 'accepted' && item.confirmedRound !== data.round);
  const waitingItems = items.filter(item => item.reviewStatus === 'waiting');
  function inFilter(item, which) {
    if (which === 'all') return true;
    if (which === 'waiting') return item.reviewStatus === 'waiting';
    if (which === 'accepted') return item.reviewStatus === 'accepted' && item.confirmedRound !== data.round;
    if (which === 'done') return rechecked(item) && item.reviewStatus !== 'waiting';
    return item.reviewStatus !== 'waiting' && !confirmed(item);
  }
  function refresh() {
    const search = $('search').value.trim().toLocaleLowerCase('zh-TW');
    const exactId = /^\d{1,2}$/.test(search) && itemById.has(search.padStart(2, '0')) ? search.padStart(2, '0') : null;
    let visible = 0;
    items.forEach(item => {
      const card = cards.get(item.id);
      const haystack = [item.id, item.title, item.currentChange, item.nextAction, item.deliveredChange, item.firstReview.note, item.previousRecheck.note, item.currentFocus, ...item.reviewHistory.flatMap(h=>[h.note,h.assistantResponse,h.assistantExplanation]), records[item.id]?.note].join(' ').toLocaleLowerCase('zh-TW');
      card.hidden = !inFilter(item, filter) || (exactId ? item.id !== exactId : (search && !haystack.includes(search)));
      if (!card.hidden) visible++;
      card.classList.toggle('complete', confirmed(item));
      const input = card.querySelector('input[type=checkbox]');
      if (input) input.checked = confirmed(item);
      const result = card.querySelector('.result');
      result.textContent = rechecked(item) ? '本輪複檢通過' : item.reviewStatus === 'accepted' && !confirmed(item) ? '重新開啟' : '';
      result.hidden = !result.textContent;
    });
    for (const button of document.querySelectorAll('[data-filter]')) {
      button.setAttribute('aria-pressed', String(button.dataset.filter === filter));
      button.querySelector('span').textContent = items.filter(item => inFilter(item, button.dataset.filter)).length;
    }
    $('remaining').textContent = items.filter(item => inFilter(item, 'todo')).length;
    $('rechecked').textContent = items.filter(item => inFilter(item, 'done')).length;
    $('accepted').textContent = acceptedIds.length;
    $('waiting').textContent = waitingItems.length;
    $('result-count').textContent = `顯示 ${visible} 項，共 ${items.length} 項`;
    $('empty').hidden = visible !== 0;
    $('empty-message').textContent = filter === 'done' && !search ? '本輪勾選通過的項目會出現在這裡。' : '換個篩選條件，或清除搜尋文字。';
  }
  const deliveryLabels = {pending:'待修改', waiting:'等資料', accepted:'此前已通過', partial:'部分完成・可先檢查', ready:'可複檢', editing:'修改中'};
  items.forEach(item => {
    const card = document.createElement('article');
    card.className = 'item'; card.id = 'item-' + item.id;
    const waiting = item.reviewStatus === 'waiting';
    const action = item.currentChange || item.nextAction || item.deliveredChange;
    const preview = new URL('../../v1/html/' + item.route, location.href);
    preview.searchParams.set('review', item.deliveryRevision);
    card.innerHTML = `<div class="item-head"><span class="number">${item.id}</span><div class="title-group"><h2>${escapeText(item.title)}</h2>${item.currentFocus ? `<p class="current-focus">本輪：${escapeText(item.currentFocus)}</p>` : ''}<div class="meta-badges"><span class="badge ${item.deliveryStatus}">${item.confirmedRound === data.round ? '本輪已通過' : deliveryLabels[item.deliveryStatus]}</span><span class="badge passed result" hidden></span></div></div></div><div class="body-grid"><div>${item.partialApproval ? `<p class="partial">${escapeText(item.partialApproval)}</p>` : ''}<h3>${item.reviewStatus === 'accepted' ? '已完成並通過的內容' : item.currentChange ? '這次已實際修改的內容' : item.reviewStatus === 'followup' ? '我的回覆／這次修改方向' : waiting ? '等待內容' : '已通過的內容'}</h3><p class="action-text">${escapeText(action)}</p>${item.currentCheck ? `<section class="current-check"><h3>這次請檢查</h3><p>${escapeText(item.currentCheck)}</p></section>` : ''}${item.deliveryLimit ? `<p class="delivery-limit"><strong>保留事項：</strong>${escapeText(item.deliveryLimit)}</p>` : ''}${item.assistantResponse ? `<section class="explanation"><h3>這次我的回覆</h3><p>${escapeText(item.assistantResponse)}</p></section>` : ''}${item.previousRecheck.note ? `<section class="original"><h3>你此前複檢的留言</h3><blockquote>${escapeText(item.previousRecheck.note)}</blockquote></section>` : ''}${item.reviewHistory.slice().reverse().map(history=>`<details class="prior-work"><summary>${escapeText(history.round)}｜${history.confirmed ? '已通過' : '尚未通過'}｜交付與回覆紀錄</summary><h3>當時交付</h3><p>${escapeText(history.deliveredChange || '沿用此前已交付內容')}</p>${history.check ? `<p>當時檢查：${escapeText(history.check)}</p>` : ''}${history.note ? `<h3>你的原留言</h3><blockquote>${escapeText(history.note)}</blockquote>` : ''}${history.assistantResponse || history.assistantExplanation ? `<h3>當時我的回覆</h3><p>${escapeText(history.assistantResponse || history.assistantExplanation)}</p>` : ''}${history.deliveryLimit ? `<p>當時保留事項：${escapeText(history.deliveryLimit)}</p>` : ''}</details>`).join('')}${item.dependency ? `<p class="dependency">相關調整：${escapeText(item.dependency)}</p>` : ''}<div class="preview-links"><a class="open" target="_blank" rel="noopener" href="${escapeText(preview.href)}">開啟頁面檢查 ↗</a>${item.id === '08' ? '<a class="open" target="_blank" rel="noopener" href="../../v1/html/board.html?term=2022">已通過的第一、二屆 ↗</a>' : ''}</div></div><div class="review-form">${waiting ? '<p class="waiting-hint">這項仍等資料，可先在下方補充素材進度。</p>' : `<label class="check-label" for="confirm-${item.id}"><input id="confirm-${item.id}" type="checkbox">${item.reviewStatus === 'accepted' ? '維持通過' : item.deliveryLimit ? '本輪已修改部分通過' : '我已複檢，這項通過'}</label>${item.reviewStatus === 'accepted' ? `<p class="carry-hint">${item.confirmationSource === 'conversation' ? '已依你在對話中的確認記錄通過' : '沿用你這次匯出的通過紀錄'}，需要再改可取消勾選。</p>` : ''}`}<label class="note-label" for="note-${item.id}">新的複檢意見</label><textarea id="note-${item.id}" rows="3" placeholder="還有需要調整的地方，可以寫在這裡。"></textarea></div></div>`;
    const note = card.querySelector('textarea');
    note.value = records[item.id]?.note || '';
    note.addEventListener('input', () => { save(item, {note:note.value}); });
    const checkbox = card.querySelector('input[type=checkbox]');
    if (checkbox) checkbox.addEventListener('change', () => { save(item, {confirmed:checkbox.checked}); refresh(); });
    cards.set(item.id, card); $('review-list').append(card);
  });
  const pendingCount = items.filter(item => ['pending','editing'].includes(item.deliveryStatus)).length;
  const readyCount = items.filter(item => item.deliveryStatus === 'ready').length;
  const partialCount = items.filter(item => item.deliveryStatus === 'partial').length;
  $('delivery-notice').textContent = `${readyCount} 項已實際修改、可複檢${partialCount ? `；${partialCount} 項部分完成，限制已寫在卡片內` : ''}。${items.filter(item => item.reviewStatus === 'accepted').length} 項已通過紀錄與歷次留言完整保留；${waitingItems.length} 項仍等資料。`;
  document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {filter = button.dataset.filter; refresh();}));
  $('search').addEventListener('input', refresh);
  $('show-all').addEventListener('click', () => {filter='all'; $('search').value=''; refresh();});
  function exportResults() {
    const result = {
      version:data.version, round:data.round, sourceVersion:data.sourceVersion,
      sourceExportedAt:data.sourceExportedAt, exportedAt:timestamp(),
      items:items.map(item => ({
        id:item.id, title:item.title, currentFocus:item.currentFocus || '', deliveryStatus:item.deliveryStatus,
        deliveryRevision:item.deliveryRevision, originalReviewStatus:item.reviewStatus,
        deliveredChange:item.deliveredChange, previousCheck:item.previousCheck,
        currentChange:item.currentChange || '', currentCheck:item.currentCheck || '', deliveryLimit:item.deliveryLimit || '', route:item.route,
        nextAction:item.nextAction, assistantExplanation:item.assistantExplanation,
        firstReview:item.firstReview, partialApproval:item.partialApproval,
        previousRecheck:item.previousRecheck, reviewHistory:item.reviewHistory, assistantResponse:item.assistantResponse, dependency:item.dependency,
        confirmed:confirmed(item),
        confirmationSource:typeof recordFor(item).confirmed === 'boolean' ? 'recheck' : item.confirmationSource || (item.reviewStatus === 'accepted' ? 'third-recheck' : 'not-reviewed'),
        confirmedAt:item.confirmedAt || null,
        note:records[item.id]?.note || '', recheck:records[item.id] || null
      }))
    };
    const blob = new Blob([JSON.stringify(result,null,2)], {type:'application/json;charset=utf-8'});
    const url = URL.createObjectURL(blob); const link = document.createElement('a');
    link.href=url; link.download='TIRI-v1-第五輪複檢結果.json'; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $('save-status').textContent='已匯出複檢結果，可把 JSON 檔傳給我';
  }
  $('export').addEventListener('click', exportResults);
  $('export-bottom').addEventListener('click', exportResults);
  $('import').addEventListener('click', () => $('import-file').click());
  $('import-file').addEventListener('change', async event => {
    const file = event.target.files[0]; if (!file) return;
    try {
      if (file.size > 2000000) throw Error('檔案太大');
      const parsed = JSON.parse(await file.text());
      if (parsed.version !== data.version || !Array.isArray(parsed.items)) throw Error('請選這一頁匯出的複檢 JSON；此前複檢結果已經帶入');
      if (parsed.items.length !== items.length || new Set(parsed.items.map(item => item.id)).size !== items.length) throw Error('項目數量不完整');
      const incoming = {};
      for (const row of parsed.items) {
        if (!itemById.has(row.id)) throw Error('含有不屬於本輪的項目');
        if (row.recheck) incoming[row.id] = row.recheck;
      }
      const clean = validateRecords(incoming);
      records = mergeRecords(records, clean); const saved = persist();
      items.forEach(item => {cards.get(item.id).querySelector('textarea').value=records[item.id]?.note || '';});
      refresh(); if (saved) error('');
      $('save-status').textContent=`已匯入 ${Object.keys(clean).length} 項複檢紀錄；同項保留較新的紀錄` + (saved ? '' : '，請再次匯出保存');
    } catch (e) { error('未匯入：' + e.message + '。現有紀錄已保留。'); }
    event.target.value='';
  });
  window.addEventListener('storage', event => {
    if (event.key !== key || !event.newValue) return;
    try {
      records = mergeRecords(records, validateRecords(JSON.parse(event.newValue).records));
      items.forEach(item => {const note=cards.get(item.id).querySelector('textarea'); if (note !== document.activeElement) note.value=records[item.id]?.note || '';});
      refresh();
    } catch (e) { error('其他分頁的紀錄無法讀取，這頁內容已保留。'); }
  });
  refresh();
})();
