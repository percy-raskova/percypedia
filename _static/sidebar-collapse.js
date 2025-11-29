/* Collapsible sidebar categories for Percypedia */

document.addEventListener('DOMContentLoaded', function() {
    // ========================================
    // ATTENTION COMRADE - Global Warning Injection
    // ========================================
    // Inject surveillance warning on every page that doesn't already have one
    if (!document.querySelector('.admonition.comrade-warning')) {
        const mainContent = document.querySelector('.content') ||
                           document.querySelector('[role="main"]') ||
                           document.querySelector('main');

        if (mainContent) {
            const warning = document.createElement('div');
            warning.className = 'admonition comrade-warning';
            warning.innerHTML = `
                <p class="admonition-title">ATTENTION COMRADE</p>
                <p><strong>The FBI is probably monitoring this website.</strong> The NSA definitely is. COINTELPRO never ended, it just got a bigger budget and better software.</p>
                <p>If you're a leftist reading this: <strong>use a VPN, use Tor, or at minimum accept that you're now on a list somewhere.</strong> If you're a fed reading this: hi! Hope the per diem is worth it. Tell your supervisor I said the Labor Aristocracy article is required reading.</p>
                <p><em>This message brought to you by the "assume you're always being watched" school of operational security.</em></p>
            `;
            mainContent.insertBefore(warning, mainContent.firstChild);
        }
    }
    // Get all category captions in the sidebar
    const captions = document.querySelectorAll('.sidebar-tree .caption');

    // Load saved state from localStorage
    const savedState = JSON.parse(localStorage.getItem('sidebarCollapsed') || '{}');

    captions.forEach(function(caption) {
        const categoryName = caption.textContent.trim();

        // Restore saved collapsed state
        if (savedState[categoryName]) {
            caption.classList.add('collapsed');
        }

        // Add click handler
        caption.addEventListener('click', function(e) {
            e.preventDefault();
            this.classList.toggle('collapsed');

            // Save state to localStorage
            const currentState = JSON.parse(localStorage.getItem('sidebarCollapsed') || '{}');
            const name = this.textContent.trim();

            if (this.classList.contains('collapsed')) {
                currentState[name] = true;
            } else {
                delete currentState[name];
            }

            localStorage.setItem('sidebarCollapsed', JSON.stringify(currentState));
        });
    });
});
