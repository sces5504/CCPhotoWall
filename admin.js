import {loadGallery,validateVisibility} from './gallery.js';
const $=selector=>document.querySelector(selector);
const status=$('#admin-status'),grid=$('#admin-grid');
let manifest,published,hidden,filter='all',query='',selected=new Set(),loaded=false,lastDraft='';
const draftKey='ccphotowall-admin-draft-v1';
const serialize=set=>JSON.stringify({version:1,hidden:[...set].sort()});
function notify(message){status.textContent=message;}
function currentPhotos(){return manifest.photos.filter(photo=>(filter==='all'||(filter==='hidden'?hidden.has(photo.id):!hidden.has(photo.id)))&&photo.filename.toLocaleLowerCase().includes(query));}
function updateCounts(){
  const hiddenCount=manifest.photos.filter(photo=>hidden.has(photo.id)).length;
  $('#all-count').textContent=manifest.photos.length;$('#hidden-count').textContent=hiddenCount;$('#visible-count').textContent=manifest.photos.length-hiddenCount;
  $('#selection-count').textContent=`已選 ${selected.size} 張`;
  for(const id of ['hide','restore','clear'])$(`#${id}`).disabled=!selected.size;
  $('#reset').disabled=serialize(hidden)===serialize(published);
}
function render(){
  const fragment=document.createDocumentFragment();
  const photos=currentPhotos();
  for(const photo of photos){
    const label=document.createElement('label');label.className=`admin-photo${hidden.has(photo.id)?' is-hidden':''}${selected.has(photo.id)?' selected':''}`;label.dataset.photoId=photo.id;
    const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.checked=selected.has(photo.id);checkbox.setAttribute('aria-label',`選取 ${photo.filename}`);
    checkbox.addEventListener('change',()=>{if(checkbox.checked)selected.add(photo.id);else selected.delete(photo.id);label.classList.toggle('selected',checkbox.checked);updateCounts();});
    const img=document.createElement('img');img.src=photo.src;img.alt='';img.loading='lazy';img.decoding='async';
    const filename=document.createElement('span');filename.className='filename';filename.textContent=photo.filename;filename.title=photo.filename;
    label.append(checkbox,img,filename);
    if(hidden.has(photo.id)){const badge=document.createElement('span');badge.className='badge';badge.textContent='已隱藏';label.append(badge);}
    fragment.append(label);
  }
  grid.replaceChildren(fragment);grid.setAttribute('aria-busy','false');$('#empty').hidden=!!photos.length;$('#select-all').disabled=!photos.length;updateCounts();
}
function persist(){
  lastDraft=serialize(hidden);
  try{localStorage.setItem(draftKey,JSON.stringify({base:serialize(published),visibility:JSON.parse(lastDraft)}));}catch{/* Draft still works when storage is unavailable. */}
}
function changeSelection(hide){
  for(const id of selected){if(hide)hidden.add(id);else hidden.delete(id);}
  const count=selected.size;selected.clear();persist();render();notify(`已${hide?'隱藏':'恢復'} ${count} 張照片。這是草稿，下載並上傳名單後才會發布。`);
}
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{if(!loaded)return;filter=button.dataset.filter;selected.clear();document.querySelectorAll('[data-filter]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));render();}));
$('#search').addEventListener('input',()=>{if(!loaded)return;query=$('#search').value.trim().toLocaleLowerCase();selected.clear();render();});
$('#select-all').addEventListener('click',()=>{currentPhotos().forEach(photo=>selected.add(photo.id));render();});
$('#clear').addEventListener('click',()=>{selected.clear();render();});
$('#hide').addEventListener('click',()=>changeSelection(true));$('#restore').addEventListener('click',()=>changeSelection(false));
$('#reset').addEventListener('click',()=>{hidden=new Set(published);selected.clear();persist();render();notify('已還原為網站目前發布的名單。');});
$('#download').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(JSON.parse(serialize(hidden)),null,2)+'\n'],{type:'application/json'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='visibility.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),10000);notify('已下載 visibility.json。請按「上傳名單」，提交到 GitHub 後才會對外生效。');});
$('#preview').addEventListener('click',()=>{try{sessionStorage.setItem('ccphotowall-preview',serialize(hidden));window.open('./?preview=1','_blank');}catch{notify('瀏覽器無法儲存預覽，請允許此網站的儲存功能後再試。');}});
$('#import').addEventListener('change',async event=>{const file=event.target.files[0];if(!file||!loaded)return;try{const imported=validateVisibility(JSON.parse(await file.text()));hidden=imported;selected.clear();persist();render();notify('已匯入名單草稿。請先預覽，再下載並上傳發布。');}catch(error){notify(`匯入失敗：${error.message}，原本的名單已保留。`);}event.target.value='';});
try{
  const data=await loadGallery();manifest=data.manifest;published=data.hidden;hidden=new Set(published);
  let restored=false,stale=false;
  try{const stored=JSON.parse(localStorage.getItem(draftKey)||'null');if(stored){if(stored.base===serialize(published)){hidden=validateVisibility(stored.visibility);restored=serialize(hidden)!==serialize(published);}else stale=true;}}catch{/* Ignore malformed local drafts, use published settings. */}
  loaded=true;lastDraft=serialize(hidden);render();
  for(const id of ['preview','download'])$(`#${id}`).disabled=false;
  notify(restored?'已恢復這台裝置尚未發布的草稿。':stale?'已載入最新發布名單；舊草稿已過期。':`已載入 ${manifest.photos.length.toLocaleString()} 張照片。勾選照片即可批次隱藏或恢復。`);
}catch(error){grid.setAttribute('aria-busy','false');notify(error.message);}
