import {loadGallery,renderWall,createViewer,validateVisibility} from './gallery.js';
const wall=document.querySelector('#wall'),status=document.querySelector('#status');
try{
  const {manifest,hidden:published}=await loadGallery();
  let hidden=published;
  if(new URLSearchParams(location.search).has('preview')){
    const draft=sessionStorage.getItem('ccphotowall-preview');
    if(!draft)throw new Error('預覽已過期，請返回管理頁重新開啟');
    hidden=validateVisibility(JSON.parse(draft));
    const notice=document.createElement('p');notice.className='status';notice.textContent='目前為草稿預覽，尚未發布。';document.body.prepend(notice);
  }
  const count=renderWall(wall,manifest,hidden,createViewer(document.querySelector('#viewer')));
  status.textContent=count?'':'目前沒有顯示的照片。';
}catch(error){wall.setAttribute('aria-busy','false');status.textContent=error.message;}
