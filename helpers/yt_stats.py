import json
import requests
from tqdm import tqdm


class YTstats:

    def __init__(self, api_key, search_limit):
        self.api_key = api_key
        self.channel_statistics = None
        self.video_data = None
        self.search_limit = search_limit

    def get_channel_name(self,url):
        parts = url.split('/')
        return parts[-1].replace('@','')

    def get_channel_id(self,channel_name):
        #url = f"https://youtube.googleapis.com/youtube/v3/channels?part=id&forUsername={channel_name}&key={self.api_key}"
        url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={channel_name}&key={self.api_key}"
        json_url = requests.get(url=url, params=f'["Autorization": "Bearer {self.api_key}"]')
        data = json.loads(json_url.text)
        id = ''
        try:
            id = data['items'][0]['id']
        except KeyError as e:
            print(f'Error! Could not get id of { channel_name } in data: \n{data}')
            id = ''
        return id

    def extract(self, channel_url):
        channel_name = self.get_channel_name(channel_url)
        channel_id = self.get_channel_id(self.get_channel_name(channel_url))
        #print(f"Channel {channel_name}, Id: {channel_id}")
        if channel_id == '':
            raise Exception(f"Channel not found {channel_name}")
        #self.get_channel_statistics(channel_id)
        self.get_channel_video_data(channel_id)

    def get_channel_statistics(self, channel_id):
        """Extract the channel statistics"""
        #print('get channel statistics...')
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={self.api_key}'
        pbar = tqdm(total=1)

        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0]['statistics']
        except KeyError:
            print('Could not get channel statistics')
            data = {}

        self.channel_statistics = data
        pbar.update()
        pbar.close()
        return data

    def get_channel_video_data(self, channel_id):
        "Extract all video information of the channel"
        #print('get video data...')
        channel_videos, channel_playlists = self._get_channel_content(channel_id=channel_id, limit=self.search_limit,check_all_pages=False)

        #parts = ["snippet", "statistics", "contentDetails", "topicDetails"]
        parts = ["snippet"]
        #for video_id in tqdm(channel_videos):
        #    for part in parts:
        #        data = self._get_single_video_data(video_id, part)
        #        channel_videos[video_id].update(data)

        self.video_data = channel_videos
        return channel_videos

    def _get_single_video_data(self, video_id, part):
        """
        Extract further information for a single video
        parts can be: 'snippet', 'statistics', 'contentDetails', 'topicDetails'
        """

        url = f"https://youtube.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}"
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0][part]
        except KeyError as e:
            print(f'Error! Could not get {part} part of data: \n{data}')
            data = dict()
        return data

    def _get_channel_content(self, channel_id, limit, check_all_pages=True):
        """
        Extract all videos and playlists, can check all available search pages
        channel_videos = videoId: title, publishedAt
        channel_playlists = playlistId: title, publishedAt
        return channel_videos, channel_playlists
        """
        #url = f"https://youtube.googleapis.com/youtube/v3/search?channelId={channel_id}&part=snippet&order=date&eventType=completed&maxResults={str(limit)}&key={self.api_key}"
        url = f"https://www.googleapis.com/youtube/v3/search?channelId={channel_id}&part=snippet&order=date&eventType=completed&maxResults={str(limit)}&key={self.api_key}"

        vid, pl, npt = self._get_channel_content_per_page(url)
        idx = 0
        while (check_all_pages and npt is not None and idx < 10):
            nexturl = url + "&pageToken=" + npt
            next_vid, next_pl, npt = self._get_channel_content_per_page(nexturl)
            vid.update(next_vid)
            #pl.update(next_pl)
            idx += 1

        return vid, None

    def _get_channel_content_per_page(self, url):
        """
        Extract all videos and playlists per page
        return channel_videos, channel_playlists, nextPageToken
        """
        try:
            json_url = requests.get(url=url, params=f'["Autorization": "Bearer {self.api_key}"]')
            data = json.loads(json_url.text)
            channel_videos = dict()
            if 'items' not in data:
                #print('Error! Could not get correct channel data!\n', data)
                #return channel_videos, channel_videos, None
                raise Exception(f'Could not get correct channel data using {url}')
            nextPageToken = data.get("nextPageToken", None)

            item_data = data['items']

            for item in item_data:
                try:
                    kind = item['id']['kind']
                    published_at = item['snippet']['publishedAt']
                    title = item['snippet']['title']
                    if kind == 'youtube#video':
                        video_id = item['id']['videoId']
                        channel_videos[video_id] = {'publishedAt': published_at, 'title': title}
                except KeyError as e:
                    print('Error! Could not extract data from item:\n', item)

        except Exception as e:
            print(f'Error!\n', e)

        return channel_videos, None, nextPageToken

    def dump_(self, channel_id):
        """Dumps channel statistics and video data in a single json file"""
        if self.channel_statistics is None or self.video_data is None:
            print('data is missing!\nCall get_channel_statistics() and get_channel_video_data() first!')
            return

        fused_data = {channel_id: {"channel_statistics": self.channel_statistics,
                                        "video_data": self.video_data}}

        channel_title = self.video_data.popitem()[1].get('channelTitle', channel_id)
        channel_title = channel_title.replace(" ", "_").lower()
        filename = channel_title + '.json'
        with open(filename, 'w') as f:
            json.dump(fused_data, f, indent=4)

        print('file dumped to', filename)

    def dump(self):
        return self.video_data