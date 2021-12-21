import requests
import json
import re

url = "https://github.com/imsorx/blog/raw/main/index.json"
blog_url = "https://sorx.space/blog/"

res = requests.get(url)
posts = json.loads(res.text)

try:
    reader = open('README.md', encoding='utf-8')
    readme = reader.read()
    reader.close()

    updates = '<!-- start -->\n'

    for post in posts[-5:]:
        updates += '- [{title}]({link})\n'.format(
            title=post['title'], link=blog_url + post['file']
        )

    updates += '<!-- end -->'

    pattern = re.compile(r'<!-- start -->[\s\S]*<!-- end -->')
    readme = re.sub(pattern, updates, readme)

    writer = open('README.md','w', encoding='utf-8')
    writer.write(readme)
    writer.close()

except Exception as e:
    print(e.__class__)