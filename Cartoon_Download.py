import requests, bs4, os

base_url = 'https://xkcd.com'
url = base_url
os.makedirs('xkcd', exist_ok=True)


def Download_img(url_to_download):
    image_file = open(os.path.join('xkcd', os.path.basename(url_to_download)), 'wb')
    img_res = requests.get(url_to_download)

    try:
        img_res.raise_for_status()
        for chunk in img_res.iter_content(100000):
            image_file.write(chunk)
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    image_file.close()


while not url.endswith('#'):

    res = requests.get(url)

    try:
        res.raise_for_status()
        website = bs4.BeautifulSoup(res.text, 'lxml')

        image = website.select('#comic > img')
        if len(image) > 0:
            img_url = base_url + image[0].get("src")
            Download_img(img_url)
        else:
            print("No image found on " + url)

        prev_button = website.select('#middleContainer > ul:nth-child(2) > li:nth-child(2) > a')
        url = 'https://xkcd.com' + prev_button[0].get("href")
        print(url)
    except Exception as exc:
        print('There was a problem: %s' % (exc))
