// ==================== SEMIRA AI AGENT v3.0 ====================
(function () {
    'use strict';

    var AI_ENDPOINT        = '/api/ai-chat';
    var SUGGESTIONS_ENDPOINT = '/api/ai-chat/suggestions';
    var MAX_HISTORY        = 20;
    var HISTORY_SENT       = 8;
    var SESSION_KEY        = 'semira_ai_history';

    var history    = [];
    var isOpen     = false;
    var isTyping   = false;
    var suggestions = [];
    var lastFailedMsg = null;  // for retry

    var panel, msgList, inputEl, sendBtn, badge, toggleBtn;

    // ── Load/save history via sessionStorage ──────────────────────────────
    function loadHistory() {
        try {
            var raw = sessionStorage.getItem(SESSION_KEY);
            if (raw) history = JSON.parse(raw);
        } catch (e) { history = []; }
    }

    function saveHistory() {
        try {
            sessionStorage.setItem(SESSION_KEY, JSON.stringify(history.slice(-MAX_HISTORY)));
        } catch (e) {}
    }

    // ── Init ──────────────────────────────────────────────────────────────
    function init() {
        panel     = document.getElementById('semira-ai-panel');
        msgList   = document.getElementById('semira-ai-messages');
        inputEl   = document.getElementById('semira-ai-input');
        sendBtn   = document.getElementById('semira-ai-send');
        badge     = document.getElementById('semira-ai-badge');
        toggleBtn = document.getElementById('semira-ai-toggle');

        if (!panel) return;

        loadHistory();

        sendBtn.addEventListener('click', handleSend);
        inputEl.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
        });
        inputEl.addEventListener('input', function () {
            sendBtn.disabled = !this.value.trim();
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 110) + 'px';
            // Character counter update
            var counter = document.getElementById('ai-char-counter');
            if (counter) {
                var len = this.value.length;
                counter.textContent = len > 0 ? len + '/500' : '';
                counter.style.color = len > 450 ? '#ef4444' : '#9ca3af';
            }
        });

        fetch(SUGGESTIONS_ENDPOINT)
            .then(function (r) { return r.json(); })
            .then(function (d) { if (d.success) suggestions = d.suggestions; })
            .catch(function () {});

        // Pulse badge after 5s if user hasn't opened
        setTimeout(function () {
            if (!isOpen && badge) {
                badge.style.display = 'flex';
                badge.classList.add('ai-badge-pulse');
            }
        }, 5000);
    }

    // ── Toggle / Close ────────────────────────────────────────────────────
    window.toggleAIPanel = function () {
        isOpen = !isOpen;
        if (isOpen) {
            panel.classList.add('open');
            if (badge) { badge.style.display = 'none'; badge.classList.remove('ai-badge-pulse'); }
            if (msgList.children.length === 0) {
                if (history.length > 0) restoreHistory();
                else showWelcome();
            }
            setTimeout(function () { if (inputEl) inputEl.focus(); }, 300);
        } else {
            panel.classList.remove('open');
        }
    };

    window.closeAIPanel = function () {
        isOpen = false;
        panel.classList.remove('open');
    };

    window.clearAIChat = function () {
        history = [];
        saveHistory();
        lastFailedMsg = null;
        if (msgList) {
            msgList.innerHTML = '';
            showWelcome();
        }
    };

    // ── Restore history from sessionStorage ───────────────────────────────
    function restoreHistory() {
        history.forEach(function (h) {
            if (h.role === 'user' || h.role === 'assistant') {
                appendMessage(h.role, h.content, false);
            }
        });
        scrollBottom();
    }

    // ── Welcome message ───────────────────────────────────────────────────
    function showWelcome() {
        var lang = document.documentElement.lang || 'am';
        var welcome = {
            ar: 'أهلاً! 👗 أنا **سيميرا**، مساعدتك في SEMIRA FASHION.\n\nيمكنني مساعدتك في المنتجات والأسعار والطلبات والمقاسات والشحن.',
            en: "Hello! 👗 I'm **SEMIRA**, your AI shopping assistant.\n\nI can help with products, prices, orders, cart, sizing & shipping!",
            am: 'ሰላም! 👗 እኔ **ሰሚራ** ነኝ — የ SEMIRA FASHION AI አስተናጋጅ።\n\nምርቶች፣ ዋጋ፣ ቅርጫት፣ ትዕዛዝ ሁኔታ — ሁሉ ልረዳ እችላለሁ! 🌸',
        }[lang] || 'ሰላም! 👗 እኔ ሰሚራ ነኝ — ምን ልርዳዎ?';
        appendMessage('assistant', welcome, true);
        if (suggestions.length) setTimeout(showSuggestions, 500);
    }

    // ── Suggestion chips ──────────────────────────────────────────────────
    function showSuggestions() {
        if (!msgList) return;
        // Remove existing chips
        var existing = document.getElementById('ai-suggestion-chips');
        if (existing) existing.remove();

        var div = document.createElement('div');
        div.className = 'ai-suggestions';
        div.id = 'ai-suggestion-chips';
        suggestions.forEach(function (s) {
            var btn = document.createElement('button');
            btn.className = 'ai-chip';
            btn.textContent = s;
            btn.onclick = function () {
                div.remove();
                inputEl.value = s;
                inputEl.dispatchEvent(new Event('input'));
                handleSend();
            };
            div.appendChild(btn);
        });
        msgList.appendChild(div);
        scrollBottom();
    }

    // ── Send handler ──────────────────────────────────────────────────────
    function handleSend(textOverride) {
        var text = textOverride || (inputEl ? inputEl.value.trim() : '');
        if (!text || isTyping) return;

        if (!textOverride) {
            inputEl.value = '';
            inputEl.style.height = 'auto';
            var counter = document.getElementById('ai-char-counter');
            if (counter) counter.textContent = '';
        }
        sendBtn.disabled = true;
        lastFailedMsg = null;

        var chips = document.getElementById('ai-suggestion-chips');
        if (chips) chips.remove();

        appendMessage('user', text, true);
        showTyping();

        fetch(AI_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                history: history.slice(-HISTORY_SENT)
            })
        })
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(function (d) {
            hideTyping();
            var reply = d.reply || 'ይቅርታ፣ አሁን ልረዳ አልቻልኩም። እንደገና ይሞክሩ።';
            appendMessage('assistant', reply, true);
            history.push({ role: 'user', content: text });
            history.push({ role: 'assistant', content: reply });
            if (history.length > MAX_HISTORY) history = history.slice(-MAX_HISTORY);
            saveHistory();
        })
        .catch(function (err) {
            hideTyping();
            lastFailedMsg = text;
            showError();
            console.warn('AI Agent error:', err);
        });
    }

    // ── Error message with retry ──────────────────────────────────────────
    function showError() {
        if (!msgList) return;
        var lang = document.documentElement.lang || 'am';
        var errText = {
            ar: 'حدث خطأ في الاتصال.',
            en: 'Connection error. Please try again.',
            am: 'ግንኙነት ችግር ነበር። እንደገና ይሞክሩ።',
        }[lang] || 'ግንኙነት ችግር ነበር። እንደገና ይሞክሩ።';
        var retryLabel = { ar: '↻ إعادة', en: '↻ Retry', am: '↻ እንደገና' }[lang] || '↻ Retry';

        var wrap = document.createElement('div');
        wrap.className = 'ai-msg-wrap ai-msg-assistant';

        var bubble = document.createElement('div');
        bubble.className = 'ai-bubble ai-bubble-error';
        bubble.innerHTML = '<span>⚠️ ' + escapeHtml(errText) + '</span>';

        var retryBtn = document.createElement('button');
        retryBtn.className = 'ai-retry-btn';
        retryBtn.textContent = retryLabel;
        retryBtn.onclick = function () {
            wrap.remove();
            if (lastFailedMsg) handleSend(lastFailedMsg);
        };
        bubble.appendChild(retryBtn);
        wrap.appendChild(bubble);
        msgList.appendChild(wrap);
        scrollBottom();
        requestAnimationFrame(function () { wrap.classList.add('ai-msg-visible'); });
    }

    // ── Message bubble ────────────────────────────────────────────────────
    function appendMessage(role, content, animate) {
        if (!msgList) return;
        var wrap = document.createElement('div');
        wrap.className = 'ai-msg-wrap ai-msg-' + role;

        var bubble = document.createElement('div');
        bubble.className = 'ai-bubble';

        if (role === 'assistant') {
            bubble.innerHTML = safeRender(content);
        } else {
            bubble.textContent = content;
        }

        wrap.appendChild(bubble);
        msgList.appendChild(wrap);
        scrollBottom();

        if (animate !== false) {
            requestAnimationFrame(function () { wrap.classList.add('ai-msg-visible'); });
        } else {
            wrap.classList.add('ai-msg-visible');
        }
    }

    // ── Safe Markdown-aware HTML renderer ────────────────────────────────
    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function safeRender(text) {
        // 1. Escape HTML entities first
        var s = escapeHtml(String(text));

        // 2. Bold: **text** or __text__
        s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        s = s.replace(/__(.+?)__/g, '<strong>$1</strong>');

        // 3. Italic: *text* or _text_ (single — avoid false positives)
        s = s.replace(/\*([^\s*][^*]*?)\*/g, '<em>$1</em>');

        // 4. Strikethrough: ~~text~~
        s = s.replace(/~~(.+?)~~/g, '<del>$1</del>');

        // 5. Inline code: `code`
        s = s.replace(/`([^`]+)`/g, '<code class="ai-code">$1</code>');

        // 6. Bullet list items: lines starting with • · - * (after escape)
        //    We convert them to <ul><li> blocks
        s = s.replace(/((?:^|\n)[•·\-\*] .+)+/g, function (block) {
            var items = block.trim().split(/\n/).map(function (line) {
                var content = line.replace(/^[•·\-\*]\s+/, '').trim();
                return content ? '<li>' + content + '</li>' : '';
            }).filter(Boolean).join('');
            return '<ul class="ai-list">' + items + '</ul>';
        });

        // 7. Numbered lists: lines starting with "1. " "2. " etc.
        s = s.replace(/((?:^|\n)\d+\.\s+.+)+/g, function (block) {
            var items = block.trim().split(/\n/).map(function (line) {
                var content = line.replace(/^\d+\.\s+/, '').trim();
                return content ? '<li>' + content + '</li>' : '';
            }).filter(Boolean).join('');
            return '<ol class="ai-list">' + items + '</ol>';
        });

        // 8. Convert newlines to <br> (but not inside list blocks)
        s = s.replace(/\n/g, '<br>');

        // 9. Convert https:// URLs to safe links
        s = s.replace(
            /(https?:\/\/[^\s<&"']+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // 10. WhatsApp shorthand: wa.me/number
        s = s.replace(
            /wa\.me\/(\d+)/g,
            '<a href="https://wa.me/$1" target="_blank" rel="noopener noreferrer" class="ai-wa-link">📱 WhatsApp</a>'
        );

        // 11. Internal links: /products/123 or /orders /cart etc.
        s = s.replace(
            /\/(products(?:\/\d+)?|orders|categories|cart|profile|login|register|about|contact|search|wishlist|branches)((?:[\/?][a-zA-Z0-9_=&%-]+)*)/g,
            '<a href="/$1$2" class="ai-internal-link">/$1$2 →</a>'
        );

        return s;
    }

    // ── Typing indicator ──────────────────────────────────────────────────
    function showTyping() {
        isTyping = true;
        if (!msgList) return;
        var div = document.createElement('div');
        div.className = 'ai-msg-wrap ai-msg-assistant';
        div.id = 'ai-typing-indicator';
        div.innerHTML = '<div class="ai-bubble ai-typing"><span></span><span></span><span></span></div>';
        msgList.appendChild(div);
        scrollBottom();
        requestAnimationFrame(function () { div.classList.add('ai-msg-visible'); });
    }

    function hideTyping() {
        isTyping = false;
        sendBtn.disabled = false;
        var el = document.getElementById('ai-typing-indicator');
        if (el) el.remove();
    }

    // ── Helpers ───────────────────────────────────────────────────────────
    function scrollBottom() {
        if (msgList) msgList.scrollTop = msgList.scrollHeight;
    }

    // ── Boot ──────────────────────────────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
