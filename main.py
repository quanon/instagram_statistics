import os
import sys
import urllib
import requests
import csv

class PostList():
    def __init__(self, insta_id):
        self.insta_id = insta_id
        self.posts = []

    def to_list(self):
        if self.posts:
            return self.posts

        max_id = None

        while True:
            json = self.__get_json_response(max_id)

            for i in json['items']:
                self.posts.append(i)

            if json['more_available'] is not True:
                break

            max_id = json['items'][-1]['id']

        return self.posts

    def __get_json_response(self, max_id):
        url =  self.__build_url(max_id)
        response = requests.get(url)
        json = response.json()

        return json

    def __build_url(self, max_id):
        url = os.path.join('https://www.instagram.com', self.insta_id, 'media')

        if max_id:
            url += ('?max_id=' + max_id)

        return url

def extract_statistics(post_list):
    '''
    INTAKE: a list of posts
    RETURN: a dictionary of lists
    '''
    num_of_posts = len(post_list)

    stats_list = []
    caption_list = []

    for i in range(0, num_of_posts):
        stats_list.append([post_list[i]['code'], post_list[i]['likes']['count'], post_list[i]['comments']['count']])
        if post_list[i]['caption'] == None: # check if there is caption
            caption_list.append([post_list[i]['code'], ''])
        else:
            caption_list.append([post_list[i]['code'], post_list[i]['caption']['text'].replace("\n", " ")])
            # some captions have '\n' but we want them to be in one line

    account_info = {'stats_list': stats_list, 'caption_list': caption_list}

    return account_info

def download_photos(post_list):
    '''
    INTAKE: a list of posts
    RETURN: 0
    '''
    if (os.path.exists("/Users/USERNAME/Desktop/"+ insta_id) == False):
            os.mkdir("/Users/USERNAME/Desktop/"+ insta_id)

    for x in post_list:
        url = x["images"]["standard_resolution"]["url"].replace("s640x640", "s1080x1080")
        # will replace with high resolution version if there is one
        file_name = x["code"]
        urllib.urlretrieve(url, "/Users/USERNAME/Desktop/"+ insta_id + "/" + file_name + ".jpg")

    return 0

def write_to_csv(list_name,file_name,col_names):
    '''
    INTAKE: a list, name of the csv file, column names of the csv file
    RETURN: a csv file with given name and column names
    '''
    output_file = open(file_name+'.csv','w')
    output_writer = csv.writer(output_file)
    output_writer.writerow(col_names)

    for i in list_name:
        output_writer.writerow(i)

    output_file.close()

def write_bio(insta_id):
    '''
    INTAKE: an Instagram id
    RETURN: a csv file with bio
    '''
    r = requests.get("https://www.instagram.com/" + insta_id)
    page_source = r.text

    start_index = page_source.find("<meta property=\"og:description\" content=") + len("<meta property=\"og:description\" content=")
    end_index = page_source.find("/>\n",start_index)
    bio = page_source[start_index:end_index]

    bio_file = open(insta_id + '_bio.csv','w')
    bio_writer = csv.writer(bio_file)
    bio_writer.writerow(['instagram_id','bio'])
    bio_writer.writerow([insta_id,bio])

if __name__ == '__main__':
    insta_id = sys.argv[1]

    post_list = PostList(insta_id).to_list()
    account_info = extract_statistics(post_list)

    write_to_csv(account_info['stats_list'], 'stats_list', ['post_id','num_of_likes','num_of_comments'])
    write_to_csv(account_info['caption_list'], 'caption_list', ['post_id','caption'])
    # download_photos(post_list)
    write_bio(insta_id)
