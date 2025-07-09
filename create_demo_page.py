#!/usr/bin/env python3
"""
姿勢分析アプリ - HTMLデモページ作成スクリプト
"""

import os
from pathlib import Path

def create_demo_html():
    """Create HTML demo page for posture analysis"""
    
    html_content = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>姿勢分析デモ - Posture Analysis Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #00C853 0%, #009624 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .upload-section {
            border: 3px dashed #00C853;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8fff8;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }
        
        .upload-section:hover {
            border-color: #009624;
            background: #f0fff0;
        }
        
        .upload-section.dragover {
            border-color: #009624;
            background: #e8f5e8;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 4em;
            color: #00C853;
            margin-bottom: 20px;
        }
        
        .upload-text {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
        }
        
        .upload-button {
            background: linear-gradient(135deg, #00C853 0%, #009624 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .upload-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,200,83,0.3);
        }
        
        .file-input {
            display: none;
        }
        
        .demo-images {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .demo-image {
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .demo-image:hover {
            border-color: #00C853;
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .demo-image img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #00C853;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
            margin-top: 30px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(#00C853 0deg, #00C853 var(--score-deg), #e0e0e0 var(--score-deg));
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            position: relative;
        }
        
        .score-circle::before {
            content: '';
            width: 90px;
            height: 90px;
            background: white;
            border-radius: 50%;
            position: absolute;
        }
        
        .score-text {
            font-size: 24px;
            font-weight: bold;
            z-index: 1;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .metric {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #00C853;
        }
        
        .metric-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.2em;
            color: #00C853;
        }
        
        .error {
            display: none;
            background: #ffebee;
            color: #c62828;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #c62828;
            margin-top: 20px;
        }
        
        .api-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }
        
        .api-status.online {
            background: #4caf50;
        }
        
        .api-status.offline {
            background: #f44336;
        }
    </style>
</head>
<body>
    <div class="api-status" id="apiStatus">API確認中...</div>
    
    <div class="container">
        <div class="header">
            <h1>🏥 姿勢分析デモ</h1>
            <p>MediaPipe を使った高精度姿勢分析システム</p>
        </div>
        
        <div class="content">
            <div class="upload-section" id="uploadSection">
                <div class="upload-icon">📷</div>
                <div class="upload-text">
                    画像をドラッグ＆ドロップするか、<br>
                    クリックして姿勢分析したい画像を選択してください
                </div>
                <button class="upload-button" onclick="document.getElementById('fileInput').click()">
                    画像を選択
                </button>
                <input type="file" id="fileInput" class="file-input" accept="image/*">
            </div>
            
            <div class="demo-images">
                <div class="demo-image" onclick="showDemoInfo('front')">
                    <div style="width: 100%; height: 150px; background: #e3f2fd; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 3em;">🧍</div>
                    <h3>正面姿勢</h3>
                    <p>肩の高さ・骨盤傾斜をチェック</p>
                </div>
                <div class="demo-image" onclick="showDemoInfo('side')">
                    <div style="width: 100%; height: 150px; background: #e8f5e9; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 3em;">🚶</div>
                    <h3>側面姿勢</h3>
                    <p>頭部前方偏位・脊椎カーブをチェック</p>
                </div>
                <div class="demo-image" onclick="showDemoInfo('back')">
                    <div style="width: 100%; height: 150px; background: #fff3e0; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 3em;">🚶‍♂️</div>
                    <h3>後面姿勢</h3>
                    <p>肩甲骨・脊椎側弯をチェック</p>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
                <h3>姿勢分析中...</h3>
                <p>MediaPipeで高精度解析を実行しています</p>
            </div>
            
            <div class="results" id="results">
                <h2>📊 姿勢分析結果</h2>
                <div class="score-circle" id="scoreCircle" style="--score-deg: 306deg">
                    <div class="score-text" id="scoreText">85</div>
                </div>
                <div class="metrics" id="metrics">
                    <!-- Results will be inserted here -->
                </div>
            </div>
            
            <div class="error" id="error">
                <h3>⚠️ エラーが発生しました</h3>
                <p id="errorMessage"></p>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = 'http://localhost:8000';
        
        // API接続確認
        async function checkApiStatus() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                if (response.ok) {
                    document.getElementById('apiStatus').textContent = 'API オンライン';
                    document.getElementById('apiStatus').className = 'api-status online';
                } else {
                    throw new Error('API応答エラー');
                }
            } catch (error) {
                document.getElementById('apiStatus').textContent = 'API オフライン';
                document.getElementById('apiStatus').className = 'api-status offline';
            }
        }
        
        // ファイルアップロード処理
        document.getElementById('fileInput').addEventListener('change', handleFileUpload);
        
        // ドラッグ&ドロップ
        const uploadSection = document.getElementById('uploadSection');
        
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('dragover');
        });
        
        uploadSection.addEventListener('dragleave', () => {
            uploadSection.classList.remove('dragover');
        });
        
        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                analyzePosture(files[0]);
            }
        });
        
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                analyzePosture(file);
            }
        }
        
        async function analyzePosture(file) {
            // UI状態リセット
            document.getElementById('results').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch(`${API_BASE}/analyze-posture`, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    displayResults(result);
                } else {
                    const error = await response.json();
                    throw new Error(error.detail || '分析に失敗しました');
                }
            } catch (error) {
                showError(error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function displayResults(result) {
            const resultsDiv = document.getElementById('results');
            const scoreText = document.getElementById('scoreText');
            const scoreCircle = document.getElementById('scoreCircle');
            const metricsDiv = document.getElementById('metrics');
            
            // スコア表示
            const score = Math.round(result.overall_score);
            scoreText.textContent = score;
            scoreCircle.style.setProperty('--score-deg', `${score * 3.6}deg`);
            
            // メトリクス表示
            const metrics = result.metrics;
            const metricNames = {
                pelvic_tilt: '骨盤傾斜角',
                thoracic_kyphosis: '胸椎後弯角',
                cervical_lordosis: '頸椎前弯角',
                shoulder_height_difference: '肩の高さの差',
                head_forward_posture: '頭部前方偏位',
                lumbar_lordosis: '腰椎前弯角',
                scapular_protraction: '肩甲骨前方突出',
                trunk_lateral_deviation: '体幹側方偏位'
            };
            
            metricsDiv.innerHTML = '';
            for (const [key, value] of Object.entries(metrics)) {
                const metricDiv = document.createElement('div');
                metricDiv.className = 'metric';
                metricDiv.innerHTML = `
                    <div class="metric-name">${metricNames[key] || key}</div>
                    <div class="metric-value">${value.toFixed(1)}${key.includes('angle') || key.includes('tilt') || key.includes('kyphosis') || key.includes('lordosis') ? '°' : 'cm'}</div>
                `;
                metricsDiv.appendChild(metricDiv);
            }
            
            resultsDiv.style.display = 'block';
        }
        
        function showError(message) {
            document.getElementById('errorMessage').textContent = message;
            document.getElementById('error').style.display = 'block';
        }
        
        function showDemoInfo(type) {
            const messages = {
                front: '正面から撮影した全身画像をアップロードしてください。肩の高さや骨盤の傾きを分析します。',
                side: '真横から撮影した全身画像をアップロードしてください。頭部の位置や背骨のカーブを分析します。',
                back: '後ろから撮影した全身画像をアップロードしてください。肩甲骨の位置や脊椎の歪みを分析します。'
            };
            alert(messages[type]);
        }
        
        // 初期化
        checkApiStatus();
        setInterval(checkApiStatus, 30000); // 30秒ごとにAPI状態確認
    </script>
</body>
</html>'''
    
    # HTMLファイルを作成
    html_path = Path('demo.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTMLデモページ作成完了: {html_path.absolute()}")
    
    # FastAPIにデモページルートを追加
    demo_route = '''
# HTMLデモページのルートを追加
from fastapi.responses import HTMLResponse

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """HTML demo page for posture analysis"""
    with open("demo.html", "r", encoding="utf-8") as f:
        return f.read()
'''
    
    print("\n🔧 FastAPIルート追加:")
    print("backend/app/main.py に以下を追加してください:")
    print(demo_route)
    
    return html_path

if __name__ == "__main__":
    create_demo_html()
    print("\n🌐 使用方法:")
    print("1. ./start_server.sh でサーバー起動")
    print("2. ブラウザで http://localhost:8000/demo を開く")
    print("3. 画像をアップロードして姿勢分析テスト")