from pathlib import Path
s=(Path(__file__).parent/'PASMacApp.swift').read_text()
section=s.split('// Validate actual generated image bytes before returning them to the editor.',1)[1].split('self.replyImage(id,base64:b64)',1)[0]
checks={
    'Encoded output bound': 'b64.utf8.count <= 33_000_000' in section,
    'Decoded output bound': 'decoded.count <= 24_000_000' in section,
    'PNG signature': 'decoded.starts(with: [137,80,78,71,13,10,26,10])' in section,
    'PNG IHDR': 'Array(decoded[12..<16]) == [73,72,68,82]' in section,
    'Actual image decode': 'NSBitmapImageRep(data: decoded)' in section,
    'Pixel dimension limit': 'resultImage.pixelsWide <= 8192' in section and 'resultImage.pixelsHigh <= 8192' in section,
    'Pixel count limit': '<= 40_000_000' in section,
    'Validation before reply': 'self.reply(id,ok:false' in section,
}
for k,v in checks.items():print(('PASS' if v else 'FAIL')+': '+k)
assert all(checks.values())
