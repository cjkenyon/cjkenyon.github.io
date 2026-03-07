import shutil
from pathlib import Path
from datetime import datetime

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

        posts.append({"url": url, "title": title, "date": date_str})

    # order posts by date
    posts.sort(key=lambda p: p["date"], reverse=True)

    index_html = index_template.render(
        site_title="cjkenyon", site_desc="Programmer and Musician", posts=posts
    )

    with open(output_dir.joinpath("index.html"), "w") as f:
        f.write(index_html)

    print("Done.")


if __name__ == "__main__":
    main()
