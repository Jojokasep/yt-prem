from flask import Flask, jsonify, render_template_string, request
import scrapetube
import random
import json
import logging
import os
import time
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
    <link rel="manifest" href="/manifest.json?v=19">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <script src="https://www.youtube.com/iframe_api"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #0f0f0f; color: #f1f1f1; overflow-x: hidden; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #717171; }
        a { text-decoration: none; color: inherit; }

        /* ===== HEADER ===== */
        #header { position: fixed; top: 0; left: 0; right: 0; height: 56px; background: #0f0f0f; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 100; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .header-left { display: flex; align-items: center; gap: 16px; }
        .yt-logo { display: flex; align-items: center; gap: 4px; cursor: pointer; user-select: none; }
        .yt-logo-text { font-size: 20px; font-weight: 700; letter-spacing: -1px; margin-left: 2px; }
        
        .header-right { display: flex; align-items: center; gap: 12px; }
        .header-icon { background: transparent; border: none; color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; padding: 10px; border-radius: 50%; min-width: 44px; min-height: 44px; transition: background 0.15s; }
        .header-icon:hover { background: rgba(255,255,255,0.1); }
        .header-icon .material-icons-outlined { font-size: 24px; }
        
        /* Search Form Desktop */
        .search-form-desktop { display: flex; flex: 1; max-width: 600px; align-items: center; margin: 0 40px; }
        .search-input-wrap-desk { flex: 1; display: flex; align-items: center; border: 1px solid #303030; border-right: none; border-radius: 20px 0 0 20px; background: #121212; height: 40px; padding: 0 16px; transition: border-color 0.2s; }
        .search-input-wrap-desk:focus-within { border-color: #1c62b9; }
        .search-input-wrap-desk input { width: 100%; background: transparent; border: none; color: #fff; font-size: 16px; outline: none; }
        .search-btn-desk { height: 40px; width: 64px; border: 1px solid #303030; border-radius: 0 20px 20px 0; background: #222; color: #fff; cursor: pointer; transition: background 0.15s; display: flex; align-items: center; justify-content: center; }
        .search-btn-desk:hover { background: #333; }
        
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
        #main { margin-left: 240px; margin-top: 56px; padding: 24px; min-height: 100vh; display: block; }
        
        .chips-wrapper { position: sticky; top: 56px; background: #0f0f0f; z-index: 10; padding: 12px 0; margin-bottom: 24px; }
        .chips-bar { display: flex; gap: 10px; overflow-x: auto; scrollbar-width: none; }
        .chips-bar::-webkit-scrollbar { display: none; }
        .chip { padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; white-space: nowrap; border: none; background: #272727; color: #f1f1f1; cursor: pointer; min-height: 40px; transition: background 0.15s, color 0.15s; }
        .chip:hover { background: #383838; }
        .chip.active { background: #f1f1f1; color: #0f0f0f; }

        .video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 40px 16px; }
        
        .vid-card { cursor: pointer; display: flex; flex-direction: column; gap: 12px; }
        .thumb-wrap { position: relative; width: 100%; aspect-ratio: 16/9; background: #272727; border-radius: 12px; overflow: hidden; will-change: transform; }
        .thumb-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.25s ease; }
        .vid-card:hover .thumb-img { transform: scale(1.04); }
        .duration-badge { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.85); color: #fff; font-size: 12px; font-weight: 500; padding: 3px 6px; border-radius: 4px; }
        
        .vid-info { display: flex; gap: 12px; align-items: flex-start; }
        .channel-avatar { width: 36px; height: 36px; border-radius: 50%; background: #444; flex-shrink: 0; overflow: hidden; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:bold; }
        .channel-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .vid-text { flex: 1; min-width: 0; }
        .vid-title { font-size: 16px; font-weight: 500; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; }
        .vid-meta { font-size: 14px; color: #aaa; }

        /* ===== PLAYER SECTION ===== */
        #player-section { display: none; margin-left: 240px; margin-top: 56px; padding: 24px; max-width: 1500px; }
        .player-layout { display: grid; grid-template-columns: 1fr 400px; gap: 24px; }
        
        .player-main-col { width: 100%; min-width: 0; }
        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; overflow: hidden; }
        .player-container iframe { width: 100%; height: 100%; border: none; display: block; }
        
        .player-meta { padding: 16px 0; }
        .player-title { font-size: 20px; font-weight: 700; margin-bottom: 12px; line-height: 1.35; }
        
        .channel-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; margin-bottom: 16px; }
        .channel-info { display: flex; align-items: center; gap: 12px; }
        .channel-name { font-weight: 600; font-size: 16px; }
        .btn-subscribe { background: #f1f1f1; color: #0f0f0f; font-weight: 600; border: none; padding: 10px 20px; border-radius: 20px; font-size: 14px; cursor: pointer; min-height: 40px; transition: background 0.15s; }
        .btn-subscribe:hover { background: #d9d9d9; }
        .btn-subscribe.subscribed { background: #272727; color: #f1f1f1; border: 1px solid rgba(255,255,255,0.1); }
        
        .action-row { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 4px; }
        .action-pill { display: flex; align-items: center; gap: 6px; background: #272727; padding: 10px 18px; border-radius: 20px; font-size: 14px; font-weight: 500; cursor: pointer; white-space: nowrap; min-height: 40px; transition: background 0.15s; border: none; color: #fff; }
        .action-pill:hover { background: #3f3f3f; }
        .action-pill.active { color: #3ea6ff; }
        
        .comments-box { background: #272727; border-radius: 12px; padding: 16px; margin-top: 16px; }

        /* Related Videos Column */
        .related-col { display: flex; flex-direction: column; gap: 12px; }
        .related-title { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
        .related-card { display: flex; gap: 8px; cursor: pointer; }
        .related-thumb { width: 168px; aspect-ratio: 16/9; background: #272727; border-radius: 8px; overflow: hidden; flex-shrink: 0; position: relative; }
        .related-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .related-info { flex: 1; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
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
        .profile-btn { background: #272727; border: none; color: #fff; padding: 8px 16px; border-radius: 16px; font-size: 13px; font-weight: 500; cursor: pointer; min-height: 36px; transition: background 0.15s; }
        .profile-btn:hover { background: #383838; }
        
        .horizontal-list { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 16px; scrollbar-width: none; }
        .horizontal-list::-webkit-scrollbar { display: none; }
        .hist-card { width: 160px; flex-shrink: 0; cursor: pointer; }
        .hist-thumb { width: 100%; aspect-ratio: 16/9; background: #272727; border-radius: 8px; margin-bottom: 8px; object-fit: cover; }
        .hist-title { font-size: 14px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; }
        .hist-channel { font-size: 13px; color: #aaa; }
        
        /* Scroll to Top Button */
        #scrollTopBtn { display: none; position: fixed; bottom: 70px; right: 20px; background: #272727; color: #fff; border: 1px solid rgba(255,255,255,0.1); width: 44px; height: 44px; border-radius: 50%; align-items: center; justify-content: center; cursor: pointer; z-index: 99; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: background 0.15s; }
        #scrollTopBtn:hover { background: #3f3f3f; }

        /* Loaders & End-of-content */
        .loader-container { display: flex; justify-content: center; align-items: center; padding: 30px 0; width: 100%; min-height: 60px; }
        .spinner { width: 32px; height: 32px; border: 3px solid #333; border-top-color: #ff0000; border-radius: 50%; animation: spin 0.8s linear infinite; }
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
            
            #main { margin-left: 0; padding: 0; padding-bottom: 70px; }
            .chips-wrapper { padding: 12px 16px; margin-bottom: 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
            
            .search-form-desktop { display: none; }
            .search-btn-mobile-toggle { display: block; }
            
            .video-grid { display: flex; flex-direction: column; gap: 0; }
            .vid-card { margin-bottom: 16px; gap: 12px; }
            .thumb-wrap { border-radius: 0; }
            .vid-info { padding: 0 16px; }
            .vid-title { font-size: 15px; }
            .vid-meta { font-size: 13px; }
            
            #player-section { margin-left: 0; margin-top: 0; padding: 0; padding-bottom: 70px; max-width: 100%; width: 100%; overflow: hidden; }
            .player-container { width: 100%; max-width: 100vw; border-radius: 0; position: sticky; top: 56px; z-index: 95; }
            .player-meta { padding: 12px 16px; }
            .player-title { font-size: 18px; }
            .related-col { padding: 0 16px; }

            #profile-section { margin-left: 0; padding: 0; padding-bottom: 70px; }
            .profile-header { padding: 24px 16px; margin-bottom: 0; }
            .horizontal-list { padding: 0 16px 16px; }
            #scrollTopBtn { bottom: 65px; right: 15px; }
        }

        /* ===== PLAYLIST SECTION ===== */
        #playlist-section { display: none; margin-left: 240px; margin-top: 56px; padding: 24px; min-height: 100vh; }
        .playlist-section-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
        .playlist-section-title { font-size: 22px; font-weight: 700; flex: 1; }
        .btn-create-playlist { background: #ff4e45; color: #fff; border: none; padding: 10px 20px; border-radius: 20px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: background 0.15s; }
        .btn-create-playlist:hover { background: #ff3b32; }
        .playlists-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
        .playlist-card { background: #1c1c1c; border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform 0.15s, background 0.15s; }
        .playlist-card:hover { background: #272727; transform: translateY(-2px); }
        .playlist-thumb-wrap { position: relative; width: 100%; aspect-ratio: 16/9; background: #272727; overflow: hidden; }
        .playlist-thumb-wrap img { width: 100%; height: 100%; object-fit: cover; }
        .playlist-thumb-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #aaa; font-size: 48px; }
        .playlist-badge { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.85); color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px; display: flex; align-items: center; gap: 4px; }
        .playlist-info { padding: 12px; }
        .playlist-card-title { font-size: 16px; font-weight: 600; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .playlist-card-meta { font-size: 13px; color: #aaa; }

        /* Playlist detail view */
        .playlist-detail-header { display: flex; gap: 24px; margin-bottom: 24px; align-items: flex-start; flex-wrap: wrap; }
        .playlist-detail-thumb { width: 280px; aspect-ratio: 16/9; border-radius: 12px; background: #272727; overflow: hidden; flex-shrink: 0; }
        .playlist-detail-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .playlist-detail-info { flex: 1; min-width: 260px; }
        .playlist-detail-title { font-size: 24px; font-weight: 700; margin-bottom: 8px; }
        .playlist-detail-meta { font-size: 14px; color: #aaa; margin-bottom: 16px; }
        .playlist-detail-actions { display: flex; gap: 12px; flex-wrap: wrap; }
        .btn-play-all { background: #f1f1f1; color: #0f0f0f; border: none; padding: 12px 24px; border-radius: 24px; font-size: 15px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .btn-play-all:hover { background: #d9d9d9; }
        .btn-playlist-delete { background: #272727; color: #fff; border: none; padding: 12px 24px; border-radius: 24px; font-size: 15px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .btn-playlist-delete:hover { background: #ff4e45; color: #fff; }
        .playlist-videos-list { display: flex; flex-direction: column; gap: 8px; }
        .playlist-item { display: flex; gap: 12px; padding: 8px; border-radius: 8px; cursor: pointer; transition: background 0.15s; align-items: center; }
        .playlist-item:hover { background: #272727; }
        .playlist-item.active { background: #3f3f3f; }
        .playlist-item-index { font-size: 14px; color: #aaa; width: 24px; text-align: center; flex-shrink: 0; }
        .playlist-item-thumb { width: 120px; aspect-ratio: 16/9; background: #272727; border-radius: 6px; overflow: hidden; flex-shrink: 0; position: relative; }
        .playlist-item-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .playlist-item-info { flex: 1; min-width: 0; }
        .playlist-item-title { font-size: 14px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; }
        .playlist-item-channel { font-size: 12px; color: #aaa; }
        .playlist-item-remove { background: transparent; border: none; color: #aaa; cursor: pointer; padding: 8px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .playlist-item-remove:hover { color: #ff4e45; background: rgba(255,78,69,0.15); }
        .back-btn { background: transparent; border: none; color: #fff; cursor: pointer; padding: 8px 12px; font-size: 14px; display: flex; align-items: center; gap: 4px; }
        .back-btn:hover { color: #aaa; }

        /* ===== ADD-TO-PLAYLIST MODAL ===== */
        #playlist-modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; padding: 16px; }
        #playlist-modal.active { display: flex; }
        .modal-content { background: #1c1c1c; border-radius: 16px; max-width: 460px; width: 100%; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column; }
        .modal-header { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: space-between; }
        .modal-title { font-size: 18px; font-weight: 700; }
        .modal-close { background: transparent; border: none; color: #aaa; cursor: pointer; padding: 6px; border-radius: 50%; }
        .modal-close:hover { background: rgba(255,255,255,0.1); color: #fff; }
        .modal-body { padding: 12px 20px; overflow-y: auto; flex: 1; }
        .modal-create-row { display: flex; gap: 8px; margin-bottom: 12px; }
        .modal-create-input { flex: 1; background: #272727; border: 1px solid #3f3f3f; color: #fff; padding: 10px 14px; border-radius: 20px; font-size: 14px; outline: none; }
        .modal-create-input:focus { border-color: #1c62b9; }
        .modal-create-btn { background: #3ea6ff; color: #0f0f0f; border: none; padding: 10px 18px; border-radius: 20px; font-size: 14px; font-weight: 600; cursor: pointer; }
        .modal-create-btn:hover { background: #5ab8ff; }
        .modal-playlist-list { display: flex; flex-direction: column; gap: 4px; }
        .modal-playlist-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; cursor: pointer; transition: background 0.15s; }
        .modal-playlist-item:hover { background: #272727; }
        .modal-playlist-icon { width: 40px; height: 40px; background: #272727; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #aaa; flex-shrink: 0; overflow: hidden; }
        .modal-playlist-icon img { width: 100%; height: 100%; object-fit: cover; }
        .modal-playlist-info { flex: 1; min-width: 0; }
        .modal-playlist-name { font-size: 14px; font-weight: 500; }
        .modal-playlist-count { font-size: 12px; color: #aaa; }
        .modal-playlist-check { color: #3ea6ff; visibility: hidden; }
        .modal-playlist-item.has-video .modal-playlist-check { visibility: visible; }
        .modal-empty { padding: 24px; text-align: center; color: #aaa; font-size: 14px; }

        /* ===== AUTOPLAY COUNTDOWN ===== */
        #autoplay-countdown { display: none; position: fixed; bottom: 100px; right: 24px; background: #1c1c1c; padding: 14px 16px; border-radius: 12px; z-index: 250; box-shadow: 0 6px 18px rgba(0,0,0,0.7); max-width: 360px; border: 1px solid rgba(255,255,255,0.1); }
        .ac-row { display: flex; align-items: center; gap: 12px; }
        .ac-thumb { width: 96px; aspect-ratio: 16/9; background: #272727; border-radius: 6px; overflow: hidden; flex-shrink: 0; }
        .ac-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .ac-text { flex: 1; min-width: 0; }
        .ac-label { font-size: 12px; color: #ff4e45; font-weight: 600; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        .ac-title { font-size: 13px; font-weight: 600; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.3; margin-bottom: 6px; }
        .ac-meta-row { display: flex; align-items: center; gap: 8px; }
        .ac-timer-ring { width: 30px; height: 30px; border-radius: 50%; border: 3px solid #3f3f3f; border-top-color: #ff4e45; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; }
        .ac-cancel { background: #444; border: none; color: #fff; padding: 6px 14px; border-radius: 16px; cursor: pointer; font-size: 12px; font-weight: 500; flex-shrink: 0; }
        .ac-cancel:hover { background: #555; }
        @media (max-width: 792px) {
            #autoplay-countdown { right: 12px; left: 12px; bottom: 80px; max-width: none; }
            .ac-thumb { width: 80px; }
            #playlist-section { margin-left: 0; padding: 0 16px 70px; }
            .playlists-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
            .playlist-detail-thumb { width: 100%; }
        }

        /* ===== PLAYER PLAYLIST BAR (when a playlist is active) ===== */
        #playlist-queue-bar { display: none; background: #1c1c1c; border-radius: 12px; padding: 12px; margin-top: 16px; }
        .pq-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; gap: 8px; }
        .pq-title { font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0; }
        .pq-title-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .pq-controls { display: flex; gap: 6px; flex-shrink: 0; }
        .pq-btn { background: #272727; border: none; color: #fff; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.15s; }
        .pq-btn:hover:not(:disabled) { background: #3f3f3f; }
        .pq-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .pq-btn.close { color: #ff4e45; }
        .pq-list { max-height: 240px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
        .pq-item { display: flex; gap: 8px; padding: 6px; border-radius: 6px; cursor: pointer; align-items: center; }
        .pq-item:hover { background: #272727; }
        .pq-item.active { background: #3f3f3f; }
        .pq-item-thumb { width: 80px; aspect-ratio: 16/9; border-radius: 4px; overflow: hidden; flex-shrink: 0; background: #272727; }
        .pq-item-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .pq-item-info { flex: 1; min-width: 0; }
        .pq-item-title { font-size: 12px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .pq-item-channel { font-size: 11px; color: #aaa; }

        /* ===== ADD TO PLAYLIST BUTTON (in action row) ===== */
        .playlist-added-flash { animation: playlistFlash 1.2s ease; }
        @keyframes playlistFlash { 0% { background: #272727; } 30% { background: #3ea6ff; color: #0f0f0f; } 100% { background: #272727; } }
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
        <button type="button" class="header-icon" style="background:#181818; margin-left:12px;" onclick="triggerVoiceSearch()"><span class="material-icons-outlined">mic</span></button>
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
        <button type="button" class="header-icon" style="background:#222; border-radius:50%; width:36px; height:36px;" onclick="triggerVoiceSearch()"><span class="material-icons-outlined" style="font-size:20px;">mic</span></button>
    </form>
</header>

<nav id="sidebar">
    <div class="sidebar-item active" onclick="goHome(event)"><span class="material-icons-outlined">home</span><span class="sidebar-label">Beranda</span></div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-item" onclick="showProfile(this)"><span class="material-icons-outlined">history</span><span class="sidebar-label">Histori</span></div>
    <div class="sidebar-item" onclick="showPlaylistsView(this)"><span class="material-icons-outlined">playlist_play</span><span class="sidebar-label">Playlist Saya</span></div>
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
                    <button class="btn-subscribe" id="btn-subscribe-player" onclick="toggleSubscribe(this)">Subscribe</button>
                </div>
                <div class="action-row">
                    <button class="action-pill" id="btn-like-player" onclick="toggleLike(this)"><span class="material-icons-outlined">thumb_up</span> Suka</button>
                    <button class="action-pill" id="btn-dislike-player" onclick="toggleDislike(this)"><span class="material-icons-outlined">thumb_down</span></button>
                    <button class="action-pill" onclick="shareCurrentVideo()"><span class="material-icons-outlined">reply</span> Bagikan</button>
                    <button class="action-pill" id="btn-add-to-playlist" onclick="openAddToPlaylistModal()"><span class="material-icons-outlined">playlist_add</span> Simpan</button>
                    <button class="action-pill" onclick="alert('Mengunduh video dalam kualitas tinggi... (Fitur Premium Aktif)')"><span class="material-icons-outlined">download</span> Download</button>
                </div>
                <div id="playlist-queue-bar"></div>
                <div class="comments-box">
                    <div style="font-weight:700; margin-bottom:8px; font-size:14px;">Komentar <span style="font-weight:400; color:#aaa;">245</span></div>
                    <div style="display:flex; gap:10px; font-size:13px; align-items:center;">
                        <div class="channel-avatar global-avatar-disp" style="width:28px; height:28px;">t</div>
                        <input type="text" placeholder="Tulis komentar..." style="flex:1; background:transparent; border:none; border-bottom:1px solid #444; color:#fff; padding:4px 0; outline:none;" onkeydown="if(event.key==='Enter'){alert('Komentar berhasil ditambahkan!'); this.value='';}">
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

<div id="playlist-section">
    <button class="back-btn" onclick="showPlaylistsView(document.querySelectorAll('.sidebar-item, .nav-item')[document.querySelectorAll('.nav-item').length-1] || document.querySelector('.sidebar-item'))" style="margin-bottom: 8px; display:none;" id="playlist-back-btn"><span class="material-icons-outlined">arrow_back</span> Kembali</button>
    <div id="playlist-section-content"></div>
</div>

<div id="playlist-modal">
    <div class="modal-content">
        <div class="modal-header">
            <div class="modal-title">Simpan ke playlist</div>
            <button class="modal-close" onclick="closeAddToPlaylistModal()"><span class="material-icons-outlined">close</span></button>
        </div>
        <div class="modal-body">
            <div class="modal-create-row">
                <input type="text" id="modal-new-playlist-name" class="modal-create-input" placeholder="Buat playlist baru..." maxlength="60">
                <button class="modal-create-btn" onclick="createPlaylistFromModal()">Buat</button>
            </div>
            <div class="modal-playlist-list" id="modal-playlist-list"></div>
        </div>
    </div>
</div>

<div id="autoplay-countdown">
    <div class="ac-row">
        <div class="ac-thumb"><img id="ac-thumb-img" src="" alt=""></div>
        <div class="ac-text">
            <div class="ac-label">Putar Selanjutnya</div>
            <div class="ac-title" id="ac-title"></div>
            <div class="ac-meta-row">
                <div class="ac-timer-ring" id="ac-timer">5</div>
                <button class="ac-cancel" onclick="cancelAutoplay()">Batal</button>
            </div>
        </div>
    </div>
</div>

<button id="scrollTopBtn" onclick="scrollToTop()" title="Ke atas"><span class="material-icons-outlined">arrow_upward</span></button>

<nav id="bottom-nav">
    <div class="nav-item active" onclick="goHome(event, this)"><span class="material-icons-outlined">home</span><span class="nav-label">Beranda</span></div>
    <div class="nav-item" onclick="showPlaylistsView(this)"><span class="material-icons-outlined">playlist_play</span><span class="nav-label">Playlist</span></div>
    <div class="nav-item" onclick="showProfile(this)"><div class="nav-avatar global-avatar-disp">t</div><span class="nav-label">Anda</span></div>
</nav>

<script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js?v=19').then(reg => {
                reg.update();
            }).catch(() => {});
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
            await deferredPrompt.userChoice;
            deferredPrompt = null;
            installBtn.style.display = 'none';
        }
    });

    window.addEventListener('appinstalled', () => {
        installBtn.style.display = 'none';
    });

    // App state
    let currentQuery = '';
    let currentCategory = '';
    let currentOffset = 0;
    let isLoadingMore = false;
    let hasMoreHome = true;
    
    let currentRelatedKeyword = '';
    let currentRelatedOffset = 0;
    let isRelatedLoading = false;
    let hasMoreRelated = true;
    
    let currentPlayingVideo = null;
    const loadedGridIds = new Set();
    const loadedRelatedIds = new Set();
    let relatedVideosList = [];

    // ===== YouTube IFrame API state =====
    let ytPlayer = null;
    let pendingPlayVideoId = null;
    let autoplayCountdownTimer = null;
    let autoplayCountdownCallback = null;

    // ===== Playlist state =====
    let activePlaylist = null;          // { name, videos: [], created }
    let activePlaylistIndex = -1;      // index of currently playing video in activePlaylist
    let currentDetailPlaylistName = null;  // currently viewed playlist detail
    let modalPendingVideo = null;      // video to add via modal
    
    window.addEventListener('DOMContentLoaded', () => { 
        loadCustomAvatar();
        history.replaceState({view: 'home'}, '', '');
        initInfiniteScrollObservers();
        loadHome(); 
    });

    window.addEventListener('popstate', (e) => {
        isLoadingMore = false;
        isRelatedLoading = false;
        if (e.state && e.state.view === 'player') {
            playVideo(e.state.video, false);
        } else if (e.state && e.state.view === 'profile') {
            showProfile(document.querySelectorAll('.nav-item')[1], false);
        } else if (e.state && e.state.view === 'playlists') {
            showPlaylistsView(null, false);
        } else if (e.state && e.state.view === 'playlist-detail' && e.state.name) {
            currentDetailPlaylistName = e.state.name;
            showPlaylistDetail(e.state.name, false);
        } else {
            goHome(null, document.querySelector('.nav-item'), false);
        }
    });

    // Setup intersection observer for true seamless infinite scroll
    function initInfiniteScrollObservers() {
        const mainLoader = document.getElementById('main-scroll-loader');
        if (mainLoader && 'IntersectionObserver' in window) {
            const mainObserver = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting && !isLoadingMore && hasMoreHome && isMainVisible()) {
                    loadMoreData();
                }
            }, { rootMargin: '300px' });
            mainObserver.observe(mainLoader);
        }

        const relatedLoader = document.getElementById('related-scroll-loader');
        if (relatedLoader && 'IntersectionObserver' in window) {
            const relatedObserver = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting && !isRelatedLoading && hasMoreRelated && isPlayerVisible()) {
                    loadMoreRelated();
                }
            }, { rootMargin: '300px' });
            relatedObserver.observe(relatedLoader);
        }
    }

    function isMainVisible() {
        const m = document.getElementById('main');
        return m && m.style.display !== 'none';
    }

    function isPlayerVisible() {
        const p = document.getElementById('player-section');
        return p && p.style.display === 'block';
    }
    
    // Throttled scroll listener backup & scroll-to-top button
    let scrollTicking = false;
    window.addEventListener('scroll', () => {
        if (!scrollTicking) {
            window.requestAnimationFrame(() => {
                const scrollTopBtn = document.getElementById('scrollTopBtn');
                scrollTopBtn.style.display = window.scrollY > 400 ? 'flex' : 'none';

                if (!isLoadingMore && hasMoreHome && isMainVisible()) {
                    const scrollBottom = window.innerHeight + window.pageYOffset;
                    if (scrollBottom >= document.documentElement.scrollHeight - 350) {
                        loadMoreData();
                    }
                } else if (!isRelatedLoading && hasMoreRelated && isPlayerVisible()) {
                    const scrollBottom = window.innerHeight + window.pageYOffset;
                    if (scrollBottom >= document.documentElement.scrollHeight - 350) {
                        loadMoreRelated();
                    }
                }
                scrollTicking = false;
            });
            scrollTicking = true;
        }
    }, { passive: true });

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
        document.querySelectorAll('.global-avatar-disp').forEach(el => {
            el.innerHTML = `<img src="${imgSrc}" alt="Avatar" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
        });
        const profileInner = document.getElementById('profile-avatar-inner');
        if (profileInner) {
            profileInner.innerHTML = `<img src="${imgSrc}" alt="Avatar" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
        }
    }

    async function loadHome(category = '') {
        isLoadingMore = false;
        hasMoreHome = true;
        currentQuery = '';
        currentCategory = category;
        currentOffset = 0;
        loadedGridIds.clear();

        document.getElementById('keyword-desktop').value = '';
        document.getElementById('keyword-mobile').value = '';
        document.getElementById('main').style.display = 'block';
        document.getElementById('main-scroll-loader').style.display = 'flex';
        showSkeletons();

        try {
            let url = category ? `/api/home?category=${encodeURIComponent(category)}&offset=0` : '/api/home?offset=0';
            const res = await fetch(url);
            const data = await res.json();
            currentOffset = data.length;
            renderGrid(data);
        } catch(e) {
            console.error(e);
        }
    }

    async function loadMoreData() {
        if (isLoadingMore || !hasMoreHome) return;
        isLoadingMore = true; 
        document.getElementById('main-scroll-loader').style.display = 'flex';
        try {
            let fetchUrl = currentQuery 
                ? `/api/search?q=${encodeURIComponent(currentQuery)}&offset=${currentOffset}` 
                : `/api/home?category=${encodeURIComponent(currentCategory)}&offset=${currentOffset}`;
            const res = await fetch(fetchUrl);
            const data = await res.json();
            if (data && data.length > 0) { 
                currentOffset += data.length; 
                appendToGrid(data); 
            } else {
                hasMoreHome = false;
                document.getElementById('main-scroll-loader').style.display = 'none';
            }
        } catch(e) {
            console.error(e);
        } finally { 
            isLoadingMore = false; 
        }
    }

    function toggleMobileSearch(show) {
        const form = document.getElementById('mobile-search-form');
        const input = document.getElementById('keyword-mobile');
        if (show) { 
            form.classList.add('active'); 
            input.focus(); 
        } else { 
            form.classList.remove('active'); 
        }
    }

    function triggerVoiceSearch() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRec) {
            const rec = new SpeechRec();
            rec.lang = 'id-ID';
            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                document.getElementById('keyword-desktop').value = text;
                document.getElementById('keyword-mobile').value = text;
                executeSearch(text);
            };
            rec.start();
        } else {
            const q = prompt('Telusuri video:');
            if (q) {
                document.getElementById('keyword-desktop').value = q;
                document.getElementById('keyword-mobile').value = q;
                executeSearch(q);
            }
        }
    }

    function searchVideos(e, source) {
        e.preventDefault(); 
        const inputEl = document.getElementById(source === 'desktop' ? 'keyword-desktop' : 'keyword-mobile');
        const q = inputEl.value.trim();
        document.getElementById('keyword-desktop').value = q; 
        document.getElementById('keyword-mobile').value = q;
        if (q) executeSearch(q);
    }

    function executeSearch(q) {
        activateNav(document.querySelector('.nav-item')); 
        currentQuery = q; 
        currentCategory = '';
        currentOffset = 0; 
        isLoadingMore = false;
        hasMoreHome = true;
        loadedGridIds.clear();
        
        document.getElementById('main-scroll-loader').style.display = 'flex';
        showSkeletons();
        fetch('/api/search?q=' + encodeURIComponent(q) + '&offset=0')
            .then(r => r.json())
            .then(d => { 
                currentOffset = d.length; 
                renderGrid(d); 
            });
    }

    function chipClick(btn, category) {
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        if (btn) btn.classList.add('active');
        document.getElementById('keyword-desktop').value = '';
        document.getElementById('keyword-mobile').value = '';
        loadHome(category);
    }

    function activateNav(el) {
        if(!el) return;
        isLoadingMore = false;
        document.querySelectorAll('.nav-item, .sidebar-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
        document.getElementById('main').style.display = 'block';
        document.getElementById('player-section').style.display = 'none';
        document.getElementById('profile-section').style.display = 'none';
        document.getElementById('playlist-section').style.display = 'none';
        document.getElementById('player-box').innerHTML = '';
        ytPlayer = null;  // iframe cleared, must recreate
        hideAutoplayCountdown();
    }

    function goHome(e, el, push = true) { 
        if (e) e.preventDefault(); 
        activePlaylist = null;
        activePlaylistIndex = -1;
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
        if(hist.length === 0) { 
            container.innerHTML = '<div style="color:#aaa; font-size:13px; padding-left:16px;">Belum ada histori tontonan.</div>'; 
            return; 
        }
        container.innerHTML = hist.slice(0, 15).map(v => `
            <div class="hist-card" onclick="playVideo('${encodeURIComponent(JSON.stringify(v))}')">
                <img src="https://i.ytimg.com/vi/${v.id}/mqdefault.jpg" class="hist-thumb" loading="lazy">
                <div class="hist-title">${v.title}</div>
                <div class="hist-channel">${v.channel || ''}</div>
            </div>
        `).join('');
    }

    function playVideo(videoStr, push = true) {
        let v; try { v = JSON.parse(decodeURIComponent(videoStr)); } catch(e){ return; }
        
        currentPlayingVideo = v;
        isLoadingMore = false;
        isRelatedLoading = false;
        hasMoreRelated = true;
        loadedRelatedIds.clear();
        relatedVideosList = [];
        hideAutoplayCountdown();

        let hist = JSON.parse(localStorage.getItem('yt_history') || '[]');
        hist = hist.filter(x => x.id !== v.id);
        hist.unshift(v);
        if(hist.length > 50) hist.pop();
        localStorage.setItem('yt_history', JSON.stringify(hist));

        toggleMobileSearch(false);

        document.getElementById('main').style.display = 'none';
        document.getElementById('profile-section').style.display = 'none';
        document.getElementById('playlist-section').style.display = 'none';
        
        document.getElementById('player-title').textContent = v.title;
        document.getElementById('player-channel-name').textContent = v.channel || 'Channel Name';
        document.getElementById('player-channel-avatar').src = v.avatar || 'https://via.placeholder.com/40';
        
        const subBtn = document.getElementById('btn-subscribe-player');
        if (subBtn) {
            subBtn.className = 'btn-subscribe';
            subBtn.textContent = 'Subscribe';
        }
        const likeBtn = document.getElementById('btn-like-player');
        if (likeBtn) likeBtn.classList.remove('active');
        const dislikeBtn = document.getElementById('btn-dislike-player');
        if (dislikeBtn) dislikeBtn.classList.remove('active');

        // Use YouTube IFrame API instead of plain iframe, so we can detect when video ends
        playVideoInPlayer(v.id);
        
        document.getElementById('player-section').style.display = 'block';
        window.scrollTo(0, 0);

        // Update playlist-queue-bar (only when a playlist is active)
        renderPlaylistQueueBar();

        if (push) {
            history.pushState({view: 'player', video: videoStr}, '', '#watch?v=' + v.id);
        }

        currentRelatedKeyword = v.channel || v.title.split(' ').slice(0, 3).join(' ');
        currentRelatedOffset = 0;
        document.getElementById('related-videos-container').innerHTML = '';
        loadMoreRelated(true);
    }

    function toggleSubscribe(btn) {
        btn.classList.toggle('subscribed');
        btn.textContent = btn.classList.contains('subscribed') ? 'Disubscribe' : 'Subscribe';
    }

    function toggleLike(btn) {
        btn.classList.toggle('active');
        document.getElementById('btn-dislike-player').classList.remove('active');
    }

    function toggleDislike(btn) {
        btn.classList.toggle('active');
        document.getElementById('btn-like-player').classList.remove('active');
    }

    function shareCurrentVideo() {
        if (!currentPlayingVideo) return;
        const url = `https://youtu.be/${currentPlayingVideo.id}`;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => alert('Tautan video berhasil disalin!')).catch(() => alert('Tautan: ' + url));
        } else {
            alert('Tautan: ' + url);
        }
    }

    async function loadMoreRelated(isFirstLoad = false) {
        if(isRelatedLoading || (!isFirstLoad && !hasMoreRelated)) return;
        isRelatedLoading = true;
        const container = document.getElementById('related-videos-container');
        
        if (isFirstLoad) {
            container.innerHTML = Array(4).fill(`<div class="skeleton-card"><div class="skeleton-thumb"></div><div class="skeleton-info"><div class="skeleton-line" style="width: 90%;"></div><div class="skeleton-line" style="width: 60%;"></div></div></div>`).join('');
            document.getElementById('related-scroll-loader').style.display = 'flex';
        } else {
            document.getElementById('related-scroll-loader').style.display = 'flex';
        }

        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(currentRelatedKeyword)}&offset=${currentRelatedOffset}`);
            const data = await res.json();
            
            if (isFirstLoad) container.innerHTML = ''; 
            
            if (data && data.length > 0) {
                currentRelatedOffset += data.length;
                const newItems = data.filter(item => item.id && !loadedRelatedIds.has(item.id));
                newItems.forEach(item => loadedRelatedIds.add(item.id));
                newItems.forEach(item => relatedVideosList.push(item));

                const html = newItems.map(item => {
                    const itemStr = encodeURIComponent(JSON.stringify(item));
                    let meta = [item.channel, item.views].filter(Boolean).join(' • ');
                    return `<div class="related-card" onclick="playVideo('${itemStr}')"><div class="related-thumb"><img src="https://i.ytimg.com/vi/${item.id}/mqdefault.jpg" loading="lazy">${item.duration ? '<span class="duration-badge">' + item.duration + '</span>' : ''}</div><div class="related-info"><div class="related-vid-title">${item.title}</div><div class="related-vid-channel">${item.channel || ''}</div><div class="related-vid-meta">${meta}</div></div></div>`;
                }).join('');
                container.insertAdjacentHTML('beforeend', html);
            } else {
                hasMoreRelated = false;
                document.getElementById('related-scroll-loader').style.display = 'none';
                if (isFirstLoad) {
                    container.innerHTML = '<div style="color:#aaa; font-size:13px;">Tidak ada video serupa.</div>';
                }
            }
        } catch(e) {
            if(isFirstLoad) container.innerHTML = '<div style="color:#aaa; font-size:13px;">Gagal memuat video serupa.</div>';
        } finally {
            isRelatedLoading = false;
        }
    }

    function showSkeletons() { 
        document.getElementById('video-grid').innerHTML = Array(6).fill(`<div class="vid-card"><div class="thumb-wrap" style="background:#272727; animation: pulse 1.5s infinite;"></div><div class="vid-info"><div class="channel-avatar" style="animation: pulse 1.5s infinite;"></div><div class="vid-text"><div style="height:14px; background:#272727; margin-bottom:8px; width:90%; border-radius:4px; animation: pulse 1.5s infinite;"></div><div style="height:12px; background:#272727; width:60%; border-radius:4px; animation: pulse 1.5s infinite;"></div></div></div></div>`).join(''); 
    }

    function renderGrid(data) { 
        const g = document.getElementById('video-grid'); 
        g.innerHTML = ''; 
        loadedGridIds.clear();
        appendToGrid(data); 
    }

    function appendToGrid(data) {
        const g = document.getElementById('video-grid');
        data.forEach(v => {
            if (!v.id || loadedGridIds.has(v.id)) return;
            loadedGridIds.add(v.id);
            const card = document.createElement('div'); 
            card.className = 'vid-card';
            card.onclick = () => playVideo(encodeURIComponent(JSON.stringify(v)));
            let avatarHtml = v.avatar ? `<div class="channel-avatar"><img src="${v.avatar}" loading="lazy"></div>` : `<div class="channel-avatar">${v.channel ? v.channel.charAt(0).toUpperCase() : '?'}</div>`;
            card.innerHTML = `<div class="thumb-wrap"><img class="thumb-img" src="https://i.ytimg.com/vi/${v.id}/hqdefault.jpg" loading="lazy">${v.duration ? '<span class="duration-badge">' + v.duration + '</span>' : ''}</div><div class="vid-info">${avatarHtml}<div class="vid-text"><div class="vid-title">${v.title}</div><div class="vid-meta">${[v.channel, v.views, v.published].filter(Boolean).join(' • ')}</div></div></div>`;
            g.appendChild(card);
        });
    }

    // =========================================================================
    //  YOUTUBE IFRAME API - diperlukan untuk mendeteksi kapan video selesai
    //  sehingga kita bisa memutar video selanjutnya secara otomatis.
    // =========================================================================
    function onYouTubeIframeAPIReady() {
        if (pendingPlayVideoId) {
            const id = pendingPlayVideoId;
            pendingPlayVideoId = null;
            initYtPlayer(id);
        }
    }

    function playVideoInPlayer(videoId) {
        // Jika player sudah ada, cukup ganti videonya (tanpa buang container)
        if (ytPlayer && typeof ytPlayer.loadVideoById === 'function') {
            try {
                ytPlayer.loadVideoById(videoId);
                return;
            } catch(e) {
                console.warn('loadVideoById gagal, membuat player baru:', e);
                ytPlayer = null;
            }
        }
        // Jika API belum siap, simpan id untuk diputar nanti
        if (typeof YT === 'undefined' || !YT.Player) {
            pendingPlayVideoId = videoId;
            return;
        }
        initYtPlayer(videoId);
    }

    function initYtPlayer(videoId) {
        const box = document.getElementById('player-box');
        box.innerHTML = '<div id="yt-player-mount"></div>';
        try {
            ytPlayer = new YT.Player('yt-player-mount', {
                height: '100%',
                width: '100%',
                videoId: videoId,
                playerVars: {
                    autoplay: 1,
                    rel: 0,
                    modestbranding: 1,
                    iv_load_policy: 3,
                    playsinline: 1
                },
                events: {
                    'onStateChange': onPlayerStateChange,
                    'onReady': onPlayerReady,
                    'onError': onPlayerError
                }
            });
        } catch(e) {
            console.error('Gagal membuat YT.Player:', e);
            // Fallback ke iframe biasa (autoplay tetap jalan, tapi auto-next tidak akan bekerja)
            box.innerHTML = `<iframe src="https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1&iv_load_policy=3" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
            ytPlayer = null;
        }
    }

    function onPlayerReady(event) {
        try { event.target.playVideo(); } catch(e) {}
    }

    function onPlayerError(event) {
        console.warn('Player error:', event.data);
        // Kalau video error (mis. diblokir), langsung lanjut ke video selanjutnya
        hideAutoplayCountdown();
        setTimeout(() => handleVideoEnded(true), 800);
    }

    function onPlayerStateChange(event) {
        if (event.data === YT.PlayerState.ENDED) {
            handleVideoEnded();
        } else if (event.data === YT.PlayerState.PLAYING) {
            hideAutoplayCountdown();
        }
    }

    // =========================================================================
    //  AUTOPLAY NEXT VIDEO LOGIC
    //  - Jika ada playlist aktif → mainkan video berikutnya dari playlist
    //  - Kalau tidak, cari "episode selanjutnya" (ep 2 → ep 3) di related list
    //  - Kalau tidak ketemu, ambil video related berikutnya
    // =========================================================================
    function handleVideoEnded(forceImmediate = false) {
        // 1) Jika sedang main dari playlist, lanjut ke video berikutnya
        if (activePlaylist && activePlaylistIndex >= 0 && activePlaylistIndex < activePlaylist.videos.length - 1) {
            const nextVid = activePlaylist.videos[activePlaylistIndex + 1];
            if (forceImmediate) {
                playNextVideoNow(nextVid);
            } else {
                showAutoplayCountdown(nextVid, () => playNextVideoNow(nextVid));
            }
            return;
        }

        // 2) Cari "episode selanjutnya" berdasarkan pola judul (ep 2 → ep 3)
        const nextEp = findNextEpisode();
        if (nextEp) {
            if (forceImmediate) {
                playNextVideoNow(nextEp);
            } else {
                showAutoplayCountdown(nextEp, () => playNextVideoNow(nextEp));
            }
            return;
        }

        // 3) Kalau tidak ada pola episode, ambil video related berikutnya
        const nextRelated = getNextRelatedVideo();
        if (nextRelated) {
            if (forceImmediate) {
                playNextVideoNow(nextRelated);
            } else {
                showAutoplayCountdown(nextRelated, () => playNextVideoNow(nextRelated));
            }
            return;
        }
        // Tidak ada video lanjutan — diam saja
    }

    function playNextVideoNow(v) {
        if (!v || !v.id) return;
        // Jika playlist aktif, update index
        if (activePlaylist && activePlaylistIndex >= 0) {
            const idx = activePlaylist.videos.findIndex(x => x.id === v.id);
            if (idx >= 0) activePlaylistIndex = idx;
        }
        playVideo(encodeURIComponent(JSON.stringify(v)));
    }

    // Pola judul episode yang umum: "Episode 2", "Eps 2", "Ep 2", "Part 2", "Bagian 2", "E2", dll
    function findNextEpisode() {
        if (!currentPlayingVideo || !currentPlayingVideo.title) return null;
        const title = currentPlayingVideo.title;

        // Match pola seperti: Episode 2, Eps. 2, Ep 2, Part 2, Bagian 2, E2, eps2
        const epMatch = title.match(/(?:episode|eps\\.?|ep\\.?|part|bagian|e|s\\d+e)\\s?\\.?\\s*(\\d{1,3})/i);
        if (!epMatch) return null;

        const currentEp = parseInt(epMatch[1], 10);
        if (isNaN(currentEp)) return null;
        const nextEp = currentEp + 1;

        // Cari di related list video yang judulnya mengandung "Episode 3", "Ep 3", dll
        // dan bila mungkin mengandung kata kunci yang sama dengan video sekarang
        // (mis. nama series / judul utama)
        const titleWithoutEp = title.replace(epMatch[0], '').trim().toLowerCase();
        // Ambil 2-3 kata pertama dari judul (tanpa nomor episode) sebagai kata kunci
        const keywords = titleWithoutEp.split(/\\s+/).filter(w => w.length > 2).slice(0, 3);

        // Pola judul untuk episode selanjutnya
        const nextPatterns = [
            new RegExp(`\\bep(?:isode)?\\.?\\s?\\.?${nextEp}\\b`, 'i'),
            new RegExp(`\\beps\\.?\\s?\\.?${nextEp}\\b`, 'i'),
            new RegExp(`\\bpart\\s?${nextEp}\\b`, 'i'),
            new RegExp(`\\bbagian\\s?${nextEp}\\b`, 'i'),
            new RegExp(`\\be${nextEp}\\b`, 'i')
        ];

        for (const v of relatedVideosList) {
            if (!v.title || v.id === currentPlayingVideo.id) continue;
            const vTitle = v.title;
            const matchesEp = nextPatterns.some(p => p.test(vTitle));
            if (!matchesEp) continue;
            // Pastikan judul punya kemiripan (mengandung minimal satu keyword yang sama)
            if (keywords.length === 0) return v;
            const vLower = vTitle.toLowerCase();
            if (keywords.some(k => vLower.includes(k))) return v;
        }
        return null;
    }

    function getNextRelatedVideo() {
        if (!currentPlayingVideo) return null;
        // Cari posisi video sekarang di related list
        const idx = relatedVideosList.findIndex(v => v.id === currentPlayingVideo.id);
        if (idx >= 0 && idx < relatedVideosList.length - 1) {
            return relatedVideosList[idx + 1];
        }
        // Kalau tidak ada di list, ambil video pertama yang bukan video sekarang
        return relatedVideosList.find(v => v.id && v.id !== currentPlayingVideo.id) || null;
    }

    function showAutoplayCountdown(video, callback) {
        if (!video || !video.id) return;
        autoplayCountdownCallback = callback;
        const el = document.getElementById('autoplay-countdown');
        const timerEl = document.getElementById('ac-timer');
        const titleEl = document.getElementById('ac-title');
        const thumbEl = document.getElementById('ac-thumb-img');

        titleEl.textContent = video.title || 'Video selanjutnya';
        thumbEl.src = `https://i.ytimg.com/vi/${video.id}/mqdefault.jpg`;
        let seconds = 5;
        timerEl.textContent = seconds;
        el.style.display = 'block';

        if (autoplayCountdownTimer) clearInterval(autoplayCountdownTimer);
        autoplayCountdownTimer = setInterval(() => {
            seconds--;
            if (timerEl) timerEl.textContent = seconds;
            if (seconds <= 0) {
                clearInterval(autoplayCountdownTimer);
                autoplayCountdownTimer = null;
                el.style.display = 'none';
                const cb = autoplayCountdownCallback;
                autoplayCountdownCallback = null;
                if (cb) cb();
            }
        }, 1000);
    }

    function hideAutoplayCountdown() {
        const el = document.getElementById('autoplay-countdown');
        if (el) el.style.display = 'none';
        if (autoplayCountdownTimer) {
            clearInterval(autoplayCountdownTimer);
            autoplayCountdownTimer = null;
        }
        autoplayCountdownCallback = null;
    }

    function cancelAutoplay() {
        hideAutoplayCountdown();
    }

    // =========================================================================
    //  PLAYLIST MANAGEMENT (disimpan di localStorage)
    // =========================================================================
    function getPlaylists() {
        try {
            return JSON.parse(localStorage.getItem('yt_playlists') || '[]');
        } catch(e) { return []; }
    }

    function savePlaylists(playlists) {
        try { localStorage.setItem('yt_playlists', JSON.stringify(playlists)); } catch(e) {}
    }

    function showPlaylistsView(el, push = true) {
        isLoadingMore = false;
        hideAutoplayCountdown();
        if (el) {
            document.querySelectorAll('.nav-item, .sidebar-item').forEach(n => n.classList.remove('active'));
            el.classList.add('active');
        }
        document.getElementById('main').style.display = 'none';
        document.getElementById('player-section').style.display = 'none';
        document.getElementById('profile-section').style.display = 'none';
        document.getElementById('playlist-section').style.display = 'block';
        document.getElementById('playlist-back-btn').style.display = 'none';
        currentDetailPlaylistName = null;

        if (push) {
            history.pushState({view: 'playlists'}, '', '#playlists');
        }
        renderPlaylistsList();
    }

    function renderPlaylistsList() {
        const container = document.getElementById('playlist-section-content');
        const playlists = getPlaylists();
        let html = `
            <div class="playlist-section-header">
                <div class="playlist-section-title">Playlist Saya</div>
                <button class="btn-create-playlist" onclick="createPlaylistFromPrompt()">
                    <span class="material-icons-outlined">add</span> Playlist Baru
                </button>
            </div>
        `;
        if (playlists.length === 0) {
            html += `<div style="padding:40px 20px; text-align:center; color:#aaa;">
                <span class="material-icons-outlined" style="font-size:64px; color:#444; display:block; margin-bottom:16px;">queue_music</span>
                <div style="font-size:16px; margin-bottom:8px;">Belum ada playlist</div>
                <div style="font-size:13px;">Buat playlist pertama Anda, lalu tambahkan video dengan tombol "Simpan" pada pemutar.</div>
            </div>`;
        } else {
            html += `<div class="playlists-grid">`;
            playlists.forEach(pl => {
                const first = pl.videos && pl.videos[0];
                const thumbHtml = first
                    ? `<img src="https://i.ytimg.com/vi/${first.id}/mqdefault.jpg" alt="">`
                    : `<div class="playlist-thumb-placeholder"><span class="material-icons-outlined">queue_music</span></div>`;
                html += `
                    <div class="playlist-card" onclick="showPlaylistDetail('${escapeAttr(pl.name)}')">
                        <div class="playlist-thumb-wrap">${thumbHtml}
                            <div class="playlist-badge"><span class="material-icons-outlined" style="font-size:14px;">playlist_play</span> ${pl.videos.length}</div>
                        </div>
                        <div class="playlist-info">
                            <div class="playlist-card-title">${escapeHtml(pl.name)}</div>
                            <div class="playlist-card-meta">${pl.videos.length} video</div>
                        </div>
                    </div>
                `;
            });
            html += `</div>`;
        }
        container.innerHTML = html;
    }

    function createPlaylistFromPrompt() {
        const name = prompt('Nama playlist baru:', 'Playlist Tanpa Judul');
        if (!name || !name.trim()) return;
        const playlists = getPlaylists();
        if (playlists.find(p => p.name === name.trim())) {
            alert('Playlist dengan nama tersebut sudah ada.');
            return;
        }
        playlists.push({ name: name.trim(), videos: [], created: Date.now() });
        savePlaylists(playlists);
        if (document.getElementById('playlist-section').style.display === 'block' && !currentDetailPlaylistName) {
            renderPlaylistsList();
        }
        if (document.getElementById('playlist-modal').classList.contains('active')) {
            renderModalPlaylistList();
        }
    }

    function createPlaylistFromModal() {
        const input = document.getElementById('modal-new-playlist-name');
        const name = input.value.trim();
        if (!name) return;
        const playlists = getPlaylists();
        if (playlists.find(p => p.name === name)) {
            alert('Playlist dengan nama tersebut sudah ada.');
            return;
        }
        playlists.push({ name, videos: [], created: Date.now() });
        savePlaylists(playlists);
        input.value = '';
        renderModalPlaylistList();
    }

    function showPlaylistDetail(name, push = true) {
        const playlists = getPlaylists();
        const pl = playlists.find(p => p.name === name);
        if (!pl) {
            showPlaylistsView(null, false);
            return;
        }
        currentDetailPlaylistName = name;
        document.getElementById('playlist-section').style.display = 'block';
        document.getElementById('playlist-back-btn').style.display = 'inline-flex';
        document.getElementById('main').style.display = 'none';
        document.getElementById('player-section').style.display = 'none';
        document.getElementById('profile-section').style.display = 'none';

        if (push) {
            history.pushState({view: 'playlist-detail', name: name}, '', '#playlist=' + encodeURIComponent(name));
        }
        renderPlaylistDetail(pl);
    }

    function renderPlaylistDetail(pl) {
        const container = document.getElementById('playlist-section-content');
        const first = pl.videos[0];
        const thumbHtml = first
            ? `<img src="https://i.ytimg.com/vi/${first.id}/mqdefault.jpg" alt="">`
            : `<div class="playlist-thumb-placeholder"><span class="material-icons-outlined">queue_music</span></div>`;
        let html = `
            <button class="back-btn" onclick="showPlaylistsView(null, true)" style="margin-bottom: 12px;">
                <span class="material-icons-outlined">arrow_back</span> Kembali ke Playlist
            </button>
            <div class="playlist-detail-header">
                <div class="playlist-detail-thumb">${thumbHtml}</div>
                <div class="playlist-detail-info">
                    <div class="playlist-detail-title">${escapeHtml(pl.name)}</div>
                    <div class="playlist-detail-meta">${pl.videos.length} video • Dibuat ${new Date(pl.created || Date.now()).toLocaleDateString('id-ID')}</div>
                    <div class="playlist-detail-actions">
                        <button class="btn-play-all" onclick="playPlaylist('${escapeAttr(pl.name)}')">
                            <span class="material-icons-outlined">play_arrow</span> Putar Semua
                        </button>
                        <button class="btn-playlist-delete" onclick="deletePlaylist('${escapeAttr(pl.name)}')">
                            <span class="material-icons-outlined">delete</span> Hapus Playlist
                        </button>
                    </div>
                </div>
            </div>
            <div class="playlist-videos-list">
        `;
        if (pl.videos.length === 0) {
            html += `<div style="padding:24px; text-align:center; color:#aaa;">Playlist ini masih kosong. Tambahkan video lewat tombol "Simpan" di pemutar.</div>`;
        } else {
            pl.videos.forEach((v, i) => {
                const isActive = activePlaylist && activePlaylist.name === pl.name && activePlaylistIndex === i;
                html += `
                    <div class="playlist-item ${isActive ? 'active' : ''}" onclick="playPlaylistFromIndex('${escapeAttr(pl.name)}', ${i})">
                        <div class="playlist-item-index">${isActive ? '<span class="material-icons-outlined" style="font-size:16px; color:#ff4e45;">play_arrow</span>' : (i+1)}</div>
                        <div class="playlist-item-thumb"><img src="https://i.ytimg.com/vi/${v.id}/mqdefault.jpg" loading="lazy"></div>
                        <div class="playlist-item-info">
                            <div class="playlist-item-title">${escapeHtml(v.title || 'No title')}</div>
                            <div class="playlist-item-channel">${escapeHtml(v.channel || '')}</div>
                        </div>
                        <button class="playlist-item-remove" onclick="event.stopPropagation(); removeFromPlaylist('${escapeAttr(pl.name)}', '${v.id}')" title="Hapus dari playlist">
                            <span class="material-icons-outlined" style="font-size:20px;">delete_outline</span>
                        </button>
                    </div>
                `;
            });
        }
        html += `</div>`;
        container.innerHTML = html;
    }

    function playPlaylistFromIndex(name, index) {
        const playlists = getPlaylists();
        const pl = playlists.find(p => p.name === name);
        if (!pl || index < 0 || index >= pl.videos.length) return;
        activePlaylist = pl;
        activePlaylistIndex = index;
        playVideo(encodeURIComponent(JSON.stringify(pl.videos[index])));
    }

    function playPlaylist(name) {
        const playlists = getPlaylists();
        const pl = playlists.find(p => p.name === name);
        if (!pl || pl.videos.length === 0) {
            alert('Playlist ini kosong.');
            return;
        }
        activePlaylist = pl;
        activePlaylistIndex = 0;
        playVideo(encodeURIComponent(JSON.stringify(pl.videos[0])));
    }

    function removeFromPlaylist(name, videoId) {
        const playlists = getPlaylists();
        const pl = playlists.find(p => p.name === name);
        if (!pl) return;
        pl.videos = pl.videos.filter(v => v.id !== videoId);
        savePlaylists(playlists);
        // Kalau playlist aktif sedang diputar, sinkronkan
        if (activePlaylist && activePlaylist.name === name) {
            activePlaylist = pl;
            if (activePlaylistIndex >= pl.videos.length) activePlaylistIndex = pl.videos.length - 1;
            renderPlaylistQueueBar();
        }
        renderPlaylistDetail(pl);
    }

    function deletePlaylist(name) {
        if (!confirm(`Hapus playlist "${name}"?`)) return;
        let playlists = getPlaylists();
        playlists = playlists.filter(p => p.name !== name);
        savePlaylists(playlists);
        if (activePlaylist && activePlaylist.name === name) {
            activePlaylist = null;
            activePlaylistIndex = -1;
            renderPlaylistQueueBar();
        }
        showPlaylistsView(null, true);
    }

    // =========================================================================
    //  PLAYLIST QUEUE BAR (di bawah player saat playlist aktif)
    // =========================================================================
    function renderPlaylistQueueBar() {
        const bar = document.getElementById('playlist-queue-bar');
        if (!bar) return;
        if (!activePlaylist || activePlaylistIndex < 0 || activePlaylist.videos.length === 0) {
            bar.style.display = 'none';
            bar.innerHTML = '';
            return;
        }
        bar.style.display = 'block';
        const hasPrev = activePlaylistIndex > 0;
        const hasNext = activePlaylistIndex < activePlaylist.videos.length - 1;
        let html = `
            <div class="pq-header">
                <div class="pq-title">
                    <span class="material-icons-outlined" style="font-size:18px; color:#ff4e45;">queue_music</span>
                    <span class="pq-title-text">${escapeHtml(activePlaylist.name)} • ${activePlaylistIndex+1}/${activePlaylist.videos.length}</span>
                </div>
                <div class="pq-controls">
                    <button class="pq-btn" ${hasPrev ? '' : 'disabled'} onclick="prevInPlaylist()" title="Sebelumnya">
                        <span class="material-icons-outlined" style="font-size:18px;">skip_previous</span>
                    </button>
                    <button class="pq-btn" ${hasNext ? '' : 'disabled'} onclick="nextInPlaylist()" title="Selanjutnya">
                        <span class="material-icons-outlined" style="font-size:18px;">skip_next</span>
                    </button>
                    <button class="pq-btn close" onclick="exitPlaylistMode()" title="Keluar dari playlist">
                        <span class="material-icons-outlined" style="font-size:18px;">close</span>
                    </button>
                </div>
            </div>
            <div class="pq-list">
        `;
        activePlaylist.videos.forEach((v, i) => {
            const isActive = i === activePlaylistIndex;
            html += `
                <div class="pq-item ${isActive ? 'active' : ''}" onclick="playPlaylistFromIndex('${escapeAttr(activePlaylist.name)}', ${i})">
                    <div class="pq-item-thumb"><img src="https://i.ytimg.com/vi/${v.id}/mqdefault.jpg" loading="lazy"></div>
                    <div class="pq-item-info">
                        <div class="pq-item-title">${escapeHtml(v.title || 'No title')}</div>
                        <div class="pq-item-channel">${escapeHtml(v.channel || '')}</div>
                    </div>
                </div>
            `;
        });
        html += `</div>`;
        bar.innerHTML = html;
    }

    function nextInPlaylist() {
        if (!activePlaylist || activePlaylistIndex < 0) return;
        if (activePlaylistIndex >= activePlaylist.videos.length - 1) return;
        hideAutoplayCountdown();
        activePlaylistIndex++;
        playVideo(encodeURIComponent(JSON.stringify(activePlaylist.videos[activePlaylistIndex])));
    }

    function prevInPlaylist() {
        if (!activePlaylist || activePlaylistIndex <= 0) return;
        hideAutoplayCountdown();
        activePlaylistIndex--;
        playVideo(encodeURIComponent(JSON.stringify(activePlaylist.videos[activePlaylistIndex])));
    }

    function exitPlaylistMode() {
        activePlaylist = null;
        activePlaylistIndex = -1;
        renderPlaylistQueueBar();
    }

    // =========================================================================
    //  ADD TO PLAYLIST MODAL
    // =========================================================================
    function openAddToPlaylistModal() {
        if (!currentPlayingVideo) return;
        modalPendingVideo = currentPlayingVideo;
        document.getElementById('modal-new-playlist-name').value = '';
        renderModalPlaylistList();
        document.getElementById('playlist-modal').classList.add('active');
    }

    function closeAddToPlaylistModal() {
        document.getElementById('playlist-modal').classList.remove('active');
        modalPendingVideo = null;
    }

    function renderModalPlaylistList() {
        const list = document.getElementById('modal-playlist-list');
        const playlists = getPlaylists();
        if (playlists.length === 0) {
            list.innerHTML = `<div class="modal-empty">Belum ada playlist. Buat baru di kotak di atas.</div>`;
            return;
        }
        const v = modalPendingVideo;
        list.innerHTML = playlists.map(pl => {
            const hasVideo = v && pl.videos.some(x => x.id === v.id);
            const first = pl.videos[0];
            const thumbHtml = first
                ? `<img src="https://i.ytimg.com/vi/${first.id}/default.jpg" alt="">`
                : `<span class="material-icons-outlined">queue_music</span>`;
            return `
                <div class="modal-playlist-item ${hasVideo ? 'has-video' : ''}" onclick="toggleVideoInPlaylist('${escapeAttr(pl.name)}')">
                    <div class="modal-playlist-icon">${thumbHtml}</div>
                    <div class="modal-playlist-info">
                        <div class="modal-playlist-name">${escapeHtml(pl.name)}</div>
                        <div class="modal-playlist-count">${pl.videos.length} video${hasVideo ? ' • Sudah ditambahkan' : ''}</div>
                    </div>
                    <span class="material-icons-outlined modal-playlist-check">check_circle</span>
                </div>
            `;
        }).join('');
    }

    function toggleVideoInPlaylist(name) {
        const playlists = getPlaylists();
        const pl = playlists.find(p => p.name === name);
        if (!pl || !modalPendingVideo) return;
        const idx = pl.videos.findIndex(v => v.id === modalPendingVideo.id);
        if (idx >= 0) {
            pl.videos.splice(idx, 1);
        } else {
            pl.videos.push({...modalPendingVideo});
        }
        savePlaylists(playlists);
        // Animasi feedback pada tombol "Simpan"
        const btn = document.getElementById('btn-add-to-playlist');
        if (btn) {
            btn.classList.remove('playlist-added-flash');
            void btn.offsetWidth;  // restart animation
            btn.classList.add('playlist-added-flash');
        }
        renderModalPlaylistList();
        // Update queue bar jika playlist aktif
        if (activePlaylist && activePlaylist.name === name) {
            activePlaylist = pl;
            renderPlaylistQueueBar();
        }
    }

    // =========================================================================
    //  Helper escape
    // =========================================================================
    function escapeHtml(s) {
        if (!s) return '';
        return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }
    function escapeAttr(s) {
        if (!s) return '';
        return String(s).replace(/'/g, "\\'").replace(/"/g, '&quot;');
    }

    // Klik di luar modal = tutup modal
    document.addEventListener('click', (e) => {
        const modal = document.getElementById('playlist-modal');
        if (modal && modal.classList.contains('active') && e.target === modal) {
            closeAddToPlaylistModal();
        }
    });
</script>
</body>
</html>
"""

def extract_video_data(video):
    data = {"id": video.get("videoId"), "title": "No Title"}
    try: 
        runs = video.get("title", {}).get("runs")
        if runs: data["title"] = runs[0].get("text", "No Title")
        elif video.get("title", {}).get("simpleText"):
            data["title"] = video["title"]["simpleText"]
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
    const CACHE_NAME = 'yt-clone-v19';
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

# ==============================================================================
# SISTEM CACHING TINGKAT LANJUT (PERSISTEN DISK & MEMORI RAM)
# Mencegah scraping berulang dari awal. Video disimpan dan di-cache secara otomatis.
# ==============================================================================

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt_cache.json")
CACHE_TTL = 86400  # Masa aktif cache: 24 jam dalam detik

GLOBAL_CACHE = {}

def load_cache():
    global GLOBAL_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    GLOBAL_CACHE = data
                    logging.info(f"Loaded cache from disk: {len(GLOBAL_CACHE)} keyword tersimpan.")
        except Exception as e:
            logging.warning(f"Gagal membaca file cache: {e}")

def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(GLOBAL_CACHE, f, ensure_ascii=False)
    except Exception as e:
        logging.warning(f"Gagal menyimpan cache ke disk: {e}")

def get_videos_with_cache(keyword, offset=0, limit=15):
    """
    Mengambil video dari cache memori/disk tanpa scraping ulang dari awal.
    Jika video di cache belum mencapai (offset + limit), hanya scrape tambahannya.
    """
    global GLOBAL_CACHE
    keyword = keyword.strip().lower()
    if not keyword:
        return []

    now = time.time()
    entry = GLOBAL_CACHE.get(keyword)
    cached_videos = entry.get("videos", []) if entry else []

    # Cek apakah cache mencukupi dan belum kadaluarsa
    if entry and len(cached_videos) >= (offset + limit) and (now - entry.get("timestamp", 0) < CACHE_TTL):
        return cached_videos[offset : offset + limit]

    # Jika cache belum mencapai jumlah yang dibutuhkan, scrape kelanjutannya
    needed = max(50, offset + limit + 25)
    try:
        logging.info(f"Cache butuh data tambahan untuk '{keyword}' (total {needed} video)...")
        seen_ids = set()
        combined_videos = []

        # Pertahankan data lama yang sudah ada di cache
        for v in cached_videos:
            if v.get("id") and v["id"] not in seen_ids:
                seen_ids.add(v["id"])
                combined_videos.append(v)

        # Scrape untuk melengkapi batas yang dibutuhkan
        for v in scrapetube.get_search(keyword, limit=needed):
            d = extract_video_data(v)
            if d.get("id") and d["id"] not in seen_ids:
                seen_ids.add(d["id"])
                combined_videos.append(d)

        GLOBAL_CACHE[keyword] = {
            "timestamp": now,
            "videos": combined_videos
        }
        save_cache()
        return combined_videos[offset : offset + limit]
    except Exception as e:
        logging.error(f"Gagal scraping data untuk '{keyword}': {e}")
        # Jika koneksi gagal, kembalikan apa yang sudah ada di cache
        if cached_videos:
            return cached_videos[offset : offset + limit]
        return []

# Muat cache saat startup
load_cache()

@app.route("/api/home")
def api_home():
    category = request.args.get("category", "").strip()
    offset = int(request.args.get("offset", 0))
    limit = 15
    search_key = f"{category} Indonesia" if category else "Trending Indonesia"
    results = get_videos_with_cache(search_key, offset=offset, limit=limit)
    return jsonify(results)

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    offset = int(request.args.get("offset", 0))
    limit = 15
    if not query: 
        return jsonify([])
    results = get_videos_with_cache(query, offset=offset, limit=limit)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=2000)
