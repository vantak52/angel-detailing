"""Build a dependency-free, multi-page redesign from the original public content."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote, urlsplit, parse_qs
from html import escape as e
import hashlib,json,re

ROOT=Path(__file__).parent
DIST=ROOT/'dist'
CAT=json.loads((ROOT/'content/catalog.json').read_text(encoding='utf8'))
PAGES=json.loads((ROOT/'content/pages.json').read_text(encoding='utf8'))
DETAILS=json.loads((ROOT/'content/services.json').read_text(encoding='utf8'))
BY_URL={p['url']:p for p in PAGES}
ARROW='<svg class="icon" width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5 15 15 5M5 5h10v10" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/></svg>'
MAP='https://yandex.ru/maps/org/angel/1087404926/'
TELEGRAM='https://t.me/+79210989000'
MAX='https://max.ru/u/f9LHodD0cOLqgE_gbBccMwOzc1V6d8FoZyz32WiGXqQiT2DGUtQoDP3lc-k'

def asset(path):
    local='/assets/'+path.rsplit('/',1)[-1].rsplit('.',1)[0]+'.webp'
    return local if (DIST/local.lstrip('/')).exists() else 'https://angeldetailing.ru'+quote(path,safe='/')

def clean(html):
    soup=BeautifulSoup(html or '', 'html.parser')
    for x in soup(['script','style','iframe','img']): x.decompose()
    for tag in soup.find_all(True):
        href=tag.get('href')
        tag.attrs={}
        if tag.name=='a' and href:
            tag['href']=href
            if href.startswith('/tags/'): tag['href']='https://angeldetailing.ru'+quote(href,safe='/')
    for a in soup.find_all('a'):
        if not a.get_text(strip=True): a.decompose()
    for x in soup.find_all(['li','p']):
        if not x.get_text(strip=True): x.decompose()
    return str(soup)

works=[]
for entry in CAT['works']:
    p=BY_URL.get(entry['url'],{})
    title=p.get('title') or entry['url'].rsplit('/',1)[-1].replace('_',' ').replace('.html','')
    title=re.split(r'\s[—–]\s',title)[0]
    soup=BeautifulSoup(p.get('text',''),'html.parser')
    txt=soup.get_text(' ',strip=True)
    tags=BeautifulSoup(p.get('html',''),'html.parser').select('.tags a')
    tagtext=' '.join(x.get_text() for x in tags).lower()
    category=[]
    if 'полиров' in txt.lower(): category.append('polish')
    if any(x in txt.lower() for x in ['керами','полиуретан','защитн']): category.append('protection')
    if any(x in txt.lower() for x in ['салон','интерьер','сиден']): category.append('interior')
    if any(x in txt.lower() for x in ['стайлинг','винил','окраска','антихром']): category.append('styling')
    brand=title.split(' ')[0]
    if title.startswith('Mercedes'): brand='Mercedes-Benz'
    if title.startswith('Land Rover') or title.startswith('Range Rover'): brand='Land Rover'
    if title.startswith('Rolls'): brand='Rolls-Royce'
    if title.startswith('Li '): brand='Li Auto'
    labels=[x.get_text(' ',strip=True) for x in soup.select('li') if x.get_text(strip=True)][:2]
    works.append({**entry,'title':title,'image':asset((p.get('images') or [entry['thumbnail']])[0]),'categories':category,'brand':brand,'caption':' · '.join(labels) or 'Проект Angel Detailing'})

def logo(animated=False):
    emblem='<span class="emblem" aria-hidden="true">'+''.join(f'<img class="logo-{part}" src="/assets/emblem-{part}.png" width="440" height="212" alt="">' for part in ['left','center','right'])+'<i class="trail trail-left"></i><i class="trail trail-right"></i></span>' if animated else '<img class="static-emblem" src="/assets/emblem.png" width="440" height="212" alt="">'
    return f'<a class="brand" href="/" aria-label="Angel Detailing — главная">{emblem}<img class="wordmark" src="/assets/wordmark.png" width="274" height="79" alt="Angel Detailing"></a>'

navitems=[('/uslugi/','Услуги'),('/galereya/','Работы'),('/avtomobili/','Автомобили'),('/otzyvy/','Отзывы'),('/kontakty','Контакты')]
def theme_toggle(variant='desktop'):
    label='<span>Светлая тема</span><span class="theme-switch" aria-hidden="true"></span>' if variant=='mobile' else '<span>Тема</span>' if variant=='hero' else ''
    return f'''<button class="theme-toggle theme-toggle-{variant}" type="button" data-theme-toggle aria-label="Светлая тема" aria-pressed="false" title="Включить светлую тему"><svg class="theme-sun" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></svg><svg class="theme-moon" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z"/></svg>{label}</button>'''

def header(path):
    nav=''.join(f'<a href="{u}"'+(' aria-current="page"' if path.startswith(u) else '')+f'>{t}</a>' for u,t in navitems)+'<a href="/poisk" class="search-link" aria-label="Поиск по сайту"><svg width="15" height="15" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" stroke="currentColor" stroke-width="1.2"/><path d="m13 13 4 4" stroke="currentColor" stroke-width="1.2"/></svg><span>Поиск</span></a>'
    return f'''<a class="skip" href="#main">Перейти к содержимому</a><header class="header"><div class="header-inner">{logo(True)}<nav class="desktop-nav" aria-label="Основная навигация">{nav}</nav><a class="header-phone" href="tel:+79210989000">+7 (921) 098-90-00</a>{theme_toggle()}<button class="button button-small header-book" data-book>Записаться {ARROW}</button><button class="menu-toggle" aria-label="Открыть меню" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span></button></div></header><nav id="mobile-menu" class="mobile-menu" aria-label="Мобильная навигация" hidden>{nav}{theme_toggle('mobile')}<a class="mobile-call" href="tel:+79210989000">+7 (921) 098-90-00</a><p>Санкт-Петербург<br>Выборгская набережная, 51</p><button class="button" data-book>Записаться {ARROW}</button></nav>'''

def footer():
    return f'''<footer class="footer"><div class="container footer-top">{logo()}<p>Детейлинг-студия<br>Санкт-Петербург</p><div class="footer-social"><a href="{TELEGRAM}" target="_blank" rel="noopener">Telegram {ARROW}</a><a href="https://vk.com/angel_auto" target="_blank" rel="noopener">ВКонтакте {ARROW}</a><a href="https://dzen.ru/angeldetailing" target="_blank" rel="noopener">Дзен {ARROW}</a></div></div><div class="container footer-bottom"><span>© {2026} Angel Detailing</span><span>Санкт-Петербург</span><a href="/politika">Политика конфиденциальности</a></div></footer>'''

def booking():
    return f'''<dialog id="booking" aria-labelledby="booking-title">
      <button class="dialog-close" data-close aria-label="Закрыть окно">×</button><div class="booking-scroll">
      <div class="eyebrow">ANGEL DETAILING</div><h2 id="booking-title">Запись в студию</h2>
      <p class="muted">Позвоните или напишите нам. Обсудим автомобиль, услуги и удобное время визита.</p>
      <div class="booking-direct"><a class="button" href="tel:+79210989000">+7 (921) 098-90-00 {ARROW}</a><a class="button button-outline" href="{TELEGRAM}" target="_blank" rel="noopener">Написать в Telegram {ARROW}</a></div>
      <details class="booking-details"><summary>Или подготовить запрос на почту</summary>
        <form id="booking-form" method="post" data-connected="false">
          <label>Ваше имя<input name="cb_name" autocomplete="given-name" placeholder="Как к вам обращаться"></label>
          <label>Телефон <span aria-hidden="true">*</span><input name="cb_phone" type="tel" autocomplete="tel" inputmode="tel" required maxlength="22" placeholder="+7 (___) ___-__-__" aria-describedby="phone-help"></label>
          <small id="phone-help">Не менее 10 цифр</small>
          <label>Автомобиль и пожелания<textarea name="cb_comment" rows="2" placeholder="Марка, модель, интересующая услуга"></textarea></label>
          <input type="hidden" value="sendcb" name="do">
          <label class="consent"><input type="checkbox" name="consent" required><span>Согласен с <a href="/politika">политикой обработки персональных данных</a></span></label>
          <button class="button" type="submit">Подготовить письмо {ARROW}</button><p class="form-status" role="status" aria-live="polite"></p>
          <div class="booking-options" hidden><a class="button button-outline" data-email-draft href="mailto:info@angeldetailing.ru">Открыть письмо {ARROW}</a><a class="text-link" href="tel:+79210989000">Позвонить в студию {ARROW}</a></div>
          <p class="form-note">Откроется ваше почтовое приложение. Письмо нужно будет отправить самостоятельно.</p>
        </form>
      </details></div>
    </dialog><dialog id="lightbox" aria-label="Просмотр фотографии"><button class="dialog-close" data-close aria-label="Закрыть фотографию">×</button><button class="lightbox-prev" aria-label="Предыдущая фотография">←</button><img alt=""><button class="lightbox-next" aria-label="Следующая фотография">→</button><div class="lightbox-count" aria-live="polite"></div></dialog>'''

def write(path,title,body,description='',extra=''):
    rel=path.lstrip('/')
    target=DIST/rel
    if not rel or path.endswith('/'): target=target/'index.html'
    elif '.' not in target.name: target=target/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    theme_boot="""(()=>{let theme='dark';try{if(localStorage.getItem('angel-theme')==='light')theme='light'}catch(e){}document.documentElement.dataset.theme=theme;document.querySelector('meta[name="theme-color"]').content=theme==='light'?'#faf9f6':'#111313'})();"""
    doc=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101111"><title>{e(title)} — Angel Detailing</title><meta name="description" content="{e(description or 'Angel Detailing — студия профессионального ухода и восстановления автомобилей. Санкт-Петербург, Выборгская набережная, 51.')} "><script>{theme_boot}</script><link rel="icon" href="/assets/emblem.png"><link rel="preload" href="/assets/manrope-regular.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/editorial.css"><script>try{{if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&!sessionStorage.getItem('angel-logo-played')){{document.documentElement.classList.add('logo-intro');sessionStorage.setItem('angel-logo-played','1')}}}}catch(e){{}}</script>{extra}<script src="/app.js" defer></script></head><body>{header(path)}<main id="main">{body}</main>{footer()}{booking()}</body></html>'''
    target.write_text(doc,encoding='utf8')

def card(w,index=0):
    return f'''<a class="work-card" href="{e(w['url'])}"><div class="work-image"><img src="{w['image']}" width="640" height="800" alt="{e(w['title'])} в Angel Detailing" loading="lazy"></div><div class="work-meta"><h3>{e(w['title'])}</h3></div><p>{e(w['caption'])}</p></a>'''

def service_cards(limit=None):
    order=[0,1,3,7,2,5,6,8,4]
    arr=[CAT['services'][i] for i in order]
    if limit: arr=arr[:limit]
    return '<div class="services-grid">'+''.join(f'''<a href="{s['url']}" class="service-card"><div class="service-image"><img src="{asset(s['image'])}" width="650" height="400" alt="{e(s['title'])}" loading="lazy"><span>{i+1:02d}</span></div><div class="service-title"><h3>{s['title']}</h3>{ARROW}</div><p>{s['description']}</p></a>''' for i,s in enumerate(arr))+'</div>'

def contacts_section():
    return f'''<section class="contact-section section" id="contacts"><div class="container contact-grid"><div><div class="eyebrow">Выборгская набережная, 51</div><h2>Обсудим ваш<br>автомобиль.</h2><button class="button" data-book>Связаться со студией {ARROW}</button></div><div class="contact-details"><div><span class="label">ПОЗВОНИТЕ НАМ</span><a class="big-phone" href="tel:+79210989000">+7 (921) 098-90-00</a></div><div><span class="label">ПРИЕЗЖАЙТЕ</span><p>Санкт-Петербург<br>Выборгская набережная, 51</p><a href="{MAP}" target="_blank" rel="noopener" class="text-link">Построить маршрут {ARROW}</a></div><div><span class="label">НАПИШИТЕ НАМ</span><a href="mailto:info@angeldetailing.ru">info@angeldetailing.ru</a><div class="contact-messengers"><a href="{TELEGRAM}" target="_blank" rel="noopener">Telegram {ARROW}</a><a href="https://wa.me/79210989000" target="_blank" rel="noopener">WhatsApp {ARROW}</a><a href="{MAX}" target="_blank" rel="noopener">MAX {ARROW}</a></div></div></div></div></section>'''

def home_service_index():
    order=[0,1,3,7,2,5,6,8,4]
    return ''.join(f'<a class="service-index-link" href="{s["url"]}" data-preview="{asset(s["image"])}" data-caption="{e(s["title"])}"><span class="service-index-number" aria-hidden="true">{i+1:02d}</span><div><h3>{s["title"]}</h3><p>{s["description"]}</p></div>{ARROW}</a>' for i,s in enumerate([CAT['services'][n] for n in order]))

home=(ROOT/'templates/home.html').read_text(encoding='utf8')
picks=[next(w for w in works if 'porsche_911_carrera_992' in w['url']),next(w for w in works if 'bmw_x3_g01_lci_2026_09_02' in w['url'])]
for key,value in {'theme_toggle':theme_toggle('hero'),'arrow':ARROW,'projects':''.join(card(w) for w in picks),'service_image':asset(CAT['services'][0]['image']),'services':home_service_index(),'map':MAP,'contacts':contacts_section()}.items():
    home=home.replace('{{'+key+'}}',value)
write('/','Студия детейлинга в Санкт-Петербурге',home,extra='<link rel="preload" as="image" href="/assets/works_161_gh9bnm.webp">')

def intro(kicker,title,desc=''):
    return f'<section class="page-intro container"><div class="eyebrow">{kicker}</div><h1>{title}</h1>'+ (f'<p>{desc}</p>' if desc else '')+'</section>'

write('/uslugi/','Услуги',intro('КУЗОВ / ИНТЕРЬЕР / ЗАЩИТА','Услуги студии','Подберите направление ухода для вашего автомобиля. Детали работ и стоимость уточним при обращении в студию.')+'<section class="container section section-compact">'+service_cards()+'</section>'+contacts_section())

gallerydata=json.dumps(works,ensure_ascii=False).replace('</',r'<\/')
(DIST/'works.js').write_text('window.ANGEL_WORKS='+gallerydata+';',encoding='utf8')
brands=sorted(set(w['brand'] for w in works))
for path,is_cars in [('/galereya/',False),('/avtomobili/',True)]:
    filters='<div class="filter-tabs" role="group" aria-label="Фильтр по работам">'+''.join(f'<button class="filter-tab" data-filter="{v}" aria-pressed="{str(v=="all").lower()}">{t}</button>' for v,t in [('all','Все работы'),('polish','Полировка'),('protection','Защита кузова'),('interior','Интерьер'),('styling','Стайлинг')])+'</div>'
    brandselect='<label class="brand-filter">Марка автомобиля<select id="brand-filter"><option value="all">Все марки</option>'+''.join(f'<option value="{e(b)}">{e(b)}</option>' for b in brands)+'</select></label>'
    title='Автомобили' if is_cars else 'Работы студии'
    content=intro('АВТОМОБИЛИ' if is_cars else 'АРХИВ ПРОЕКТОВ',title,'Выберите автомобиль или направление работ. В каждом проекте — фотографии и подробности.')+f'<section class="container section section-compact"><div class="gallery-controls">{brandselect}{filters}</div><p class="gallery-status" role="status" aria-live="polite"></p><div class="gallery-grid" id="gallery-grid">'+''.join(card(w) for w in works[:12])+'</div><div class="load-more-wrap"><button id="load-more" class="button button-outline">Показать ещё <span aria-hidden="true">↓</span></button></div></section>'+contacts_section()
    write(path,'Автомобили' if is_cars else 'Галерея работ',content,extra='<script src="/works.js" defer></script>')

# Work detail URLs remain unchanged; the images and text are the original studio content.
for w in works:
    p=BY_URL.get(w['url'],{})
    images=p.get('images',[])
    desc=clean(p.get('text',''))
    if not images: images=[w['thumbnail']]
    title=p.get('title',w['title'])
    first=images[0]
    photos=''.join(f'<button class="project-photo" data-photo="{asset(src)}" aria-label="Открыть фото {i+1}: {e(w["title"])}"><img src="{asset(src)}" alt="{e(w["title"])} — фото {i+1}" width="640" height="800" loading="{"eager" if i==0 else "lazy"}"></button>' for i,src in enumerate(images))
    write(w['url'],title,intro('ПРОЕКТ ANGEL DETAILING',e(title))+f'<section class="container project-layout"><div class="project-photos">{photos}</div><aside class="project-info"><div class="eyebrow">О ПРОЕКТЕ</div><div class="prose">{desc or "<p>Фотография из архива Angel Detailing.</p>"}</div><button class="button" data-book>Обсудить похожий проект {ARROW}</button><a class="text-link" href="/galereya/">Вернуться в галерею <span aria-hidden="true">→</span></a></aside></section>')

# Service category pages, preserving both direct and ?sl= addresses.
service_details={}

def related_services(category, current_slug, summaries):
    siblings=[(slug,item) for slug,item in DETAILS.items() if item['parent']==category['url'] and slug!=current_slug]
    if not siblings:
        return ''
    cards=[]
    for slug,item in siblings:
        summary=summaries.get(slug,'')
        text=f'<p>{e(summary)}</p>' if summary else ''
        cards.append(f'<a class="related-service-card" href="{e(item["query"])}"><div><h3>{e(item["title"])}</h3>{text}</div>{ARROW}</a>')
    return f'<section class="container related-services" aria-labelledby="related-services-title"><div class="related-services-heading"><h2 id="related-services-title">Другие услуги</h2><p>Также в направлении «{e(category["title"])}»</p></div><div class="related-services-grid">'+''.join(cards)+'</div></section>'

for s in CAT['services']:
    p=BY_URL[s['url']]
    soup=BeautifulSoup(p['html'],'html.parser')
    copy=clean(str(soup.select_one('.serv .content') or s['description']))
    summaries={}
    for item in soup.select('.servlist .elem'):
        link=item.select_one('.cont a')
        comment=item.select_one('.comment')
        if link:
            item_slug=parse_qs(urlsplit(link.get('href','')).query).get('sl',[''])[0]
            if item_slug and comment:
                summaries[item_slug]=comment.get_text(' ',strip=True)
    children=[]
    for slug,d in DETAILS.items():
        if d['parent']!=s['url']: continue
        src=BeautifulSoup(d.get('html',''),'html.parser')
        # The legacy sidebar contains counters and selection marks, not the service description.
        selected=src.select_one('.serv > .info > .content')
        if selected:
            for price in selected.select('.prc'): price.decompose()
            for link in selected.select('a[href]'):
                url=urlsplit(link['href'])
                if url.hostname in {'angeldetailing.ru','www.angeldetailing.ru'} and url.path.startswith('/uslugi/'):
                    link['href']=url.path+('?' + url.query if url.query else '')+('#' + url.fragment if url.fragment else '')
        description=clean(str(selected or ''))
        if not BeautifulSoup(description,'html.parser').get_text(strip=True):
            item=next((el for el in soup.select('.servlist .elem') if (el.select_one('a') and slug in el.select_one('a').get('href',''))),None)
            description=clean(str(item.select_one('.comment'))) if item else ''
        child_body=intro('УСЛУГИ / '+s['title'].upper(),e(d['title']))+f'<section class="container service-detail"><div class="service-detail-image"><img src="{asset(s["image"])}" width="1300" height="731" alt="{e(s["title"])}"></div><div><div class="prose">{description}</div><p class="muted">Объём работ и стоимость уточняются в студии.</p><button class="button" data-book>Обсудить услугу {ARROW}</button><a class="text-link" href="{s["url"]}">Все услуги направления {ARROW}</a></div></section>'+related_services(s,slug,summaries)
        write(d['url'],d['title'],child_body)
        service_details[slug]={'title':d['title'],'body':child_body}
        children.append(f'<a class="service-row" href="{d["query"]}"><h3>{e(d["title"])}</h3>{ARROW}</a>')
    body=intro('УСЛУГИ / ANGEL DETAILING',s['title'])+f'<section class="container service-detail"><div class="service-detail-image"><img src="{asset(s["image"])}" width="1300" height="731" alt="{s["title"]}"></div><div><div class="prose">{copy}</div><button class="button" data-book>Обсудить уход {ARROW}</button></div></section><section class="container section section-compact"><div class="eyebrow">ВЫБЕРИТЕ УСЛУГУ</div><div class="service-rows">'+''.join(children)+'</div></section>'+contacts_section()
    write(s['url'],s['title'],body,extra='<script src="/service-details.js" defer></script>')
(DIST/'service-details.js').write_text('window.ANGEL_SERVICES='+json.dumps(service_details,ensure_ascii=False).replace('</',r'<\/')+';',encoding='utf8')

review=intro('ЯНДЕКС КАРТЫ','Отзывы клиентов','Отзывы клиентов о работе Angel Detailing — напрямую с Яндекс Карт.')+f'''<section class="container reviews-layout"><div><div class="eyebrow">О СТУДИИ И РАБОТЕ</div><h2>После визита<br>в Angel.</h2><p class="muted">Посмотрите отзывы или расскажите о своём визите в студию.</p><a class="text-link" href="{MAP}?tab=reviews" target="_blank" rel="noopener">Открыть Яндекс Карты {ARROW}</a></div><div class="review-widget"><iframe title="Отзывы клиентов Angel Detailing на Яндекс Картах" src="https://yandex.ru/maps-reviews-widget/1087404926?comments" loading="lazy" width="750" height="800"></iframe></div></section>'''+contacts_section()
write('/otzyvy/','Отзывы клиентов',review)
searchitems=[{'title':s['title'],'url':s['url'],'type':'Услуга'} for s in CAT['services']]+[{'title':d['title'],'url':d['url'],'type':'Услуга'} for d in DETAILS.values()]+[{'title':w['title'],'url':w['url'],'type':'Проект','description':w['caption']} for w in works]
(DIST/'search-data.js').write_text('window.ANGEL_SEARCH='+json.dumps(searchitems,ensure_ascii=False).replace('</',r'<\/')+';',encoding='utf8')
write('/poisk','Поиск',intro('ANGEL DETAILING','Поиск по сайту','Услуги и автомобили из архива студии.')+'<section class="container search-section"><form id="site-search" action="/poisk" method="get" role="search"><label for="search-query">Услуга или автомобиль</label><div class="search-input-row"><input id="search-query" name="query" type="search" placeholder="Например, полировка или Porsche" required><button class="button" type="submit">Найти ↗</button></div></form><p id="search-status" role="status" aria-live="polite"></p><div id="search-results"></div></section>',extra='<script src="/search-data.js" defer></script>')
write('/kontakty','Контакты',intro('САНКТ-ПЕТЕРБУРГ','Контакты')+contacts_section()+'''<section class="container map-section"><iframe title="Angel Detailing — Выборгская набережная, 51" src="https://yandex.ru/map-widget/v1/?um=constructor%3A7040bfd4533273fd886fbb14055d8cf066042467641fc79fe10c475e38cbfac9&amp;source=constructor" loading="lazy" width="1200" height="460"></iframe></section>''')
policy=BY_URL.get('/politika',{})
s=BeautifulSoup(policy.get('html',''),'html.parser')
if s.h1:s.h1.decompose()
write('/politika','Политика конфиденциальности',intro('ДОКУМЕНТЫ','Политика конфиденциальности')+'<article class="container prose policy">'+clean(str(s))+'</article>')
write('/404.html','Страница не найдена',intro('404 / СТРАНИЦА НЕ НАЙДЕНА','Продолжим знакомство?')+'<div class="container error-actions"><a class="button" href="/">На главную ↗</a><a class="text-link" href="/galereya/">Посмотреть работы ↗</a></div>')
# Version shared assets so returning visitors receive the current styles and behavior.
asset_versions={name:hashlib.sha256((DIST/name).read_bytes()).hexdigest()[:12] for name in ('editorial.css','service-details.js','app.js')}
for page in DIST.rglob('*.html'):
    doc=page.read_text(encoding='utf8')
    for name,version in asset_versions.items():
        doc=doc.replace(f'"/{name}"',f'"/{name}?v={version}"')
    page.write_text(doc,encoding='utf8')
print('Built',len(list(DIST.rglob('*.html'))),'pages;',len(works),'projects;',len(DETAILS),'individual services')
