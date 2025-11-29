/**
 * Email Protection & Deobfuscation
 *
 * Reveals email addresses only to JavaScript-enabled browsers (humans).
 * Bots that don't execute JS will only see the honeypot emails.
 */
(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {

        // Find all protected email spans
        const emailSpans = document.querySelectorAll('.email-protect');

        emailSpans.forEach(function(span) {
            const user = span.dataset.user;
            const domain = span.dataset.domain;

            if (user && domain) {
                const email = user + '@' + domain;

                // Create the clickable email element
                const emailLink = document.createElement('a');
                emailLink.href = 'mailto:' + email;
                emailLink.textContent = email;
                emailLink.className = 'email-protect';
                emailLink.title = 'Click to email, or right-click to copy';

                // Click handler: open mailto OR copy to clipboard
                emailLink.addEventListener('click', function(e) {
                    // Let mailto work normally, but also offer copy
                });

                // Add copy on double-click
                emailLink.addEventListener('dblclick', function(e) {
                    e.preventDefault();
                    copyToClipboard(email, emailLink);
                });

                // Context menu hint
                emailLink.addEventListener('contextmenu', function(e) {
                    // Browser's native "Copy email address" works
                });

                // Replace the span with the link
                span.parentNode.replaceChild(emailLink, span);
            }
        });
    });

    /**
     * Copy text to clipboard with visual feedback
     */
    function copyToClipboard(text, element) {
        navigator.clipboard.writeText(text).then(function() {
            // Visual feedback
            const originalText = element.textContent;
            element.textContent = 'Copied!';
            element.classList.add('copied');

            setTimeout(function() {
                element.textContent = originalText;
                element.classList.remove('copied');
            }, 1500);
        }).catch(function(err) {
            console.error('Failed to copy:', err);
        });
    }

})();
