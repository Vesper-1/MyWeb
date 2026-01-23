// ========================================
// Language Switching
// ========================================
function switchLanguage(newLang) {
    const currentPath = window.location.pathname;
    const currentLang = currentPath.split('/')[1];

    // Check if current path already has a language prefix
    if (['zh', 'en'].includes(currentLang)) {
        // Replace current language with new language
        const newPath = currentPath.replace(`/${currentLang}/`, `/${newLang}/`);
        window.location.href = newPath;
    } else {
        // No language prefix, add one
        window.location.href = `/${newLang}/`;
    }
}

// ========================================
// Card Tilt Effect (for home page cards)
// ========================================
function initCardTilt() {
    const cards = document.querySelectorAll('[data-tilt]');

    cards.forEach(card => {
        card.addEventListener('mousemove', handleTilt);
        card.addEventListener('mouseleave', resetTilt);
    });

    function handleTilt(e) {
        const card = e.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    }

    function resetTilt(e) {
        const card = e.currentTarget;
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
    }
}

// ========================================
// Smooth Scroll
// ========================================
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ========================================
// Intersection Observer for Animations
// ========================================
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Observe elements that need animation
    document.querySelectorAll('.post-card, .feature-card, .tool-card, .project-card').forEach(el => {
        observer.observe(el);
    });
}

// ========================================
// Active Nav Link Highlight
// ========================================
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
}

// ========================================
// Keyboard Navigation
// ========================================
function initKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // Alt + H: Home
        if (e.altKey && e.key === 'h') {
            const lang = window.location.pathname.split('/')[1] || 'zh';
            window.location.href = `/${lang}/`;
        }

        // Alt + B: Blog
        if (e.altKey && e.key === 'b') {
            const lang = window.location.pathname.split('/')[1] || 'zh';
            window.location.href = `/${lang}/blog/`;
        }

        // Alt + T: Toolbox
        if (e.altKey && e.key === 't') {
            const lang = window.location.pathname.split('/')[1] || 'zh';
            window.location.href = `/${lang}/toolbox/`;
        }
    });
}

// ========================================
// Performance: Lazy Load Images
// ========================================
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// ========================================
// Check for Reduced Motion Preference
// ========================================
function respectReducedMotion() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
        // Disable animations
        document.documentElement.style.setProperty('--transition', 'none');
        console.log('Reduced motion mode enabled');
    }
}

// ========================================
// Copy Code Block (if any)
// ========================================
function initCodeCopy() {
    const codeBlocks = document.querySelectorAll('pre code');

    codeBlocks.forEach(block => {
        const pre = block.parentElement;
        const button = document.createElement('button');
        button.className = 'copy-code-btn';
        button.textContent = 'Copy';
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            padding: 4px 8px;
            background: var(--neon-cyan);
            color: var(--bg-primary);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        pre.style.position = 'relative';
        pre.appendChild(button);

        pre.addEventListener('mouseenter', () => {
            button.style.opacity = '1';
        });

        pre.addEventListener('mouseleave', () => {
            button.style.opacity = '0';
        });

        button.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(block.textContent);
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
}

// ========================================
// Initialize All Features
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    respectReducedMotion();
    initCardTilt();
    initSmoothScroll();
    initScrollAnimations();
    highlightActiveNavLink();
    initKeyboardNavigation();
    initLazyLoading();
    initCodeCopy();

    console.log('🚀 Site initialized successfully!');
});

// ========================================
// Service Worker Registration (optional)
// ========================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js')
        //     .then(reg => console.log('Service Worker registered'))
        //     .catch(err => console.log('Service Worker registration failed'));
    });
}
