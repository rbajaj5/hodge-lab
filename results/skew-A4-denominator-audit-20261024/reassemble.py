from pathlib import Path, PurePosixPath
import hashlib,json,zipfile
b=Path(__file__).resolve().parent
files={x['name']:Path(x['path']) for x in json.loads((b/'downloads.json').read_text(encoding='utf-8'))}
lines=files['PARTS.sha256'].read_text(encoding='utf-8').splitlines()
assert len(lines)==11
pins={}
for line in lines:
    digest,name=line.split()
    assert PurePosixPath(name).parent.as_posix()=='parts'
    pins[PurePosixPath(name).name]=digest
names=['A4-denominator.zip.part'+str(i).zfill(3) for i in range(1,12)]
assert set(pins)==set(names)
records=[]; chunks=[]
for n in names:
    raw=files[n].read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    assert digest==pins[n],n
    records.append({'file':n,'sha256':digest,'bytes':len(raw)})
    chunks.append(raw)
raw=b''.join(chunks); h=hashlib.sha256(raw).hexdigest()
assert len(raw)==20142445 and h=='8abdf70cb3861435a6b284e57cefdfac0a9f8f58db82cf0ec7d018aa86a843a9'
out=b/'A4-denominator-reassembled.zip';out.write_bytes(raw)
review=hashlib.sha256(files['A4-review.zip'].read_bytes()).hexdigest()
assert review=='11f7f87a73b9ca11c847a4098511527e78fb69b92df8b6422482ee41d05d19b8'
receipt={'status':'PASS','archive_sha256':h,'archive_bytes':len(raw),'parts':records,
 'download_failures':0,'review_sha256':review,
 'coordinator_repair':'Initial inline reassembler expected bare part names and rejected the manifest parts/ prefix before writing output; a premature extraction then found no archive. This script validates the explicit parts/ directory and maps to observed download basenames. No payload or mathematical computation changed.'}
(b/'transfer-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(h);print(zipfile.ZipFile(out).namelist()[:7])
