/* Collapsible sidebar categories for Percypedia */

document.addEventListener('DOMContentLoaded', function() {
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
