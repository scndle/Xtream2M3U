import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/get.php')
def proxy_m3u():
    host = request.args.get('host')
    username = request.args.get('username')
    password = request.args.get('password')
    output = request.args.get('output', 'ts')
    custom_ua = request.args.get('user_agent', 'IPTVSmartersPlayer')

    if not all([host, username, password]):
        return "Error: Missing 'host', 'username', or 'password' parameters.", 400

    host = host.rstrip('/')
    headers = {'User-Agent': custom_ua}
    
    # Header to force M3U file download
    download_headers = {'Content-Disposition': 'attachment; filename="playlist.m3u"'}

    direct_url = f"{host}/get.php?username={username}&password={password}&type=m3u_plus&output={output}"
    
    try:
        print(f"Attempting direct M3U download from {host} with UA: {custom_ua}...")
        res = requests.get(direct_url, headers=headers, timeout=15)
        
        if res.status_code == 200 and res.text.startswith("#EXTM3U"):
            print("Success: Direct M3U link is active and working.")
            return Response(res.text, mimetype='audio/x-mpegurl', headers=download_headers)
    except requests.RequestException as e:
        print(f"Direct M3U request failed or timed out: {e}")

    print("Direct M3U blocked or disabled. Falling back to Xtream API to rebuild M3U...")

    cat_url = f"{host}/player_api.php?username={username}&password={password}&action=get_live_categories"
    streams_url = f"{host}/player_api.php?username={username}&password={password}&action=get_live_streams"

    try:
        cat_res = requests.get(cat_url, headers=headers, timeout=15)
        stream_res = requests.get(streams_url, headers=headers, timeout=15)
        cat_res.raise_for_status()
        stream_res.raise_for_status()
    except requests.RequestException as e:
        return f"Fatal Error: Cannot connect to Provider API. {e}", 502

    try:
        categories_list = cat_res.json()
        categories = {str(c.get('category_id')): c.get('category_name', 'Unknown') for c in categories_list}
    except Exception:
        categories = {}

    try:
        streams_list = stream_res.json()
    except Exception:
        return "API Error: Unreadable stream data from provider.", 502

    m3u_lines = ["#EXTM3U"]
    for s in streams_list:
        name = str(s.get('name', 'Unknown')).replace('"', '')
        stream_id = s.get('stream_id')
        icon = s.get('stream_icon', '')
        epg_id = s.get('epg_channel_id', '')
        cat_id = str(s.get('category_id', ''))
        cat_name = str(categories.get(cat_id, 'Uncategorized')).replace('"', '')
        
        stream_url = f"{host}/{username}/{password}/{stream_id}.{output}"
        
        extinf = f'#EXTINF:-1 tvg-id="{epg_id}" tvg-name="{name}" tvg-logo="{icon}" group-title="{cat_name}",{name}'
        m3u_lines.append(extinf)
        m3u_lines.append(stream_url)

    print("Success: M3U playlist rebuilt from API.")
    return Response("\n".join(m3u_lines), mimetype='audio/x-mpegurl', headers=download_headers)

@app.route('/xmltv.php')
def proxy_epg():
    host = request.args.get('host')
    username = request.args.get('username')
    password = request.args.get('password')
    custom_ua = request.args.get('user_agent', 'IPTVSmartersPlayer')

    if not all([host, username, password]):
        return "Error: Missing 'host', 'username', or 'password' parameters.", 400

    host = host.rstrip('/')
    headers = {'User-Agent': custom_ua}
    epg_url = f"{host}/xmltv.php?username={username}&password={password}"

    # Header to force XML file download
    download_headers = {'Content-Disposition': 'attachment; filename="epg.xml"'}

    try:
        print(f"Proxying XMLTV EPG from {host}...")
        req = requests.get(epg_url, headers=headers, stream=True, timeout=30)
        req.raise_for_status()
        
        return Response(
            req.iter_content(chunk_size=1024 * 1024), 
            mimetype='text/xml',
            headers=download_headers
        )
    except requests.RequestException as e:
        return f"Error fetching EPG: {e}", 502

# The "if __name__ == '__main__':" block is not strictly necessary with Gunicorn, 
# but useful for local testing without Docker if needed.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)