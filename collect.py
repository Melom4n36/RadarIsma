#!/usr/bin/env python3
"""Recopilador Reddit con OAuth de aplicación, biblioteca estándar y fallos explícitos."""
import argparse, base64, csv, datetime as dt, json, os, pathlib, sys, time
import urllib.parse, urllib.request, urllib.error

SUBREDDITS = [
 'ArtificialInteligence','ChatGPT','ClaudeAI','CompTIA','DeepSeek','Futurology',
 'GeminiAI','GoogleAIStudio','MistralAI','OpenAI','PromptEngineering','antiai',
 'claude','filen_io','opensource','perplexity_ai','singularity','sysadmin','vibecoding'
]
API='https://oauth.reddit.com'

def request(url, headers, data=None, retries=2):
    for attempt in range(retries+1):
        req=urllib.request.Request(url, headers=headers, data=data)
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503,504) and attempt<retries:
                time.sleep(min(2**attempt*3,15)); continue
            raise RuntimeError(f'HTTP {e.code} en {urllib.parse.urlsplit(url).path}') from e
        except (TimeoutError, urllib.error.URLError) as e:
            if attempt<retries:
                time.sleep(2**attempt*2); continue
            raise RuntimeError(f'Error de conexión: {e}') from e

def token(cid, secret, agent):
    auth=base64.b64encode(f'{cid}:{secret}'.encode()).decode()
    data=urllib.parse.urlencode({'grant_type':'client_credentials'}).encode()
    obj=request('https://www.reddit.com/api/v1/access_token',
                {'Authorization':f'Basic {auth}','User-Agent':agent,'Content-Type':'application/x-www-form-urlencoded'},data)
    if 'access_token' not in obj:
        raise RuntimeError('OAuth no proporcionó access_token; comprueba permisos y credenciales')
    return obj['access_token']

def get(path, headers, params=None):
    url=API+path
    if params: url+='?'+urllib.parse.urlencode(params)
    return request(url,headers)

def comments_for(post, headers, count):
    path=post['permalink']
    listing=get(path.rstrip('/')+'.json',headers,{'limit':count,'depth':1,'sort':'top','raw_json':1})
    if not isinstance(listing,list) or len(listing)<2: return []
    out=[]
    for child in listing[1].get('data',{}).get('children',[]):
        if child.get('kind')!='t1': continue
        d=child.get('data',{})
        if not d.get('body') or d.get('body') in ('[deleted]','[removed]'): continue
        out.append({'id':d.get('id'),'body':d['body'][:6000], 'score':d.get('score'),
                    'created_utc':d.get('created_utc'),'permalink':'https://www.reddit.com'+d.get('permalink','')})
        if len(out)>=count: break
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--days',type=int,default=7)
    ap.add_argument('--end-date',help='Fecha UTC inclusiva YYYY-MM-DD')
    ap.add_argument('--pages',type=int,default=3,help='Páginas de 100 resultados por ordenación (máx. 10)')
    ap.add_argument('--comments',type=int,default=10,help='Comentarios por publicación (0 desactiva)')
    ap.add_argument('--max-comment-posts',type=int,default=6,help='Máximo de hilos comentados por subreddit')
    args=ap.parse_args()
    if not 1<=args.days<=90 or not 1<=args.pages<=10 or not 0<=args.comments<=100 or not 0<=args.max_comment_posts<=100:
        ap.error('Parámetros fuera de rango')
    cid=os.getenv('REDDIT_CLIENT_ID'); secret=os.getenv('REDDIT_CLIENT_SECRET'); agent=os.getenv('REDDIT_USER_AGENT')
    if not all((cid,secret,agent)):
        sys.exit('Faltan REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET o REDDIT_USER_AGENT. Consulta README.md')
    if args.end_date:
        end_day=dt.date.fromisoformat(args.end_date)
        end=dt.datetime.combine(end_day+dt.timedelta(days=1),dt.time.min,tzinfo=dt.timezone.utc).timestamp()
    else:
        end=time.time(); end_day=dt.datetime.fromtimestamp(end,dt.timezone.utc).date()
    start=end-args.days*86400
    access=token(cid,secret,agent)
    headers={'Authorization':f'bearer {access}','User-Agent':agent}
    records=[]; coverage={}
    for sub in SUBREDDITS:
        found={}; errors=[]; examined=0
        for sort in ('new','top'):
            after=None
            for page in range(args.pages):
                params={'limit':100,'raw_json':1}
                if sort=='top': params['t']='week'
                if after: params['after']=after
                try:
                    listing=get(f'/r/{sub}/{sort}',headers,params)
                    children=listing['data']['children']; after=listing['data'].get('after')
                    examined+=len(children)
                    for item in children:
                        if item.get('kind')!='t3':continue
                        p=item['data']; ts=p.get('created_utc',0)
                        if p.get('subreddit','').lower()!=sub.lower() or not start<=ts<end:continue
                        if p.get('stickied'):continue
                        pid=p.get('id')
                        if pid:found[pid]=p
                    if not after or (sort=='new' and children and children[-1]['data'].get('created_utc',0)<start):break
                    time.sleep(.6)
                except (RuntimeError,KeyError,TypeError) as e:
                    errors.append(f'{sort}, página {page+1}: {e}'); break
        selected=sorted(found.values(),key=lambda p:(p.get('score',0),p.get('num_comments',0)),reverse=True)
        for idx,p in enumerate(selected):
            path=p.get('permalink','')
            item={'id':p.get('id'),'subreddit':sub,'title':p.get('title',''),
                  'selftext':p.get('selftext','')[:15000],
                  'url':'https://www.reddit.com'+path if path.startswith('/') else p.get('url',''),
                  'created_utc':p.get('created_utc'),
                  'created_iso':dt.datetime.fromtimestamp(p.get('created_utc',0),dt.timezone.utc).isoformat(),
                  'score':p.get('score'),'num_comments':p.get('num_comments'),
                  'is_self':p.get('is_self'),'external_url':p.get('url'),
                  'comments':[],'comments_error':None}
            if idx<args.max_comment_posts and args.comments:
                try: item['comments']=comments_for(p,headers,args.comments)
                except (RuntimeError,KeyError,TypeError,ValueError) as e:item['comments_error']=str(e)
                time.sleep(.6)
            records.append(item)
        coverage[sub]={'posts_found':len(found),'listing_items_examined':examined,
                       'posts_with_comments':sum(bool(x['comments']) for x in records if x['subreddit']==sub),
                       'errors':errors,'status':'partial_or_failed' if errors else 'retrieved_not_exhaustive'}
        print(f'r/{sub}: {len(found)} publicaciones, {len(errors)} errores',flush=True)
    out=pathlib.Path('output');out.mkdir(exist_ok=True)
    date=end_day.isoformat()
    (out/f'reddit_{date}.json').write_text(json.dumps({'period_start_utc':start,'period_end_utc_exclusive':end,
        'generated_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'posts':records},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/f'coverage_{date}.json').write_text(json.dumps({'period_start_utc':start,'period_end_utc_exclusive':end,
        'communities':coverage},ensure_ascii=False,indent=2),encoding='utf-8')
    fields=['subreddit','title','url','created_iso','score','num_comments','selftext','id']
    with (out/f'reddit_{date}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for item in records:writer.writerow({k:item.get(k) for k in fields})
    print(f'Archivos generados en {out.resolve()} | publicaciones: {len(records)}')
    if any(x['errors'] for x in coverage.values()):
        print('ATENCIÓN: hubo errores; consulta coverage_*.json. No considerar exhaustiva esta recopilación.')

if __name__=='__main__':main()
