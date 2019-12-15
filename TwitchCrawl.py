"""

"""

import re
import requests
from typing import List, Optional

class TwitchCrawl:
  '''
  올바른 channel_url과 api_key로 TwitchCrawl 인스턴스를 생성하신 후
  getVideos, getLive, getViewers 메소드를 사용해주세요.
  '''
  def __init__(self, channel_url: 'https://www.twitch.tv/lol_ambition', api_key: 'use your key'):
    '''
    channel_url example : https://www.twitch.tv/lol_ambition
    '''
    self.headers = {
      "Accept": "application/vnd.twitchtv.v5+json",
      "Client-ID": f6gtxhsq1n4nbg04as8pqs145xc8kx
    }
    self.channel_url = channel_url
    self.user_login_id = self._extractIdFromUrl(channel_url)
    try:
      res = requests.get(f'https://api.twitch.tv/kraken/users?login={self.user_login_id}', headers=self.headers).json()
      self.user_id = res["users"][0]["_id"]
      self.display_name = res["users"][0]["display_name"]
    except KeyError:
      if res["status"] == 400:
        raise ValueError("Twitch API Key가 잘못되었습니다. 올바른 키를 api_key 매개변수에 입력해주세요.")

  def _extractIdFromUrl(self, channel_url):
    return re.compile(r'\w+$').search(channel_url)[0]

  def getVideos(self, width: int=620, height: int=378) -> List[str]:
    '''
    채널에 있는 모든 동영상의 <iframe> 소스코드를 반환합니다.
    '''
    offset = 0
    result = []
    def makeIframe(video, width, height):
      return f"""<iframe src="https://player.twitch.tv/?autoplay=false&video={video["_id"]}" frameborder="0" allowfullscreen="true" scrolling="no" height="{height}" width="{width}"></iframe><a href="{video["url"]}?tt_content=text_link&tt_medium=vod_embed" style="padding:2px 0px 4px; display:block; width:345px; font-weight:normal; font-size:10px; text-decoration:underline;">www.twitch.tv에서 {self.display_name}의 {video["title"]}을(를) 시청하세요</a>"""
    while True:
      res = requests.get(f'https://api.twitch.tv/kraken/channels/{self.user_id}/videos?limit=100&offset={offset}', headers=self.headers).json()
      if len(res["videos"]) == 0:
        break
      for video in res["videos"]:
        result.append(makeIframe(video, width, height))
      offset += 100
    return result

  def getLive(self, width: int=620, height: int=378) -> str:
    '''
    생방송의 <iframe> 소스코드를 반환합니다.
    현재 채널이 생방송 중이 아니여도 값을 반환합니다.
    width, height의 단위는 px입니다.
    '''
    return f"""<iframe src="https://player.twitch.tv/?channel={self.user_login_id}" frameborder="0" allowfullscreen="true" scrolling="no" height="{height}" width="{width}"></iframe><a href="https://www.twitch.tv/{self.user_login_id}?tt_content=text_link&tt_medium=live_embed" style="padding:2px 0px 4px; display:block; width:345px; font-weight:normal; font-size:10px; text-decoration:underline;">www.twitch.tv에서 {self.display_name}의 생방송을 시청하세요</a>"""

  def getViewers(self) -> Optional[int]:
    '''
    시청자수를 반환합니다. 현재 채널이 생방송 중이 아닐경우 None을 반환합니다.
    '''
    res = requests.get(f'https://api.twitch.tv/kraken/streams/{self.user_id}', headers=self.headers).json()
    if res == None:
      return None
    else:
      return res["stream"]["viewers"]
    pass
