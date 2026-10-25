"""Acquire and preserve Wikimedia Commons file-level licensing and identity."""
from pathlib import Path
import urllib.request,urllib.parse,json,re,time,hashlib,sys,html
from PIL import Image
R=Path(__file__).resolve().parents[1]
UA='DimsumAtlasEducationalBook/1.1 (Wikimedia Commons attributed reuse)'
def request(url):
 err=None
 for wait in (0,2):
  if wait:time.sleep(wait)
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=35) as r:return r.read()
  except Exception as e:err=e
 raise err

def api(params):
 return json.loads(request('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'format':'json',**params})))
def clean(s):return html.unescape(re.sub('<[^>]+>','',s)).strip()
def info(page):
 i=page['imageinfo'][0];e=i.get('extmetadata',{})
 def v(k):return clean(e.get(k,{}).get('value',''))
 return {'title':page['title'],'page_id':page['pageid'],'source_page':i['descriptionurl'],'original_url':i['url'],'download_url':i.get('thumburl',i['url']),'original_width':i['width'],'original_height':i['height'],'author':v('Artist'),'credit':v('Credit'),'description':v('ImageDescription'),'license':v('LicenseShortName'),'license_url':v('LicenseUrl'),'attribution_required':v('AttributionRequired'),'copyrighted':v('Copyrighted'),'timestamp':i.get('timestamp')}
def search(q,n=5):
 data=api({'action':'query','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':n,'prop':'imageinfo','iiprop':'url|size|extmetadata|timestamp','iiurlwidth':1100})
 return [info(x) for x in sorted(data.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',0)) if 'imageinfo' in x]
def download(title,id):
 data=api({'action':'query','titles':title,'prop':'imageinfo','iiprop':'url|size|extmetadata|timestamp','iiurlwidth':1100})
 rec=info(next(iter(data['query']['pages'].values())))
 lic=rec['license'].lower()
 if not (lic.startswith(('cc by','cc0')) or lic in ['public domain','pd']):raise ValueError('unsupported license '+rec['license'])
 content=request(rec['download_url'])
 # Identity-preserving download: keep server thumbnail or original bytes, never crop or retouch.
 import io
 im=Image.open(io.BytesIO(content));im.verify();im=Image.open(io.BytesIO(content))
 ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}.get(im.format)
 if not ext:raise ValueError('unsupported format '+str(im.format))
 if min(im.size)<350:raise ValueError('too small '+str(im.size))
 path=R/'assets/images'/('real-'+id+ext);path.write_bytes(content)
 rec.update({'id':'real-'+id,'file':str(path.relative_to(R)),'sha256':hashlib.sha256(content).hexdigest(),'downloaded_size':list(im.size),'retrieved':'2026-10-25','changes':'No crop, retouch, or color changes. Wikimedia-supplied resized copy if available.'})
 return rec
if __name__=='__main__':
 if sys.argv[1]=='search':print(json.dumps(search(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 5),ensure_ascii=False,indent=2))
 elif sys.argv[1]=='download':print(json.dumps(download(sys.argv[2],sys.argv[3]),ensure_ascii=False,indent=2))
