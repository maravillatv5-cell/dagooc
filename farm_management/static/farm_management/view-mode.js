(function () {
    var storageKey = 'dagooc-view-mode';

    function updateScrollState() {
        var mobileMode = document.body.dataset.viewMode === 'mobile';
        document.body.dataset.pageScrolled = String(mobileMode && window.scrollY > 4);
    }

    function applyViewMode(mode) {
        var selectedMode = mode === 'mobile' ? 'mobile' : 'desktop';
        document.body.dataset.viewMode = selectedMode;
        updateScrollState();
        document.querySelectorAll('[data-view-mode-choice]').forEach(function (button) {
            button.setAttribute('aria-pressed', String(button.dataset.viewModeChoice === selectedMode));
        });
    }

    var savedMode = window.localStorage.getItem(storageKey) || 'desktop';
    applyViewMode(savedMode);
    window.addEventListener('scroll', updateScrollState, { passive: true });
    window.addEventListener('resize', updateScrollState);

    document.addEventListener('click', function (event) {
        var button = event.target.closest('[data-view-mode-choice]');
        if (!button) return;

        var selectedMode = button.dataset.viewModeChoice;
        window.localStorage.setItem(storageKey, selectedMode);
        applyViewMode(selectedMode);
    });
})();
