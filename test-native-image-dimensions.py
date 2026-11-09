from pathlib import Path
s=(Path(__file__).parent/'PASMacApp.swift').read_text()
checks={'PNG IHDR': 'Array(data[12..<16]) == [73,72,68,82]' in s,'PNG decode':'NSBitmapImageRep(data: data)' in s,'pixel limit':'<= 40_000_000' in s,'dimension limit':'bitmap.pixelsWide <= 8192, bitmap.pixelsHigh <= 8192' in s,'before API':s.index('NSBitmapImageRep(data: data)')<s.index('let boundary =')}
for k,v in checks.items(): print(('PASS' if v else 'FAIL')+': '+k)
assert all(checks.values())
