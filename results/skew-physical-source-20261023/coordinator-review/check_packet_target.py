"""Compare exact mathematical record fields, allowing rendering metadata changes."""
from pathlib import Path
import argparse
import hashlib
import json
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--protected', type=Path, required=True)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError('Output already exists')
    blobs = [p.read_bytes() for p in [args.protected, args.packet]]
    hashes = [hashlib.sha256(b).hexdigest() for b in blobs]
    if hashes != ['c6621c8845addf857ed30726f86449d5ea3310c7609641db9e326f9b85f10fbd',
                  'fc7e070e4f459a521e3515c3b0d7e85fe4a557e345839f9cdb324491c289063f']:
        raise RuntimeError('Input pins differ')
    def fields(blob):
        text = blob.decode('utf-8', errors='strict')
        answer = {}
        for key in ['id', 'q', 'F', 'A']:
            match = re.search(r'^'+key+r':([^\n]*)(?:\n( +[^\n]*))*', text, re.M)
            if match is None:
                raise RuntimeError('Missing field: '+key)
            answer[key] = ''.join(match.group(0).split())[len(key)+1:]
        return answer
    protected, packet = [fields(b) for b in blobs]
    if protected != packet:
        raise RuntimeError('Mathematical fields differ')
    result = {'status':'PASS', 'executor':'Codex coordinator; exact field comparison',
              'protected_commit':'b790130d43b49ec0ddc6865d0bdc949eeeee2319',
              'protected_sha256':hashes[0], 'packet_sha256':hashes[1],
              'equal_fields':protected,
              'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limits':'Whitespace-normalized text equality of id,q,F,A; no new polynomial, geometric, or Lean computation. Different rendering metadata is excluded intentionally.'}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
