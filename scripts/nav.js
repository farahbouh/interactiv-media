document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        var nav = document.querySelector('nav');
        var btn = document.querySelector('.menu-toggle');
        if (nav && nav.classList.contains('open')) {
            nav.classList.remove('open');
            btn.classList.remove('open');
            btn.setAttribute('aria-expanded', 'false');
        }
    }
});