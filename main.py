import os
import sys
import urllib
import requests
import csv

class Post():
    def __init__(self, insta_id, max_id):
        self.insta_id = insta_id
        self.max_id = max_id
        self.__url = None
        self.__json_response = None
        self.__items = []

    @property
    def url(self):
        if self.__url:
            return self.__url

        self.__url = os.path.join('https://www.instagram.com', self.insta_id, 'media')

        if self.max_id:
            self.__url += ('?max_id=' + self.max_id)

        return self.__url

    @property
    def json_response(self):
        if self.__json_response:
            return self.__json_response

        response = requests.get(self.url)
        self.__json_response = response.json()

        return self.__json_response

    @property
    def items(self):
        if self.__items:
            return self.__items

        self.__items = self.json_response['items']

        return self.__items

    def more_available(self):
        return self.json_response['more_available'] == True

class PostList():
    def __init__(self, insta_id):
        self.insta_id = insta_id
        self.items = []

    def to_list(self):
        if self.items:
            return self.items

        max_id = None

        while True:
            post = Post(insta_id, max_id)

            for item in post.items:
                self.items.append(item)

            if post.more_available() is not True:
                break

            max_id = post.items[-1]['id']

        return self.items

class Account():
    def __init__(self, insta_id):
        self.insta_id = insta_id
        self.__post_list = []
        self.__stats_list = []
        self.__caption_list = []
        self.__bio = None

    @property
    def post_list(self):
        if self.__post_list:
            return self.__post_list

        self.__post_list = PostList(insta_id).to_list()

        return self.__post_list

    @property
    def stats_list(self):
        if self.__stats_list:
            return self.__stats_list

        post_list = self.post_list

        for post in post_list:
            self.__stats_list.append([
                post['code'],
                post['likes']['count'],
                post['comments']['count']
            ])

        return self.__stats_list

    @property
    def caption_list(self):
        if self.__caption_list:
            return self.__caption_list

        post_list = self.post_list

        for post in post_list:
            caption = [post['code']]

            if post['caption']:
                caption.append(post['caption']['text'].replace('\n', ' '))

            self.__caption_list.append(caption)

        return self.__caption_list

    @property
    def bio(self):
        if self.__bio:
            return self.__bio

        response = requests.get('https://www.instagram.com/' + self.insta_id)
        page_source = response.text
        import pdb; pdb.set_trace()
        start_index = page_source.find("<meta property=\"og:description\" content=") + len("<meta property=\"og:description\" content=")
        end_index = page_source.find("/>\n",start_index)
        self.__bio = page_source[start_index:end_index]

        return self.__bio

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

def write_bio(account):
    '''
    INTAKE: an Account object
    RETURN: a csv file with bio
    '''
    bio = account.bio

    bio_file = open(insta_id + '_bio.csv','w')
    bio_writer = csv.writer(bio_file)
    bio_writer.writerow(['instagram_id','bio'])
    bio_writer.writerow([insta_id, bio])

if __name__ == '__main__':
    insta_id = sys.argv[1]

    account = Account(insta_id)

    write_to_csv(account.stats_list, 'stats_list', ['post_id','num_of_likes','num_of_comments'])
    write_to_csv(account.caption_list, 'caption_list', ['post_id','caption'])
    # download_photos(post_list)
    write_bio(account)
