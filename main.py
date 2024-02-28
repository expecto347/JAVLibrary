import requests
import re
from tqdm import tqdm
from bs4 import BeautifulSoup

JAV_url = 'https://www.javlibrary.com/cn/'


def fetch_page_content(url):
    """
    Fetch the content of the page specified by the given URL.

    Parameters:
    - url: The URL of the page to fetch.

    Returns:
    The HTML content of the page.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 '
                                                            'Safari/537.36 Edg/122.0.0.0'})
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error fetching page: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


def parse_content(html_content):
    """
    Parse the given HTML content using BeautifulSoup.

    Parameters:
    - html_content: The HTML content to parse.

    Returns:
    A BeautifulSoup object.
    """
    return BeautifulSoup(html_content, 'html.parser')


def get_genre_links():
    genre_html_content = fetch_page_content(JAV_url + '/genres.php')
    genre_soup = parse_content(genre_html_content)

    # Initialize an empty dictionary to store the genre categories.
    categories_dict = {}

    # Find all the genre items on the page.
    genre_items = genre_soup.find_all('div', class_='genreitem')

    # Loop through the genre items and extract the category name and URL.
    for item in genre_items:
        a_tag = item.find('a')
        if a_tag:
            category_name = a_tag.text
            category_url = a_tag['href']
            categories_dict[category_name] = category_url

    # Print the category names and URLs.
    # for category, url in categories_dict.items():
    #     print(f'{category}: {url}')
    return categories_dict


def get_last_page(url):
    html_content = fetch_page_content(url)
    soup = parse_content(html_content)

    # Find the last page number.
    page_links = soup.find_all('a', class_='page last')

    if page_links:
        last_page_link = page_links[0]
        last_page_url = last_page_link['href']
        last_page_number = int(last_page_url.split('=')[-1])
        return last_page_number

def get_movie_link(url):
    html_content = fetch_page_content(url)
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the movie link
    videos = []
    video_divs = soup.find_all('div', class_='video')  # 跳过标题行

    # Get the title and URL of each video
    for video_div in video_divs:
        a_tag = video_div.find('a')
        if a_tag:
            title = a_tag['title']
            url = a_tag['href']
            videos.append((title, url))

    # Results
    return videos

def get_movie_info(url):
    html_content = fetch_page_content(url)
    soup = parse_content(html_content)

    movie_info = {}
    # Get the rate
    rate_text = soup.find('span', class_='score')
    if rate_text:
        match = re.search(r'\((.*?)\)', rate_text.text)
        if match:
            movie_info['score'] = float(match.group(1))
        else:
            movie_info['score'] = 0
    else:
        movie_info['score'] = 0

    # # Get the number of votes
    # fav_edit_div = soup.find('div', id='video_favorite_edit')
    # for a_tag in fav_edit_div.find_all('a'):
    #     text = a_tag.text.strip()
    #     if '个使用者想要这影片' in text:
    #         movie_info["我想要"] = int(text.split(' ')[0])
    #     elif '个使用者看过这影片' in text:
    #         movie_info["看过了"] = int(text.split(' ')[0])
    #     elif '个使用者拥有这影片' in text:
    #         movie_info["已拥有"] = int(text.split(' ')[0])

    movie_info['url'] = url

    return movie_info

def main():
    category = 'SM'
    category_dict = get_genre_links()

    category_url = JAV_url + category_dict[category] + '?&mode=&g=ae&page='
    last_page = get_last_page(category_url + '1')
    # last_page = 1
    videos = []
    for i in tqdm(range(1, last_page + 1)):
        tmp = get_movie_link(category_url + str(i))
        videos.extend(tmp)

    videos_info = []
    for video in tqdm(videos):
        movie_info = get_movie_info(JAV_url + video[1][2:])
        videos_info.append(movie_info)

    # Sort the videos by score
    videos_info.sort(key=lambda x: x['score'], reverse=True)

    # print the result
    for video in videos_info:
        print(video)

if __name__ == '__main__':
    main()
