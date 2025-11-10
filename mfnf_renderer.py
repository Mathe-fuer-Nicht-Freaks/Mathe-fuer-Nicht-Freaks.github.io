import sys

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import markdown

print("This is the MfNF renderer\n")

if len(sys.argv) != 4:
    print("Usage {} job-name plastex-dir output-dir".format(sys.argv[0]))
    sys.exit(1)

job_name = sys.argv[1]
plastex_dir = sys.argv[2]
output_dir = sys.argv[3]

env = Environment(loader = FileSystemLoader('site-templates'))

def get_article_name(identifier):
    return '{}.html'.format(identifier.replace(' ', '-'))

def get_toc():
    # read xml version of tex file
    with open('{}/{}.xml'.format(plastex_dir,job_name), 'r') as f:
        bs = BeautifulSoup(f.read(), "xml")

        # get all books
        books = bs.find_all("part")

        toc = []
        for book in books:
            book_toc = []
            for chapter in book.find_all("chapter"):
                book_toc.append({
                    "identifier": chapter["id"],
                    "title": chapter.find("plastex:arg", {'name':'title'}).text,
                    "url": get_article_name(chapter["id"])
                })
            toc.append({
                "identifier": book["id"],
                "title": book.find("plastex:arg", {'name':'title'}).text,
                "toc": book_toc,
                "url": get_article_name(book["id"])
            })

        return toc

toc = get_toc()

site_config = {
    'header': [{"url": 'index.html', "title": "Home"}],
    'footer': [{"url": 'impressum.html', "title": "Impressum"}, {"url": 'datenschutz.html', "title": "Datenschutz"}],
}

static_sites = [
    {"name": "impressum", "meta": {"title": "Impressum"}},
    {"name": "datenschutz", "meta": {"title": "Datenschutz"}},
]

site_info = []

def populate_header():
    for book in toc:
        site_config['header'].append({"url":book['url'], 'title':book['title']})

def render_template(template_name, **params):
    template = env.get_template(template_name)
    return template.render(**params,
                           **site_config)

def render_book(book):
    return render_template('book.jinja2', book=book)
    
def render_home():
    return render_template('home.jinja2', books = toc)

def extract_article_content(article):
    with open('{}/{}'.format(plastex_dir, article), 'r') as f:
        bs = BeautifulSoup(f.read(), "html.parser")
        return str(bs.find("article"))

def render_article(article):
    return render_template('article.jinja2',
                           body = extract_article_content(get_article_name(article['identifier'])),
                           article = article,
                           title = article["title"])

def render_static_site(name, meta):
    """Render a markdown file as a static site"""
    with open('{}.md'.format(name), 'r') as f:
        content = markdown.markdown(f.read())
        return render_template("base.jinja2", body=content, **meta)

def output_file(name, content):
    with open('{}/{}'.format(output_dir, name), 'w') as f:
        print("Writing {}".format(name))
        print(content, file = f)

def copy_articles():
    for book in toc:
        for article in book['toc']:
            output_file(get_article_name(article['identifier']), render_article(article))

def render_site():
    populate_header()
    copy_articles()
    for site in static_sites:
        output_file('{}.html'.format(site["name"]), render_static_site(site['name'], site['meta']))
    for book in toc:
        output_file(book["url"], render_book(book))
    output_file('index.html', render_home())

print(toc)

render_site()
