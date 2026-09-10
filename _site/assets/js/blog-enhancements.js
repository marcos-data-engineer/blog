(function () {
  'use strict';

  var WORDS_PER_MINUTE = 200;

  function slugify(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-');
  }

  function addCopyButtons() {
    document.querySelectorAll('.content pre code').forEach(function (code) {
      var pre = code.parentElement;
      if (!pre || pre.querySelector('.copy-code-button')) return;

      pre.classList.add('copy-code-block');
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'copy-code-button';
      button.textContent = 'Copy';
      button.addEventListener('click', function () {
        var onSuccess = function () {
          button.textContent = 'Copied!';
          button.classList.add('is-copied');
          window.setTimeout(function () {
            button.textContent = 'Copy';
            button.classList.remove('is-copied');
          }, 1800);
        };

        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(code.textContent).then(onSuccess);
          return;
        }

        var range = document.createRange();
        range.selectNodeContents(code);
        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        var copied = document.execCommand('copy');
        selection.removeAllRanges();
        if (copied) onSuccess();
      });
      pre.appendChild(button);
    });
  }

  function addReadingTime() {
    var content = document.querySelector('.content');
    var target = document.querySelector('[data-reading-time]');
    if (!content || !target) return;

    var words = content.textContent.trim().split(/\s+/).filter(Boolean).length;
    var minutes = Math.max(1, Math.ceil(words / WORDS_PER_MINUTE));
    target.textContent = minutes + ' min read';
    target.setAttribute('aria-label', 'Estimated reading time: ' + minutes + ' minutes');
  }

  function buildTableOfContents() {
    var content = document.querySelector('.content');
    var toc = document.querySelector('#toc');
    if (!content || !toc) return;

    var headings = Array.from(content.querySelectorAll('h2, h3'));
    if (!headings.length) {
      toc.closest('#toc-wrapper')?.classList.add('d-none');
      return;
    }

    var usedIds = {};
    var list = document.createElement('ol');
    headings.forEach(function (heading) {
      var baseId = heading.id || slugify(heading.textContent);
      var id = baseId || 'section';
      var suffix = 2;
      while (usedIds[id] || (document.getElementById(id) && document.getElementById(id) !== heading)) {
        id = baseId + '-' + suffix++;
      }
      usedIds[id] = true;
      heading.id = id;

      var item = document.createElement('li');
      item.className = heading.tagName === 'H3' ? 'toc-h3' : 'toc-h2';
      var link = document.createElement('a');
      link.href = '#' + id;
      link.textContent = heading.textContent.trim();
      item.appendChild(link);
      list.appendChild(item);
    });

    toc.replaceChildren(list);
    toc.closest('#toc-wrapper')?.classList.remove('invisible');
  }

  function init() {
    addCopyButtons();
    addReadingTime();
    buildTableOfContents();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
