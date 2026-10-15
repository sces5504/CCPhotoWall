export function validateVisibility(value){
  if(value?.version!==1||!Array.isArray(value.hidden)||value.hidden.some(id=>typeof id!=='string'||!id.trim()))throw new Error('隱藏名單格式不正確');
  return new Set(value.hidden);
}
export async function loadGallery(){
  const responses=await Promise.all(['data/photos.json','data/visibility.json'].map(url=>fetch(url,{cache:'no-cache'})));
  if(responses.some(response=>!response.ok))throw new Error('照片資料載入失敗，請稍後重新整理');
  const [manifest,visibility]=await Promise.all(responses.map(response=>response.json()));
  if(!Array.isArray(manifest.photos)||!Array.isArray(manifest.rows))throw new Error('照片清單格式不正確');
  return {manifest,hidden:validateVisibility(visibility)};
}
export function visibleRows(rows,hidden){
  // Keep the reference's row capacities, shifting visible photos into vacated places.
  const visible=rows.flat().filter(id=>!hidden.has(id));
  let offset=0;
  return rows.map(row=>{const filled=visible.slice(offset,offset+row.length);offset+=row.length;return filled;}).filter(row=>row.length);
}
export function renderWall(wall,manifest,hidden,onOpen){
  const photos=new Map(manifest.photos.map(photo=>[photo.id,photo]));
  const rows=visibleRows(manifest.rows,hidden);
  const displayed=rows.flat().map(id=>photos.get(id)).filter(Boolean);
  let index=0;
  const fragment=document.createDocumentFragment();
  for(const row of rows){
    const section=document.createElement('div');section.className='photo-row';
    for(const id of row){
      const photo=photos.get(id);if(!photo)continue;
      const position=index++;
      const button=document.createElement('button');button.type='button';button.className='photo';button.dataset.photoId=id;
      button.setAttribute('aria-label',`檢視第 ${position+1} 張照片`);
      const img=document.createElement('img');img.src=photo.src;img.alt='';img.loading=position<9?'eager':'lazy';img.decoding='async';img.width=photo.width||480;img.height=photo.height||480;
      img.addEventListener('error',()=>button.classList.add('failed'),{once:true});
      button.append(img);button.addEventListener('click',()=>onOpen(displayed,position));section.append(button);
    }
    fragment.append(section);
  }
  wall.replaceChildren(fragment);wall.setAttribute('aria-busy','false');
  return displayed.length;
}
export function createViewer(dialog){
  const image=dialog.querySelector('img'),counter=dialog.querySelector('figcaption');
  const prev=dialog.querySelector('.viewer-prev'),next=dialog.querySelector('.viewer-next');
  let photos=[],position=0,previousFocus;
  function show(index){position=Math.max(0,Math.min(index,photos.length-1));const photo=photos[position];image.onerror=photo.large?()=>{image.onerror=null;image.src=photo.src;}:null;image.src=photo.large||photo.src;image.alt=`第 ${position+1} 張照片`;counter.textContent=`${position+1} / ${photos.length}`;prev.disabled=position===0;next.disabled=position===photos.length-1;}
  prev.addEventListener('click',()=>show(position-1));next.addEventListener('click',()=>show(position+1));
  dialog.querySelector('.viewer-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('keydown',event=>{if(event.key==='ArrowLeft'){event.preventDefault();show(position-1);}if(event.key==='ArrowRight'){event.preventDefault();show(position+1);}});
  dialog.addEventListener('close',()=>{document.body.style.overflow='';image.removeAttribute('src');previousFocus?.focus({preventScroll:true});});
  return (list,index)=>{if(!list.length)return;photos=list;previousFocus=document.activeElement;show(index);document.body.style.overflow='hidden';dialog.showModal();};
}
