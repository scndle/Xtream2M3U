# Xtream2M3U Proxy

A lightweight, Dockerized Python proxy that automatically converts Xtream Codes API JSON endpoints into standard M3U playlists, and safely proxies XMLTV (EPG) files.

## ⚠️ The Problem
Many IPTV providers disable or block the standard M3U download endpoint (`get.php?type=m3u_plus`) and XMLTV endpoint to prevent users from using tools like **Threadfin**, **Emby**, **Plex**, or **xTeVe**. Instead, they force users to use modern apps that rely on their JSON API (`player_api.php`).

## 💡 The Solution
This proxy sits between your local media server (Emby/Threadfin) and your IPTV provider. 
1. It first attempts to fetch the standard M3U playlist or XMLTV file while spoofing a legitimate IPTV player.
2. If the provider blocks the M3U request (e.g., Error 884, 403, 401), the proxy seamlessly falls back to the Xtream JSON API.
3. It downloads the categories and streams, rebuilds a perfectly formatted M3U playlist on the fly, and serves it to your media server.
4. It streams the XMLTV file in chunks to prevent memory overload on your local server.

## 🚀 Installation (Docker Compose)

1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/Xtream2M3U.git](https://github.com/YOUR_USERNAME/Xtream2M3U.git)
   cd Xtream2M3U
   ```
2. Start the container:
   ```bash
   docker compose up -d --build
   ```
The proxy will now be running on port `5050`.

## ⚙️ Usage (M3U Playlist)

Instead of giving your IPTV provider's URL to Threadfin/Emby, you provide your local proxy URL with your provider's details passed as parameters.

**Format:**
`http://<YOUR_LOCAL_IP>:5050/get.php?host=<PROVIDER_URL>&username=<USER>&password=<PASS>&output=ts`

**Example:**
`http://192.168.1.201:5050/get.php?host=http://provider.url&username=myuser&password=mypass&output=ts`

## 📅 Usage (XMLTV / EPG Guide)

To proxy the TV Guide through the same system:

**Format:**
`http://<YOUR_LOCAL_IP>:5050/xmltv.php?host=<PROVIDER_URL>&username=<USER>&password=<PASS>`

**Example:**
`http://192.168.1.201:5050/xmltv.php?host=http://provider.url&username=myuser&password=mypass`

## 🛡️ Advanced Features

### Custom User-Agent Spoofing
By default, the proxy disguises itself as `IPTVSmartersPlayer` to bypass basic firewall rules. You can override this by appending the `&user_agent=` parameter to your URLs.

**Example with VLC:**
`http://192.168.1.201:5050/get.php?host=http://provider.url&username=myuser&password=mypass&user_agent=VLC/3.0.12`

**Example with HotPlayer:**
`http://192.168.1.201:5050/get.php?host=http://provider.url&username=myuser&password=mypass&user_agent=HotPlayer`