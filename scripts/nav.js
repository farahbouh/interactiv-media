document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('.menu-toggle');
    var nav = document.querySelector('nav');
    if (btn && nav) {
        btn.addEventListener('click', function () {
            this.classList.toggle('open');
            this.setAttribute('aria-expanded', this.classList.contains('open'));
            nav.classList.toggle('open');
        });
    }
});

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