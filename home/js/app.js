import {PRODUCTS} from './products.js';
const $=s=>document.getElementById(s), storeKey='ferrisariato-home-saved-v1';
let viewer=null,engineReady=false,selected=PRODUCTS[0],saved=new Set(),mode='studio',modelPlaced=true,moving=false,rotation=0,scale=1;let toastTimer=0;
try{saved=new Set(JSON.parse(localStorage.getItem(storeKey)||'[]').filter(id=>PRODUCTS.some(p=>p.id===id)));}catch{}

// Three original furniture models share the current PlayCanvas and WebAR viewer.
const MOCKUP=PRODUCTS.every(p=>!p.modelReady);
function updateConcept(){
 const root=$('viewer'),photo=$('concept-photo');
 root.classList.toggle('is-concept',!selected.modelReady);
 if(!selected.modelReady){
  photo.src=selected.thumb;photo.alt=selected.name;photo.onerror=()=>{photo.onerror=null;photo.src=selected.previewThumb||'./assets/img/terraza-referencia.jpg';};
  $('concept-title').textContent=selected.name;
  $('concept-category').textContent='FERRISARIATO / '+selected.category;
  $('concept-description').textContent=selected.description;
  $('concept-source').href=selected.source;
  $('mode-label').textContent='REFERENCIA VISUAL';
  hint('REFERENCIA FOTOGRÁFICA · PRÓXIMAMENTE EN AR');
 }else{
  $('mode-label').textContent='MODELO 3D ORIGINAL';
  hint('DESLIZA PARA GIRAR · PELLIZCA PARA CAMBIAR TAMAÑO');
  $('active-product-title').textContent=selected.name;
  $('active-product-desc').textContent=selected.description;
  $('active-product-gesture').textContent='1 DEDO: GIRAR · PELLIZCA: CAMBIAR TAMAÑO';
 }
 $('active-product-copy').hidden=!selected.modelReady;
 $('mode-ar').innerHTML=selected.modelReady?'VER EN AR <span>↗</span>':'AR PRÓXIMAMENTE <span>↗</span>';
}

const hint=value=>{const el=document.getElementById('gesture-hint');if(el)el.textContent=value;};
const setMessage=(message,error=false)=>{const elem=$('guidance');elem.innerHTML=`<b>${error?'ATENCIÓN':'VISUALIZA EN TU ESPACIO'}</b><span>${message.replaceAll('<','&lt;').replaceAll('>','&gt;')}</span>`;if(error){$('mobile-status').textContent=message;$('mobile-status').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('mobile-status').hidden=true,4600);}};

function renderARSurface(state){
 const target=$('floor-target'),marker=target?.querySelector('.target-ring span'),label=$('floor-target-label');
 if(!target)return;
 const scanning=state==='searching',found=state==='ready';
 target.classList.toggle('visible',scanning||found);
 target.classList.toggle('detected',found);
 if(marker)marker.textContent=found?'✓':'+';
 if(label)label.textContent=found?'PISO DETECTADO · PULSA COLOCAR':scanning?'MUEVE EL TELÉFONO HACIA EL SUELO':'';
 if(state==='ready')setMessage('Piso detectado. Pulsa COLOCAR EN TU ESPACIO.');
 else if(scanning)setMessage('Mueve lentamente el teléfono apuntando al suelo. Espera el círculo amarillo o la marca de confirmación.');
 else if(state==='placed')setMessage('Mueble colocado. Gíralo o utiliza CAMBIAR POSICIÓN para volver a colocarlo.');
}

