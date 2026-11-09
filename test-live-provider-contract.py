"""Offline contract tests of live-provider probe, with stubbed network replies."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('provider_probe',Path(__file__).parent/'test-live-providers.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def tmdb(url,headers):
    assert headers['Authorization']=='Bearer example-token'
    if url.endswith('/configuration'):return {'images':{'secure_base_url':'https://image.tmdb.org/t/p/'}}
    assert '/movie/550?' in url
    return {'id':550,'production_companies':[],'images':{'posters':[]}}
mod.check_tmdb('example-token',tmdb)

def fanart(url):
    assert url.startswith('https://webservice.fanart.tv/v3/movies/550?')
    assert 'api_key=example-key' in url
    return {'name':'Fight Club','movieposter':[]}
mod.check_fanart('example-key',fanart)
try:
    mod.check_tmdb('example-token',lambda url,headers:{'id':550})
except AssertionError: pass
else:raise AssertionError('Missing artwork fields must fail')
print('PASS: offline provider integration contracts and missing-gallery detection')
