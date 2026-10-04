from flask import Flask, jsonify, render_template_string, request
import scrapetube
import random
import urllib.request
import json

app = Flask(__name__)

search_cache = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Valora Tube</title>
    
    <!-- PWA Manifest & Meta -->
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0f0f0f">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Valora Tube">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
        
        :root {
            --bg-gradient: linear-gradient(-45deg, #0f0f0f, #181111, #0f0f0f, #111818);
            --bg-color: #0f0f0f;
            --text-color: #f1f1f1;
            --sub-text: #aaa;
            --surface-color: rgba(15,15,15,0.95);
            --card-bg: #272727;
            --border-color: rgba(255,255,255,0.1);
            --accent-color: #ff334b;
        }
        [data-theme="light"] {
            --bg-gradient: linear-gradient(-45deg, #f9f9f9, #ffffff, #f1f1f1, #ffffff);
            --bg-color: #f9f9f9;
            --text-color: #0f0f0f;
            --sub-text: #606060;
            --surface-color: rgba(255,255,255,0.95);
            --card-bg: #e5e5e5;
            --border-color: rgba(0,0,0,0.1);
        }

        @keyframes bgGradientMove {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        body { 
            background: var(--bg-gradient); 
            background-size: 400% 400%; 
            animation: bgGradientMove 15s ease infinite;
            color: var(--text-color); 
            overflow-x: hidden; 
            min-height: 100vh;
            transition: background 0.3s, color 0.3s;
        }
        
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: rgba(128,128,128,0.3); border-radius: 4px; }
        a { text-decoration: none; color: inherit; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeIn 0.4s ease-out forwards; }

        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        .skeleton {
            background: var(--card-bg);
            background-image: linear-gradient(90deg, var(--card-bg) 0px, #444 40px, var(--card-bg) 80px);
            background-size: 1000px 100%;
            animation: shimmer 2s infinite linear;
        }

        #toast {
            position: fixed; bottom: 70px; left: 50%; transform: translateX(-50%) translateY(100px);
            background: #333; color: #fff; padding: 10px 20px; border-radius: 20px; font-size: 14px;
            z-index: 99999; transition: transform 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            pointer-events: none;
        }
        #toast.show { transform: translateX(-50%) translateY(0); }

        #header { position: fixed; top: 0; left: 0; right: 0; height: 56px; background: var(--surface-color); backdrop-filter: blur(10px); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 100; border-bottom: 1px solid var(--border-color); }
        .header-left { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        
        /* Logo YouTube Original style + Valora Tube text */
        .yt-logo-box { display: flex; align-items: center; background: #ff0000; width: 32px; height: 22px; border-radius: 5px; justify-content: center; position: relative; flex-shrink: 0; }
        .yt-logo-box::after { content: ""; position: absolute; width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 9px solid #fff; left: 12px; }
        .valora-brand-text { font-size: 18px; font-weight: 700; letter-spacing: -0.5px; color: var(--text-color); font-family: 'Roboto', sans-serif; }
        .valora-brand-text span { color: var(--accent-color); }
        
        .header-right { display: flex; align-items: center; gap: 4px; }
        .header-icon { background: transparent; border: none; color: var(--text-color); display: flex; align-items: center; justify-content: center; cursor: pointer; width: 40px; height: 40px; border-radius: 50%; }
        
        .search-active-header { display: none; align-items: center; width: 100%; height: 56px; gap: 8px; position: fixed; top: 0; left: 0; background: var(--surface-color); z-index: 105; padding: 0 12px; }
        .search-active-header.active { display: flex; }
        .search-bar-box { flex: 1; display: flex; align-items: center; background: var(--card-bg); border-radius: 20px; padding: 0 16px; height: 38px; justify-content: space-between; cursor: pointer; }
        .search-bar-text { font-size: 15px; color: var(--text-color); overflow: hidden; white-space: nowrap; text-overflow: ellipsis; flex: 1; }

        .search-form-mobile { display: none; position: fixed; inset: 0; background: var(--bg-color); padding: 0 12px; flex-direction: column; z-index: 110; }
        .search-form-mobile.active { display: flex; }
        .search-top-bar { display: flex; align-items: center; height: 56px; gap: 8px; width: 100%; flex-shrink: 0; }
        .search-input-wrap-mob { flex: 1; display: flex; align-items: center; background: var(--card-bg); border-radius: 20px; padding: 0 16px; height: 38px; }
        .search-input-wrap-mob input { flex: 1; background: transparent; border: none; color: var(--text-color); font-size: 15px; outline: none; }
        .search-suggestions-list { flex: 1; overflow-y: auto; width: 100%; background: var(--bg-color); padding-top: 4px; }
        .suggestion-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; color: var(--text-color); font-size: 15px; cursor: pointer; }
        .suggestion-item:active { background: rgba(128,128,128,0.2); }
        .suggestion-left { display: flex; align-items: center; gap: 16px; flex: 1; }
        .suggestion-left .material-icons-outlined { color: var(--sub-text); font-size: 20px; }

        .chips-wrapper { position: sticky; top: 56px; background: var(--surface-color); backdrop-filter: blur(10px); z-index: 10; padding: 12px 16px; display: flex; gap: 12px; align-items: center; border-bottom: 1px solid var(--border-color); }
        .explore-icon { background: var(--card-bg); padding: 6px; border-radius: 4px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-color); }
        .chips-bar { display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; }
        .chip { padding: 6px 14px; border-radius: 8px; font-size: 14px; font-weight: 500; white-space: nowrap; border: none; background: var(--card-bg); color: var(--text-color); cursor: pointer; transition: 0.2s; display: flex; align-items: center; gap: 4px; }
        .chip.active { background: var(--text-color); color: var(--bg-color); }

        #main { margin-top: 56px; padding-bottom: 70px; min-height: 100vh; }
        .video-grid { display: flex; flex-direction: column; gap: 0; }
        .vid-card { cursor: pointer; display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
        .thumb-wrap { position: relative; width: 100%; aspect-ratio: 16/9; background: var(--card-bg); }
        .thumb-img { width: 100%; height: 100%; object-fit: cover; }
        .duration-badge { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: #fff; font-size: 12px; font-weight: 500; padding: 3px 6px; border-radius: 4px; }
        .vid-info { display: flex; gap: 12px; align-items: flex-start; padding: 0 16px; }
        .channel-avatar { width: 36px; height: 36px; border-radius: 50%; background: #444; flex-shrink: 0; overflow: hidden; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:bold; }
        .channel-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .vid-text { flex: 1; }
        .vid-title { font-size: 15px; font-weight: 500; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; color: var(--text-color); }
        .vid-meta { font-size: 13px; color: var(--sub-text); }

        .shorts-container { display: flex; flex-direction: column; gap: 24px; padding: 16px; align-items: center; }
        .short-card { width: 100%; max-width: 360px; aspect-ratio: 9/16; background: #000; border-radius: 16px; position: relative; overflow: hidden; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .short-card iframe { width: 100%; height: 100%; border: none; pointer-events: none; }
        .short-overlay { position: absolute; bottom: 16px; left: 16px; right: 16px; color: #fff; z-index: 2; pointer-events: none; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }

        #player-section { display: none; margin-top: 0; padding-bottom: 70px; min-height: 100vh; background: var(--bg-color); z-index: 200; position: absolute; top: 0; left: 0; width: 100%; }
        
        /* Pemutar stabil, posisinya sticky di atas dan tidak berubah jadi mini player saat scroll */
        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; position: sticky; top: 56px; z-index: 105; transition: all 0.3s ease; cursor: pointer; }
        .player-container iframe { width: 100%; height: 100%; border: none; pointer-events: auto; }
        
        /* Overlay Kontrol Pemutar */
        .player-overlay-ui {
            position: absolute; inset: 0; background: rgba(0,0,0,0.4);
            display: flex; flex-direction: column; justify-content: space-between;
            padding: 12px; opacity: 0; transition: opacity 0.2s ease; z-index: 106; pointer-events: none;
        }
        .player-container:hover .player-overlay-ui, .player-overlay-ui.active { opacity: 1; pointer-events: auto; }
        
        .overlay-top { display: flex; justify-content: space-between; align-items: center; }
        .overlay-top-left { display: flex; gap: 12px; align-items: center; }
        .overlay-top-right { display: flex; gap: 16px; align-items: center; }
        .overlay-top .material-icons { color: #fff; font-size: 24px; cursor: pointer; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }

        .overlay-center { display: flex; justify-content: center; align-items: center; gap: 32px; }
        .overlay-center .material-icons { color: #fff; font-size: 42px; cursor: pointer; text-shadow: 0 2px 6px rgba(0,0,0,0.8); }

        .overlay-bottom { display: flex; flex-direction: column; gap: 4px; }
        .overlay-timeline-bar { width: 100%; height: 3px; background: rgba(255,255,255,0.4); border-radius: 2px; position: relative; cursor: pointer; }
        .overlay-timeline-progress { width: 35%; height: 100%; background: var(--accent-color); border-radius: 2px; position: relative; }
        .overlay-timeline-progress::after { content: ""; position: absolute; right: -4px; top: -3px; width: 9px; height: 9px; background: #fff; border-radius: 50%; }
        .overlay-time-info { display: flex; justify-content: space-between; font-size: 11px; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }

        .css-fullscreen { position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; max-width: none !important; aspect-ratio: auto !important; z-index: 999999 !important; border-radius: 0 !important; background: #000; display: flex; align-items: center; justify-content: center; }

        .player-meta { padding: 12px 16px; background: var(--surface-color); backdrop-filter: blur(5px); }
        .player-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; line-height: 1.3; color: var(--text-color); }
        .player-views-date { font-size: 13px; color: var(--sub-text); margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
        
        .action-row { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 16px; scrollbar-width: none; border-bottom: 1px solid var(--border-color); margin-bottom: 16px; }
        .action-pill { display: flex; align-items: center; gap: 6px; background: var(--card-bg); padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; color: var(--text-color); }
        .action-pill .material-icons-outlined { font-size: 18px; }
        
        .channel-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
        .channel-info { display: flex; align-items: center; gap: 10px; }
        .channel-name { font-weight: 500; font-size: 15px; color: var(--text-color); }
        .channel-subs { font-size: 12px; color: var(--sub-text); }
        .btn-subscribe { background: var(--text-color); color: var(--bg-color); font-weight: 500; border: none; padding: 8px 16px; border-radius: 20px; font-size: 14px; cursor: pointer; transition: opacity 0.2s; }
        .btn-subscribe.subscribed { background: var(--card-bg); color: var(--text-color); }
        
        .comments-box { background: var(--card-bg); border-radius: 12px; padding: 12px 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 500; color: var(--text-color); cursor: pointer; }

        #bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; height: 50px; background: var(--surface-color); backdrop-filter: blur(10px); z-index: 100; display: flex; justify-content: space-around; align-items: center; border-top: 1px solid var(--border-color); }
        .nav-item { display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-color); flex: 1; height: 100%; cursor: pointer; opacity: 0.7; }
        .nav-item.active { opacity: 1; color: var(--text-color); }
        .nav-item.active .material-icons-outlined { display: none; }
        .nav-item:not(.active) .material-icons { display: none; }
        .nav-item .material-icons, .nav-item .material-icons-outlined { font-size: 24px; }
        .nav-item .nav-label { font-size: 10px; margin-top: 3px; }
        .nav-avatar { width: 24px; height: 24px; border-radius: 50%; background: var(--accent-color); display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; border: 2px solid transparent; color: #fff; }
        .nav-item.active .nav-avatar { border-color: var(--text-color); }

        #sheet-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 9999; opacity: 0; transition: opacity 0.3s; }
        #sheet-overlay.show { display: block; opacity: 1; }
        #settings-sheet { display: flex; flex-direction: column; position: fixed; bottom: -100%; left: 0; right: 0; background: var(--bg-color); border-top: 1px solid var(--border-color); border-radius: 16px 16px 0 0; z-index: 10000; transition: bottom 0.3s cubic-bezier(0.4, 0, 0.2, 1); padding-bottom: 24px; max-height: 80vh; overflow-y: auto; color: var(--text-color); }
        #settings-sheet.show { bottom: 0; }
        .sheet-handle { width: 40px; height: 4px; background: var(--sub-text); border-radius: 2px; margin: 12px auto 8px; }
        .setting-item { display: flex; align-items: center; gap: 16px; padding: 14px 24px; color: var(--text-color); font-size: 15px; cursor: pointer; transition: background 0.2s; }
        .setting-item:hover { background: rgba(128,128,128,0.1); }
        .setting-item .material-icons-outlined { font-size: 24px; color: var(--text-color); }
        
        #scroll-loader { display: none; justify-content: center; padding: 20px 0; }
        .spinner { width: 30px; height: 30px; border: 3px solid var(--card-bg); border-top-color: var(--text-color); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* ===== CSS DESKTOP RESPONSIF ===== */
        @media (min-width: 1024px) {
            body { padding-left: 72px; }
            #bottom-nav { 
                top: 56px; bottom: auto; left: 0; right: auto; width: 72px; height: calc(100vh - 56px); 
                flex-direction: column; justify-content: flex-start; padding-top: 12px; gap: 16px; border-top: none; border-right: 1px solid var(--border-color); 
            }
            .nav-item { flex: unset; width: 100%; height: 72px; }
            .nav-item .nav-label { font-size: 11px; }

            #main { padding: 24px 32px 70px 32px; max-width: 1600px; margin-left: auto; margin-right: auto; }
            .video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px 16px; }
            .vid-card { margin-bottom: 0; }
            .thumb-wrap { border-radius: 12px; overflow: hidden; }
            .vid-info { padding: 8px 0 0 0; }

            #player-section { 
                padding: 24px 40px; display: none; position: relative; max-width: 1700px; margin-left: 72px; 
            }
            .player-container { 
                width: calc(100% - 420px) !important; aspect-ratio: 16/9; position: relative !important; top: 0 !important; border-radius: 12px; overflow: hidden; float: left; 
            }
            .player-meta { 
                width: calc(100% - 420px) !important; float: left; background: transparent; padding: 16px 0; 
            }
            #player-section #related-grid { 
                width: 380px !important; float: right; display: flex !important; flex-direction: column !important; gap: 12px; 
            }
            #player-section #related-grid .vid-card { 
                flex-direction: row !important; gap: 10px; margin-bottom: 8px; 
            }
            #player-section #related-grid .thumb-wrap { 
                width: 168px !important; flex-shrink: 0; aspect-ratio: 16/9; border-radius: 8px; 
            }
            #player-section #related-grid .channel-avatar { display: none; }
            #player-section #related-grid .vid-title { font-size: 14px; font-weight: 500; }
            #player-section #related-grid .vid-meta { font-size: 12px; }
        }
    </style>
</head>
<body>

<div id="toast">Pesan notifikasi</div>
<audio id="bg-audio" loop style="display:none;"></audio>

<header id="header">
    <div class="header-left" onclick="goHome(event)">
        <div class="yt-logo-box"></div>
        <span class="valora-brand-text">Valora<span>Tube</span></span>
    </div>
    <div class="header-right">
        <button class="header-icon" onclick="toggleSearch(true)"><span class="material-icons-outlined">search</span></button>
        <button class="header-icon" onclick="showToast('Fitur suara belum tersedia')"><span class="material-icons-outlined">mic</span></button>
        <button class="header-icon" onclick="openSettings()"><span class="material-icons-outlined">more_vert</span></button>
    </div>
    
    <div class="search-active-header" id="search-active-header">
        <button type="button" class="header-icon" onclick="goHome(null)"><span class="material-icons-outlined">arrow_back</span></button>
        <div class="search-bar-box" onclick="toggleSearch(true)">
            <span class="search-bar-text" id="active-search-keyword">Ketik pencarian...</span>
            <span class="material-icons-outlined" style="font-size:18px; color:var(--sub-text);" onclick="event.stopPropagation(); clearSearchQuery()">close</span>
        </div>
        <button type="button" class="header-icon" onclick="showToast('Fitur suara belum tersedia')"><span class="material-icons-outlined">mic</span></button>
    </div>

    <form class="search-form-mobile" id="mobile-search-form" onsubmit="submitSearch(event)">
        <div class="search-top-bar">
            <button type="button" class="header-icon" onclick="toggleSearch(false)"><span class="material-icons-outlined">arrow_back</span></button>
            <div class="search-input-wrap-mob">
                <input type="text" id="keyword-mobile" placeholder="Telusuri Valora Tube" autocomplete="off" oninput="debounceFetchSuggestions(this.value)">
            </div>
            <button type="submit" class="header-icon" style="background:var(--card-bg);"><span class="material-icons-outlined" style="font-size:20px;">search</span></button>
        </div>
        <div class="search-suggestions-list" id="suggestions-list"></div>
    </form>
</header>

<main id="main">
    <div class="chips-wrapper" id="chips-container">
        <div class="explore-icon" onclick="loadTrending()"><span class="material-icons-outlined" style="font-size: 20px;">explore</span></div>
        <div class="chips-bar" id="chips-bar-content">
            <button class="chip active" onclick="chipClick(this,'')">Semua</button>
            <button class="chip" onclick="chipClick(this,'Musik')">Musik</button>
            <button class="chip" onclick="chipClick(this,'Game')">Game</button>
            <button class="chip" onclick="chipClick(this,'Podcast')">Podcast</button>
            <button class="chip" onclick="chipClick(this,'Berita')">Berita</button>
            <button class="chip" onclick="chipClick(this,'Cuplikan')">Cuplikan</button>
        </div>
    </div>
    <div class="video-grid" id="video-grid"></div>
    <div id="scroll-loader"><div class="spinner"></div></div>
</main>

<div id="player-section">
    <div class="player-container" id="player-container-box" onclick="toggleOverlayUI(event)">
        <div id="player-box" style="width:100%; height:100%;"></div>
        
        <!-- Overlay UI interaktif -->
        <div class="player-overlay-ui" id="player-overlay">
            <div class="overlay-top">
                <div class="overlay-top-left">
                    <span class="material-icons" onclick="closePlayerToHome(event)">close</span>
                    <span class="material-icons" onclick="showToast('Otomatis putar aktif')">autoplay</span>
                </div>
                <div class="overlay-top-right">
                    <span class="material-icons" onclick="showToast('Casting perangkat diaktifkan')">cast</span>
                    <span class="material-icons" onclick="openSettings()">settings</span>
                </div>
            </div>
            
            <div class="overlay-center">
                <span class="material-icons" onclick="showToast('Video sebelumnya')">skip_previous</span>
                <span class="material-icons" id="overlay-play-icon" onclick="toggleMiniPlay(event)">pause</span>
                <span class="material-icons" onclick="showToast('Video selanjutnya')">skip_next</span>
            </div>
            
            <div class="overlay-bottom">
                <div class="overlay-timeline-bar">
                    <div class="overlay-timeline-progress"></div>
                </div>
                <div class="overlay-time-info">
                    <span id="current-time-label">00:11</span>
                    <span id="total-time-label">23:47</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="player-meta fade-in" id="player-meta-info">
        <div class="player-title" id="player-title">Judul Video</div>
        <div class="player-views-date">
            <span id="player-views">572 rb tampilan • 3 hari yang lalu</span>
            <span><span class="material-icons" style="font-size:14px; vertical-align:middle;">thumb_up</span> 3,2 rb</span>
        </div>
        
        <div class="action-row">
            <div class="action-pill" onclick="shareVideo()"><span class="material-icons-outlined">share</span> Bagikan</div>
            <div class="action-pill" onclick="downloadVideo()"><span class="material-icons-outlined">download</span> Unduh</div>
            <div class="action-pill" onclick="saveTontonNanti()"><span class="material-icons-outlined">playlist_add</span> Simpan</div>
            <div class="action-pill" onclick="showToast('Mode audio aktif')"><span class="material-icons-outlined">headphones</span> Audio</div>
        </div>
        
        <div class="channel-row">
            <div class="channel-info">
                <img id="player-channel-avatar" src="" style="width:36px; height:36px; border-radius:50%; object-fit:cover; background:#444;">
                <div>
                    <div class="channel-name" id="player-channel-name">Nama Channel</div>
                    <div class="channel-subs" id="player-subs-count">1,2 jt pelanggan</div>
                </div>
            </div>
            <button class="btn-subscribe" id="subscribe-btn" onclick="toggleSubscribe()">Berlangganan</button>
        </div>
        
        <div class="comments-box" onclick="showToast('Kolom komentar disembunyikan pemilik video')">
            <span>Komentar (244)</span>
            <span class="material-icons-outlined">unfold_more</span>
        </div>
        
        <div style="font-size: 16px; font-weight: 700; margin-bottom: 12px;">Video lainnya</div>
    </div>
    
    <div class="video-grid" id="related-grid"></div>
    <div id="related-loader" style="display:none; justify-content:center; padding:20px 0;"><div class="spinner"></div></div>
</div>

<div id="sheet-overlay" onclick="closeSettings()"></div>
<div id="settings-sheet">
    <div class="sheet-handle"></div>
    <div id="main-settings">
        <div class="setting-item" onclick="toggleTheme()"><span class="material-icons-outlined">brightness_6</span> Ganti Tema (Terang / Gelap)</div>
        <div class="setting-item" onclick="showToast('Mode ulang otomatis aktif')"><span class="material-icons-outlined">repeat</span> Mode ulang (Tidak diulang)</div>
        <div class="setting-item" onclick="showQualitySettings()"><span class="material-icons-outlined">hd</span> Kualitas (<span id="current-quality">Otomatis</span>)</div>
        <div class="setting-item" onclick="showToast('Takarir disetel ke Otomatis')"><span class="material-icons-outlined">closed_caption</span> Takarir (Indonesia)</div>
        <div class="setting-item" onclick="closeSettings()"><span class="material-icons-outlined">close</span> Tutup Menu</div>
    </div>
    <div id="quality-settings" style="display:none;">
        <div class="setting-item" onclick="showMainSettings()" style="border-bottom: 1px solid var(--border-color); margin-bottom:8px;"><span class="material-icons-outlined">arrow_back</span> Kembali</div>
        <div class="setting-item" onclick="setQuality(1080)">1080p Premium HD</div>
        <div class="setting-item" onclick="setQuality(720)">720p HD</div>
        <div class="setting-item" onclick="setQuality(480)">480p</div>
        <div class="setting-item" onclick="setQuality(360)">360p Data Saver</div>
    </div>
</div>

<nav id="bottom-nav">
    <div class="nav-item active" onclick="goHome(event, this)">
        <span class="material-icons-outlined">home</span><span class="material-icons">home</span>
        <span class="nav-label">Beranda</span>
    </div>
    <div class="nav-item" onclick="loadShorts(this)">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M17.77,10.32l-1.2-.5L18,9.06a3.74,3.74,0,0,0-3.5-6.62L6,6.94a3.74,3.74,0,0,0,.23,6.74l1.2.49L6,14.93a3.75,3.75,0,0,0,3.5,6.63l8.5-4.5a3.74,3.74,0,0,0-.23-6.74ZM10,14.65V9.35L14.75,12Z"/></svg>
        <span class="nav-label">Shorts</span>
    </div>
    <div class="nav-item" onclick="loadSubscriptions(this)">
        <span class="material-icons-outlined">subscriptions</span><span class="material-icons">subscriptions</span>
        <span class="nav-label">Langganan</span>
    </div>
    <div class="nav-item" onclick="loadTrendingNav(this)">
        <span class="material-icons-outlined">trending_up</span><span class="material-icons">trending_up</span>
        <span class="nav-label">Trending</span>
    </div>
    <div class="nav-item" onclick="loadProfile(this)">
        <div class="nav-avatar">V</div>
        <span class="nav-label">Valora</span>
    </div>
</nav>

<script>
    let currentQuery = '';
    let currentOffset = 0;
    let relatedOffset = 0;
    let currentRelatedKeyword = '';
    let isLoadingMore = false;
    let currentPlayingVideoStr = ''; 
    let activeData = [];
    let debounceTimer = null;
    let isSubscribed = false;
    let isMiniPlaying = true;
    let activeVideoId = '';
    let currentResolution = '';

    window.addEventListener('DOMContentLoaded', () => { 
        loadHome(); 
        history.pushState({page: 'home'}, '', '');
        const savedTheme = localStorage.getItem('yt_theme');
        if(savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
        
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').catch(() => {});
        }
    });

    function showToast(msg) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 2000);
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        if(next === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('yt_theme', 'light');
            showToast('Mode terang diaktifkan');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('yt_theme', 'dark');
            showToast('Mode gelap diaktifkan');
        }
        closeSettings();
    }
    
    window.addEventListener('popstate', (e) => {
        const sheet = document.getElementById('settings-sheet');
        const playerSec = document.getElementById('player-section');
        const searchForm = document.getElementById('mobile-search-form');
        
        if (sheet.classList.contains('show')) {
            closeSettings();
            history.pushState({page: 'home'}, '', '');
        } else if (searchForm.classList.contains('active')) {
            toggleSearch(false);
            history.pushState({page: 'home'}, '', '');
        } else if (playerSec.style.display === 'block') {
            goHome(null);
            history.pushState({page: 'home'}, '', '');
        } else {
            history.pushState({page: 'home'}, '', '');
        }
    });

    // Scroll listener hanya untuk infinite scroll beranda atau related video, tanpa mengubah ukuran pemutar menjadi mini
    window.addEventListener('scroll', () => {
        if (isLoadingMore) return;
        
        const mainDisplay = document.getElementById('main').style.display;
        const playerDisplay = document.getElementById('player-section').style.display;

        if (mainDisplay !== 'none' && currentQuery !== 'shorts') {
            if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300) {
                loadMoreData();
            }
        }
        
        if (playerDisplay === 'block') {
            if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300) {
                loadMoreRelatedData();
            }
        }
    });

    async function loadHome() {
        showSkeletons();
        currentQuery = '';
        currentOffset = 0;
        document.getElementById('search-active-header').classList.remove('active');
        resetChipsToHome();
        try { 
            const res = await fetch('/api/home'); 
            activeData = await res.json(); 
            currentOffset = activeData.length;
            renderGrid(activeData); 
        } catch(e) {
            showToast('Gagal memuat beranda. Periksa koneksi Anda.');
        }
    }

    async function loadMoreData() {
        if (isLoadingMore) return;
        isLoadingMore = true; 
        document.getElementById('scroll-loader').style.display = 'flex';
        try {
            let fetchUrl = currentQuery ? `/api/search?q=${encodeURIComponent(currentQuery)}&offset=${currentOffset}` : `/api/home`;
            const res = await fetch(fetchUrl);
            const data = await res.json();
            if (data && data.length > 0) { 
                currentOffset += data.length; 
                activeData = activeData.concat(data);
                appendToGrid(data, 'video-grid'); 
            }
        } catch(e){} finally { 
            isLoadingMore = false; 
            document.getElementById('scroll-loader').style.display = 'none'; 
        }
    }

    async function loadMoreRelatedData() {
        if (isLoadingMore || !currentRelatedKeyword) return;
        isLoadingMore = true;
        document.getElementById('related-loader').style.display = 'flex';
        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(currentRelatedKeyword)}&offset=${relatedOffset}`);
            const data = await res.json();
            if (data && data.length > 0) {
                relatedOffset += data.length;
                appendToGrid(data, 'related-grid');
            }
        } catch(e) {} finally {
            isLoadingMore = false;
            document.getElementById('related-loader').style.display = 'none';
        }
    }

    function toggleSearch(show) {
        const form = document.getElementById('mobile-search-form');
        const input = document.getElementById('keyword-mobile');
        if (show) { 
            input.value = currentQuery; 
            form.classList.add('active'); 
            input.focus(); 
            history.pushState({page: 'search'}, '', '');
        } else { 
            form.classList.remove('active'); 
            document.getElementById('suggestions-list').innerHTML = '';
        }
    }

    function debounceFetchSuggestions(keyword) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchSuggestions(keyword);
        }, 300);
    }

    async function fetchSuggestions(keyword) {
        const listContainer = document.getElementById('suggestions-list');
        if (!keyword.trim()) {
            listContainer.innerHTML = '';
            return;
        }
        try {
            const res = await fetch(`/api/suggestions?q=${encodeURIComponent(keyword)}`);
            const suggestions = await res.json();
            listContainer.innerHTML = '';
            suggestions.forEach(item => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.innerHTML = `
                    <div class="suggestion-left" onclick="selectSuggestion('${item}')">
                        <span class="material-icons-outlined">search</span>
                        <span>${item}</span>
                    </div>
                `;
                listContainer.appendChild(div);
            });
        } catch(e) {}
    }

    function selectSuggestion(text) {
        document.getElementById('keyword-mobile').value = text;
        executeSearch(text);
    }

    function submitSearch(e) {
        if(e) e.preventDefault();
        const q = document.getElementById('keyword-mobile').value.trim();
        if (q) {
            executeSearch(q);
        }
    }

    function executeSearch(q) {
        activateNav(document.querySelector('.nav-item')); 
        currentQuery = q; 
        currentOffset = 0; 
        toggleSearch(false); 
        showSkeletons();
        
        document.getElementById('active-search-keyword').textContent = q;
        document.getElementById('search-active-header').classList.add('active');

        renderSearchFilterChips();

        fetch('/api/search?q=' + encodeURIComponent(q) + '&offset=0')
            .then(r => r.json())
            .then(d => { 
                currentOffset = d.length; 
                activeData = d; 
                renderGrid(d); 
            })
            .catch(() => showToast('Pencarian gagal'));
    }

    function clearSearchQuery() {
        currentQuery = '';
        document.getElementById('search-active-header').classList.remove('active');
        loadHome();
    }

    function renderSearchFilterChips() {
        const bar = document.getElementById('chips-bar-content');
        bar.innerHTML = `
            <button class="chip active" onclick="filterSearchType(this, 'all')"><span class="material-icons-outlined" style="font-size:16px;">done</span> Semua</button>
            <button class="chip" onclick="filterSearchType(this, 'video')">Video</button>
            <button class="chip" onclick="filterSearchType(this, 'channel')">Saluran</button>
            <button class="chip" onclick="filterSearchType(this, 'playlist')">Daftar Putar</button>
            <button class="chip" onclick="filterSearchType(this, 'music')">Lagu Valora Music</button>
        `;
    }

    function resetChipsToHome() {
        const bar = document.getElementById('chips-bar-content');
        bar.innerHTML = `
            <button class="chip active" onclick="chipClick(this,'')">Semua</button>
            <button class="chip" onclick="chipClick(this,'Musik')">Musik</button>
            <button class="chip" onclick="chipClick(this,'Game')">Game</button>
            <button class="chip" onclick="chipClick(this,'Podcast')">Podcast</button>
            <button class="chip" onclick="chipClick(this,'Berita')">Berita</button>
            <button class="chip" onclick="chipClick(this,'Cuplikan')">Cuplikan</button>
        `;
    }

    function filterSearchType(btn, type) {
        document.querySelectorAll('.chips-bar .chip').forEach(c => {
            c.classList.remove('active');
            c.innerHTML = c.textContent.replace('done ', '');
        });
        btn.classList.add('active');
        btn.innerHTML = `<span class="material-icons-outlined" style="font-size:16px;">done</span> ` + btn.textContent;
        showToast('Filter ' + type + ' diterapkan');
    }

    function chipClick(btn, query) {
        document.querySelectorAll('.chips-bar .chip').forEach(c => c.classList.remove('active')); 
        btn.classList.add('active');
        if (query) { 
            currentQuery = query; 
            currentOffset = 0; 
            showSkeletons(); 
            fetch('/api/search?q=' + encodeURIComponent(query) + '&offset=0').then(r=>r.json()).then(d => { currentOffset=d.length; activeData=d; renderGrid(d); }); 
        } else {
            loadHome();
        }
    }

    function loadTrending() {
        document.getElementById('chips-container').style.display = 'flex';
        showSkeletons();
        currentQuery = 'trending';
        fetch('/api/trending').then(r=>r.json()).then(d => { activeData=d; renderGrid(d); }).catch(() => showToast('Gagal memuat trending'));
    }

    function activateNav(el) {
        if(!el) return;
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
        document.getElementById('main').style.display = 'block';
        document.getElementById('player-section').style.display = 'none';
        
        const container = document.getElementById('player-container-box');
        container.style.display = 'none';
    }

    function goHome(e, el) { 
        if (e) e.preventDefault(); 
        activateNav(el || document.querySelector('.nav-item')); 
        document.getElementById('chips-container').style.display = 'flex';
        document.getElementById('search-active-header').classList.remove('active');
        resetChipsToHome();
        window.scrollTo(0,0);
        if(currentQuery !== '') loadHome(); 
    }
    
    function loadShorts(el) {
        activateNav(el);
        document.getElementById('chips-container').style.display = 'none';
        document.getElementById('search-active-header').classList.remove('active');
        showSkeletons();
        currentQuery = 'shorts'; 
        fetch('/api/shorts').then(r=>r.json()).then(d => { 
            activeData = d; 
            renderShortsGrid(d); 
        }).catch(() => showToast('Gagal memuat Shorts'));
    }

    function renderShortsGrid(data) {
        const g = document.getElementById('video-grid');
        g.innerHTML = '';
        const container = document.createElement('div');
        container.className = 'shorts-container';
        data.forEach(v => {
            const card = document.createElement('div');
            card.className = 'short-card fade-in';
            card.onclick = () => playVideo(encodeURIComponent(JSON.stringify(v)));
            card.innerHTML = `
                <iframe src="https://www.youtube-nocookie.com/embed/${v.id}?autoplay=0&controls=0&loop=1&mute=1"></iframe>
                <div class="short-overlay">
                    <div style="font-weight:700; font-size:14px; margin-bottom:6px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">${v.title}</div>
                    <div style="font-size:12px; opacity:0.8;">${v.channel || 'Shorts Creator'}</div>
                </div>
            `;
            container.appendChild(card);
        });
        g.appendChild(container);
    }

    function loadSubscriptions(el) {
        activateNav(el);
        document.getElementById('chips-container').style.display = 'none';
        document.getElementById('search-active-header').classList.remove('active');
        let subs = JSON.parse(localStorage.getItem('valora_subscriptions') || '[]');
        if(subs.length === 0) {
            document.getElementById('video-grid').innerHTML = '<div style="text-align:center; padding:40px; color:var(--sub-text);">Belum ada channel yang diikuti. Klik "Berlangganan" pada video untuk menambahkan.</div>';
        } else {
            renderGrid(subs);
        }
    }

    function loadTrendingNav(el) {
        activateNav(el);
        document.getElementById('chips-container').style.display = 'none';
        document.getElementById('search-active-header').classList.remove('active');
        loadTrending();
    }

    function loadProfile(el) {
        activateNav(el);
        document.getElementById('chips-container').style.display = 'none';
        document.getElementById('search-active-header').classList.remove('active');
        let wl = JSON.parse(localStorage.getItem('valora_watch_later') || '[]');
        let html = '<div style="padding:16px;"><h2 style="margin-bottom:16px;">Tonton Nanti ('+wl.length+')</h2>';
        if(wl.length === 0) {
            html += '<p style="color:var(--sub-text);">Belum ada video tersimpan.</p>';
        }
        html += '</div>';
        document.getElementById('video-grid').innerHTML = html;
        if(wl.length > 0) appendToGrid(wl, 'video-grid');
    }

    function saveTontonNanti() {
        if(!currentPlayingVideoStr) return;
        try {
            let v = JSON.parse(decodeURIComponent(currentPlayingVideoStr));
            let wl = JSON.parse(localStorage.getItem('valora_watch_later') || '[]');
            if(!wl.find(x => x.id === v.id)) {
                wl.unshift(v); localStorage.setItem('valora_watch_later', JSON.stringify(wl));
                showToast('Disimpan ke Tonton Nanti');
            } else {
                showToast('Video sudah ada di playlist');
            }
        } catch(e){}
    }

    function toggleSubscribe() {
        isSubscribed = !isSubscribed;
        const btn = document.getElementById('subscribe-btn');
        let subs = JSON.parse(localStorage.getItem('valora_subscriptions') || '[]');
        if(currentPlayingVideoStr) {
            let v = JSON.parse(decodeURIComponent(currentPlayingVideoStr));
            if(isSubscribed) {
                btn.textContent = 'Berlangganan';
                btn.classList.add('subscribed');
                if(!subs.find(x => x.id === v.id)) subs.unshift(v);
                showToast('Berhasil Berlangganan');
            } else {
                btn.textContent = 'Berlangganan';
                btn.classList.remove('subscribed');
                subs = subs.filter(x => x.id !== v.id);
                showToast('Berhenti Berlangganan');
            }
            localStorage.setItem('valora_subscriptions', JSON.stringify(subs));
        }
    }

    function shareVideo() {
        if(!currentPlayingVideoStr) return;
        let v = JSON.parse(decodeURIComponent(currentPlayingVideoStr));
        const url = `https://youtu.be/${v.id}`;
        if (navigator.share) {
            navigator.share({ title: v.title, url: url }).catch(() => {});
        } else {
            navigator.clipboard.writeText(url);
            showToast('Tautan disalin ke clipboard');
        }
    }

    function downloadVideo() {
        if(!currentPlayingVideoStr) return;
        let v = JSON.parse(decodeURIComponent(currentPlayingVideoStr));
        window.open(`https://www.ssyoutube.com/watch?v=${v.id}`, '_blank');
        showToast('Mengarahkan ke pengunduh eksternal');
    }

    function openSettings() {
        document.getElementById('sheet-overlay').classList.add('show');
        setTimeout(() => document.getElementById('settings-sheet').classList.add('show'), 10);
    }
    
    function closeSettings() {
        document.getElementById('settings-sheet').classList.remove('show');
        setTimeout(() => {
            document.getElementById('sheet-overlay').classList.remove('show');
            showMainSettings();
        }, 300);
    }
    
    function showQualitySettings() {
        document.getElementById('main-settings').style.display = 'none';
        document.getElementById('quality-settings').style.display = 'block';
    }
    
    function showMainSettings() {
        document.getElementById('main-settings').style.display = 'block';
        document.getElementById('quality-settings').style.display = 'none';
    }
    
    function setQuality(res) {
        currentResolution = res;
        document.getElementById('current-quality').textContent = res + 'p';
        closeSettings();
        showToast('Resolusi diubah ke ' + res + 'p');
        
        if (activeVideoId) {
            const iframe = document.getElementById('yt-iframe');
            if (iframe) {
                iframe.src = `https://www.youtube-nocookie.com/embed/${activeVideoId}?autoplay=1&rel=0&fs=0&iv_load_policy=3&modestbranding=1&vq=${res}p`;
            }
        }
    }

    function toggleOverlayUI(e) {
        const overlay = document.getElementById('player-overlay');
        overlay.classList.toggle('active');
    }

    function closePlayerToHome(e) {
        if(e) e.stopPropagation();
        goHome(null);
    }

    async function playVideo(videoStr) {
        let v; try { v = JSON.parse(decodeURIComponent(videoStr)); } catch(e){ return; }
        currentPlayingVideoStr = videoStr; 
        isMiniPlaying = true;
        activeVideoId = v.id;
        
        document.getElementById('main').style.display = 'none';
        
        const container = document.getElementById('player-container-box');
        container.style.display = 'block';
        document.body.style.overflow = '';

        const ps = document.getElementById('player-section');
        ps.style.display = 'block';
        document.getElementById('player-meta-info').style.display = 'block';
        
        document.getElementById('player-title').textContent = v.title;
        document.getElementById('player-channel-name').textContent = v.channel || 'Valora Creator';
        document.getElementById('player-channel-avatar').src = v.avatar || '';
        document.getElementById('player-views').textContent = (v.views || '123 rb tampilan') + ' • ' + (v.published || 'Baru saja');
        
        document.getElementById('related-grid').innerHTML = Array(4).fill(`<div class="vid-card"><div class="thumb-wrap skeleton" style="border-radius:8px;"></div><div class="vid-info"><div class="vid-text"><div class="skeleton" style="height:14px; margin-bottom:8px; width:90%; border-radius:4px;"></div><div class="skeleton" style="height:12px; width:60%; border-radius:4px;"></div></div></div></div>`).join('');

        let vqParam = currentResolution ? `&vq=${currentResolution}p` : '';
        document.getElementById('player-box').innerHTML = `<iframe id="yt-iframe" src="https://www.youtube-nocookie.com/embed/${v.id}?autoplay=1&rel=0&fs=0&iv_load_policy=3&modestbranding=1${vqParam}" allow="autoplay"></iframe>`;
        
        if ('mediaSession' in navigator) {
            navigator.mediaSession.metadata = new MediaMetadata({
                title: v.title,
                artist: v.channel || 'Valora Creator',
                artwork: [{ src: `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`, sizes: '512x512', type: 'image/jpeg' }]
            });
            navigator.mediaSession.setActionHandler('play', () => { toggleMiniPlay({stopPropagation:()=>{}}); });
            navigator.mediaSession.setActionHandler('pause', () => { toggleMiniPlay({stopPropagation:()=>{}}); });
        }

        const bgAudio = document.getElementById('bg-audio');
        bgAudio.src = "https://actions.google.com/sounds/v1/ambiences/rain_heavy.ogg";
        bgAudio.volume = 0.01;
        bgAudio.play().catch(()=>{});

        currentRelatedKeyword = v.title.split(' ').slice(0, 3).join(' ') || 'viral';
        relatedOffset = 0;

        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(currentRelatedKeyword)}&offset=0`);
            const related = await res.json();
            relatedOffset = related.length;
            document.getElementById('related-grid').innerHTML = '';
            appendToGrid(related, 'related-grid');
        } catch(e) {
            let relatedFallback = [...activeData].sort(() => 0.5 - Math.random()).slice(0, 5);
            document.getElementById('related-grid').innerHTML = '';
            appendToGrid(relatedFallback, 'related-grid');
        }

        document.getElementById('overlay-play-icon').textContent = 'pause';
        window.scrollTo(0,0);
    }

    function toggleMiniPlay(e) {
        e.stopPropagation();
        const icon = document.getElementById('overlay-play-icon');
        const iframe = document.getElementById('yt-iframe');
        const bgAudio = document.getElementById('bg-audio');
        
        if (isMiniPlaying) {
            isMiniPlaying = false;
            icon.textContent = 'play_arrow';
            if(iframe) {
                iframe.dataset.src = iframe.src;
                iframe.src = '';
            }
            bgAudio.pause();
            showToast('Video dijeda');
        } else {
            isMiniPlaying = true;
            icon.textContent = 'pause';
            let vqParam = currentResolution ? `&vq=${currentResolution}p` : '';
            if(iframe && iframe.dataset.src) {
                iframe.src = iframe.dataset.src;
            } else if(activeVideoId) {
                iframe.src = `https://www.youtube-nocookie.com/embed/${activeVideoId}?autoplay=1&rel=0&fs=0&iv_load_policy=3&modestbranding=1${vqParam}`;
            }
            bgAudio.play().catch(()=>{});
            showToast('Video dilanjutkan');
        }
    }

    function showSkeletons() { 
        document.getElementById('video-grid').innerHTML = Array(6).fill(`<div class="vid-card"><div class="thumb-wrap skeleton" style="border-radius:0;"></div><div class="vid-info"><div class="channel-avatar skeleton"></div><div class="vid-text"><div class="skeleton" style="height:14px; margin-bottom:8px; width:90%; border-radius:4px;"></div><div class="skeleton" style="height:12px; width:60%; border-radius:4px;"></div></div></div></div>`).join(''); 
    }

    function renderGrid(data) {
        document.getElementById('video-grid').innerHTML = ''; 
        appendToGrid(data, 'video-grid');
    }

    function appendToGrid(data, targetId) {
        const g = document.getElementById(targetId);
        data.forEach(v => {
            const card = document.createElement('div'); 
            card.className = 'vid-card fade-in';
            const vStr = encodeURIComponent(JSON.stringify(v));
            card.onclick = () => playVideo(vStr);
            let initial = v.channel ? v.channel.charAt(0).toUpperCase() : 'V';
            let avatarHtml = v.avatar ? `<div class="channel-avatar"><img src="${v.avatar}"></div>` : `<div class="channel-avatar">${initial}</div>`;
            let meta = [v.channel, v.views, v.published].filter(Boolean).join(' • ');
            
            card.innerHTML = `
                <div class="thumb-wrap">
                    <img class="thumb-img" src="https://i.ytimg.com/vi/${v.id}/hqdefault.jpg" loading="lazy">
                    ${v.duration ? '<span class="duration-badge">' + v.duration + '</span>' : ''}
                </div>
                <div class="vid-info">
                    ${avatarHtml}
                    <div class="vid-text">
                        <div class="vid-title">${v.title}</div>
                        <div class="vid-meta">${meta}</div>
                    </div>
                </div>`;
            g.appendChild(card);
        });
    }
