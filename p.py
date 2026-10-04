from flask import Flask, jsonify, render_template_string, request
import scrapetube
import random

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>YouTube Clone</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Roboto', Arial, sans-serif; background: #0f0f0f; color: #f1f1f1; overflow-x: hidden; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #717171; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #a0a0a0; }
        a { text-decoration: none; color: inherit; }

        /* ===== SPLASH ===== */
        #splash { position: fixed; inset: 0; background: #0f0f0f; display: flex; align-items: center; justify-content: center; z-index: 9999; transition: opacity 0.5s, visibility 0.5s; }
        #splash.hide { opacity: 0; visibility: hidden; pointer-events: none; }
        .splash-logo { width: 80px; animation: spPulse 1.5s ease-in-out infinite; }
        @keyframes spPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.06); } }

        /* ===== HEADER ===== */
        #header { position: fixed; top: 0; left: 0; right: 0; height: 56px; background: rgba(15,15,15,0.98); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 100; }
        .header-left { display: flex; align-items: center; gap: 16px; min-width: 200px; }
        .menu-btn { background: none; border: none; color: #fff; cursor: pointer; padding: 8px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
        .menu-btn:hover { background: rgba(255,255,255,0.1); }
        .yt-logo { display: flex; align-items: center; gap: 4px; cursor: pointer; user-select: none; }
        .yt-logo-text { font-size: 19px; font-weight: 700; letter-spacing: -1px; margin-left: 2px; }
        .yt-logo .country { font-size: 10px; color: #aaa; font-weight: 500; margin-top: -10px; margin-left: 2px;}
        
        .header-center { flex: 1; display: flex; align-items: center; justify-content: center; max-width: 720px; margin: 0 auto; position: relative; }
        .search-form { display: flex; flex: 1; align-items: center; }
        .search-input-wrap { flex: 1; position: relative; display: flex; align-items: center; }
        .search-input-wrap input { width: 100%; height: 40px; padding: 0 16px; font-size: 16px; border: 1px solid #303030; border-right: none; border-radius: 20px 0 0 20px; background: #121212; color: #fff; outline: none; }
        .search-input-wrap input:focus { border-color: #1c62b9; }
        .search-btn { height: 40px; width: 64px; border: 1px solid #303030; border-radius: 0 20px 20px 0; background: #222222; color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
        .search-btn:hover { background: #303030; }
        .mic-btn { width: 40px; height: 40px; border: none; border-radius: 50%; background: #181818; color: #fff; cursor: pointer; margin-left: 12px; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
        
        .suggestion-box { position: absolute; top: 44px; left: 0; right: 64px; background: #212121; border-radius: 0 0 12px 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); overflow: hidden; z-index: 200; display: none; border: 1px solid #303030; border-top: none;}
        .suggestion-box.show { display: block; }
        .suggestion-item { padding: 8px 16px; cursor: pointer; display: flex; align-items: center; gap: 16px; font-size: 14px; }
        .suggestion-item:hover { background: rgba(255,255,255,0.1); }
        .suggestion-item .material-icons-outlined { font-size: 20px; color: #aaa; }

        .header-right { display: flex; align-items: center; gap: 8px; min-width: 200px; justify-content: flex-end; }
        .header-icon { width: 40px; height: 40px; border: none; border-radius: 50%; background: transparent; color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; position: relative; }
        .header-icon:hover { background: rgba(255,255,255,0.1); }
        .avatar-btn { width: 32px; height: 32px; border-radius: 50%; background: #ff4e45; color: #fff; border: none; cursor: pointer; font-size: 14px; font-weight: 500; display: flex; align-items: center; justify-content: center; margin-left: 8px; }

        /* ===== SIDEBAR ===== */
        #sidebar { position: fixed; top: 56px; left: 0; width: 240px; height: calc(100vh - 56px); background: #0f0f0f; overflow-y: auto; overflow-x: hidden; padding: 12px 0; z-index: 90; transition: transform 0.2s ease, width 0.2s ease; }
        #sidebar.collapsed { width: 72px; }
        #sidebar.collapsed .sidebar-label { font-size: 10px; display: block; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%; text-align: center; }
        #sidebar.collapsed .sidebar-item { flex-direction: column; padding: 16px 0; gap: 0; justify-content: center; border-radius: 10px; margin: 0 4px; height: auto; }
        #sidebar.collapsed .sidebar-item .material-icons-outlined, #sidebar.collapsed .sidebar-item .material-icons { font-size: 24px; margin: 0; }
        
        .sidebar-item { display: flex; align-items: center; gap: 24px; padding: 0 12px; height: 40px; cursor: pointer; border-radius: 10px; margin: 0 12px; transition: background 0.15s; white-space: nowrap; }
        .sidebar-item:hover { background: rgba(255,255,255,0.1); }
        .sidebar-item.active { background: rgba(255,255,255,0.15); font-weight: 500; }
        .sidebar-item.active .material-icons-outlined { display: none; }
        .sidebar-item:not(.active) .material-icons { display: none; }
        .sidebar-item .icon-wrapper { font-size: 24px; flex-shrink: 0; display: flex; }
        .sidebar-label { font-size: 14px; }
        .sidebar-divider { height: 1px; background: rgba(255,255,255,0.1); margin: 12px 0; }
        .sidebar-heading { padding: 8px 24px 4px; font-size: 16px; font-weight: 500; margin-bottom: 4px; }
        #sidebar.collapsed .sidebar-heading, #sidebar.collapsed .sidebar-divider, #sidebar.collapsed .hide-on-collapse { display: none; }

        /* ===== BOTTOM NAV (MOBILE) ===== */
        #bottom-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; height: 48px; background: rgba(15,15,15,0.98); border-top: 1px solid rgba(255,255,255,0.1); z-index: 100; justify-content: space-around; align-items: center; }
        .nav-item { display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; cursor: pointer; width: 100%; padding: 4px 0; height: 100%; transition: background 0.2s; }
        .nav-item .material-icons-outlined, .nav-item .material-icons { font-size: 24px; }
        .nav-item .nav-label { font-size: 10px; margin-top: 2px; }
        .nav-item.active .material-icons-outlined { display: none; }
        .nav-item:not(.active) .material-icons { display: none; }

        /* ===== MAIN CONTENT ===== */
        #main { margin-left: 240px; margin-top: 56px; padding: 0 24px 40px; transition: margin-left 0.2s ease; min-height: calc(100vh - 56px); padding-bottom: 100px; }
        #main.expanded { margin-left: 72px; }
        #main.mini-open { padding-bottom: 80px; } /* Space for mini player */

        .chips-wrapper { position: sticky; top: 56px; background: rgba(15,15,15,0.98); z-index: 10; padding: 12px 0; }
        .chips-bar { display: flex; gap: 12px; overflow-x: auto; scrollbar-width: none; -ms-overflow-style: none; }
        .chips-bar::-webkit-scrollbar { display: none; }
        .chip { padding: 8px 12px; border-radius: 8px; font-size: 14px; font-weight: 500; white-space: nowrap; cursor: pointer; border: none; background: rgba(255,255,255,0.1); color: #f1f1f1; transition: background 0.2s; }
        .chip:hover { background: rgba(255,255,255,0.2); }
        .chip.active { background: #f1f1f1; color: #0f0f0f; }

        /* ===== PLAYER SECTION ===== */
        #player-section { display: none; max-width: 1280px; margin: 24px auto; opacity: 0; transition: opacity 0.3s; }
        #player-section.show { display: block; opacity: 1; }
        
        .player-container { position: relative; width: 100%; padding-bottom: 56.25%; background: #000; border-radius: 12px; overflow: hidden; }
        .player-container iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: none; }
        
        #player-section.theatre { max-width: 100%; margin: 0 -24px 24px -24px; }
        #player-section.theatre .player-container { border-radius: 0; max-height: 70vh; padding-bottom: 0; height: 70vh; }
        #player-section.theatre .player-meta { padding: 16px 24px 0; max-width: 1280px; margin: 0 auto; }

        .player-meta { padding: 16px 0 0; }
        .player-title { font-size: 20px; font-weight: 700; line-height: 1.4; margin-bottom: 12px; }
        .player-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: space-between; }
        .player-actions-left { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .player-actions-right { display: flex; gap: 8px; flex-wrap: wrap; }
        .action-btn { display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 20px; background: rgba(255,255,255,0.1); border: none; color: #f1f1f1; cursor: pointer; font-size: 14px; font-weight: 500; transition: background 0.2s; }
        .action-btn:hover { background: rgba(255,255,255,0.2); }
        
        /* Resolution Selector Outside Player */
        .resolution-panel { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; margin-top: 12px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
        .res-label { font-size: 14px; font-weight: 500; color: #aaa; }
        .res-btn { padding: 6px 12px; border-radius: 8px; background: #303030; color: #fff; border: none; cursor: pointer; font-size: 13px; font-weight: 500; transition: 0.2s; }
        .res-btn.active, .res-btn:hover { background: #fff; color: #000; }

        .player-description-box { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; margin-top: 16px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; cursor: pointer; }
        .desc-views-date { font-weight: 700; margin-bottom: 6px; }

        /* ===== MINI PLAYER (LIKE REAL YT) ===== */
        #mini-player { position: fixed; bottom: 0; left: 0; right: 0; height: 70px; background: #212121; z-index: 999; display: none; align-items: center; padding: 0 12px; border-top: 1px solid rgba(255,255,255,0.1); box-shadow: 0 -2px 10px rgba(0,0,0,0.5); transition: transform 0.3s; }
        #mini-player.show { display: flex; }
        .mini-thumb { width: 110px; height: 62px; border-radius: 6px; background: #000; overflow: hidden; flex-shrink: 0; cursor: pointer; margin-right: 12px; }
        .mini-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .mini-info { flex: 1; overflow: hidden; cursor: pointer; padding-right: 12px; }
        .mini-title { font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .mini-channel { font-size: 12px; color: #aaa; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .mini-controls { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
        .mini-action { width: 36px; height: 36px; border-radius: 50%; background: transparent; border: none; color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
        .mini-action:hover { background: rgba(255,255,255,0.2); }

        /* ===== VIDEO GRID ===== */
        .video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 40px 16px; padding-top: 24px; }
        .page-title { grid-column: 1 / -1; margin-bottom: -16px; font-size: 24px; font-weight: 700; display: flex; align-items: center; gap: 12px; }
        
        .vid-card { cursor: pointer; display: flex; flex-direction: column; gap: 12px; }
        .thumb-wrap { position: relative; width: 100%; aspect-ratio: 16/9; border-radius: 12px; overflow: hidden; background: #272727; }
        .vid-card:hover .thumb-wrap { border-radius: 0px; }
        .thumb-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
        .vid-card:hover .thumb-img { transform: scale(1.05); }
        .duration-badge { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: #fff; font-size: 12px; font-weight: 500; padding: 3px 4px; border-radius: 4px; }
        
        .vid-info { display: flex; gap: 12px; align-items: flex-start; }
        .channel-avatar { width: 36px; height: 36px; border-radius: 50%; background: #444; flex-shrink: 0; overflow: hidden; }
        .channel-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .vid-text { flex: 1; min-width: 0; }
        .vid-title { font-size: 16px; font-weight: 500; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; color: #f1f1f1; }
        .vid-channel { font-size: 14px; color: #aaa; line-height: 1.4; margin-bottom: 2px; display: inline-block; }
        .vid-channel:hover { color: #fff; }
        .vid-meta { font-size: 14px; color: #aaa; line-height: 1.4; }

        /* ===== SKELETON ===== */
        .skel-card { display: flex; flex-direction: column; gap: 12px; }
        .skel-thumb { width: 100%; aspect-ratio: 16/9; border-radius: 12px; background: #272727; animation: pulse 1.5s infinite ease-in-out; }
        .skel-info { display: flex; gap: 12px; }
        .skel-avatar { width: 36px; height: 36px; border-radius: 50%; background: #272727; flex-shrink: 0; animation: pulse 1.5s infinite ease-in-out; }
        .skel-lines { flex: 1; display: flex; flex-direction: column; gap: 8px; padding-top: 4px; }
        .skel-line { height: 14px; border-radius: 4px; background: #272727; animation: pulse 1.5s infinite ease-in-out; }
        .skel-line.short { width: 80%; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

        .empty-state { text-align: center; padding: 60px 20px; color: #aaa; grid-column: 1 / -1; }
        .empty-state .material-icons-outlined { font-size: 64px; margin-bottom: 12px; opacity: 0.5; }

        #scroll-loader { display: none; justify-content: center; padding: 24px 0; width: 100%; grid-column: 1 / -1; }
        #scroll-loader.show { display: flex; }
        .spinner { width: 32px; height: 32px; border: 3px solid rgba(255,255,255,0.1); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        #toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(80px); background: #f1f1f1; color: #0f0f0f; padding: 12px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 9999; transition: transform 0.3s; pointer-events: none; }
        #toast.show { transform: translateX(-50%) translateY(0); }

        .overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 85; opacity: 0; transition: opacity 0.3s; }
        .overlay.show { display: block; opacity: 1; }

        @media(max-width: 792px) {
            #sidebar { transform: translateX(-100%); width: 240px; }
            #sidebar.mobile-open { transform: translateX(0); }
            #main { margin-left: 0 !important; padding: 0 16px 70px !important; }
            #bottom-nav { display: flex; }
            #toast { bottom: 70px; }
            .header-left, .header-right { min-width: auto; }
            .search-input-wrap input { padding-left: 12px; }
            .search-btn { width: 48px; }
            .mic-btn { display: none; }
            .video-grid { grid-template-columns: 1fr; gap: 24px; }
            #player-section.theatre .player-container { height: 35vh; }
            .suggestion-box { right: 0; }
            #mini-player { height: 60px; }
            .mini-thumb { width: 90px; height: 50px; }
            #main.mini-open { padding-bottom: 130px !important; }
        }
    </style>
</head>
<body>

<div id="splash">
    <svg class="splash-logo" viewBox="0 0 68 48">
        <path fill="#FF0000" d="M66.52,7.74c-0.78-2.93-2.49-5.41-5.42-6.19C55.79,.13,34,0,34,0S12.21,.13,6.9,1.55 C3.97,2.33,2.27,4.81,1.48,7.74C0.06,13.05,0,24,0,24s0.06,10.95,1.48,16.26c0.78,2.93,2.49,5.41,5.42,6.19 C12.21,47.87,34,48,34,48s21.79-0.13,27.1-1.55c2.93-0.78,4.64-3.26,5.42-6.19C67.94,34.95,68,24,68,24S67.94,13.05,66.52,7.74z"/>
        <path fill="#FFF" d="M45,24L27,14v20L45,24z"/>
    </svg>
</div>

<div class="overlay" id="overlay" onclick="toggleSidebar()"></div>

<header id="header">
    <div class="header-left">
        <button class="menu-btn" onclick="toggleSidebar()"><span class="material-icons-outlined">menu</span></button>
        <a class="yt-logo" href="#" onclick="goHome(event)">
            <svg viewBox="0 0 24 24" style="height:24px; color:#FF0000; fill:currentColor;"><path d="M21.58,7.19C21.35,6.33 20.67,5.65 19.81,5.42C18.25,5 12,5 12,5C12,5 5.75,5 4.19,5.42C3.33,5.65 2.65,6.33 2.42,7.19C2,8.75 2,12 2,12C2,12 2,15.25 2.42,16.81C2.65,17.67 3.33,18.35 4.19,18.58C5.75,19 12,19 12,19C12,19 18.25,19 19.81,18.58C20.67,18.35 21.35,17.67 21.58,16.81C22,15.25 22,12 22,12C22,12 22,8.75 21.58,7.19Z"/><path d="M10,15L15.5,12L10,9V15Z" fill="white"/></svg>
            <span class="yt-logo-text">YouTube</span><span class="country">ID</span>
        </a>
    </div>
    <div class="header-center">
        <form class="search-form" onsubmit="searchVideos(event)">
            <div class="search-input-wrap">
                <input type="text" id="keyword" placeholder="Telusuri" autocomplete="off" oninput="fetchSuggestions()" onfocus="fetchSuggestions()">
                <div class="suggestion-box" id="suggestion-box"></div>
            </div>
            <button type="submit" class="search-btn"><span class="material-icons-outlined" style="font-size:24px">search</span></button>
            <button type="button" class="mic-btn" onclick="showToast('Fitur suara segera hadir')"><span class="material-icons-outlined" style="font-size:24px">mic</span></button>
        </form>
    </div>
    <div class="header-right">
        <button class="header-icon" onclick="showToast('Buat Video')"><span class="material-icons-outlined">video_call</span></button>
        <button class="header-icon"><span class="material-icons-outlined">notifications</span></button>
        <button class="avatar-btn">U</button>
    </div>
</header>

<nav id="sidebar">
    <div class="sidebar-item active" onclick="goHome(event)"><span class="icon-wrapper material-icons-outlined">home</span><span class="icon-wrapper material-icons">home</span><span class="sidebar-label">Beranda</span></div>
    <div class="sidebar-item" onclick="loadShorts()"><span class="icon-wrapper material-icons-outlined">play_circle</span><span class="icon-wrapper material-icons">play_circle</span><span class="sidebar-label">Shorts</span></div>
    <div class="sidebar-item" onclick="showToast('Subscription')"><span class="icon-wrapper material-icons-outlined">subscriptions</span><span class="icon-wrapper material-icons">subscriptions</span><span class="sidebar-label">Subscription</span></div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-heading hide-on-collapse">Anda ></div>
    <div class="sidebar-item" onclick="showHistory(this)"><span class="icon-wrapper material-icons-outlined">history</span><span class="icon-wrapper material-icons">history</span><span class="sidebar-label">Riwayat</span></div>
    <div class="sidebar-item" onclick="showWatchLater(this)"><span class="icon-wrapper material-icons-outlined">schedule</span><span class="icon-wrapper material-icons">schedule</span><span class="sidebar-label">Tonton nanti</span></div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-heading hide-on-collapse">Eksplorasi</div>
    <div class="sidebar-item" onclick="searchChip('Trending', this)"><span class="icon-wrapper material-icons-outlined">local_fire_department</span><span class="sidebar-label">Trending</span></div>
    <div class="sidebar-item" onclick="searchChip('Musik', this)"><span class="icon-wrapper material-icons-outlined">music_note</span><span class="sidebar-label">Musik</span></div>
    <div class="sidebar-item" onclick="searchChip('Gaming', this)"><span class="icon-wrapper material-icons-outlined">sports_esports</span><span class="sidebar-label">Gaming</span></div>
</nav>

<main id="main">
    <div class="chips-wrapper" id="chips-container">
        <div class="chips-bar" id="chips-bar">
            <button class="chip active" onclick="chipClick(this,'')">Semua</button>
            <button class="chip" onclick="chipClick(this,'Musik Indonesia')">Musik</button>
            <button class="chip" onclick="chipClick(this,'Gaming')">Gaming</button>
            <button class="chip" onclick="chipClick(this,'Live')">Live</button>
            <button class="chip" onclick="chipClick(this,'Viral 2024')">Viral</button>
            <button class="chip" onclick="chipClick(this,'Podcast Indonesia')">Podcast</button>
            <button class="chip" onclick="chipClick(this,'Komedi')">Komedi</button>
            <button class="chip" onclick="chipClick(this,'Teknologi')">Teknologi</button>
        </div>
    </div>

    <div id="player-section">
        <div class="player-container" id="player-box"></div>
        <div class="player-meta">
            <div class="player-title" id="player-title"></div>
            <div class="player-actions">
                <div class="player-actions-left">
                    <a id="player-channel-link" href="#" target="_blank" style="display:flex; align-items:center; gap:12px; text-decoration:none;">
                        <img id="player-channel-avatar" src="" style="width:40px; height:40px; border-radius:50%; object-fit:cover;">
                        <div style="display:flex; flex-direction:column;">
                            <span id="player-channel-name" style="font-weight:600; font-size:16px; color:#fff;"></span>
                            <span style="font-size:12px; color:#aaa;">Subscribe</span>
                        </div>
                    </a>
                    <button class="action-btn" style="background:#f1f1f1;color:#0f0f0f;font-weight:600;">Subscribe</button>
                    <div style="display:flex;background:rgba(255,255,255,0.1);border-radius:20px;overflow:hidden;">
                        <button class="action-btn" style="border-radius:0;background:transparent" onclick="showToast('Suka')"><span class="material-icons-outlined" style="font-size:20px">thumb_up</span></button>
                        <div style="width:1px;background:rgba(255,255,255,0.2);margin:8px 0"></div>
                        <button class="action-btn" style="border-radius:0;background:transparent" onclick="showToast('Tidak suka')"><span class="material-icons-outlined" style="font-size:20px">thumb_down</span></button>
                    </div>
                </div>
                <div class="player-actions-right">
                    <button class="action-btn" onclick="showToast('Tautan disalin!')"><span class="material-icons-outlined" style="font-size:20px">reply</span> Bagikan</button>
                    <button class="action-btn" onclick="addToWatchLater()"><span class="material-icons-outlined" style="font-size:20px">playlist_add</span> Simpan</button>
                    <button class="action-btn" onclick="toggleTheatre()"><span class="material-icons-outlined" style="font-size:20px" id="theatre-icon">crop_16_9</span></button>
                </div>
            </div>
            
            <div class="resolution-panel">
                <span class="res-label">Resolusi Video:</span>
                <button class="res-btn active" onclick="changeRes(1080, this)">1080p</button>
                <button class="res-btn" onclick="changeRes(720, this)">720p</button>
                <button class="res-btn" onclick="changeRes(480, this)">480p</button>
                <button class="res-btn" onclick="changeRes(360, this)">360p</button>
            </div>

            <div class="player-description-box" onclick="this.style.maxHeight=this.style.maxHeight==='none'?'120px':'none'">
                <div class="desc-views-date" id="player-views-date"></div>
                <div id="player-description" style="max-height:120px;overflow:hidden;"></div>
            </div>
        </div>
    </div>
    <div class="video-grid" id="video-grid"></div>
    <div id="scroll-loader"><div class="spinner"></div></div>
</main>

<!-- MINI PLAYER EXACTLY LIKE YOUTUBE -->
<div id="mini-player">
    <div class="mini-thumb" onclick="expandMiniPlayer()">
        <img id="mini-thumb-img" src="">
    </div>
    <div class="mini-info" onclick="expandMiniPlayer()">
        <div class="mini-title" id="mini-title"></div>
        <div class="mini-channel" id="mini-channel"></div>
    </div>
    <div class="mini-controls">
        <button class="mini-action" onclick="toggleMiniPlayPause()">
            <span class="material-icons-outlined" id="mini-pause-icon">pause</span>
        </button>
        <button class="mini-action" onclick="closeMiniPlayer()">
            <span class="material-icons-outlined">close</span>
        </button>
    </div>
</div>

<nav id="bottom-nav">
    <div class="nav-item active" id="bnav-home" onclick="goHome(event)"><span class="material-icons-outlined">home</span><span class="material-icons">home</span><span class="nav-label">Beranda</span></div>
    <div class="nav-item" id="bnav-shorts" onclick="loadShorts()"><span class="material-icons-outlined">play_circle</span><span class="material-icons">play_circle</span><span class="nav-label">Shorts</span></div>
    <div class="nav-item" onclick="showToast('Buat')"><span class="material-icons-outlined" style="font-size: 36px; font-weight: 200;">add_circle_outline</span></div>
    <div class="nav-item" id="bnav-subs" onclick="showToast('Subscription')"><span class="material-icons-outlined">subscriptions</span><span class="material-icons">subscriptions</span><span class="nav-label">Subscription</span></div>
    <div class="nav-item" id="bnav-you" onclick="showHistory(null)"><span class="material-icons-outlined">video_library</span><span class="material-icons">video_library</span><span class="nav-label">Anda</span></div>
</nav>

<div id="toast"></div>

<script>
    let sidebarOpen = window.innerWidth > 792;
    let isTheatreMode = false;
    let currentPlayingVideo = null;
    let currentRes = 1080;
    let isMiniActive = false;
    
    let currentQuery = '';
    let currentOffset = 0;
    let isLoadingMore = false;
    let hasMoreData = true;

    window.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => document.getElementById('splash').classList.add('hide'), 600);
        loadHome();
        window.addEventListener('scroll', handleInfiniteScroll);
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.header-center')) document.getElementById('suggestion-box').classList.remove('show');
        });
    });

    function handleInfiniteScroll() {
        if (isLoadingMore || !hasMoreData || !currentQuery) return;
        const scrollY = window.scrollY || window.pageYOffset;
        if (scrollY + window.innerHeight >= document.documentElement.scrollHeight - 600) loadMoreData();
    }

    async function loadMoreData() {
        isLoadingMore = true;
        document.getElementById('scroll-loader').classList.add('show');
        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(currentQuery)}&offset=${currentOffset}`);
            const data = await res.json();
            if (data.length === 0) hasMoreData = false;
            else { currentOffset += data.length; appendToGrid(data); }
        } catch (e) {} 
        finally { isLoadingMore = false; document.getElementById('scroll-loader').classList.remove('show'); }
    }

    function toggleSidebar() {
        const sb = document.getElementById('sidebar'), mn = document.getElementById('main'), ov = document.getElementById('overlay');
        if (window.innerWidth <= 792) { sb.classList.toggle('mobile-open'); ov.classList.toggle('show'); } 
        else { sidebarOpen = !sidebarOpen; sb.classList.toggle('collapsed'); mn.classList.toggle('expanded'); }
    }

    function showToast(msg) {
        const t = document.getElementById('toast'); t.textContent = msg; t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 3000);
    }

    function goHome(e) {
        if (e) e.preventDefault();
        document.getElementById('keyword').value = '';
        document.getElementById('chips-container').style.display = 'block';
        closeMiniPlayer(); hidePlayer();
        document.querySelectorAll('.chip').forEach((c,i) => c.classList.toggle('active', i === 0));
        document.querySelectorAll('.sidebar-item').forEach((el, i) => el.classList.toggle('active', i === 0));
        currentQuery = ''; currentOffset = 0; hasMoreData = true;
        loadHome();
        if (window.innerWidth <= 792) { document.getElementById('sidebar').classList.remove('mobile-open'); document.getElementById('overlay').classList.remove('show'); }
    }

    function saveToHistory(video) {
        let history = JSON.parse(localStorage.getItem('yt_history') || '[]');
        history = history.filter(v => v.id !== video.id);
        history.unshift(video); if(history.length > 50) history.pop();
        localStorage.setItem('yt_history', JSON.stringify(history));
    }

    function addToWatchLater() {
        if(!currentPlayingVideo) return;
        let wl = JSON.parse(localStorage.getItem('yt_watch_later') || '[]');
        if(!wl.find(v => v.id === currentPlayingVideo.id)) { wl.unshift(currentPlayingVideo); localStorage.setItem('yt_watch_later', JSON.stringify(wl)); showToast('Disimpan ke Tonton Nanti!'); }
        else showToast('Sudah ada di Tonton Nanti');
    }

    function showHistory(sidebarEl) {
        document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
        if(sidebarEl) sidebarEl.classList.add('active');
        document.getElementById('chips-container').style.display = 'none'; closeMiniPlayer(); hidePlayer(); currentQuery = '';
        renderGrid(JSON.parse(localStorage.getItem('yt_history') || '[]'), false, 'Riwayat Tontonan', 'history');
    }

    function showWatchLater(sidebarEl) {
        document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
        if(sidebarEl) sidebarEl.classList.add('active');
        document.getElementById('chips-container').style.display = 'none'; closeMiniPlayer(); hidePlayer(); currentQuery = '';
        renderGrid(JSON.parse(localStorage.getItem('yt_watch_later') || '[]'), false, 'Tonton Nanti', 'schedule');
    }

    function loadShorts() {
        document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
        document.getElementById('chips-container').style.display = 'none'; closeMiniPlayer(); hidePlayer(); showSkeletons(); currentQuery = '__shorts__';
        fetch('/api/shorts').then(res => res.json()).then(data => renderGrid(data, true, 'Shorts', 'play_circle')).catch(() => showError('Gagal memuat Shorts.'));
    }

    function chipClick(btn, query) {
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active')); btn.classList.add('active');
        document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
        if (query) { document.getElementById('keyword').value = query; doSearch(query); } else goHome();
    }

    function searchChip(query, sidebarEl) {
        document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active')); if(sidebarEl) sidebarEl.classList.add('active');
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        document.getElementById('chips-container').style.display = 'block'; document.getElementById('keyword').value = query; doSearch(query);
    }

    function searchVideos(e) {
        e.preventDefault(); const q = document.getElementById('keyword').value.trim(); if (!q) { goHome(); return; }
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active')); document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
        document.getElementById('suggestion-box').classList.remove('show'); doSearch(q);
    }

    async function doSearch(query) {
        closeMiniPlayer(); hidePlayer(); showSkeletons(); currentQuery = query; currentOffset = 0; hasMoreData = true;
        try { const res = await fetch('/api/search?q=' + encodeURIComponent(query)); const data = await res.json(); currentOffset = data.length; renderGrid(data); } catch (e) { showError('Gagal memuat hasil pencarian.'); }
    }

    async function loadHome() {
        closeMiniPlayer(); hidePlayer(); showSkeletons(); currentQuery = '';
        try { const res = await fetch('/api/home'); const data = await res.json(); renderGrid(data); } catch (e) { showError('Gagal memuat beranda.'); }
    }

    let suggestTimeout;
    async function fetchSuggestions() {
        const input = document.getElementById('keyword'), box = document.getElementById('suggestion-box'), q = input.value.trim();
        if (!q) { box.classList.remove('show'); return; }
        clearTimeout(suggestTimeout);
        suggestTimeout = setTimeout(async () => {
            try { const res = await fetch('/api/suggest?q=' + encodeURIComponent(q)); const suggestions = await res.json();
                if (suggestions.length > 0) { box.innerHTML = suggestions.map(s => `<div class="suggestion-item" onclick="selectSuggestion('${escHtml(s)}')"><span class="material-icons-outlined">search</span><span>${escHtml(s)}</span></div>`).join(''); box.classList.add('show'); } else box.classList.remove('show');
            } catch(e) { box.classList.remove('show'); }
        }, 300);
    }
    function selectSuggestion(val) { document.getElementById('keyword').value = val; document.getElementById('suggestion-box').classList.remove('show'); searchVideos(new Event('submit')); }

    function playVideo(videoStr) {
        let v; try { v = JSON.parse(decodeURIComponent(videoStr)); } catch(e) { return; }
        currentPlayingVideo = v; saveToHistory(v);
        
        const ps = document.getElementById('player-section');
        ps.classList.remove('theatre'); isTheatreMode = false;

        document.getElementById('player-title').textContent = v.title;
        
        const iframeSrc = `https://www.youtube-nocookie.com/embed/${v.id}?autoplay=1&rel=0&vq=${currentRes}`;
        document.getElementById('player-box').innerHTML = `<iframe id="yt-iframe" src="${iframeSrc}" allow="autoplay;encrypted-media;picture-in-picture" allowfullscreen></iframe>`;
        
        document.getElementById('player-channel-link').href = v.channelUrl ? "https://www.youtube.com" + v.channelUrl : "#";
        document.getElementById('player-channel-avatar').src = v.avatar || '';
        document.getElementById('player-channel-name').textContent = v.channel;
        document.getElementById('player-views-date').textContent = [v.views, v.published].filter(Boolean).join(' • ');
        document.getElementById('player-description').textContent = v.description || 'Tidak ada deskripsi.';

        ps.style.display = 'block'; requestAnimationFrame(() => ps.classList.add('show'));
        
        // Setup Mini Player Data
        document.getElementById('mini-thumb-img').src = `https://i.ytimg.com/vi/${v.id}/mqdefault.jpg`;
        document.getElementById('mini-title').textContent = v.title;
        document.getElementById('mini-channel').textContent = v.channel;
        document.getElementById('mini-pause-icon').textContent = 'pause';

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function changeRes(res, btn) {
        currentRes = res;
        document.querySelectorAll('.res-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const iframe = document.getElementById('yt-iframe');
        if(iframe) {
            let src = iframe.src.split('&vq=')[0]; // remove old vq
            iframe.src = src + '&vq=' + res; // apply new
        }
        showToast(`Resolusi diatur ke ${res}p`);
    }

    function toggleTheatre() {
        const ps = document.getElementById('player-section'), icon = document.getElementById('theatre-icon');
        isTheatreMode = !isTheatreMode;
        if(isTheatreMode) { ps.classList.add('theatre'); icon.textContent = 'fullscreen_exit'; } 
        else { ps.classList.remove('theatre'); icon.textContent = 'crop_16_9'; }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function hidePlayer() {
        const ps = document.getElementById('player-section'); ps.classList.remove('show', 'theatre');
        setTimeout(() => { ps.style.display = 'none'; document.getElementById('player-box').innerHTML = ''; }, 300);
    }

    // MINI PLAYER LOGIC
    function expandMiniPlayer() {
        closeMiniPlayer();
        playVideo(encodeURIComponent(JSON.stringify(currentPlayingVideo)));
    }

    function toggleMiniPlayPause() {
        const icon = document.getElementById('mini-pause-icon');
        const iframe = document.getElementById('yt-iframe');
        if(icon.textContent === 'pause') {
            icon.textContent = 'play_arrow';
            if(iframe) iframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
        } else {
            icon.textContent = 'pause';
            if(iframe) iframe.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
        }
    }

    function closeMiniPlayer() {
        isMiniActive = false;
        document.getElementById('mini-player').classList.remove('show');
        document.getElementById('main').classList.remove('mini-open');
        const iframe = document.getElementById('yt-iframe');
        if(iframe) iframe.contentWindow.postMessage('{"event":"command","func":"stopVideo","args":""}', '*');
        hidePlayer();
    }

    // Listen to scroll to activate mini player
    window.addEventListener('scroll', () => {
        if(!currentPlayingVideo || isTheatreMode) return;
        const ps = document.getElementById('player-section');
        if(!ps.classList.contains('show')) return;

        const rect = ps.getBoundingClientRect();
        // If player is scrolled out of view significantly
        if(rect.bottom < -200 && !isMiniActive) {
            isMiniActive = true;
            document.getElementById('mini-player').classList.add('show');
            document.getElementById('main').classList.add('mini-open');
            hidePlayer(); // Hide the big player but keep iframe logic in mini
        }
    });

    function showSkeletons() { document.getElementById('video-grid').innerHTML = Array(8).fill(`<div class="skel-card"><div class="skel-thumb"></div><div class="skel-info"><div class="skel-avatar"></div><div class="skel-lines"><div class="skel-line"></div><div class="skel-line short"></div></div></div></div>`).join(''); }
    function showError(msg) { document.getElementById('video-grid').innerHTML = `<div class="empty-state"><span class="material-icons-outlined">error_outline</span><p>${msg}</p></div>`; }

    function renderGrid(data, isShortsMode = false, pageTitle = null, iconName = '') {
        const g = document.getElementById('video-grid'); g.innerHTML = '';
        if(pageTitle) { const titleEl = document.createElement('div'); titleEl.className = 'page-title'; titleEl.innerHTML = (iconName ? `<span class="material-icons-outlined">${iconName}</span> ` : '') + pageTitle; g.appendChild(titleEl); }
        if (!data || data.length === 0) { g.innerHTML += '<div class="empty-state"><span class="material-icons-outlined">search_off</span><p>Tidak ada video ditemukan.</p></div>'; return; }
        g.style.gridTemplateColumns = isShortsMode ? "repeat(auto-fill, minmax(180px, 1fr))" : "";
        appendToGrid(data, isShortsMode);
    }

    function appendToGrid(data, isShortsMode = false) {
        const g = document.getElementById('video-grid');
        data.forEach(v => {
            const card = document.createElement('div'); card.className = 'vid-card';
            const vStr = encodeURIComponent(JSON.stringify(v)); card.onclick = () => playVideo(vStr);
            let dur = v.duration || '', channelName = v.channel || '', views = v.views || '', published = v.published || '', avatarUrl = v.avatar || '', initial = channelName ? channelName.charAt(0).toUpperCase() : '?';
            let cUrl = v.channelUrl ? "https://www.youtube.com" + v.channelUrl : "#";
            let avatarHtml = avatarUrl ? `<a href="${cUrl}" target="_blank" onclick="event.stopPropagation()" class="channel-avatar"><img src="${avatarUrl}" onerror="this.style.display='none'"></a>` : `<a href="${cUrl}" target="_blank" onclick="event.stopPropagation()" class="channel-avatar" style="display:flex;align-items:center;justify-content:center;font-size:16px;">${initial}</a>`;
            let channelHtml = `<a href="${cUrl}" target="_blank" onclick="event.stopPropagation()" class="vid-channel">${escHtml(channelName)}</a>`;
            let metaStr = [views, published].filter(Boolean).join(' • '), thumbUrl = `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`, aspectStyle = isShortsMode ? 'aspect-ratio: 9/16;' : 'aspect-ratio: 16/9;';
            card.innerHTML = `<div class="thumb-wrap" style="${aspectStyle}"><img class="thumb-img" src="${thumbUrl}" loading="lazy" alt="">${dur ? '<span class="duration-badge">' + dur + '</span>' : ''}</div><div class="vid-info">${isShortsMode ? '' : avatarHtml}<div class="vid-text"><div class="vid-title">${escHtml(v.title)}</div>${isShortsMode ? '' : channelHtml}<div class="vid-meta">${escHtml(metaStr)}</div></div></div>`;
            g.appendChild(card);
        });
    }

    function escHtml(s) { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }
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
            data["channelUrl"] = run.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", "")
    except Exception: 
        data["channel"] = ""; data["channelUrl"] = ""
    try:
        avatar_thumbs = video.get("channelThumbnailSupportedRenderers", {}).get("channelThumbnailWithLinkRenderer", {}).get("thumbnail", {}).get("thumbnails", [])
        if avatar_thumbs: data["avatar"] = avatar_thumbs[0].get("url", "")
    except Exception: 
        data["avatar"] = ""
    try:
        desc_runs = video.get("detailedMetadataSnippets", [{}])[0].get("snippetText", {}).get("runs", [])
        if not desc_runs: desc_runs = video.get("descriptionSnippet", {}).get("runs", [])
        data["description"] = "".join([r.get("text", "") for r in desc_runs]) if desc_runs else ""
    except Exception: data["description"] = ""
    return data

@app.route("/")
def home(): return render_template_string(HTML_TEMPLATE)

@app.route("/api/home")
def api_home():
    """ Generates a random viral/hits feed like real YouTube Home """
    results = []
    try:
        # Mix trending and random viral searches
        base_keywords = ["Viral 2024", "Hits Indonesia", "Populer Hari Ini", "Trending Video"]
        random_keyword = random.choice(base_keywords)
        
        videos = scrapetube.get_search(random_keyword, limit=30)
        for v in videos:
            d = extract_video_data(v)
            if d.get("id"): results.append(d)
                
        # Add some global trending too
        try:
            trending = scrapetube.get_trending("ID", limit=10)
            for v in trending:
                d = extract_video_data(v)
                if d.get("id") and not any(r["id"] == d["id"] for r in results): results.insert(random.randint(0, 10), d)
        except: pass
            
        # Shuffle for randomness like YT home
        random.shuffle(results)
    except Exception: pass
    return jsonify(results)

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    offset = int(request.args.get("offset", 0))
    limit = 20; results = []
    if not query: return jsonify(results)
    try:
        videos = scrapetube.get_search(query, limit=offset+limit)
        for i, v in enumerate(videos):
            if i >= offset:
                d = extract_video_data(v)
                if d.get("id"): results.append(d)
    except Exception: pass
    return jsonify(results)

@app.route("/api/shorts")
def api_shorts():
    results = []
    try:
        videos = scrapetube.get_search("shorts viral #shorts", limit=60)
        for v in videos:
            d = extract_video_data(v); dur_text = d.get("duration", ""); is_short = False
            if dur_text:
                parts = dur_text.split(":")
                if len(parts) == 1: is_short = True
                elif len(parts) == 2 and int(parts[0]) == 0 and int(parts[1]) <= 60: is_short = True
            if is_short and d.get("id"):
                if not any(r["id"] == d["id"] for r in results): results.append(d)
            if len(results) >= 20: break
    except Exception: pass
    return jsonify(results)

@app.route("/api/suggest")
def api_suggest():
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2: return jsonify([])
    suggestions = set()
    try:
        videos = scrapetube.get_search(query, limit=5)
        for v in videos:
            title = v.get("title", {}).get("runs", [{}])[0].get("text", "")
            if title and query.lower() in title.lower(): suggestions.add(title)
            byline = v.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
            if byline and query.lower() in byline.lower(): suggestions.add(byline)
    except Exception: pass
    return jsonify(list(suggestions)[:7])

if __name__ == "__main__":
    app.run(debug=True, port=2000)
