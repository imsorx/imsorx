import requests
import json
import re
import os


def main():
    reader = open('README.md', encoding='utf-8')
    content = reader.read()
    reader.close()

    readme = build_updates(content)

    writer = open('README.md', 'w', encoding='utf-8')
    writer.write(readme)
    writer.close()


def build_updates(content: str) -> str:
    # Load varaibles
    url = os.getenv("BLOG_INDEX_URL",
                    "https://github.com/imsorx/blog/raw/main/index.json")
    blog_url = os.getenv("BLOG_BASE_URL", "https://sorx.space/blog/")

    # Load posts
    res = requests.get(url)
    posts: list = json.loads(res.text)
    posts.reverse()

    # Build post updates
    updates = '<!-- posts-start -->\n'

    for post in posts[-5:]:
        updates += '- [{title}]({link})\n'.format(
            title=post['title'], link=blog_url + post['file']
        )

    updates += '<!-- posts-end -->'

    # Replace posts
    pattern = re.compile(r'<!-- posts-start -->[\s\S]*<!-- posts-end -->')
    readme = re.sub(pattern, updates, content)

    return readme


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e.__class__)