</script>
</body>
</html>
"""

def extract_video_data(video):
    data = {"id": video.get("videoId"), "title": "No Title"}
    try: 
        runs = video.get("title", {}).get("runs")
        if runs: data["title"] = runs[0].get("text", "No Title")
    except Exception: pass
    try: data["duration"] = video.get("lengthText", {}).get("simpleText", "")
    except Exception: pass
    try: data["views"] = video.get("viewCountText", {}).get("simpleText", "")
    except Exception: pass
    try: data["published"] = video.get("publishedTimeText", {}).get("simpleText", "")
    except Exception: pass
    try:
        byline = video.get("longBylineText") or video.get("ownerText")
        if byline:
            run = byline.get("runs", [{}])[0]
            data["channel"] = run.get("text", "")
    except Exception: 
        data["channel"] = ""
    try:
        avatar_thumbs = video.get("channelThumbnailSupportedRenderers", {}).get("channelThumbnailWithLinkRenderer", {}).get("thumbnail", {}).get("thumbnails", [])
        if avatar_thumbs: data["avatar"] = avatar_thumbs[0].get("url", "")
    except Exception: 
        data["avatar"] = ""
    return data

@app.route("/")
def home(): return render_template_string(HTML_TEMPLATE)

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "Valora Tube",
        "short_name": "ValoraTube",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f0f0f",
        "theme_color": "#0f0f0f",
        "icons": [
            {
                "src": "https://www.gstatic.com/youtube/img/branding/favicon/favicon_144x144.png",
                "sizes": "144x144",
                "type": "image/png"
            }
        ]
    })

@app.route("/sw.js")
def service_worker():
    sw_code = """
    self.addEventListener('install', (e) => { self.skipWaiting(); });
    self.addEventListener('activate', (e) => { e.waitUntil(clients.claim()); });
    self.addEventListener('fetch', (e) => { e.respondWith(fetch(e.request).catch(() => caches.match(e.request))); });
    """
    return sw_code, 200, {'Content-Type': 'application/javascript'}

@app.route("/api/suggestions")
def api_suggestions():
    query = request.args.get("q", "").strip()
    suggestions = []
    if not query: return jsonify(suggestions)
    try:
        url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={urllib.request.quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('latin1')
            start = data.find('([')
            end = data.rfind('])')
            if start != -1 and end != -1:
                parsed = json.loads(data[start+1:end+1])
                for item in parsed:
                    if isinstance(item, list):
                        for sub in item:
                            if isinstance(sub, list) and len(sub) > 0 and isinstance(sub[0], str):
                                suggestions.append(sub[0])
    except Exception: pass
    return jsonify(suggestions[:10])

@app.route("/api/home")
def api_home():
    results = []
    try:
        base_keywords = ["Sakura School Simulator", "Viral", "Hits Indonesia", "Populer Hari Ini", "Trending Video", "Gaming"]
        random_keyword = random.choice(base_keywords)
        videos = scrapetube.get_search(random_keyword, limit=25)
        for v in videos:
            d = extract_video_data(v)
            if d.get("id"): results.append(d)
        random.shuffle(results)
    except Exception: pass
    return jsonify(results)

@app.route("/api/trending")
def api_trending():
    results = []
    try:
        videos = scrapetube.get_trending("ID", limit=25)
        for v in videos:
            d = extract_video_data(v)
            if d.get("id"): results.append(d)
    except Exception: pass
    return jsonify(results)

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    offset = int(request.args.get("offset", 0))
    limit = 15; results = []
    if not query: return jsonify(results)
    
    cache_key = f"{query}_{offset}"
    if cache_key in search_cache:
        return jsonify(search_cache[cache_key])

    try:
        videos = scrapetube.get_search(query, limit=offset+limit)
        for i, v in enumerate(videos):
            if i >= offset:
                d = extract_video_data(v)
                if d.get("id"): results.append(d)
        search_cache[cache_key] = results
    except Exception: pass
    return jsonify(results)

@app.route("/api/shorts")
def api_shorts():
    results = []
    try:
        videos = scrapetube.get_search("shorts viral #shorts", limit=40)
        for v in videos:
            d = extract_video_data(v); dur_text = d.get("duration", ""); is_short = False
            if dur_text:
                parts = dur_text.split(":")
                if len(parts) == 1: is_short = True
                elif len(parts) == 2 and int(parts[0]) == 0 and int(parts[1]) <= 60: is_short = True
            if is_short and d.get("id"):
                if not any(r["id"] == d["id"] for r in results): results.append(d)
            if len(results) >= 12: break
    except Exception: pass
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=2000)
