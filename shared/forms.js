/* TIRI 過渡期表單串接：把報名表單改送自建後端（原版 Weebly 表單＋V1/V2 改版表單通用） */
(function () {
  var IS_LOCAL = location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.protocol === 'file:';
  var API_BASE = window.TIRI_FORMS_API || (IS_LOCAL ? 'http://localhost:8000' : 'https://tiribackend.justhings.com.tw');

  /* 只有這六種表單是真的要收件的；其他 data-demo-form（訂閱/登入/搜尋）維持示意 */
  var REAL_FORMS = ['join', 'trainbod', 'tiric', 'bodperform', 'corpperform', 'contact'];

  var slug = location.pathname.split('/').pop().replace(/\.html$/, '');
  var isRealFormPage = REAL_FORMS.indexOf(slug.split('-')[0]) !== -1;

  function cleanLabel(el) {
    if (!el) return '';
    return el.textContent.replace(/\*/g, '').replace(/表示必填欄位/, '').trim();
  }

  /* ---- 原版（Weebly 匯出）欄位 ---- */

  function wsiteValue(fieldEl) {
    var radios = fieldEl.querySelectorAll('input[type="radio"]');
    if (radios.length) {
      for (var i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
          var radioLabel = radios[i].closest('label') || radios[i].parentElement;
          return (radioLabel ? radioLabel.textContent : radios[i].value).trim();
        }
      }
      return '';
    }
    var parts = [];
    fieldEl.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], textarea, select').forEach(function (el) {
      if (el.value && el.value.trim()) parts.push(el.value.trim());
    });
    return parts.join(' ');
  }

  function collectWsite(form) {
    var fields = [], missing = [];
    form.querySelectorAll('.wsite-form-field').forEach(function (fieldEl) {
      var label = cleanLabel(fieldEl.querySelector('.wsite-form-label'));
      if (!label) return;
      var value = wsiteValue(fieldEl);
      var required = fieldEl.querySelector('.form-required, [aria-required="true"]');
      if (required && !value) missing.push(label);
      fields.push({ label: label, value: value });
    });
    return { fields: fields, missing: missing };
  }

  /* ---- V1/V2 改版表單欄位（.field > label + input/select/textarea） ---- */

  function collectRedesign(form) {
    var fields = [], missing = [];
    form.querySelectorAll('.field').forEach(function (fieldEl) {
      var label = cleanLabel(fieldEl.querySelector('label'));
      var input = fieldEl.querySelector('input, select, textarea');
      if (!label || !input) return;
      var value = (input.value || '').trim();
      if (input.required && !value) missing.push(label);
      fields.push({ label: label, value: value });
    });
    return { fields: fields, missing: missing };
  }

  function showMessage(form, text, isError) {
    var msg = form.parentElement.querySelector('.tiri-form-msg');
    if (!msg) {
      msg = document.createElement('p');
      msg.className = 'tiri-form-msg';
      form.parentElement.insertBefore(msg, form);
    }
    msg.textContent = text;
    msg.style.cssText = 'padding:12px 16px;border:1px solid;margin:0 0 16px;' +
      (isError ? 'color:#a4262c;border-color:#a4262c;background:#fdf3f4;'
               : 'color:#1b5e20;border-color:#1b5e20;background:#f1f8f2;');
  }

  function bind(form, collect) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var data = collect(form);
      if (data.missing.length) {
        showMessage(form, '請填寫必填欄位:' + data.missing.join('、'), true);
        return;
      }

      var submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      fetch(API_BASE + '/api/submit/' + encodeURIComponent(slug), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page: location.href,
          website: '', /* honeypot */
          fields: data.fields
        })
      }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        form.style.display = 'none';
        showMessage(form, '已收到您的填寫，我們會盡快與您聯繫，謝謝!');
      }).catch(function () {
        if (submitBtn) submitBtn.disabled = false;
        showMessage(form, '送出失敗，請稍後再試，或直接來信 office@tiri.tw', true);
      });
    });

    /* 原版裝飾用的 <a class="wsite-button"> 也綁定提交 */
    var fancy = form.querySelector('a.wsite-button');
    if (fancy) {
      fancy.style.cursor = 'pointer';
      fancy.addEventListener('click', function () {
        if (typeof form.requestSubmit === 'function') form.requestSubmit();
        else form.dispatchEvent(new Event('submit', { cancelable: true }));
      });
    }
  }

  document.querySelectorAll('form[action*="formSubmit"]').forEach(function (form) {
    bind(form, collectWsite);
  });

  if (isRealFormPage) {
    document.querySelectorAll('form[data-demo-form]').forEach(function (form) {
      /* 同頁可能還有搜尋/訂閱等示意表單，只綁真正的報名表（至少兩個 .field 欄位） */
      if (form.querySelectorAll('.field').length < 2) return;
      bind(form, collectRedesign);
    });
  }
})();
