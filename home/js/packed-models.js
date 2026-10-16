const cache = new Map();
export async function resolvePackedModel(product) {
 if(!product.pack)return product.local;
 const key=product.pack.name;
 if(cache.has(key))return cache.get(key);
 const promise=(async()=>{
  if(typeof DecompressionStream==='undefined')throw new Error('Este navegador no soporta descompresión de modelos. Usa Chrome o Safari reciente.');
  const {name,parts}=product.pack;
  const texts=await Promise.all(Array.from({length:parts},(_,i)=>fetch('./assets/models/packed/'+name+'.'+String(i).padStart(3,'0')+'.b64').then(r=>{if(!r.ok)throw Error('Fragmento no disponible: '+name+' '+i);return r.text();})));
  const base64=texts.join('').replace(/\\s+/g,'');
  const compressed=Uint8Array.from(atob(base64),c=>c.charCodeAt(0));
  const decompressed=await new Response(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'))).blob();
  return URL.createObjectURL(new Blob([decompressed],{type:'model/gltf-binary'}));
 })();
 cache.set(key,promise);
 try{return await promise;}catch(e){cache.delete(key);throw e;}
}
