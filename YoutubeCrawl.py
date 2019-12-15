"""

"""

import re
import requests
from typing import List, Optional

class YoutubeCrawl:
  '''
  올바른 channel_url과 api_key로 YoutubeCrawl 인스턴스를 생성하신 후 
  getVideos, getLive, getViewers 메소드를 사용해주세요.
  '''
  def __init__(self, channel_url: str, api_key: str):
    '''
    channel_url example : https://www.youtube.com/channel/UCIA_jLpi8Tp2YM8ZTe4nD5A
    api_key example : <api-key>
    '''
    self.api_key = api_key
    self.channel_url = channel_url
    self.user_id = self._extractIdFromUrl(channel_url)

  def _extractIdFromUrl(self, channel_url):
    return re.compile(r'[^\/]*$').search(channel_url)[0]

  def _responseErrorHandler(self, res):
    if ('error' in res) and (res["error"]["errors"]["reason"] == 'quotaExceeded'):
      raise Exception('유튜브 API 할당량이 초과되었습니다.')
    elif ('error' in res) and (res["error"]["errors"]["reason"] == 'keyInvalid'):
      raise Exception('올바르지 않은 API key입니다.')

  def getVideos(self, width: int=560, height: int=315) -> List[str]:
    '''
    채널에 있는 모든 동영상의 <iframe> 소스코드를 반환합니다.
    '''
    result = []
    token = None
    def parsePage(token):
      base_url = f"https://www.googleapis.com/youtube/v3/search?channelId={self.user_id}&part=id&maxResults=50&order=date&type=video&key={self.api_key}"
      if token != None:
        base_url += f"&pageToken={token}"
      res = requests.get(base_url).json()
      self._responseErrorHandler(res)
      _token = res["nextPageToken"] if "nextPageToken" in res else None
      return _token, res["items"]
    def makeIframe(video, width, height):
      video_id = video["id"]["videoId"]
      return f"""<iframe width="{width}" height="{height}" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""

    while True:
      _token, res = parsePage(token)
      for elem in res:
        result.append(makeIframe(elem, width, height))
      if _token == None:
        break
      token = _token
    
    return result

  def getLive(self, width: int=560, height: int=315) -> Optional[str]:
    '''
    생방송의 <iframe> 소스코드를 반환합니다. 
    현재 채널이 생방송 중이 아니면 None을 반환합니다.
    width, height의 단위는 px입니다.
    '''
    res = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={self.user_id}&type=video&eventType=live&key={self.api_key}").json()
    self._responseErrorHandler(res)
    if len(res["items"]) == 0:
      return None
    video_id = res["items"][0]["id"]["videoId"]
    return f"""<iframe width="{width}" height="{height}" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""

  def getViewers(self) -> Optional[int]:
    '''
    시청자수를 반환합니다. 현재 채널이 생방송 중이 아닐경우 None을 반환합니다.
    '''
    res = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={self.user_id}&type=video&eventType=live&key={self.api_key}").json()
    self._responseErrorHandler(res)
    if len(res["items"]) == 0:
      return None
    video_id = res["items"][0]["id"]["videoId"]
    res = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={video_id}&key={self.api_key}").json()
    return int(res["items"][0]["liveStreamingDetails"]["concurrentViewers"])
