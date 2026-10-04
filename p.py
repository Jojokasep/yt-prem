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
    <title>Valora Tube Clone</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #0f0f0f; color: #f1f1f1; overflow-x: hidden; }
        ::-webkit-scrollbar { width: 0; height: 0; display: none; }
        a { text-decoration: none; color: inherit; }

        /* ===== ANIMASI LOADING ===== */
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
            background: #272727;
            background-image: linear-gradient(90deg, #272727 0px, #333 40px, #272727 80px);
            background-size: 1000px 100%;
            animation: shimmer 2s infinite linear;
        }

        /* ===== HEADER ===== */
        #header { position: fixed; top: 0; left: 0; right: 0; height: 56px; background: #0f0f0f; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 100; }
        .header-left { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        .logo-icon { color: #ff0000; font-weight: 900; font-style: italic; font-size: 24px; letter-spacing: -2px; }
        .logo-text { font-size: 20px; font-weight: 500; letter-spacing: -0.5px; }
        
        .header-right { display: flex; align-items: center; gap: 8px; }
        .header-icon { background: transparent; border: none; color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; width: 40px; height: 40px; border-radius: 50%; }
        
        .search-form-mobile { display: none; position: absolute; inset: 0; background: #0f0f0f; padding: 0 12px; align-items: center; gap: 8px; z-index: 110; }
        .search-form-mobile.active { display: flex; }
        .search-input-wrap-mob { flex: 1; display: flex; align-items: center; background: #222; border-radius: 20px; padding: 0 16px; height: 36px; }
        .search-input-wrap-mob input { flex: 1; background: transparent; border: none; color: #fff; font-size: 15px; outline: none; }

        /* ===== CHIPS ===== */
        .chips-wrapper { position: sticky; top: 56px; background: #0f0f0f; z-index: 10; padding: 12px 16px; display: flex; gap: 12px; align-items: center; }
        .explore-icon { background: #272727; padding: 6px; border-radius: 4px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .chips-bar { display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; }
        .chip { padding: 6px 14px; border-radius: 8px; font-size: 14px; font-weight: 500; white-space: nowrap; border: none; background: #272727; color: #f1f1f1; cursor: pointer; transition: 0.2s; }
        .chip.active { background: #f1f1f1; color: #0f0f0f; }

        /* ===== MAIN CONTENT & GRID ===== */
        #main { margin-top: 56px; padding-bottom: 70px; min-height: 100vh; }
        .video-grid { display: flex; flex-direction: column; gap: 0; }
        .vid-card { cursor: pointer; display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
        .thumb-wrap { position: relative; width: 100%; aspect-ratio: 16/9; background: #272727; }
        .thumb-img { width: 100%; height: 100%; object-fit: cover; }
        .duration-badge { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: #fff; font-size: 12px; font-weight: 500; padding: 3px 6px; border-radius: 4px; }
        .vid-info { display: flex; gap: 12px; align-items: flex-start; padding: 0 16px; }
        .channel-avatar { width: 36px; height: 36px; border-radius: 50%; background: #444; flex-shrink: 0; overflow: hidden; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:bold; }
        .channel-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .vid-text { flex: 1; }
        .vid-title { font-size: 15px; font-weight: 500; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; color: #fff; }
        .vid-meta { font-size: 13px; color: #aaa; }

        /* ===== PLAYER SECTION ===== */
        #player-section { display: none; margin-top: 0; padding-bottom: 70px; min-height: 100vh; background: #0f0f0f; z-index: 200; position: absolute; top: 0; left: 0; width: 100%; }
        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; position: sticky; top: 0; z-index: 105; transition: all 0.3s ease; }
        .player-container iframe { width: 100%; height: 100%; border: none; }
        
        /* Custom Fullscreen tanpa pop-up nocookie */
        .css-fullscreen { position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; max-width: none !important; aspect-ratio: auto !important; z-index: 99999 !important; border-radius: 0 !important; background: #000; display: flex; align-items: center; justify-content: center; }

        .player-meta { padding: 12px 16px; }
        .player-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; line-height: 1.3; }
        .player-views-date { font-size: 13px; color: #aaa; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
        
        .action-row { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 16px; scrollbar-width: none; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px; }
        .action-pill { display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; color: #fff; }
        .action-pill .material-icons-outlined { font-size: 18px; }
        
        .channel-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
        .channel-info { display: flex; align-items: center; gap: 10px; }
        .channel-name { font-weight: 500; font-size: 15px; color: #fff; }
        .channel-subs { font-size: 12px; color: #aaa; }
        .btn-subscribe { background: #fff; color: #000; font-weight: 500; border: none; padding: 8px 16px; border-radius: 20px; font-size: 14px; }
        
        .comments-box { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 12px 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 500; }

        /* ===== MINI PLAYER ===== */
        #mini-player { display: none; position: fixed; bottom: 50px; left: 0; right: 0; height: 56px; background: #1f1f1f; z-index: 99; align-items: center; padding: 0 12px; border-top: 1px solid rgba(255,255,255,0.1); }
        #mini-player.active { display: flex; animation: fadeIn 0.3s; }
        .mini-thumb { width: 80px; height: 45px; background: #000; margin-right: 12px; cursor: pointer; position: relative; flex-shrink: 0; }
        .mini-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .mini-info { flex: 1; overflow: hidden; white-space: nowrap; cursor: pointer; }
        .mini-title { font-size: 13px; font-weight: 500; color: #fff; text-overflow: ellipsis; overflow: hidden; margin-bottom: 2px; }
        .mini-channel { font-size: 11px; color: #aaa; text-overflow: ellipsis; overflow: hidden; }
        .mini-actions { display: flex; align-items: center; gap: 12px; color: #fff; }
        .mini-actions .material-icons { font-size: 26px; cursor: pointer; }

        /* ===== BOTTOM NAV ===== */
        #bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; height: 50px; background: #0f0f0f; z-index: 100; display: flex; justify-content: space-around; align-items: center; border-top: 1px solid rgba(255,255,255,0.05); }
        .nav-item { display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; flex: 1; height: 100%; cursor: pointer; opacity: 0.7; }
        .nav-item.active { opacity: 1; color: #fff; }
        .nav-item.active .material-icons-outlined { display: none; }
        .nav-item:not(.active) .material-icons { display: none; }
        .nav-item .material-icons, .nav-item .material-icons-outlined { font-size: 24px; }
        .nav-item .nav-label { font-size: 10px; margin-top: 3px; }
        
        .nav-avatar { width: 24px; height: 24px; border-radius: 50%; background: #ff4e45; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; border: 2px solid transparent; }
        .nav-item.active .nav-avatar { border-color: #fff; }

        /* ===== BOTTOM SHEET PENGATURAN ===== */
        #sheet-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 9999; opacity: 0; transition: opacity 0.3s; }
        #sheet-overlay.show { display: block; opacity: 1; }
        #settings-sheet { display: flex; flex-direction: column; position: fixed; bottom: -100%; left: 0; right: 0; background: #212121; border-radius: 16px 16px 0 0; z-index: 10000; transition: bottom 0.3s cubic-bezier(0.4, 0, 0.2, 1); padding-bottom: 24px; max-height: 80vh; overflow-y: auto; }
        #settings-sheet.show { bottom: 0; }
        .sheet-handle { width: 40px; height: 4px; background: #555; border-radius: 2px; margin: 12px auto 8px; }
        .setting-item { display: flex; align-items: center; gap: 16px; padding: 14px 24px; color: #f1f1f1; font-size: 15px; cursor: pointer; transition: background 0.2s; }
        .setting-item:hover { background: rgba(255,255,255,0.1); }
        .setting-item .material-icons-outlined { font-size: 24px; color: #f1f1f1; }
        
        /* Loader Spinner */
        #scroll-loader { display: none; justify-content: center; padding: 20px 0; }
        .spinner { width: 30px; height: 30px; border: 3px solid #333; border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
    </style>
</head>
<body>

<header id="header">
    <div class="header-left" onclick="goHome(event)">
        <span class="logo-icon">a</span>
        <span class="logo-text">Valora Tube</span>
    </div>

    <div class="header-right">
        <button class="header-icon" onclick="toggleSearch(true)"><span class="material-icons-outlined">search</span></button>
        <button class="header-icon"><span class="material-icons-outlined">mic</span></button>
        <button class="header-icon"><span class="material-icons-outlined">more_vert</span></button>
    </div>
    
    <form class="search-form-mobile" id="mobile-search-form" onsubmit="searchVideos(event)">
        <button type="button" class="header-icon" onclick="toggleSearch(false)"><span class="material-icons-outlined">arrow_back</span></button>
        <div class="search-input-wrap-mob">
            <input type="text" id="keyword-mobile" placeholder="Telusuri Valora Tube" autocomplete="off">
        </div>
        <button type="button" class="header-icon" style="background:#222;" onclick="searchVideos(event)"><span class="material-icons-outlined" style="font-size:20px;">search</span></button>
    </form>
</header>

<main id="main">
    <div class="chips-wrapper" id="chips-container">
        <div class="explore-icon"><span class="material-icons-outlined" style="font-size: 20px;">explore</span></div>
        <div class="chips-bar">
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
    <!-- Pemutar video bersih murni tanpa tombol melayang di atasnya -->
    <div class="player-container" id="player-container-box">
        <div id="player-box" style="width:100%; height:100%;"></div>
    </div>
    
    <div class="player-meta fade-in">
        <div class="player-title" id="player-title">Judul Video</div>
        <div class="player-views-date">
            <span id="player-views">572 rb tampilan • 3 hari yang lalu</span>
            <span><span class="material-icons" style="font-size:14px; vertical-align:middle;">thumb_up</span> 3,2 rb</span>
        </div>
        
        <!-- Tombol Pengaturan & Perbesar berdampingan di bawah video -->
        <div class="action-row">
            <div class="action-pill" onclick="openSettings()"><span class="material-icons-outlined">settings</span> Pengaturan</div>
            <div class="action-pill" onclick="toggleCustomFullscreen()"><span class="material-icons-outlined" id="fs-icon">fullscreen</span> Perbesar</div>
            <div class="action-pill"><span class="material-icons-outlined">share</span> Bagikan</div>
            <div class="action-pill"><span class="material-icons-outlined">download</span> Unduh</div>
            <div class="action-pill" onclick="saveTontonNanti()"><span class="material-icons-outlined">playlist_add</span> Simpan</div>
            <div class="action-pill"><span class="material-icons-outlined">headphones</span> Audio</div>
        </div>
        
        <div class="channel-row">
            <div class="channel-info">
                <img id="player-channel-avatar" src="" style="width:36px; height:36px; border-radius:50%; object-fit:cover; background:#444;">
                <div>
                    <div class="channel-name" id="player-channel-name">Nama Channel</div>
                    <div class="channel-subs">1,2 jt pelanggan</div>
                </div>
            </div>
            <button class="btn-subscribe">Berlangganan</button>
        </div>
        
        <div class="comments-box">
            <span>Komentar</span>
            <span class="material-icons-outlined">unfold_more</span>
        </div>
        
        <div style="font-size: 16px; font-weight: 700; margin-bottom: 12px;">Video lainnya</div>
        <div class="video-grid" id="related-grid"></div>
    </div>
</div>

<!-- Bottom Sheet Pengaturan (Settings Menu) -->
<div id="sheet-overlay" onclick="closeSettings()"></div>
<div id="settings-sheet">
    <div class="sheet-handle"></div>
    <div id="main-settings">
        <div class="setting-item" onclick="alert('Mode ulang diaktifkan')"><span class="material-icons-outlined">repeat</span> Mode ulang (Tidak diulang)</div>
        <div class="setting-item" onclick="alert('Ubah ukuran segera hadir')"><span class="material-icons-outlined">aspect_ratio</span> Mode ubah ukuran (Pas)</div>
        <div class="setting-item" onclick="alert('Kecepatan 1.5x diaktifkan')"><span class="material-icons-outlined">speed</span> Kecepatan pemutaran (1.0x)</div>
        <div class="setting-item" onclick="alert('Pewaktu dimatikan')"><span class="material-icons-outlined">dark_mode</span> Pewaktu tidur (Mati)</div>
        <div class="setting-item" onclick="showQualitySettings()"><span class="material-icons-outlined">hd</span> Kualitas (<span id="current-quality">Otomatis</span>)</div>
        <div class="setting-item" onclick="alert('Audio default')"><span class="material-icons-outlined">music_note</span> Trek audio (Indonesia - asli atau utama)</div>
        <div class="setting-item" onclick="alert('Takarir dimatikan')"><span class="material-icons-outlined">closed_caption</span> Takarir (Tidak ada)</div>
        <div class="setting-item" onclick="alert('Statistik dibuka')"><span class="material-icons-outlined">info</span> Statistik untuk kutu buku</div>
    </div>
    <div id="quality-settings" style="display:none;">
        <div class="setting-item" onclick="showMainSettings()" style="border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom:8px;"><span class="material-icons-outlined">arrow_back</span> Kembali</div>
        <div class="setting-item" onclick="setQuality(1080)">1080p Premium HD</div>
        <div class="setting-item" onclick="setQuality(720)">720p HD</div>
        <div class="setting-item" onclick="setQuality(480)">480p</div>
        <div class="setting-item" onclick="setQuality(360)">360p Data Saver</div>
    </div>
</div>

<!-- Mini Player Melayang -->
<div id="mini-player">
    <div class="mini-thumb" onclick="expandPlayer()">
        <img id="mini-thumb-img" src="">
    </div>
    <div class="mini-info" onclick="expandPlayer()">
        <div class="mini-title" id="mini-title">Judul Video</div>
        <div class="mini-channel" id="mini-channel">Channel</div>
    </div>
    <div class="mini-actions">
        <span class="material-icons" onclick="expandPlayer()">play_arrow</span>
        <span class="material-icons" onclick="closeMiniPlayer()">close</span>
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
    <div class="nav-item">
        <span class="material-icons-outlined">subscriptions</span><span class="material-icons">subscriptions</span>
        <span class="nav-label">Langganan</span>
    </div>
    <div class="nav-item">
        <span class="material-icons-outlined">trending_up</span><span class="material-icons">trending_up</span>
        <span class="nav-label">Trending</span>
    </div>
    <div class="nav-item">
        <div class="nav-avatar">V</div>
        <span class="nav-label">Valora</span>
    </div>
</nav>

<script>
    let currentQuery = '';
    let currentOffset = 0;
    let isLoadingMore = false;
    let currentPlayingVideoStr = ''; 
    let activeData = [];
    
    window.addEventListener('DOMContentLoaded', () => { loadHome(); });
    
    window.addEventListener('scroll', () => {
        if (!isLoadingMore && document.getElementById('main').style.display !== 'none') {
            if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300) {
                loadMoreData();
            }
        }
    });

    async function loadHome() {
        showSkeletons();
        currentQuery = '';
        currentOffset = 0;
        try { 
            const res = await fetch('/api/home'); 
            activeData = await res.json(); 
            renderGrid(activeData); 
        } catch(e){}
    }

    async function loadMoreData() {
        isLoadingMore = true; document.getElementById('scroll-loader').style.display = 'flex';
        try {
            let fetchUrl = currentQuery ? `/api/search?q=${encodeURIComponent(currentQuery)}&offset=${currentOffset}` : '/api/home';
            const res = await fetch(fetchUrl);
            const data = await res.json();
            if (data.length > 0) { 
                currentOffset += data.length; 
                activeData = activeData.concat(data);
                appendToGrid(data, 'video-grid'); 
            }
        } catch(e){} finally { isLoadingMore = false; document.getElementById('scroll-loader').style.display = 'none'; }
    }

    function toggleSearch(show) {
        const form = document.getElementById('mobile-search-form');
        const input = document.getElementById('keyword-mobile');
        if (show) { form.classList.add('active'); input.focus(); } 
        else { form.classList.remove('active'); input.value = ''; }
    }

    function searchVideos(e) {
        e.preventDefault(); 
        const q = document.getElementById('keyword-mobile').value.trim();
        if (q) { 
            activateNav(document.querySelector('.nav-item')); 
            currentQuery = q; currentOffset = 0; 
            toggleSearch(false); 
            showSkeletons();
            fetch('/api/search?q=' + encodeURIComponent(q)).then(r=>r.json()).then(d => { 
                currentOffset=d.length; activeData = d; renderGrid(d); 
            });
        }
    }

    function chipClick(btn, query) {
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active')); btn.classList.add('active');
        if (query) { currentQuery = query; currentOffset = 0; showSkeletons(); fetch('/api/search?q=' + encodeURIComponent(query)).then(r=>r.json()).then(d => { currentOffset=d.length; activeData=d; renderGrid(d); }); } 
        else loadHome();
    }

    function activateNav(el) {
        if(!el) return;
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
        
        document.getElementById('main').style.display = 'block';
        document.getElementById('player-section').style.display = 'none';
        
        if(currentPlayingVideoStr) {
            document.getElementById('mini-player').classList.add('active');
        }
    }

    function goHome(e, el) { 
        if (e) e.preventDefault(); 
        activateNav(el || document.querySelector('.nav-item')); 
        document.getElementById('chips-container').style.display = 'flex';
        window.scrollTo(0,0);
        if(currentQuery !== '') loadHome(); 
    }
    
    function loadShorts(el) {
        activateNav(el);
        document.getElementById('chips-container').style.display = 'none';
        showSkeletons();
        currentQuery = 'shorts'; 
        fetch('/api/shorts').then(r=>r.json()).then(d => { activeData=d; renderGrid(d); });
    }

    function saveTontonNanti() {
        if(!currentPlayingVideoStr) return;
        try {
            let v = JSON.parse(decodeURIComponent(currentPlayingVideoStr));
            let wl = JSON.parse(localStorage.getItem('yt_watch_later') || '[]');
            if(!wl.find(x => x.id === v.id)) {
                wl.unshift(v); localStorage.setItem('yt_watch_later', JSON.stringify(wl));
                alert('Tersimpan di playlist');
            }
        } catch(e){}
    }

    /* BOTTOM SHEET PENGATURAN */
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
        document.getElementById('current-quality').textContent = res + 'p';
        const iframe = document.querySelector('#player-box iframe');
        if(iframe) {
            let src = iframe.src;
            src = src.split('&vq=')[0];
            iframe.src = src + '&vq=' + res;
        }
        closeSettings();
        alert('Kualitas video diatur ke ' + res + 'p');
    }

    /* CUSTOM FULLSCREEN TANPA NOTIFIKASI */
    function toggleCustomFullscreen() {
        const box = document.getElementById('player-container-box');
        const icon = document.getElementById('fs-icon');
        
        box.classList.toggle('css-fullscreen');
        
        if(box.classList.contains('css-fullscreen')) {
            icon.textContent = 'fullscreen_exit';
            document.body.style.overflow = 'hidden';
        } else {
            icon.textContent = 'fullscreen';
            document.body.style.overflow = '';
        }
    }

    function playVideo(videoStr) {
        let v; try { v = JSON.parse(decodeURIComponent(videoStr)); } catch(e){ return; }
        currentPlayingVideoStr = videoStr; 
        
        document.getElementById('main').style.display = 'none';
        document.getElementById('mini-player').classList.remove('active');
        
        document.getElementById('player-container-box').classList.remove('css-fullscreen');
        document.getElementById('fs-icon').textContent = 'fullscreen';
        document.body.style.overflow = '';

        const ps = document.getElementById('player-section');
        document.getElementById('player-title').textContent = v.title;
        document.getElementById('player-channel-name').textContent = v.channel || 'Valora Music';
        document.getElementById('player-channel-avatar').src = v.avatar || '';
        document.getElementById('player-views').textContent = (v.views || '123 rb tampilan') + ' • ' + (v.published || 'Baru saja');
        
        document.getElementById('player-box').innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${v.id}?autoplay=1&rel=0&fs=0&iv_load_policy=3&modestbranding=1" allow="autoplay"></iframe>`;
        
        let related = [...activeData].sort(() => 0.5 - Math.random()).slice(0, 5);
        document.getElementById('related-grid').innerHTML = '';
        appendToGrid(related, 'related-grid');

        document.getElementById('mini-thumb-img').src = `https://i.ytimg.com/vi/${v.id}/mqdefault.jpg`;
        document.getElementById('mini-title').textContent = v.title;
        document.getElementById('mini-channel').textContent = v.channel;

        ps.style.display = 'block'; window.scrollTo(0,0);
    }

    function expandPlayer() {
        document.getElementById('main').style.display = 'none';
        document.getElementById('mini-player').classList.remove('active');
        document.getElementById('player-section').style.display = 'block';
    }

    function closeMiniPlayer() {
        currentPlayingVideoStr = '';
        document.getElementById('mini-player').classList.remove('active');
        document.getElementById('player-box').innerHTML = '';
        document.getElementById('player-container-box').classList.remove('css-fullscreen');
        document.getElementById('fs-icon').textContent = 'fullscreen';
        document.body.style.overflow = '';
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
        base_keywords = ["Viral 2024", "Hits Indonesia", "Populer Hari Ini", "Trending Video", "Podcast Indonesia terbaru", "Gaming Indonesia"]
        random_keyword = random.choice(base_keywords)
        
        videos = scrapetube.get_search(random_keyword, limit=30)
        for v in videos:
            d = extract_video_data(v)
            if d.get("id"): results.append(d)
                
        try:
            trending = scrapetube.get_trending("ID", limit=10)
            for v in trending:
                d = extract_video_data(v)
                if d.get("id") and not any(r["id"] == d["id"] for r in results): results.insert(random.randint(0, 10), d)
        except: pass
            
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

if __name__ == "__main__":
    app.run(debug=True, port=2000)