function renderProducts(){
 $('products').innerHTML=PRODUCTS.map((p,i)=>`<button type="button" data-product="${p.id}" class="product-card ${selected.id===p.id?'selected':''}" aria-pressed="${selected.id===p.id}"><img src="${p.thumb}" alt="${p.name}" onerror="this.onerror=null;this.src='${p.previewThumb||'./assets/img/terraza-referencia.jpg'}'"/><span class="product-desc"><small>0${i+1} / ${p.category}</small><strong>${p.name}</strong><span class="meta">${p.short}</span></span><span class="card-arrow">↗</span></button>`).join('');
 $('selected-thumb').src=selected.thumb;$('selected-thumb').onerror=()=>{$('selected-thumb').onerror=null;$('selected-thumb').src=selected.previewThumb||'./assets/img/terraza-referencia.jpg';};$('selected-title').textContent=selected.name;$('selected-dim').textContent=selected.dimensions?selected.dimensions[0].toFixed(2)+' × '+selected.dimensions[2].toFixed(2)+' m':'VISTA DE REFERENCIA · MODELO 3D PENDIENTE';updateSaved();
}
function updateSaved(){$('fav').textContent=saved.has(selected.id)?'♥':'♡';$('fav').classList.toggle('saved',saved.has(selected.id));$('save-count').textContent=String(saved.size).padStart(2,'0');}
function persistSaved(){try{localStorage.setItem(storeKey,JSON.stringify([...saved]));}catch{}}
function select(product){selected=product;updateConcept();rotation=0;scale=1;modelPlaced=false;moving=false;$('rot').value=0;$('scale').value=100;$('rot-val').textContent='0°';$('scale-val').textContent='100%';$('move-btn').classList.remove('active');$('place-btn').innerHTML=!selected.modelReady?'VER PRODUCTO ORIGINAL <b>↗</b>':mode==='ar'?'COLOCAR EN TU ESPACIO <b>↗</b>':'COLOCAR EN ESCENA <b>↗</b>';renderProducts();if(!product.modelReady){viewer?.clear();setMessage(product.description);return;}if(engineReady){$('load-message').hidden=false;$('load-text').textContent='CARGANDO MODELO 3D';viewer.select(product).finally(()=>{$('load-message').hidden=true;});}else{setMessage('Se está preparando el visor 3D. Los productos ya están disponibles en el catálogo.');}}
function setMode(next){if(next==='ar'){if(!selected.modelReady){setMessage('Referencia fotográfica: el modelo tridimensional todavía no se ha incorporado al demo.',true);return;}if(!engineReady){setMessage('El motor WebAR aún no está disponible. Comprueba la conexión a internet.',true);return;}if(!viewer.xr8Available && !viewer.arAvailable){setMessage('Este dispositivo no tiene AR compatible. Continúa en vista 3D.',true);return;}mode='ar';hint('APUNTA AL SUELO · ESPERA EL CÍRCULO · PULSA COLOCAR');document.getElementById('shell').classList.add('ar-active');setMessage('Mueve lentamente la cámara apuntando al suelo. Un círculo amarillo indicará dónde puedes colocar el mueble.');$('mode-ar').classList.add('current');$('mode-studio').classList.remove('current');$('mode-label').textContent='REALIDAD AUMENTADA';$('place-btn').innerHTML='COLOCAR EN TU ESPACIO <b>↗</b>';modelPlaced=false;
 // Synchronous call in user gesture, required by WebXR.
 if(viewer.preferredTracking==='native')viewer.startXR();else viewer.startXR8();return;}
 if(mode==='ar')viewer?.endXR();hint('DESLIZA PARA GIRAR · PELLIZCA PARA CAMBIAR TAMAÑO');mode='studio';renderARSurface('off');$('shell').classList.remove('ar-active');$('mode-studio').classList.add('current');$('mode-ar').classList.remove('current');$('mode-label').textContent='PREVISUALIZACIÓN 3D';$('place-btn').innerHTML='COLOCAR EN ESCENA <b>↗</b>';modelPlaced=true;viewer?.resize();}
