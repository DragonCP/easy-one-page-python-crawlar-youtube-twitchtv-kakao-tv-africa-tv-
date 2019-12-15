"""

"""

import re
import requests
from typing import List, Optional

class AfreecatvCrawl:
  '''
  올바른 channel_url로 AfreecatvCrawl 인스턴스를 생성하신 후 
  getVideos, getLive, getViewers 메소드를 사용해주세요.
  '''
  def __init__(self, channel_url: str):
    '''
    channel_url example : http://bj.afreecatv.com/afmusician
    '''
    self.channel_url = channel_url
    self.user_id = self._extractIdFromUrl(channel_url)
    self.headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Host': 'bjapi.afreecatv.com',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0',
    }

  def _extractIdFromUrl(self, channel_url):
    return re.compile(r'\w+$').search(channel_url)[0]

  def getVideos(self, width: int=640, height: int=360) -> List[str]:
    '''
    채널에 있는 모든 동영상의 <iframe> 소스코드를 반환합니다.
    '''
    result = []
    page = 1
    def parsePage(page):
      res = requests.get(f"http://bjapi.afreecatv.com/api/{self.user_id}/vods?page={page}", headers=self.headers).json()
      return res["data"]
    def makeIframe(video, width, height):
      category_str = video["ucc"]["category"]
      if type(category_str) == int:
        category_str = str(category_str)
      if len(category_str) == 5:
        category_str = '000' + category_str
      elif len(category_str) == 6:
        category_str = '00' + category_str
      return f"""<iframe width="{width}" height="{height}" src="http://vod.afreecatv.com/embed.php?type=station&isAfreeca=false&autoPlay=false&showChat=false&szBjId={self.user_id}&nStationNo={video["station_no"]}&nBbsNo={video["bbs_no"]}&nTitleNo={video["title_no"]}&szCategory={category_str}&szPart={video["ucc"]["file_type"]}&szVodType=STATION&isEmbedautoPlay=false&szSysType=html5" frameborder="0" allowfullscreen="true"></iframe>"""

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
    res = requests.get(f"http://bjapi.afreecatv.com/api/{self.user_id}/station", headers=self.headers).json()
    if res["broad"] == None:
      return None
    broad_no = res["broad"]["broad_no"]
    return f"""<iframe src="http://play.afreecatv.com/{self.user_id}/{broad_no}/embed" width="{width}" height="{height}" frameborder="0" allowfullscreen></iframe>"""

  def getViewers(self) -> Optional[int]:
    '''
    시청자수를 반환합니다. 현재 채널이 생방송 중이 아닐경우 None을 반환합니다.
    '''
    res = requests.get(f"http://bjapi.afreecatv.com/api/{self.user_id}/station", headers=self.headers).json()
    if res["broad"] == None:
      return None
    return res["broad"]["current_sum_viewer"]
