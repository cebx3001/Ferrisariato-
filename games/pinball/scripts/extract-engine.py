"""Reproduce the Box2D core extraction from the preserved original source."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lines=(root/'upstream/PinballGame.js').read_text().splitlines()
assert lines[3]=='// box2d-plugin-full.js.js', 'Unexpected original source layout'
source=lines[4]
end=source.index('Phaser.')
core=source[:end].rstrip(',')+';\n'
header='// Box2D core extracted verbatim from lrusso/Pinball, fcf63f97d24467248fe1eaa89adaf273209f3da2. See upstream/ and THIRD_PARTY.md.\n'
(root/'vendor/box2d.js').write_text(header+core)
print('Box2D core extracted:',len(core),'characters')
