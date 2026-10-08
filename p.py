from flask import Flask, jsonify, render_template_string, request
import scrapetube
import random
import json
import logging
from functools import lru_cache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0f0f0f">
    <title>YouTube Premium Clone</title>
    <link rel="manifest" href="/manifest.json?v=13">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #0f0f0f; color: #f1f1f1; overflow-x: hidden; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #717171; border-radius: 4px; }
        a { text-decoration: none; color: inherit; }

        /* ===== HEADER ===== */
        #header { position: fixed; top: 0; left: 0; right: 0; height: 56px; background: #0f0f0f; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 100; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .header-left { display: flex; align-items: center; gap: 16px; }
        .yt-logo { display: flex; align-items: center; gap: 4px; cursor: pointer; user-select: none; }
        .yt-logo-text { font-size: 20px; font-weight: 700; letter-spacing: -1px; margin-left: 2px; }
        
        .header-right { display: flex; align-items: center; gap: 12px; }
        .header-icon { background: transparent; border: none; color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; padding: 10px; border-radius: 50%; min-width: 44px; min-height: 44px; }
        .header-icon:hover { background: rgba(255,255,255,0.1); }
        .header-icon .material-icons-outlined { font-size: 24px; }
        
        /* Search Form Desktop */
        .search-form-desktop { display: flex; flex: 1; max-width: 600px; align-items: center; margin: 0 40px; }
        .search-input-wrap-desk { flex: 1; display: flex; align-items: center; border: 1px solid #303030; border-right: none; border-radius: 20px 0 0 20px; background: #121212; height: 40px; padding: 0 16px; }
        .search-input-wrap-desk input { width: 100%; background: transparent; border: none; color: #fff; font-size: 16px; outline: none; }
        .search-btn-desk { height: 40px; width: 64px; border: 1px solid #303030; border-radius: 0 20px 20px 0; background: #222; color: #fff; cursor: pointer; }
        
        /* Search Form Mobile */
        .search-form-mobile { display: none; position: absolute; inset: 0; background: #0f0f0f; padding: 0 12px; align-items: center; gap: 12px; z-index: 110; }
        .search-form-mobile.active { display: flex; }
        .search-input-wrap-mob { flex: 1; display: flex; align-items: center; background: #222; border-radius: 20px; padding: 0 16px; height: 38px; }
        .search-input-wrap-mob input { flex: 1; background: transparent; border: none; color: #fff; font-size: 15px; outline: none; }
        .search-btn-mobile-toggle { display: none; background: transparent; border: none; color: #fff; cursor: pointer; padding: 8px; min-width: 44px; min-height: 44px; }

        /* ===== SIDEBAR (DESKTOP) ===== */
        #sidebar { position: fixed; top: 56px; left: 0; width: 240px; height: calc(100vh - 56px); background: #0f0f0f; overflow-y: auto; padding: 12px 0; z-index: 90; }
        .sidebar-item { display: flex; align-items: center; gap: 24px; padding: 0 12px; height: 40px; cursor: pointer; border-radius: 10px; margin: 0 12px; transition: background 0.15s; }
        .sidebar-item:hover { background: rgba(255,255,255,0.1); }
        .sidebar-item.active { background: rgba(255,255,255,0.15); font-weight: 500; }
        .sidebar-item .material-icons-outlined { font-size: 24px; flex-shrink: 0; }
        .sidebar-label { font-size: 14px; }
        .sidebar-divider { height: 1px; background: rgba(255,255,255,0.1); margin: 12px 0; }

        /* ===== BOTTOM NAV (MOBILE) ===== */
        #bottom-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; height: 50px; background: #0f0f0f; border-top: 1px solid rgba(255,255,255,0.05); z-index: 100; justify-content: space-around; align-items: center; }
        .nav-item { display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; flex: 1; height: 100%; cursor: pointer; min-width: 44px; min-height: 44px; }
        .nav-item .material-icons-outlined, .nav-item .material-icons { font-size: 24px; }
        .nav-item .nav-label { font-size: 10px; margin-top: 3px; }
        .nav-avatar { width: 24px; height: 24px; border-radius: 50%; background: #ff4e45; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; border: 2px solid transparent; overflow: hidden; }
        .nav-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .nav-item.active .nav-avatar { border-color: #fff; }

        /* ===== MAIN CONTENT & GRID ===== */
        #main { margin-left: 240px; margin-top: 56px; padding: 24px; min-height: 100vh; }
        
        .chips-wrapper { position: sticky; top: 56px; background: #0f0f0f; z-index: 10; padding: 12px 0; margin-bottom: 24px; }
        .chips-bar { display: flex; gap: 10px; overflow-x: auto; scrollbar-width: none; }
        .chips-bar::-webkit-scrollbar { display: none; }
        .chip { padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; white-space: nowrap; border: none; background: #272727; color: #f1f1f1; cursor: pointer; min-height: 40px; }
        .chip.active { background: #f1f1f1; color: #0f0f0f; }

        .video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 40px 16px; }
        
        .vid-card { cursor: pointer; display: flex; flex-direction: column; gap: 12px; }
        .thumb-wrap { position: relative; width: 100%; aspect-ratio: 16/9; background: #272727; border-radius: 12px; overflow: hidden; }
        .thumb-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
        .vid-card:hover .thumb-img { transform: scale(1.05); }
        .duration-badge { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: #fff; font-size: 12px; font-weight: 500; padding: 3px 6px; border-radius: 4px; }
        
        .vid-info { display: flex; gap: 12px; align-items: flex-start; }
        .channel-avatar { width: 36px; height: 36px; border-radius: 50%; background: #444; flex-shrink: 0; overflow: hidden; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:bold; }
        .channel-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .vid-text { flex: 1; }
        .vid-title { font-size: 16px; font-weight: 500; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; }
        .vid-meta { font-size: 14px; color: #aaa; }

        /* ===== PLAYER SECTION ===== */
        #player-section { display: none; margin-left: 240px; margin-top: 56px; padding: 24px; max-width: 1500px; }
        .player-layout { display: grid; grid-template-columns: 1fr 400px; gap: 24px; }
        
        .player-main-col { width: 100%; }
        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; overflow: hidden; }
        .player-container iframe { width: 100%; height: 100%; border: none; display: block; }
        
        .player-meta { padding: 16px 0; }
        .player-title { font-size: 20px; font-weight: 700; margin-bottom: 12px; }
        
        .channel-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; margin-bottom: 16px; }
        .channel-info { display: flex; align-items: center; gap: 12px; }
        .channel-name { font-weight: 600; font-size: 16px; }
        .btn-subscribe { background: #f1f1f1; color: #0f0f0f; font-weight: 600; border: none; padding: 10px 20px; border-radius: 20px; font-size: 14px; cursor: pointer; min-height: 40px; }
        
        .action-row { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 4px; }
        .action-pill { display: flex; align-items: center; gap: 6px; background: #272727; padding: 10px 18px; border-radius: 20px; font-size: 14px; font-weight: 500; cursor: pointer; white-space: nowrap; min-height: 40px; }
        .action-pill:hover { background: #3f3f3f; }
        
        .comments-box { background: #272727; border-radius: 12px; padding: 16px; margin-top: 16px; }

        /* Related Videos Column */
        .related-col { display: flex; flex-direction: column; gap: 12px; }
        .related-title { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
        .related-card { display: flex; gap: 8px; cursor: pointer; }
        .related-thumb { width: 168px; aspect-ratio: 16/9; background: #272727; border-radius: 8px; overflow: hidden; flex-shrink: 0; position: relative; }
        .related-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .related-info { flex: 1; display: flex; flex-direction: column; gap: 4px; }
        .related-vid-title { font-size: 14px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.3; }
        .related-vid-channel, .related-vid-meta { font-size: 12px; color: #aaa; }

        /* ===== PROFILE TAB ===== */
        #profile-section { display: none; margin-left: 240px; margin-top: 56px; padding: 24px; min-height: 100vh; }
        .profile-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
        .profile-avatar-wrap { position: relative; width: 72px; height: 72px; cursor: pointer; border-radius: 50%; overflow: hidden; background: #ff4e45; color: #fff; font-size: 32px; display: flex; align-items: center; justify-content: center; border: 2px dashed rgba(255,255,255,0.4); }
        .profile-avatar-wrap img { width: 100%; height: 100%; object-fit: cover; }
        .profile-avatar-wrap:hover::after { content: 'Ubah'; position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; }
        .profile-name { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
        .profile-handle { font-size: 14px; color: #aaa; margin-bottom: 12px; }
        .profile-btn { background: #272727; border: none; color: #fff; padding: 8px 16px; border-radius: 16px; font-size: 13px; font-weight: 500; cursor: pointer; min-height: 36px; }
        
        .horizontal-list { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 16px; scrollbar-width: none; }
        .horizontal-list::-webkit-scrollbar { display: none; }
        .hist-card { width: 160px; flex-shrink: 0; cursor: pointer; }
        .hist-thumb { width: 100%; aspect-ratio: 16/9; background: #272727; border-radius: 8px; margin-bottom: 8px; object-fit: cover; }
        .hist-title { font-size: 14px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; }
        .hist-channel { font-size: 13px; color: #aaa; }
        
        /* Scroll to Top Button */
        #scrollTopBtn { display: none; position: fixed; bottom: 70px; right: 20px; background: #272727; color: #fff; border: none; width: 44px; height: 44px; border-radius: 50%; align-items: center; justify-content: center; cursor: pointer; z-index: 99; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        #scrollTopBtn:hover { background: #3f3f3f; }

        /* Loaders */
        .loader-container { display: none; justify-content: center; padding: 20px 0; width: 100%; }
        .spinner { width: 32px; height: 32px; border: 3px solid #333; border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .skeleton-card { display: flex; gap: 8px; margin-bottom: 12px; }
        .skeleton-thumb { width: 168px; aspect-ratio: 16/9; background: #272727; border-radius: 8px; animation: pulse 1.5s infinite; }
        .skeleton-info { flex: 1; }
        .skeleton-line { height: 12px; background: #272727; border-radius: 4px; margin-bottom: 8px; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

        /* =========================================
           MEDIA QUERIES (MODE HP / MOBILE)
           ========================================= */
        @media (max-width: 900px) {
            .player-layout { grid-template-columns: 1fr; }
        }

        @media (max-width: 792px) {
            #sidebar { display: none; }
            #bottom-nav { display: flex; }
            
            #main { margin-left: 0; padding: 0; padding-bottom: 60px; }
            .chips-wrapper { padding: 12px 16px; margin-bottom: 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
            
            .search-form-desktop { display: none; }
            .search-btn-mobile-toggle { display: block; }
            
            .video-grid { display: flex; flex-direction: column; gap: 0; }
            .vid-card { margin-bottom: 16px; gap: 12px; }
            .thumb-wrap { border-radius: 0; }
            .vid-info { padding: 0 16px; }
            .vid-title { font-size: 15px; }
            .vid-meta { font-size: 13px; }
            
            #player-section { margin-left: 0; margin-top: 0; padding: 0; padding-bottom: 60px; max-width: 100%; width: 100%; overflow: hidden; }
            /* DIPERBAIKI: Mengunci lebar player container agar tidak melebihi layar HP */
            .player-container { width: 100%; max-width: 100vw; border-radius: 0; position: sticky; top: 56px; z-index: 95; }
            .player-meta { padding: 12px 16px; }
            .player-title { font-size: 18px; }
            .related-col { padding: 0 16px; }

            #profile-section { margin-left: 0; padding: 0; padding-bottom: 60px; }
            .profile-header { padding: 24px 16px; margin-bottom: 0; }
            .horizontal-list { padding: 0 16px 16px; }
            #scrollTopBtn { bottom: 65px; right: 15px; }
        }
    </style>
</head>
<body>

<header id="header">
    <div class="header-left">
        <a class="yt-logo" href="#" onclick="goHome(event, document.querySelector('.nav-item'))">
            <svg viewBox="0 0 24 24" style="height:22px; color:#FF0000; fill:currentColor;"><path d="M21.58,7.19C21.35,6.33 20.67,5.65 19.81,5.42C18.25,5 12,5 12,5C12,5 5.75,5 4.19,5.42C3.33,5.65 2.65,6.33 2.42,7.19C2,8.75 2,12 2,12C2,12 2,15.25 2.42,16.81C2.65,17.67 3.33,18.35 4.19,18.58C5.75,19 12,19 12,19C12,19 18.25,19 19.81,18.58C20.67,18.35 21.35,17.67 21.58,16.81C22,15.25 22,12 22,12C22,12 22,8.75 21.58,7.19Z"/><path d="M10,15L15.5,12L10,9V15Z" fill="white"/></svg>
            <span class="yt-logo-text">Premium</span>
        </a>
    </div>

    <form class="search-form-desktop" onsubmit="searchVideos(event, 'desktop')">
        <div class="search-input-wrap-desk"><input type="text" id="keyword-desktop" placeholder="Telusuri" autocomplete="off"></div>
        <button type="submit" class="search-btn-desk"><span class="material-icons-outlined">search</span></button>
        <button type="button" class="header-icon" style="background:#181818; margin-left:12px;"><span class="material-icons-outlined">mic</span></button>
    </form>

    <div class="header-right">
        <button class="search-btn-mobile-toggle" onclick="toggleMobileSearch(true)"><span class="material-icons-outlined">search</span></button>
        <button class="header-icon" id="installAppBtn" style="display:none; color:#3ea6ff;" title="Instal Aplikasi"><span class="material-icons-outlined">install_mobile</span></button>
        <div class="nav-avatar global-avatar-disp" style="margin-left:8px; width:32px; height:32px; cursor:pointer;" onclick="showProfile(document.querySelectorAll('.nav-item')[1])">t</div>
    </div>
    
    <form class="search-form-mobile" id="mobile-search-form" onsubmit="searchVideos(event, 'mobile')">
        <button type="button" class="header-icon" onclick="toggleMobileSearch(false)"><span class="material-icons-outlined">arrow_back</span></button>
        <div class="search-input-wrap-mob">
            <input type="text" id="keyword-mobile" placeholder="Telusuri YouTube" autocomplete="off">
        </div>
        <button type="submit" class="header-icon"><span class="material-icons-outlined">search</span></button>
        <button type="button" class="header-icon" style="background:#222; border-radius:50%; width:36px; height:36px;"><span class="material-icons-outlined" style="font-size:20px;">mic</span></button>
    </form>
</header>

<nav id="sidebar">
    <div class="sidebar-item active" onclick="goHome(event)"><span class="material-icons-outlined">home</span><span class="sidebar-label">Beranda</span></div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-item" onclick="showProfile(this)"><span class="material-icons-outlined">history</span><span class="sidebar-label">Histori</span></div>
</nav>

<main id="main">
    <div class="chips-wrapper" id="chips-container">
        <div class="chips-bar">
            <button class="chip active" onclick="chipClick(this,'')">Semua</button>
            <button class="chip" onclick="chipClick(this,'Musik')">Musik</button>
            <button class="chip" onclick="chipClick(this,'Gaming')">Gaming</button>
            <button class="chip" onclick="chipClick(this,'Berita')">Berita</button>
            <button class="chip" onclick="chipClick(this,'Live')">Live</button>
        </div>
    </div>
    <div class="video-grid" id="video-grid"></div>
    <div class="loader-container" id="main-scroll-loader"><div class="spinner"></div></div>
</main>

<div id="player-section">
    <div class="player-layout">
        <div class="player-main-col">
            <div class="player-container" id="player-box"></div>
            <div class="player-meta">
                <div class="player-title" id="player-title">Judul Video</div>
                <div class="channel-row">
                    <div class="channel-info">
                        <img id="player-channel-avatar" src="" style="width:40px; height:40px; border-radius:50%; object-fit:cover; background:#444;">
                        <div>
                            <div class="channel-name" id="player-channel-name">Nama Channel</div>
                            <div style="font-size: 12px; color: #aaa;">1,2 jt subscriber</div>
                        </div>
                    </div>
                    <button class="btn-subscribe">Subscribe</button>
                </div>
                <div class="action-row">
                    <div class="action-pill"><span class="material-icons-outlined">thumb_up</span> Suka</div>
                    <div class="action-pill"><span class="material-icons-outlined">thumb_down</span></div>
                    <div class="action-pill"><span class="material-icons-outlined">reply</span> Bagikan</div>
                    <div class="action-pill" onclick="alert('Mengunduh video dalam kualitas tinggi... (Fitur Premium Aktif)')"><span class="material-icons-outlined">download</span> Download</div>
                </div>
                <div class="comments-box">
                    <div style="font-weight:700; margin-bottom:8px; font-size:14px;">Komentar <span style="font-weight:400; color:#aaa;">245</span></div>
                    <div style="display:flex; gap:10px; font-size:13px;">
                        <div style="width:24px; height:24px; border-radius:50%; background:#555;"></div>
                        <div style="flex:1;">Tulis komentar...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="related-col">
            <div class="related-title">Video Serupa</div>
            <div id="related-videos-container" style="display: flex; flex-direction: column; gap: 10px;"></div>
            <div class="loader-container" id="related-scroll-loader"><div class="spinner"></div></div>
        </div>
    </div>
</div>

<div id="profile-section">
    <div class="profile-header">
        <div class="profile-avatar-wrap" onclick="document.getElementById('avatar-file-input').click()" title="Ketuk untuk ganti foto profil">
            <div id="profile-avatar-inner" style="width:100%; height:100%; display:flex; align-items:center; justify-content:center;">t</div>
        </div>
        <input type="file" id="avatar-file-input" accept="image/*" style="display:none" onchange="handleAvatarUpload(event)">
        <div>
            <div class="profile-name">teu apal</div>
            <div class="profile-handle">@teuapal • <span style="color: #ff4e45; font-weight: 500;">Anggota Premium</span></div>
            <button class="profile-btn" onclick="document.getElementById('avatar-file-input').click()">Ganti Foto Profil</button>
        </div>
    </div>
    <div style="padding: 16px; font-size: 18px; font-weight: 700;">Histori</div>
    <div class="horizontal-list" id="history-scroll"></div>
</div>

<button id="scrollTopBtn" onclick="scrollToTop()"><span class="material-icons-outlined">arrow_upward</span></button>

<nav id="bottom-nav">
    <div class="nav-item active" onclick="goHome(event, this)"><span class="material-icons-outlined">home</span><span class="nav-label">Beranda</span></div>
    <div class="nav-item" onclick="showProfile(this)"><div class="nav-avatar global-avatar-disp">t</div><span class="nav-label">Anda</span></div>
</nav>

<script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js?v=13').then(reg => {
                reg.update();
            });
        });
    }

    let deferredPrompt;
    const installBtn = document.getElementById('installAppBtn');

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        installBtn.style.display = 'block';
    });

    installBtn.addEventListener('click', async () => {
        if (deferredPrompt !== null) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            if (outcome === 'accepted') {
                console.log('User menginstal aplikasi');
            }
            deferredPrompt = null;
            installBtn.style.display = 'none';
        }
    });

    window.addEventListener('appinstalled', () => {
        installBtn.style.display = 'none';
    });

    let currentQuery = '';
    let currentOffset = 0;
    let isLoadingMore = false;
    
    let currentRelatedKeyword = '';
    let currentRelatedOffset = 0;
    let isRelatedLoading = false;
    
    window.addEventListener('DOMContentLoaded', () => { 
        loadCustomAvatar();
        history.replaceState({view: 'home'}, '', '');
        loadHome(); 
    });

    window.addEventListener('popstate', (e) => {
        isLoadingMore = false;
        isRelatedLoading = false;
        if (e.state && e.state.view === 'player') {
            playVideo(e.state.video, false);
        } else if (e.state && e.state.view === 'profile') {
            showProfile(document.querySelectorAll('.nav-item')[1], false);
        } else {
            goHome(null, document.querySelector('.nav-item'), false);
        }
    });
    
    window.addEventListener('scroll', () => {
        const scrollTopBtn = document.getElementById('scrollTopBtn');
        if (window.scrollY > 400) {
            scrollTopBtn.style.display = 'flex';
        } else {
            scrollTopBtn.style.display = 'none';
        }

        if (!isLoadingMore && document.getElementById('main').style.display === 'block') {
            if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300) {
                loadMoreData();
            }
        }
        else if (!isRelatedLoading && document.getElementById('player-section').style.display === 'block') {
            if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300) {
                loadMoreRelated();
            }
        }
    });

    function scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function handleAvatarUpload(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64Image = e.target.result;
                localStorage.setItem('yt_custom_avatar', base64Image);
                applyCustomAvatar(base64Image);
            };
            reader.readAsDataURL(file);
        }
    }

    function loadCustomAvatar() {
        const savedAvatar = localStorage.getItem('yt_custom_avatar');
        if (savedAvatar) {
            applyCustomAvatar(savedAvatar);
        }
    }

    function applyCustomAvatar(imgSrc) {
        const avatarElements = document.querySelectorAll('.global-avatar-disp');
        avatarElements.forEach(el => {
            el.innerHTML = `<img src="${imgSrc}" alt="Avatar" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
        });
        
        const profileInner = document.getElementById('profile-avatar-inner');
        if (profileInner) {
            profileInner.innerHTML = `<img src="${imgSrc}" alt="Avatar" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
        }
    }

    async function loadHome() {
        isLoadingMore = false;
        showSkeletons();
        currentQuery = ''; currentOffset = 0;
        document.getElementById('keyword-desktop').value = '';
        document.getElementById('keyword-mobile').value = '';
        try { const res = await fetch('/api/home'); const data = await res.json(); renderGrid(data); } catch(e){}
    }

    async function loadMoreData() {
        if (isLoadingMore) return;
        isLoadingMore = true; 
        document.getElementById('main-scroll-loader').style.display = 'flex';
        try {
            let fetchUrl = currentQuery ? `/api/search?q=${encodeURIComponent(currentQuery)}&offset=${currentOffset}` : '/api/home';
            const res = await fetch(fetchUrl); const data = await res.json();
            if (data.length > 0) { currentOffset += data.length; appendToGrid(data); }
        } catch(e){} finally { isLoadingMore = false; document.getElementById('main-scroll-loader').style.display = 'none'; }
    }

    function toggleMobileSearch(show) {
        const form = document.getElementById('mobile-search-form');
        const input = document.getElementById('keyword-mobile');
        if (show) { form.classList.add('active'); input.focus(); } else { form.classList.remove('active'); }
    }

    function searchVideos(e, source) {
        e.preventDefault(); 
        const inputEl = document.getElementById(source === 'desktop' ? 'keyword-desktop' : 'keyword-mobile');
        const q = inputEl.value.trim();
        document.getElementById('keyword-desktop').value = q; 
        document.getElementById('keyword-mobile').value = q;
        
        if (q) { 
            activateNav(document.querySelector('.nav-item')); 
            currentQuery = q; 
            currentOffset = 0; 
            isLoadingMore = false;
            
            showSkeletons();
            fetch('/api/search?q=' + encodeURIComponent(q))
                .then(r => r.json())
                .then(d => { 
                    currentOffset = d.length; 
                    renderGrid(d); 
                });
        }
    }

    function chipClick(btn, query) {
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active')); btn.classList.add('active');
        document.getElementById('keyword-desktop').value = query; document.getElementById('keyword-mobile').value = query;
        isLoadingMore = false;
        if (query) { currentQuery = query; currentOffset = 0; showSkeletons(); fetch('/api/search?q=' + encodeURIComponent(query)).then(r=>r.json()).then(d => { currentOffset=d.length; renderGrid(d); }); } 
        else loadHome();
    }

    function activateNav(el) {
        if(!el) return;
        isLoadingMore = false;
        document.querySelectorAll('.nav-item, .sidebar-item').forEach(n => n.classList.remove('active')); el.classList.add('active');
        document.getElementById('main').style.display = 'block';
        document.getElementById('player-section').style.display = 'none';
        document.getElementById('profile-section').style.display = 'none';
        document.getElementById('player-box').innerHTML = ''; 
    }

    function goHome(e, el, push = true) { 
        if (e) e.preventDefault(); 
        isLoadingMore = false;
        activateNav(el || document.querySelector('.nav-item')); 
        document.getElementById('chips-container').style.display = 'block'; 
        if (push) {
            history.pushState({view: 'home'}, '', '');
        }
        loadHome(); 
    }

    function showProfile(el, push = true) {
        isLoadingMore = false;
        activateNav(el); 
        document.getElementById('main').style.display = 'none'; 
        document.getElementById('profile-section').style.display = 'block';
        if (push) {
            history.pushState({view: 'profile'}, '', '#profile');
        }
        const hist = JSON.parse(localStorage.getItem('yt_history') || '[]');
        const container = document.getElementById('history-scroll');
        if(hist.length === 0) { container.innerHTML = '<div style="color:#aaa; font-size:13px; padding-left:16px;">Belum ada histori tontonan.</div>'; return; }
        container.innerHTML = hist.slice(0,10).map(v => `<div class="hist-card" onclick="playVideo('${encodeURIComponent(JSON.stringify(v))}')"><img src="https://i.ytimg.com/vi/${v.id}/mqdefault.jpg" class="hist-thumb"><div class="hist-title">${v.title}</div><div class="hist-channel">${v.channel}</div></div>`).join('');
    }

    function playVideo(videoStr, push = true) {
        let v; try { v = JSON.parse(decodeURIComponent(videoStr)); } catch(e){ return; }
        
        isLoadingMore = false;
        isRelatedLoading = false;

        let hist = JSON.parse(localStorage.getItem('yt_history') || '[]'); hist = hist.filter(x => x.id !== v.id); hist.unshift(v);
        if(hist.length > 50) hist.pop(); localStorage.setItem('yt_history', JSON.stringify(hist));

        toggleMobileSearch(false);

        document.getElementById('main').style.display = 'none';
        document.getElementById('profile-section').style.display = 'none';
        
        document.getElementById('player-title').textContent = v.title;
        document.getElementById('player-channel-name').textContent = v.channel || 'Channel Name';
        document.getElementById('player-channel-avatar').src = v.avatar || '';
        
        document.getElementById('player-box').innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${v.id}?autoplay=1&rel=0&modestbranding=1&iv_load_policy=3" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
        
        document.getElementById('player-section').style.display = 'block'; window.scrollTo(0,0);

        if (push) {
            history.pushState({view: 'player', video: videoStr}, '', '#watch?v=' + v.id);
        }

        currentRelatedKeyword = v.title.split(' ').slice(0, 3).join(' ');
        currentRelatedOffset = 0;
        document.getElementById('related-videos-container').innerHTML = '';
        loadMoreRelated(true);
    }

    async function loadMoreRelated(isFirstLoad = false) {
        if(isRelatedLoading) return;
        isRelatedLoading = true;
        const container = document.getElementById('related-videos-container');
        
        if (isFirstLoad) {
            container.innerHTML = Array(4).fill(`<div class="skeleton-card"><div class="skeleton-thumb"></div><div class="skeleton-info"><div class="skeleton-line" style="width: 90%;"></div><div class="skeleton-line" style="width: 60%;"></div></div></div>`).join('');
        } else {
            document.getElementById('related-scroll-loader').style.display = 'flex';
        }

        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(currentRelatedKeyword)}&offset=${currentRelatedOffset}`);
            const data = await res.json();
            
            if (isFirstLoad) container.innerHTML = ''; 
            
            if (data.length > 0) {
                currentRelatedOffset += data.length;
                const html = data.map(item => {
                    const itemStr = encodeURIComponent(JSON.stringify(item));
                    let meta = [item.channel, item.views].filter(Boolean).join(' • ');
                    return `<div class="related-card" onclick="playVideo('${itemStr}')"><div class="related-thumb"><img src="https://i.ytimg.com/vi/${item.id}/mqdefault.jpg" loading="lazy">${item.duration ? '<span class="duration-badge">' + item.duration + '</span>' : ''}</div><div class="related-info"><div class="related-vid-title">${item.title}</div><div class="related-vid-channel">${item.channel || ''}</div><div class="related-vid-meta">${meta}</div></div></div>`;
                }).join('');
                container.insertAdjacentHTML('beforeend', html);
            } else if (isFirstLoad) {
                container.innerHTML = '<div style="color:#aaa; font-size:13px;">Tidak ada video serupa.</div>';
            }
        } catch(e) {
            if(isFirstLoad) container.innerHTML = '<div style="color:#aaa; font-size:13px;">Gagal memuat video serupa.</div>';
        } finally {
            isRelatedLoading = false;
            document.getElementById('related-scroll-loader').style.display = 'none';
        }
    }

    function showSkeletons() { document.getElementById('video-grid').innerHTML = Array(8).fill(`<div class="vid-card"><div class="thumb-wrap" style="background:#272727; animation: pulse 1.5s infinite;"></div><div class="vid-info"><div class="channel-avatar" style="animation: pulse 1.5s infinite;"></div><div class="vid-text"><div style="height:14px; background:#272727; margin-bottom:8px; width:90%; border-radius:4px; animation: pulse 1.5s infinite;"></div><div style="height:12px; background:#272727; width:60%; border-radius:4px; animation: pulse 1.5s infinite;"></div></div></div></div>`).join(''); }

    function renderGrid(data) { const g = document.getElementById('video-grid'); g.innerHTML = ''; appendToGrid(data); }

    function appendToGrid(data) {
        const g = document.getElementById('video-grid');
        data.forEach(v => {
            const card = document.createElement('div'); card.className = 'vid-card';
            card.onclick = () => playVideo(encodeURIComponent(JSON.stringify(v)));
            let avatarHtml = v.avatar ? `<div class="channel-avatar"><img src="${v.avatar}"></div>` : `<div class="channel-avatar">${v.channel ? v.channel.charAt(0).toUpperCase() : '?'}</div>`;
            card.innerHTML = `<div class="thumb-wrap"><img class="thumb-img" src="https://i.ytimg.com/vi/${v.id}/hqdefault.jpg" loading="lazy">${v.duration ? '<span class="duration-badge">' + v.duration + '</span>' : ''}</div><div class="vid-info">${avatarHtml}<div class="vid-text"><div class="vid-title">${v.title}</div><div class="vid-meta">${[v.channel, v.views, v.published].filter(Boolean).join(' • ')}</div></div></div>`;
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
            data["channelUrl"] = run.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", "")
    except Exception: data["channel"] = ""; data["channelUrl"] = ""
    try:
        avatar_thumbs = video.get("channelThumbnailSupportedRenderers", {}).get("channelThumbnailWithLinkRenderer", {}).get("thumbnail", {}).get("thumbnails", [])
        if avatar_thumbs: data["avatar"] = avatar_thumbs[0].get("url", "")
    except Exception: data["avatar"] = ""
    return data

@app.route("/")
def home(): 
    return render_template_string(HTML_TEMPLATE)

@app.route("/manifest.json")
def manifest():
    manifest_data = {
        "name": "YouTube Premium Clone",
        "short_name": "Premium",
        "start_url": "/?mode=pwa",
        "display": "standalone",
        "background_color": "#0f0f0f",
        "theme_color": "#0f0f0f",
        "icons": [
            {
                "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/192px-YouTube_full-color_icon_%282017%29.svg.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/512px-YouTube_full-color_icon_%282017%29.svg.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return app.response_class(json.dumps(manifest_data), mimetype='application/manifest+json')

@app.route("/sw.js")
def service_worker():
    js = """
    const CACHE_NAME = 'yt-clone-v13';
    self.addEventListener('install', (e) => { 
        self.skipWaiting(); 
    });
    self.addEventListener('activate', (e) => { 
        e.waitUntil(
            caches.keys().then((keyList) => {
                return Promise.all(keyList.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                }));
            })
        );
        self.clients.claim(); 
    });
    self.addEventListener('fetch', (e) => { 
        e.respondWith(
            fetch(e.request).catch(() => {
                return caches.match(e.request).then((response) => {
                    return response || new Response('Koneksi internet terputus. Silakan periksa kembali jaringan Anda.', {
                        status: 503,
                        headers: { 'Content-Type': 'text/plain; charset=utf-8' }
                    });
                });
            })
        );
    });
    """
    return app.response_class(js, mimetype='application/javascript')

@lru_cache(maxsize=32)
def cached_scrapetube_search(keyword, limit):
    results = []
    videos = scrapetube.get_search(keyword, limit=limit)
    for v in videos:
        d = extract_video_data(v)
        if d.get("id"): 
            results.append(d)
    return results

@app.route("/api/home")
def api_home():
    results = []
    try:
        base_keywords = ["Viral", "Hits Indonesia", "Trending Video", "Podcast Terbaru", "Gaming"]
        random_keyword = random.choice(base_keywords)
        results = cached_scrapetube_search(random_keyword, 15)
        results = list(results)
        random.shuffle(results)
    except Exception as e:
        logging.error(f"Gagal memuat API Home: {e}")
    return jsonify(results)

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    offset = int(request.args.get("offset", 0))
    limit = 15
    results = []
    if not query: 
        return jsonify(results)
    try:
        all_videos = cached_scrapetube_search(query, offset + limit)
        results = all_videos[offset:offset + limit]
    except Exception as e:
        logging.error(f"Gagal memuat API Search untuk keyword '{query}': {e}")
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=2000)
