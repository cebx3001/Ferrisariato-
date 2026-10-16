"""Build original seven-segment outlines. Optional authoring tool: fontTools.
The generated TTF ships locally; the game needs no font service or Python.
"""
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
root=Path(__file__).resolve().parents[1]
segments={
 'a':[(120,760),(480,760),(520,720),(480,680),(120,680),(80,720)],
 'g':[(120,420),(480,420),(520,380),(480,340),(120,340),(80,380)],
 'd':[(120,80),(480,80),(520,40),(480,0),(120,0),(80,40)],
 'b':[(520,680),(560,640),(560,460),(520,420),(480,460),(480,640)],
 'c':[(520,340),(560,300),(560,120),(520,80),(480,120),(480,300)],
 'e':[(80,340),(120,300),(120,120),(80,80),(40,120),(40,300)],
 'f':[(80,680),(120,640),(120,460),(80,420),(40,460),(40,640)],
}
digits=['abcdef','bc','abged','abgcd','fgbc','afgcd','afgecd','abc','abcdefg','abfgcd']
order=['.notdef','space','period','colon','hyphen']+[f'digit{i}' for i in range(10)]
glyphs={};metrics={}
def glyph(name,polys,width):
 pen=TTGlyphPen(None)
 for poly in polys:
  pts=[(int(x+y*.045),y) for x,y in poly]
  pen.moveTo(pts[0])
  for point in pts[1:]:pen.lineTo(point)
  pen.closePath()
 glyphs[name]=pen.glyph();metrics[name]=(width,0)
def dot(x,y):return [(x,y),(x+68,y),(x+68,y+68),(x,y+68)]
glyph('.notdef',[[(40,0),(40,760),(100,760),(100,0)],[(460,0),(460,760),(520,760),(520,0)]],680)
glyph('space',[],300);glyph('period',[dot(45,0)],220);glyph('colon',[dot(80,180),dot(80,530)],280);glyph('hyphen',[segments['g']],680)
for i,parts in enumerate(digits):glyph(f'digit{i}',[segments[s] for s in parts],680)
fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(order)
fb.setupCharacterMap({32:'space',46:'period',58:'colon',45:'hyphen',**{48+i:f'digit{i}' for i in range(10)}})
fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=820,descent=-180)
fb.setupNameTable({'familyName':'Pinball Segment','styleName':'Regular','uniqueFontIdentifier':'PinballSegment-1.0','fullName':'Pinball Segment Regular','psName':'PinballSegment-Regular','version':'Version 1.0'})
fb.setupOS2(sTypoAscender=820,sTypoDescender=-180,usWinAscent=820,usWinDescent=180)
fb.setupPost();fb.setupMaxp();fb.save(root/'assets/pinball-segment.ttf')
print('Local segment display font generated')
