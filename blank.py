import os
import streamlit as st
import boto3
from boto3.dynamodb.conditions import Key
import pandas as pd
import base64
from decimal import Decimal

# 页面配置（尽早设置）
st.set_page_config(page_title="Algae Box Monitor", layout="wide")

# ---------- 从 Streamlit Secrets 读取 AWS 凭证 ----------
# 注意：必须在部署时在 Streamlit Cloud 的 Secrets 中添加以下键值对
AWS_ACCESS_KEY_ID = st.secrets.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = st.secrets.get("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = st.secrets.get("AWS_DEFAULT_REGION")

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
        os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
if AWS_DEFAULT_REGION:
        os.environ['AWS_DEFAULT_REGION'] = AWS_DEFAULT_REGION

# ---------- AWS 配置 ----------
REGION = AWS_DEFAULT_REGION or 'ap-southeast-2'
TABLE_NAME = "TankSensorData"

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# ---------- 封面页处理（如果未启动则显示封面并阻止后续渲染） ----------
def show_cover_and_stop():
        try:
                img_path = os.path.join(os.path.dirname(__file__), 'assets', 'cover.jpeg')
                with open(img_path, 'rb') as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception:
                b64 = ''

        html = """
        <html>
        <head>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <style>
            html,body{height:100%;margin:0;}
            .cover{
                background: #000 url('data:image/jpeg;base64,__B64__') center/cover no-repeat;
                height:100vh;display:flex;align-items:center;justify-content:center;transition:opacity 0.8s ease, transform 0.8s ease;
            }
            .fadeout{opacity:0;transform:scale(0.98);}
            .btn{background:rgba(255,255,255,0.95);border:none;padding:24px 40px;border-radius:14px;font-size:28px;cursor:pointer;box-shadow:0 6px 18px rgba(0,0,0,0.3)}
            @media (max-width:600px){ .btn{font-size:20px;padding:18px 28px} }
        </style>
        </head>
        <body>
            <div id="cover" class="cover">
                <button id="startBtn" class="btn">Start Monitoring</button>
            </div>
            <script>
                const btn=document.getElementById('startBtn');
                const cover=document.getElementById('cover');
                btn.addEventListener('click',()=>{
                    cover.classList.add('fadeout');
                    setTimeout(()=>{
                        try{
                            window.top.location.href = window.top.location.href.split('?')[0] + '?started=1';
                        }catch(e){
                            window.parent.location.href = window.parent.location.href.split('?')[0] + '?started=1';
                        }
                    }, 800);
                });
            </script>
        </body>
        </html>
        """
        html = html.replace('__B64__', b64)
        import streamlit.components.v1 as components
        components.html(html, height=900, scrolling=False)
        st.stop()

# 只有在 query param 中有 started=1 时才渲染监控页面
try:
        params = st.experimental_get_query_params()
except Exception:
        params = {}
if 'started' not in params:
        show_cover_and_stop()

# 读取 tank id（从 query params 或使用默认）
tank_id = params.get('tank', ["ESP32_Tank_001"])[0]
        Limit=n,
        ScanIndexForward=False
    )
    items = resp.get('Items', [])
    items.reverse()
    return convert_decimals(items)

# ---------- 界面 ----------
st.title("🌿 Algae Box Monitor")
st.caption(f"当前监控 Tank: **{tank_id}**")

latest = get_latest(tank_id)
if latest:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ 温度", f"{latest.get('temperature', 'N/A')} °C")
    c2.metric("🧪 pH", f"{latest.get('ph', 'N/A')}")
    c3.metric("💧 浊度", f"{latest.get('turbidity_ntu', 'N/A')} NTU")
    c4.metric("🧂 盐度", f"{latest.get('salinity', 'N/A')} ppt")
    st.caption(f"⏱️ 设备运行毫秒数：{latest.get('timestamp', 'N/A')} ms")
else:
    st.warning("⚠️ 暂无数据，请检查表名或设备上报。")

st.markdown("---")

# ---------- 历史趋势 ----------
st.subheader("📈 历史趋势")

n_points = st.slider("显示最近多少条记录", min_value=10, max_value=500, value=100, step=10)

history = get_last_n(tank_id, n=n_points)
if len(history) > 1:
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_numeric(df['timestamp'])
    df = df.sort_values('timestamp')
    for col in ['temperature', 'ph', 'turbidity_ntu']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    st.markdown("**温度变化**")
    st.line_chart(df.set_index('timestamp')['temperature'])

    st.markdown("**pH 变化**")
    st.line_chart(df.set_index('timestamp')['ph'])

    st.markdown("**浊度变化**")
    st.line_chart(df.set_index('timestamp')['turbidity_ntu'])
else:
    st.info(f"📭 历史数据不足（当前 {len(history)} 条），请等待更多采样点。")

# ---------- 设备切换 ----------
tank_list = ["ESP32_Tank_001"]   # 可扩展
selected = st.selectbox("🔄 切换 Tank", tank_list,
                        index=tank_list.index(tank_id) if tank_id in tank_list else 0)
if selected != tank_id:
    st.query_params.tank = selected
    st.rerun()