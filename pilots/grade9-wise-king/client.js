// Public IDs only. Roster and credentials must never be placed here.
const config = {clientId:'', endpoint:'', assessment:'grade9-wise-king'};
const status=document.querySelector('[role=status]');
const buttons=[...document.querySelectorAll('button')];
const loginButton=buttons[0], playButton=buttons[1];
const form=document.querySelector('form');
const counter=playButton.previousElementSibling;
let credential='', playing=false, pendingRequest=null, closesAt=0, offset=0;
const audio=new Audio();
audio.preload='none';
function message(s){status.textContent=s;}
async function api(action,requestId) {
 const response=await fetch(config.endpoint,{
  method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+credential},
  body:JSON.stringify({action,assessment:config.assessment,requestId})
 });
 const data=await response.json();
 if(!response.ok) throw new Error(data.error || 'ACCESS_DENIED');
 return data;
}
function applyState(data){
 closesAt=Date.parse(data.closesAt);
 if(data.serverTime) offset=Date.parse(data.serverTime)-Date.now();
 counter.textContent='المحاولات المتبقية: '+data.remaining;
 playButton.disabled=playing || data.remaining<=0 ||
  Date.parse(data.activeUntil)>Date.now()+offset || Date.now()+offset>=closesAt;
}
async function refresh(){
 if(!credential) return;
 try{applyState(await api('status'));}
 catch{playButton.disabled=true;audio.pause();message('التقييم غير متاح الآن أو انتهت صلاحية الدخول.');}
}
if(config.clientId && config.endpoint.startsWith('https://')){
 form.hidden=true;
 loginButton.remove();
 const slot=document.createElement('div');
 document.querySelector('#instructions').parentElement.append(slot);
 const script=document.createElement('script');
 script.src='https://accounts.google.com/gsi/client';
 script.onload=()=>{
  google.accounts.id.initialize({client_id:config.clientId,hd:'ikns.edu.bh',
   callback:async result=>{
    credential=result.credential;
    try{
     const state=await api('status');applyState(state);form.hidden=false;
     message('تم التحقق من الحساب والقائمة والموعد. لا يزال تسليم الإجابات غير مفعّل في هذه التجربة.');
    }catch{credential='';form.hidden=true;playButton.disabled=true;
     message('الدخول غير متاح: تحقق من الحساب وموعد التقييم مع المعلم.');}
   }});
  google.accounts.id.renderButton(slot,{theme:'outline',size:'large',text:'signin_with',locale:'ar'});
 };
 script.onerror=()=>message('تعذّر تحميل تسجيل الدخول. أبلغ المعلم.');
 document.head.append(script);
 setInterval(refresh,15000);
}
playButton.addEventListener('click',async()=>{
 if(!credential || playing) return;
 playButton.disabled=true;
 pendingRequest ||= crypto.randomUUID();
 try{
  const state=await api('start',pendingRequest);
  audio.src=state.audioUrl;
  playing=true;applyState(state);
  await audio.play();
  pendingRequest=null;
  message('جارٍ الاستماع. تُحتسب هذه الجلسة ضمن المحاولات الثلاث.');
 }catch{
  playing=false;
  message('تعذّر بدء الصوت. أبلغ المعلم؛ قد تكون المحاولة حُجزت بالفعل.');
  await refresh();
 }
});
audio.addEventListener('ended',()=>{playing=false;refresh();});
audio.addEventListener('error',()=>{
 playing=false;message('حدث عطل في الصوت. أبلغ المعلم.');refresh();
});
