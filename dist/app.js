/* Angel Detailing: progressive enhancements, no framework or external runtime. */
(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const menuButton = $('.menu-toggle');
  const menu = $('#mobile-menu');
  const closeMenu = () => { menu.hidden = true; menuButton.setAttribute('aria-expanded','false'); menuButton.setAttribute('aria-label','Открыть меню'); document.body.classList.remove('menu-open'); };
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menu.hidden = !open;
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
    document.body.classList.toggle('menu-open',open);
    if(open) $('a',menu).focus();
  });
  $$('a',menu).forEach(a => a.addEventListener('click',closeMenu));
  document.addEventListener('keydown',event => {
    if (event.key === 'Escape' && !menu.hidden) {closeMenu();menuButton.focus();}
    if (event.key === 'Tab' && !menu.hidden) {
      const items = [menuButton,...$$('a,button',menu)];
      const first=items[0], last=items.at(-1);
      if(event.shiftKey && document.activeElement===first){event.preventDefault();last.focus();}
      if(!event.shiftKey && document.activeElement===last){event.preventDefault();first.focus();}
    }
  });
  matchMedia('(min-width:1051px)').addEventListener('change',e => {if(e.matches)closeMenu();});

  // Query URLs used by the original service catalogue are preserved.
  const selected = new URLSearchParams(location.search).get('sl');
  if (selected && window.ANGEL_SERVICES?.[selected]) {
    const service=window.ANGEL_SERVICES[selected];
    $('#main').innerHTML=service.body;
    document.title=service.title+' — Angel Detailing';
  }
  const booking = $('#booking');
  let previousFocus;
  document.addEventListener('click', event => {
    const trigger=event.target.closest('[data-book]');
    if(!trigger)return;
    previousFocus=menu.contains(trigger)?menuButton:trigger;
    closeMenu();
    booking.showModal();
    document.body.classList.add('modal-open');
  });
  $$('dialog').forEach(dialog => {
    $('[data-close]',dialog).addEventListener('click',() => dialog.close());
    dialog.addEventListener('click',event => {
      if(event.target!==dialog)return;
      const r=dialog.getBoundingClientRect();
      if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();
    });
    dialog.addEventListener('close',() => {
      document.body.classList.remove('modal-open');
      if(previousFocus?.isConnected)previousFocus.focus();
    });
  });
  const form=$('#booking-form');
  const phone=form.elements.cb_phone;
  form.addEventListener('input',()=>{
    $('.form-status',form).textContent='';
    $('.booking-options',form).hidden=true;
    $('[data-email-draft]',form).href='mailto:info@angeldetailing.ru';
  });
  if(form.dataset.connected==='true' && form.dataset.endpoint){
    $('.booking-details summary').textContent='Оставить заявку';
    $('[type=submit]',form).childNodes[0].textContent='Отправить заявку ';
    $('.form-note',form).textContent='После отправки студия свяжется с вами и подтвердит детали записи.';
  }
  phone.addEventListener('input',()=>phone.setCustomValidity(''));
  form.addEventListener('submit',async event => {
    event.preventDefault();
    const digits=phone.value.replace(/\D/g,'');
    if(digits.length<10||digits.length>15){
      const message='Укажите телефон: от 10 до 15 цифр.';
      phone.setCustomValidity(message);
      $('.form-status',form).textContent=message;
      phone.reportValidity();
      return;
    }
    const status=$('.form-status',form);
    // No endpoint was present in the supplied project. Never claim a booking was sent.
    // To integrate: set data-connected="true" and data-endpoint to a same-origin backend.
    const endpoint=form.dataset.endpoint;
    if(form.dataset.connected==='true' && endpoint && new URL(endpoint,location.origin).origin===location.origin){
      const submit=$('[type=submit]',form); submit.disabled=true;
      status.textContent='Отправляем заявку…';
      try{
        const response=await fetch(endpoint,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});
        const result=await response.json();
        if(!response.ok||result.success!==true)throw new Error('Not confirmed');
        status.textContent='Заявка отправлена. Менеджер свяжется с вами.';
        form.reset();
      }catch{
        status.textContent='Не удалось подтвердить отправку. Пожалуйста, позвоните или напишите в Telegram.';
        $('.booking-options',form).hidden=false;
      }finally{submit.disabled=false;}
      return;
    }
    const subject='Запрос на запись в Angel Detailing';
    const body=`Здравствуйте! Хочу обсудить запись в студию.\n\nИмя: ${form.elements.cb_name.value.trim()}\nТелефон: ${phone.value.trim()}\nАвтомобиль и пожелания: ${form.elements.cb_comment.value.trim()}`;
    $('[data-email-draft]',form).href=`mailto:info@angeldetailing.ru?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    status.textContent='Письмо подготовлено, но ещё не отправлено. Откройте его в почтовом приложении и отправьте в студию.';
    $('.booking-options',form).hidden=false;
  });

  const preview=$('.service-preview');
  if(preview){
    const front=$('.preview-front',preview), back=$('.preview-back',preview);
    let requested=front.getAttribute('src');
    let requestId=0;
    const showPreview=async link=>{
      if(!matchMedia('(min-width:761px)').matches)return;
      const src=link.dataset.preview;
      if(src===requested)return;
      requested=src;const id=++requestId;
      const photo=new Image();photo.src=src;
      try{await photo.decode();}catch{return;}
      if(id!==requestId)return;
      // Load before swapping, so rapid pointer movement never leaves a blank frame.
      preview.classList.remove('is-swapping');
      back.src=src;
      $('.preview-caption-text',preview).textContent=link.dataset.caption;
      $$('.service-index-link').forEach(item=>item.classList.toggle('is-active',item===link));
      if(reduced.matches){front.src=src;return;}
      requestAnimationFrame(()=>preview.classList.add('is-swapping'));
    };
    back.addEventListener('transitionend',event=>{
      if(event.propertyName==='opacity' && preview.classList.contains('is-swapping')){
        front.src=back.getAttribute('src');
        preview.classList.remove('is-swapping');
      }
    });
    $$('.service-index-link').forEach((link,index)=>{
      if(index===0)link.classList.add('is-active');
      link.addEventListener('pointerenter',()=>showPreview(link));
      link.addEventListener('focus',()=>showPreview(link));
    });
  }

  if($('#gallery-grid') && window.ANGEL_WORKS){
    const works=window.ANGEL_WORKS;
    const grid=$('#gallery-grid');
    const select=$('#brand-filter');
    const more=$('#load-more');
    const status=$('.gallery-status');
    let filter=new URLSearchParams(location.search).get('filter')||'all';
    if(!$$('[data-filter]').some(b=>b.dataset.filter===filter))filter='all';
    let brand='all',limit=12;
    const key=s=>s.toLowerCase().replace(/[^a-z0-9а-яё]/g,'');
    const mark=new URLSearchParams(location.search).get('mark');
    if(mark)brand=[...select.options].find(o=>key(o.value)===key(mark))?.value||'all';
    select.value=brand;
    const render=()=>{
      const found=works.filter(w=>(filter==='all'||w.categories.includes(filter))&&(brand==='all'||w.brand===brand));
      grid.innerHTML=found.slice(0,limit).map(w=>`<a class="work-card" href="${escape(w.url)}"><div class="work-image"><img src="${escape(w.image)}" width="640" height="800" alt="${escape(w.title)} в Angel Detailing" loading="lazy"><span class="image-arrow" aria-hidden="true">↗</span></div><div class="work-meta"><h3>${escape(w.title)}</h3><span aria-hidden="true">↗</span></div><p>${escape(w.caption)}</p></a>`).join('');
      status.textContent=found.length?`Показано ${Math.min(limit,found.length)} из ${found.length} проектов`:'По этому сочетанию фильтров работ пока нет. Выберите другую марку или услугу.';
      more.hidden=limit>=found.length;
      $$('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===filter)));
    };
    const saveQuery=()=>{
      const url=new URL(location.href);
      if(brand==='all')url.searchParams.delete('mark');else url.searchParams.set('mark',brand.toLowerCase().replace(/ /g,'_'));
      if(filter==='all')url.searchParams.delete('filter');else url.searchParams.set('filter',filter);
      history.replaceState(null,'',url);
    };
    select.addEventListener('change',()=>{brand=select.value;limit=12;saveQuery();render();});
    $$('[data-filter]').forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;limit=12;saveQuery();render();}));
    more.addEventListener('click',()=>{
      const firstNew=limit;limit+=12;render();
      const next=grid.children[firstNew];if(next)next.focus({preventScroll:true});
    });
    render();
  }

  if($('#site-search') && window.ANGEL_SEARCH){
    const search=$('#site-search'),input=$('#search-query');
    const render=()=>{
      const query=input.value.trim().toLocaleLowerCase('ru');
      if(!query){$('#search-status').textContent='Введите название услуги, марку или модель автомобиля.';$('#search-results').innerHTML='';return;}
      const terms=query.split(/\s+/);
      const found=window.ANGEL_SEARCH.filter(x=>terms.every(term=>(x.title+' '+(x.description||'')).toLocaleLowerCase('ru').includes(term)));
      $('#search-status').textContent=found.length?`Найдено: ${found.length}`:'Ничего не найдено. Попробуйте другую формулировку.';
      $('#search-results').innerHTML=found.map(x=>`<a class="search-result" href="${escape(x.url)}"><span class="label">${escape(x.type)}</span><h3>${escape(x.title)}</h3><span aria-hidden="true">↗</span></a>`).join('');
    };
    input.value=new URLSearchParams(location.search).get('query')||'';
    search.addEventListener('submit',event=>{event.preventDefault();const url=new URL(location.href);url.searchParams.set('query',input.value.trim());history.replaceState(null,'',url);render();});
    render();
  }
  const photos=$$('[data-photo]');
  if(photos.length){
    const lightbox=$('#lightbox');
    let index=0;
    const show=i=>{
      index=(i+photos.length)%photos.length;
      $('img',lightbox).src=photos[index].dataset.photo;
      $('img',lightbox).alt=$('img',photos[index]).alt;
      $('.lightbox-count',lightbox).textContent=`${index+1} / ${photos.length}`;
    };
    photos.forEach((p,i)=>p.addEventListener('click',()=>{index=i;previousFocus=p;show(i);lightbox.showModal();document.body.classList.add('modal-open');}));
    $('.lightbox-prev').addEventListener('click',()=>show(index-1));
    $('.lightbox-next').addEventListener('click',()=>show(index+1));
    lightbox.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')show(index-1);if(e.key==='ArrowRight')show(index+1);});
    let touchX;
    lightbox.addEventListener('touchstart',e=>{touchX=e.changedTouches[0].clientX;},{passive:true});
    lightbox.addEventListener('touchend',e=>{if(touchX==null)return;const distance=e.changedTouches[0].clientX-touchX;if(Math.abs(distance)>45)show(index+(distance<0?1:-1));touchX=null;},{passive:true});
  }

  // Content remains visible if scripts or IntersectionObserver are unavailable.
  if('IntersectionObserver'in window && !reduced.matches){
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.remove('reveal-pending');observer.unobserve(entry.target);}}),{threshold:.08});
    $$('.studio-grid,.section-heading,.services-grid,.featured-works,.trust-grid,.contact-grid,.editorial-heading,.selected-projects,.service-index,.studio-heading,.studio-story,.reviews-editorial').forEach(el=>{
      if(el.getBoundingClientRect().top>innerHeight){el.classList.add('reveal-ready','reveal-pending');observer.observe(el);}
    });
    reduced.addEventListener('change',e=>{if(e.matches){$$('.reveal-pending').forEach(el=>el.classList.remove('reveal-pending'));observer.disconnect();}});
  }
})();
