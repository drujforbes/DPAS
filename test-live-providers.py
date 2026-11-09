#!/usr/bin/env python3
"""Opt-in live provider contract checks. No keys stored or printed.

Run: TMDB_TOKEN=... FANART_API_KEY=... python3 test-live-providers.py
Exit 2 when no credentials supplied; exit 1 on real integration failure.
"""
import json, os, sys, urllib.request, urllib.error


def fetch_json(url, headers=None, timeout=18):
    request = urllib.request.Request(url, headers={**(headers or {}), 'User-Agent':'DPAS-integration-check/1.0', 'Accept':'application/json'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f'HTTP {response.status}')
        return json.load(response)


def check_tmdb(token, fetch=fetch_json):
    headers={'Authorization':f'Bearer {token}'}
    configuration=fetch('https://api.themoviedb.org/3/configuration',headers)
    assert isinstance(configuration.get('images',{}).get('secure_base_url'),str), 'TMDB image configuration missing'
    result=fetch('https://api.themoviedb.org/3/movie/550?append_to_response=images',headers)
    assert result.get('id')==550 and isinstance(result.get('production_companies'),list), 'TMDB movie contract mismatch'
    assert isinstance(result.get('images',{}).get('posters'),list), 'TMDB posters missing'
    print('PASS: live TMDB configuration, movie metadata, company list, artwork gallery')


def check_fanart(key, fetch=fetch_json):
    from urllib.parse import urlencode
    result=fetch('https://webservice.fanart.tv/v3/movies/550?'+urlencode({'api_key':key}))
    assert isinstance(result,dict), 'Fanart response is not a JSON object'
    assert result.get('name') or result.get('imdb_id') or any(k in result for k in ('movieposter','moviebackground','hdmovieclearart')), 'Fanart artwork contract mismatch'
    print('PASS: live Fanart.tv movie artwork response')


def main():
    token=os.getenv('TMDB_TOKEN','').strip()
    key=os.getenv('FANART_API_KEY','').strip()
    if not token and not key:
        print('SKIP: set TMDB_TOKEN and/or FANART_API_KEY to run live provider checks (no credentials saved).')
        return 2
    failed=False
    for label, credential, fn in [('TMDB',token,check_tmdb),('Fanart.tv',key,check_fanart)]:
        if not credential:
            print(f'SKIP: {label} credential not provided')
            continue
        try: fn(credential)
        except Exception as e:
            # Never print secrets or raw URLs containing credentials.
            print(f'FAIL: {label} live provider contract: {type(e).__name__} (check credentials, provider availability and API schema)',file=sys.stderr)
            failed=True
    return int(failed)

if __name__=='__main__':sys.exit(main())
