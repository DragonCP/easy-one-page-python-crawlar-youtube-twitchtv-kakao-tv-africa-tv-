"""

"""

import re
import requests
from typing import List, Optional
import time

class KakaotvCrawl:
  '''
  올바른 channel_url로 KakaotvCrawl 인스턴스를 생성하신 후 
  getVideos, getLive, getViewers 메소드를 사용해주세요.
  '''
  def __init__(self, channel_url: str):
    '''
    channel_url example : https://tv.kakao.com/channel/2653451/info
    '''
    self.channel_url = channel_url
    self.channel_id = self._extractIdFromUrl(channel_url)
  
  def _extractIdFromUrl(self, channel_url):
    return re.compile(r'\/([0-9]+)\/info').search(channel_url)[1]

  def getVideos(self, width: int=640, height: int=360) -> List[str]:
    '''
    채널에 있는 모든 동영상의 <iframe> 소스코드를 반환합니다.
    '''
    result = []
    page = 1
    def parsePage(page):
      res = requests.get(f"https://tv.kakao.com/api/v1/ft/channels/{self.channel_id}/videolinks?sort=CreateTime&fulllevels=clipLinkList%2CliveLinkList&fields=ccuCount%2CthumbnailUri%2C-user%2C-clipChapterThumbnailList%2C-tagList&size=20&page={page}&_={int(time.time())}").json()
      return res["clipLinkList"]
    def makeIframe(video, width, eight):
      return f"""<iframe title="{video["displayTitle"]}" width="{width}" height="{height}" src="https://play-tv.kakao.com/embed/player/cliplink/{video["id"]}?service=kakao_tv" allowfullscreen frameborder="0" scrolling="no" allow="autoplay"></iframe>"""
    
    while True:
      res = parsePage(page)
      if len(res) == 0:
        break
      for elem in res:
        result.append(makeIframe(elem, width, height))
      page += 1
    return result

  def getLive(self, width: int=640, height: int=360) -> Optional[str]:
    '''
    생방송의 <iframe> 소스코드를 반환합니다. 
    현재 채널이 생방송 중이 아니면 None을 반환합니다.
    width, height의 단위는 px입니다.
    '''
    res = requests.get(f"https://tv.kakao.com/api/v1/ft/channels/{self.channel_id}/videolinks?sort=CreateTime&fulllevels=clipLinkList%2CliveLinkList&fields=ccuCount%2CthumbnailUri%2C-user%2C-clipChapterThumbnailList%2C-tagList&size=20&page=1&_={int(time.time())}").json()
    if len(res["liveLinkList"]) == 0:
      return None
    broad_id = res["liveLinkList"][0]["id"]
    broad_title = res["liveLinkList"][0]["displayTitle"]
    return f"""
    <iframe title='{broad_title}' width='{width}px' height='{height}px' src='https://tv.kakao.com/embed/player/livelink/{broad_id}?width={width}&height={height}&service=kakao_tv' frameborder='0' scrolling='no' ></iframe>
    """

  def getViewers(self) -> Optional[int]:
    '''
    시청자수를 반환합니다. 현재 채널이 생방송 중이 아닐경우 None을 반환합니다.
    '''
    res = requests.get(f"https://tv.kakao.com/api/v1/ft/channels/{self.channel_id}/videolinks?sort=CreateTime&fulllevels=clipLinkList%2CliveLinkList&fields=ccuCount%2CthumbnailUri%2C-user%2C-clipChapterThumbnailList%2C-tagList&size=20&page=1&_={int(time.time())}").json()
    if len(res["liveLinkList"]) == 0:
      return None
    return int(res["liveLinkList"][0]["live"]["ccuCount"])
T = KakaotvCrawl("https://tv.kakao.com/channel/2663784/info")
a = T.getViewers()
print(a)