import os
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import (Flask, render_template, abort, request, url_for,
                   session, redirect, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
import frontmatter
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from functools import lru_cache, wraps

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Markdown parser
md = MarkdownIt('commonmark', {'breaks': True, 'html': True})
md.enable('table')

CONTENT_DIR = Path(__file__).parent / 'content' / 'posts'
SUPPORTED_LANGS = ['zh', 'en']
CATEGORIES = ['finance', 'tech', 'misc']

# Translations
TRANSLATIONS = {
    'zh': {
        'home': '首页',
        'blog': '博客',
        'toolbox': '工具库',
        'links': '链接',
        'all': '全部',
        'finance': '金融',
        'tech': '技术',
        'misc': '杂谈',
        'read_more': '阅读全文',
        'external_links': '外部链接',
        'created': '发布于',
        'updated': '更新于',
        'not_found': '页面未找到',
        'back_home': '返回首页',
        'category': '分类',
        'dev': '开发工具',
        'productivity': '效率工具',
        'ai': 'AI工具',
        'my_projects': '我的作品',
        'interactive_tools': '互动工具',
        'future': '未来计划',
        'coming_soon': '敬请期待',
        'recommended_tools': '推荐工具',
        'english_unavailable': '英文版本暂未提供',
        'chinese_unavailable': '中文版本暂未提供',
        'new_tool': '新工具上线',
        'try_it': '立即体验 →',
    },
    'en': {
        'home': 'Home',
        'blog': 'Blog',
        'toolbox': 'Toolbox',
        'links': 'Links',
        'all': 'All',
        'finance': 'Finance',
        'tech': 'Tech',
        'misc': 'Misc',
        'read_more': 'Read More',
        'external_links': 'External Links',
        'created': 'Published',
        'updated': 'Updated',
        'not_found': 'Page Not Found',
        'back_home': 'Back to Home',
        'category': 'Category',
        'dev': 'Development',
        'productivity': 'Productivity',
        'ai': 'AI Tools',
        'my_projects': 'My Projects',
        'interactive_tools': 'Interactive Tools',
        'future': 'Future Plans',
        'coming_soon': 'Coming Soon',
        'recommended_tools': 'Recommended Tools',
        'english_unavailable': 'English version not available',
        'chinese_unavailable': 'Chinese version not available',
        'new_tool': 'New Tool',
        'try_it': 'Try It →',
    }
}


def get_posts(lang='zh'):
    """Load and parse all posts for a given language."""
    posts = []

    if not CONTENT_DIR.exists():
        return posts

    # Get all markdown files
    md_files = list(CONTENT_DIR.glob(f'*.{lang}.md'))

    for md_file in md_files:
        try:
            post = frontmatter.load(md_file)
            slug = md_file.stem.replace(f'.{lang}', '')

            post_data = {
                'slug': slug,
                'title': post.get('title', 'Untitled'),
                'summary': post.get('summary', ''),
                'category': post.get('category', 'misc'),
                'created': post.get('created', ''),
                'updated': post.get('updated', ''),
                'external_links': post.get('external_links', []),
                'cover_image': post.get('cover_image', ''),
                'content': post.content,
                'lang': lang
            }
            posts.append(post_data)
        except Exception as e:
            print(f"Error loading {md_file}: {e}")
            continue

    # Sort by updated (if exists) then created, newest first
    def sort_key(p):
        date_str = p['updated'] if p['updated'] else p['created']
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.min

    posts.sort(key=sort_key, reverse=True)
    return posts


def get_post(slug, lang='zh'):
    """Get a single post by slug and language."""
    file_path = CONTENT_DIR / f'{slug}.{lang}.md'

    if not file_path.exists():
        return None

    try:
        post = frontmatter.load(file_path)
        post_data = {
            'slug': slug,
            'title': post.get('title', 'Untitled'),
            'summary': post.get('summary', ''),
            'category': post.get('category', 'misc'),
            'created': post.get('created', ''),
            'updated': post.get('updated', ''),
            'external_links': post.get('external_links', []),
            'cover_image': post.get('cover_image', ''),
            'content': md.render(post.content),
            'lang': lang
        }
        return post_data
    except Exception as e:
        print(f"Error loading post {slug}.{lang}: {e}")
        return None


@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    lang = request.view_args.get('lang', 'zh') if request.view_args else 'zh'
    return {
        'lang': lang,
        't': TRANSLATIONS.get(lang, TRANSLATIONS['zh']),
        'supported_langs': SUPPORTED_LANGS,
        'current_year': datetime.now().year
    }


# ── Database ──────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / 'instance' / 'dca.db'


def get_db():
    """Return a sqlite3 connection (row_factory = dict)."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS dca_entries (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            date          TEXT    NOT NULL,
            invest_amount REAL    NOT NULL,
            btc_price     REAL    NOT NULL,
            btc_amount    REAL    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.close()


init_db()


def login_required(f):
    """Redirect to auth page if not logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            lang = kwargs.get('lang', 'zh')
            return redirect(f'/{lang}/auth/?next={request.path}')
        return f(*args, **kwargs)
    return decorated


# ── Auth Routes ───────────────────────────────────────────────
@app.route('/<lang>/auth/')
def auth_page(lang):
    """Login / Register page."""
    if lang not in SUPPORTED_LANGS:
        abort(404)
    if 'user_id' in session:
        return redirect(f'/{lang}/toolbox/btc-dca/')
    return render_template('auth.html', next_url=request.args.get('next', f'/{lang}/toolbox/btc-dca/'))


@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """Register a new user."""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify(ok=False, msg='用户名和密码不能为空 / Username and password required'), 400

    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        conn.commit()
        user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        session['user_id'] = user['id']
        session['username'] = username
        return jsonify(ok=True)
    except sqlite3.IntegrityError:
        return jsonify(ok=False, msg='用户名已存在 / Username already taken'), 409
    finally:
        conn.close()


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Log in an existing user."""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify(ok=False, msg='用户名或密码错误 / Invalid username or password'), 401

    session['user_id'] = user['id']
    session['username'] = username
    return jsonify(ok=True)


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Log out."""
    session.clear()
    return jsonify(ok=True)


# ── DCA Entry API ─────────────────────────────────────────────
@app.route('/api/dca/entries', methods=['GET'])
def api_get_entries():
    """Return all DCA entries for the logged-in user."""
    if 'user_id' not in session:
        return jsonify(ok=False, msg='Unauthorized'), 401
    conn = get_db()
    rows = conn.execute(
        'SELECT id, date, invest_amount, btc_price, btc_amount '
        'FROM dca_entries WHERE user_id = ? ORDER BY date DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return jsonify(ok=True, entries=[dict(r) for r in rows])


@app.route('/api/dca/entries', methods=['POST'])
def api_add_entry():
    """Add a new DCA entry."""
    if 'user_id' not in session:
        return jsonify(ok=False, msg='Unauthorized'), 401
    data = request.get_json(silent=True) or {}
    date = data.get('date')
    invest = data.get('invest_amount')
    price  = data.get('btc_price')

    if not date or not invest or not price:
        return jsonify(ok=False, msg='Missing fields'), 400
    invest = float(invest)
    price  = float(price)
    if invest <= 0 or price <= 0:
        return jsonify(ok=False, msg='Values must be > 0'), 400

    btc_amount = invest / price
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO dca_entries (user_id, date, invest_amount, btc_price, btc_amount) '
        'VALUES (?, ?, ?, ?, ?)',
        (session['user_id'], date, invest, price, btc_amount)
    )
    conn.commit()
    entry_id = cur.lastrowid
    conn.close()
    return jsonify(ok=True, entry=dict(id=entry_id, date=date,
                   invest_amount=invest, btc_price=price, btc_amount=btc_amount))


@app.route('/api/dca/entries/<int:entry_id>', methods=['DELETE'])
def api_delete_entry(entry_id):
    """Delete a DCA entry (only if owned by current user)."""
    if 'user_id' not in session:
        return jsonify(ok=False, msg='Unauthorized'), 401
    conn = get_db()
    conn.execute(
        'DELETE FROM dca_entries WHERE id = ? AND user_id = ?',
        (entry_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    return jsonify(ok=True)


# ── Existing Routes ───────────────────────────────────────────
@app.route('/')
def index():
    """Redirect root to Chinese home."""
    return render_template('home.html', lang='zh', t=TRANSLATIONS['zh'])


@app.route('/<lang>/')
def home(lang):
    """Home page."""
    if lang not in SUPPORTED_LANGS:
        abort(404)
    return render_template('home.html')


@app.route('/<lang>/blog/')
def blog(lang):
    """Blog listing page."""
    if lang not in SUPPORTED_LANGS:
        abort(404)

    posts = get_posts(lang)
    return render_template('blog.html', posts=posts)


@app.route('/<lang>/blog/<slug>/')
def post(lang, slug):
    """Individual blog post page."""
    if lang not in SUPPORTED_LANGS:
        abort(404)

    post_data = get_post(slug, lang)

    # Fallback to other language if not found
    fallback_lang = None
    if not post_data:
        other_lang = 'en' if lang == 'zh' else 'zh'
        post_data = get_post(slug, other_lang)
        if post_data:
            fallback_lang = other_lang

    if not post_data:
        abort(404)

    return render_template('post.html', post=post_data, fallback_lang=fallback_lang)


@app.route('/<lang>/links/')
def links(lang):
    """Social links page."""
    if lang not in SUPPORTED_LANGS:
        abort(404)
    return render_template('links.html')


@app.route('/<lang>/toolbox/')
def toolbox(lang):
    """Toolbox page."""
    if lang not in SUPPORTED_LANGS:
        abort(404)

    # Tool recommendations organized by category
    tools = {
        'dev': [
            {'name': 'VS Code', 'url': 'https://code.visualstudio.com/', 'desc_zh': '强大的代码编辑器', 'desc_en': 'Powerful code editor'},
            {'name': 'GitHub', 'url': 'https://github.com', 'desc_zh': '代码托管平台', 'desc_en': 'Code hosting platform'},
            {'name': 'Docker', 'url': 'https://www.docker.com/', 'desc_zh': '容器化平台', 'desc_en': 'Containerization platform'},
        ],
        'productivity': [
            {'name': 'Notion', 'url': 'https://notion.so', 'desc_zh': '全能笔记工具', 'desc_en': 'All-in-one workspace'},
            {'name': 'Obsidian', 'url': 'https://obsidian.md', 'desc_zh': '知识管理工具', 'desc_en': 'Knowledge base tool'},
        ],
        'finance': [
            {'name': 'TradingView', 'url': 'https://tradingview.com', 'desc_zh': '金融图表分析', 'desc_en': 'Financial charts'},
            {'name': 'Yahoo Finance', 'url': 'https://finance.yahoo.com', 'desc_zh': '金融数据源', 'desc_en': 'Financial data'},
        ],
        'ai': [
            {'name': 'ChatGPT', 'url': 'https://chat.openai.com', 'desc_zh': 'AI对话助手', 'desc_en': 'AI chat assistant'},
            {'name': 'Claude', 'url': 'https://claude.ai', 'desc_zh': 'AI编程助手', 'desc_en': 'AI coding assistant'},
        ]
    }

    # My projects
    projects = [
        {
            'name': 'GitHub Profile',
            'url': 'https://github.com/yourusername',
            'desc_zh': '我的开源项目',
            'desc_en': 'My open source projects'
        },
        {
            'name': 'Demo App',
            'url': 'https://demo.example.com',
            'desc_zh': '演示应用',
            'desc_en': 'Demo application'
        },
    ]

    return render_template('toolbox.html', tools=tools, projects=projects)


@app.route('/<lang>/toolbox/btc-dca/')
@login_required
def btc_dca(lang):
    """BTC DCA Tracker tool page (login required)."""
    if lang not in SUPPORTED_LANGS:
        abort(404)
    return render_template('btc_dca.html', username=session.get('username', ''))


@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap."""
    pages = []
    base_url = request.url_root.rstrip('/')

    # Static pages
    for lang in SUPPORTED_LANGS:
        pages.append(f'{base_url}/{lang}/')
        pages.append(f'{base_url}/{lang}/blog/')
        pages.append(f'{base_url}/{lang}/toolbox/')
        pages.append(f'{base_url}/{lang}/toolbox/btc-dca/')
        pages.append(f'{base_url}/{lang}/links/')

    # Blog posts
    for lang in SUPPORTED_LANGS:
        posts = get_posts(lang)
        for post in posts:
            pages.append(f'{base_url}/{lang}/blog/{post["slug"]}/')

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_xml += f'  <url>\n    <loc>{page}</loc>\n  </url>\n'

    sitemap_xml += '</urlset>'

    return sitemap_xml, 200, {'Content-Type': 'application/xml'}


@app.route('/robots.txt')
def robots():
    """Serve robots.txt."""
    return app.send_static_file('robots.txt')


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    lang = request.view_args.get('lang', 'zh') if request.view_args else 'zh'
    return render_template('404.html', lang=lang, t=TRANSLATIONS.get(lang, TRANSLATIONS['zh'])), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
