import shutil
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent
from datetime import datetime, timezone

from jinja2 import Environment, FileSystemLoader
from markdown import markdown


def main():
    print("Generating cjkenyon.github.io!")

    output_dir = Path("./out")

    if output_dir.is_dir():
        shutil.rmtree(output_dir)

    output_dir.mkdir()

    static_dir = output_dir.joinpath("static")
    content_dir = Path("./content")
    pages_dir = content_dir.joinpath("pages")
    posts_dir = content_dir.joinpath("posts")
    templates_dir = content_dir.joinpath("templates")
    css_dir = content_dir.joinpath("css")

    env = Environment(loader=FileSystemLoader(templates_dir))
    page_template = env.get_template("page.html")
    post_template = env.get_template("post.html")
    index_template = env.get_template("index.html")

    # copy over css files
    shutil.copytree(css_dir, static_dir, dirs_exist_ok=True)

    # convert markdown pages into html
    for page in pages_dir.iterdir():
        if not page.is_file():
            continue

        with open(page, "r") as f:
            content = markdown(f.read())
            page_html = page_template.render(
                site_title="cjkenyon",
                site_desc="Programmer and Musician",
                content=content,
            )
            with open(output_dir.joinpath(page.stem + ".html"), "w") as f_out:
                f_out.write(page_html)

    posts = []
    for post in posts_dir.iterdir():
        if not post.is_file():
            continue

        parts = post.stem.split("-")
        month, day, year = parts[0], parts[1], parts[2]
        title_slug = parts[3:]
        date = datetime(int(year), int(month), int(day))
        date_str = date.strftime("%B %d, %Y")
        title = " ".join(word.capitalize() for word in title_slug)
        url = post.stem + ".html"

        with open(post, "r") as f:
            content = markdown(f.read())
            post_html = post_template.render(
                site_title="cjkenyon",
                site_desc="Programmer and Musician",
                content=content,
                title=title,
                date=date_str,
            )
            with open(output_dir.joinpath(url), "w") as f_out:
                f_out.write(post_html)

        posts.append(
            {
                "url": url,
                "title": title,
                "date_str": date_str,
                "date_obj": date,
                "content": content,
            }
        )

    # order posts by date
    posts.sort(key=lambda p: p["date_str"], reverse=True)

    index_html = index_template.render(
        site_title="cjkenyon", site_desc="Programmer and Musician", posts=posts
    )

    with open(output_dir.joinpath("index.html"), "w") as f:
        f.write(index_html)

    print("Building feed.xml.")

    ET = Element("feed", xmlns="http://www.w3.org/2005/Atom")
    SubElement(
        ET,
        "link",
        href="https://cjkenyon.github.io/feed.xml",
        rel="self",
        type="application/atom+xml",
    )
    SubElement(
        ET, "link", href="https://cjkenyon.github.io", rel="alternate", type="text/html"
    )
    SubElement(ET, "updated").text = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    SubElement(ET, "id").text = "https://cjkenyon.github.io/feed.xml"
    SubElement(ET, "title", type="html").text = "Cade Kenyon"

    author = SubElement(ET, "author")
    SubElement(author, "name").text = "Cade Kenyon"

    for post in posts:
        entry = SubElement(ET, "entry")
        SubElement(entry, "title", type="text").text = post["title"]
        SubElement(
            entry,
            "link",
            href=f"https://cjkenyon.github.io/{post['url']}",
            rel="alternate",
            type="text/html",
            title=post["title"],
        )
        SubElement(entry, "published").text = post["date_obj"].strftime(
            "%Y-%m-%dT00:00:00+00:00"
        )
        SubElement(entry, "updated").text = post["date_obj"].strftime(
            "%Y-%m-%dT00:00:00+00:00"
        )
        SubElement(entry, "id").text = f"https://cjkenyon.github.io/{post['url']}"

        entry_author = SubElement(entry, "author")
        SubElement(entry_author, "name").text = "Cade Kenyon"

        SubElement(entry, "content", type="html").text = post["content"]

    tree = ElementTree(ET)
    indent(tree, space="  ")
    tree.write(
        output_dir.joinpath("feed.xml"), encoding="unicode", xml_declaration=True
    )

    print("Done.")


if __name__ == "__main__":
    main()