function init(){renderProducts();$('products').addEventListener('click',e=>{let b=e.target.closest('button[data-product]');if(b){let p=PRODUCTS.find(x=>x.id===b.dataset.product);if(p)select(p);}});
 $('fav').addEventListener('click',()=>{saved.has(selected.id)?saved.delete(selected.id):saved.add(selected.id);persistSaved();updateSaved();setMessage(saved.has(selected.id)?'Producto guardado en este dispositivo.':'Producto quitado de guardados.');});
 $('saved-btn').addEventListener('click',()=>{if(!saved.size){setMessage('No hay productos guardados. Usa el corazón de cada producto.');return;}let item=PRODUCTS.find(p=>saved.has(p.id));if(item)select(item);setMessage('Se ha abierto el primer producto guardado.');});
 $('mode-ar').addEventListener('click',()=>setMode('ar'));$('mode-studio').addEventListener('click',()=>setMode('studio'));
 $('place-btn').addEventListener('click',()=>{if(!selected.modelReady){window.open(selected.thumb,'_blank','noopener,noreferrer');return;}if(!viewer){setMessage('Espera a que esté disponible el visor 3D.',true);return;}if(!viewer.item){select(selected);return;}if(viewer.hasPlaced){viewer.resetPlacement();$('place-btn').innerHTML=mode==='ar'?'COLOCAR EN TU ESPACIO <b>↗</b>':'COLOCAR EN ESCENA <b>↗</b>';return;}if(viewer.place()){modelPlaced=true;moving=false;$('move-btn').classList.remove('active');$('place-btn').innerHTML=mode==='ar'?'CAMBIAR POSICIÓN <b>↗</b>':'COLOCADO · MOVER <b>↗</b>';hint('1 DEDO: GIRAR · PELLIZCA: CAMBIAR TAMAÑO');$('active-product-gesture').textContent='DESLIZA: GIRAR · PELLIZCA: ESCALA · CAMBIAR POSICIÓN: REUBICAR';setMessage('Desliza con un dedo para girar el mueble. Pellizca con dos dedos para ajustar su tamaño. Para trasladarlo, pulsa CAMBIAR POSICIÓN.');}else{setMessage('Apunta con la cámara al suelo hasta que aparezca el indicador.',true);}});
 $('move-btn').addEventListener('click',()=>{if(!viewer)return;if(mode==='ar'){viewer.resetPlacement();modelPlaced=false;$('place-btn').innerHTML='COLOCAR EN TU ESPACIO <b>↗</b>';setMessage('Busca otra zona del suelo y pulsa COLOCAR.');return;}moving=!moving;viewer.moving=moving;$('move-btn').classList.toggle('active',moving);setMessage(moving?'Arrastra sobre la escena para desplazar el producto.':'Arrastra sobre la escena para girar la cámara.');});
 function setRotation(n){rotation=Math.max(-180,Math.min(180,n));$('rot').value=rotation;$('rot-val').textContent=rotation+'°';viewer?.setRotation(rotation);}
 $('rotate-left').addEventListener('click',()=>setRotation(Math.max(-180,rotation-15)));$('rotate-right').addEventListener('click',()=>setRotation(Math.min(180,rotation+15)));$('rot').addEventListener('input',e=>setRotation(+e.target.value));
 function setScale(n){scale=Math.max(50,Math.min(150,n));$('scale').value=scale;$('scale-val').textContent=scale+'%';viewer?.setScale(scale/100);} $('scale').addEventListener('input',e=>setScale(+e.target.value));$('scale-reset').addEventListener('click',()=>setScale(100));
 $('delete-btn').addEventListener('click',()=>{viewer?.clear();modelPlaced=false;$('place-btn').innerHTML='VOLVER A COLOCAR <b>↗</b>';setMessage('Producto eliminado del espacio. Elige otro o vuelve a seleccionar este producto.');});
 $('guide-btn').addEventListener('click',()=>{$('modal').hidden=false;});$('modal-close').addEventListener('click',()=>{$('modal').hidden=true;});$('modal-ok').addEventListener('click',()=>{$('modal').hidden=true;});$('modal').addEventListener('click',e=>{if(e.target===$('modal'))$('modal').hidden=true;});window.addEventListener('keydown',e=>{if(e.key==='Escape')$('modal').hidden=true;});
 updateConcept();if(!MOCKUP)loadEngine();}
async function loadEngine(){try{setMessage('Inicializando escena tridimensional con PlayCanvas…');const {FerrisARViewer}=await import('./scene.js');viewer=new FerrisARViewer($('render-canvas'),{onStatus:(msg,err)=>setMessage(msg,err),onSurface:state=>renderARSurface(state),onTracking:started=>{mode=started?'ar':'studio';document.getElementById('shell').classList.toggle('ar-active',started);$('mode-ar').classList.toggle('current',started);$('mode-studio').classList.toggle('current',!started);$('mode-label').textContent=started?'REALIDAD AUMENTADA':'PREVISUALIZACIÓN 3D';$('place-btn').innerHTML=started?'COLOCAR EN TU ESPACIO <b>↗</b>':'COLOCAR EN ESCENA <b>↗</b>';viewer.resize();},onXRStop:()=>setMode('studio')});engineReady=true;import('./mobile-gestures.js').then(({attachMobileGestures})=>attachMobileGestures(viewer,$('gesture-layer'),{onTransform:({rotation,scale})=>{ $('rot').value=rotation; $('rot-val').textContent=Math.round(rotation)+'°'; $('scale').value=Math.round(scale*100); $('scale-val').textContent=Math.round(scale*100)+'%'; }})).catch(console.warn);$('load-message').hidden=false;$('load-text').textContent='CARGANDO MODELO';await viewer.select(selected);$('load-message').hidden=true;setMessage('Modelo listo. Arrastra para explorar la escena o inicia AR en un móvil compatible.');const support=await viewer.checkAR();$('mode-ar').title=viewer.preferredTracking==='native'?'Android: ARCore mediante WebXR':viewer.preferredTracking==='xr8'?'8th Wall: iPhone o fallback Android':'Necesita un teléfono compatible';}catch(error){engineReady=false;console.error(error);$('load-message').hidden=true;setMessage('El motor 3D necesita conexión al CDN de PlayCanvas. Los modelos GLB locales están incluidos en el proyecto.',true);}}
init();
