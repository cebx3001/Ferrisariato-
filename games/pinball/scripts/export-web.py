"""Convert Blender's full-resolution layers to local web assets."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
for name in ['table','interactives','foreground','glass','ball']:
    path=root/'assets'/name
    with Image.open(path.with_suffix('.png')) as image:
        image.save(path.with_suffix('.webp'),quality=92,method=6)
    print(name, path.with_suffix('.webp').stat().st_size, 'bytes')
