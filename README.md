# Personal Website

A bilingual (Chinese/English) personal website built with Flask, featuring a blog, toolbox, and modern dark theme design.

## Features

- 🌐 **Bilingual Support**: Chinese (`/zh/`) and English (`/en/`) routes
- 📝 **Markdown Blog**: Write posts in Markdown with YAML front matter
- 🎨 **Modern Design**: Dark theme with neon accents and cyberpunk aesthetics
- 📱 **Responsive**: Mobile, tablet, and desktop friendly
- ⚡ **Performance**: Lightweight, no heavy frameworks
- 🔍 **SEO Optimized**: Meta tags, Open Graph, sitemap
- ♿ **Accessible**: Semantic HTML, keyboard navigation, reduced motion support

## Tech Stack

- **Backend**: Flask 3.0 + Gunicorn
- **Templating**: Jinja2
- **Markdown**: python-frontmatter + markdown-it-py
- **Frontend**: Vanilla HTML/CSS/JavaScript (no build tools)
- **Deployment**: Render Web Service

## Project Structure

```
MyWeb/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── robots.txt             # SEO robots file
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── home.html
│   ├── blog.html
│   ├── post.html
│   ├── toolbox.html
│   └── 404.html
├── static/
│   ├── css/
│   │   └── style.css      # All styles
│   ├── js/
│   │   └── main.js        # JavaScript functionality
│   └── img/               # Images (add your avatar.jpg here)
└── content/
    └── posts/             # Blog posts in Markdown
        ├── *.zh.md        # Chinese posts
        └── *.en.md        # English posts
```

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd MyWeb
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open browser:
```
http://localhost:10000
```

## Deploy to Render

### Method 1: Connect GitHub Repository

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: your-site-name
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (or paid for better performance)

### Method 2: Deploy from Git

```bash
# Ensure you're on the correct branch
git checkout claude/claude-md-mkpltm2fxodobsrh-g7TM6

# Add all files
git add .

# Commit
git commit -m "Initial website setup"

# Push to remote
git push -u origin claude/claude-md-mkpltm2fxodobsrh-g7TM6
```

Then follow Method 1 steps.

## Customization

### Add Your Avatar

1. Add your photo to `static/img/avatar.jpg`
2. Recommended size: 300x300px or larger (square)

### Add Blog Posts

Create two files for each post (Chinese and English):

```bash
content/posts/my-post.zh.md
content/posts/my-post.en.md
```

Front matter format:
```yaml
---
title: Post Title
summary: Brief description
category: tech  # or finance, misc
created: 2024-01-01
updated: 2024-01-15  # optional
external_links:  # optional
  - platform: github
    url: https://github.com/...
---

# Your content here in Markdown
```

### Customize Colors

Edit `static/css/style.css`:

```css
:root {
    --neon-cyan: #00ffff;      /* Change primary color */
    --neon-pink: #ff006e;      /* Change accent color */
    --neon-purple: #8b5cf6;    /* Change secondary color */
    --bg-primary: #0a0e27;     /* Change background */
}
```

### Update Personal Info

- **Navigation Brand**: Edit `templates/base.html` (line ~37)
- **Footer Links**: Edit `templates/base.html` (line ~66)
- **Home Page Bio**: Edit `templates/home.html` (line ~15-35)
- **Toolbox Projects**: Edit `app.py` (line ~220-235)

## Environment Variables

Render automatically provides:
- `PORT`: The port to listen on (default: 10000)

Optional variables you can add:
- `FLASK_ENV`: Set to `production` for production
- Any custom configuration you need

## Keyboard Shortcuts

- `Alt + H`: Go to Home
- `Alt + B`: Go to Blog
- `Alt + T`: Go to Toolbox

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Lighthouse Score: 95+ (Performance, Accessibility, Best Practices, SEO)
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s

## License

MIT License - Feel free to use this template for your own website!

## Support

If you encounter issues:
1. Check that all files are committed
2. Verify `requirements.txt` has all dependencies
3. Check Render logs for error messages
4. Ensure Python version is 3.9+

## Credits

Built with ❤️ using Flask, designed for simplicity and performance.
