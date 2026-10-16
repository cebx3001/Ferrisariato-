"""Make a labeled contact sheet from untouched reference and Cycles crops."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
root=Path(__file__).resolve().parents[1]
hero=Image.open(root/'docs/premium-hero.png').convert('RGB')
regions=[
 ('1-43912.jpg',(100,425,520,695),'Ensamblaje: flippers, slingshots y tanques'),
 ('2-43910.jpg',(50,260,240,620),'Lateral izquierdo: herramientas y microescenas'),
 ('3-43909.jpg',(65,25,260,355),'Rampa izquierda: soportes, canal y grupos inferiores'),
 ('4-43907.jpg',(145,15,480,225),'Casa: terraza, jardín, marcos y targets'),
 ('5-43908.jpg',(65,10,370,285),'Canal posterior conectado detrás de la casa'),
]
font=ImageFont.truetype('DejaVuSans.ttf',23);small=ImageFont.truetype('DejaVuSans.ttf',17)
out=Image.new('RGB',(1240,3020),'#061526');d=ImageDraw.Draw(out)
d.text((22,12),'REFERENCIAS DE DETALLE  /  ESCENA ACTUAL',font=font,fill='#ffda4d')
scale=hero.width/660
for i,(name,box,label) in enumerate(regions):
 y=65+i*585;d.text((22,y),label,font=font,fill='white')
 reference=Image.open(root/'docs/references'/name).convert('RGB')
 crop=hero.crop(tuple(round(v*scale) for v in box))
 for x,img in [(22,reference),(632,crop)]:
  panel=ImageOps.pad(img,(586,510),color='#0a2036',method=Image.Resampling.LANCZOS);out.paste(panel,(x,y+38))
 d.text((22,y+551),'Referencia proporcionada',font=small,fill='#b6c8db');d.text((632,y+551),'Recorte del render Cycles · cámara conservada',font=small,fill='#b6c8db')
out.save(root/'docs/premium-detail-comparison.jpg',quality=94)
print('DETAIL_COMPARISON_SAVED')
