from nicegui import ui
import json

# 10 vòng AQI cố định, tâm là trung tâm các quận lớn Hà Nội.
# Phân bổ màu: 2 xanh (tốt), 3 vàng (trung bình), 4 cam (nhạy cảm), 1 đỏ (xấu).
AQI_ZONES = [
    # ── 2 xanh lá (Tốt) — quận ngoại vi, radius vừa ─────────────────────────
    {"name": "Tây Hồ",       "lat": 21.0570, "lng": 105.8230, "radius": 1600, "aqi": 42,  "color": "#00E400", "category": "Tốt"},
    {"name": "Long Biên",    "lat": 21.0380, "lng": 105.9000, "radius": 1700, "aqi": 48,  "color": "#00E400", "category": "Tốt"},
    # ── 3 vàng (Trung bình) ──────────────────────────────────────────────────
    {"name": "Cầu Giấy",     "lat": 21.0370, "lng": 105.7980, "radius": 1700, "aqi": 78,  "color": "#FFFF00", "category": "Trung bình"},
    {"name": "Hoàn Kiếm",    "lat": 21.0285, "lng": 105.8520, "radius": 900,  "aqi": 88,  "color": "#FFFF00", "category": "Trung bình"},
    {"name": "Thanh Xuân",   "lat": 20.9950, "lng": 105.8120, "radius": 3000, "aqi": 95,  "color": "#FFFF00", "category": "Trung bình"},
    # ── 4 cam (Không tốt – nhạy cảm) — thu nhỏ vì chen nhau ─────────────────
    {"name": "Ba Đình",      "lat": 21.0360, "lng": 105.8360, "radius": 1300, "aqi": 118, "color": "#00E400", "category": "Tốt"},
    {"name": "Hai Bà Trưng", "lat": 21.0100, "lng": 105.8520, "radius": 1000, "aqi": 132, "color": "#00E400", "category": "Tốt"},
    {"name": "Hoàng Mai",    "lat": 20.9780, "lng": 105.8560, "radius": 1800, "aqi": 145, "color": "#00E400", "category": "Tốt"},
    {"name": "Nam Từ Liêm",  "lat": 21.0280, "lng": 105.7550, "radius": 1800, "aqi": 138, "color": "#FFFF00", "category": "Trung bình"},
    # ── 1 đỏ (Không tốt) ─────────────────────────────────────────────────────
    {"name": "Đống Đa",      "lat": 21.0200, "lng": 105.8400, "radius": 1100, "aqi": 168, "color": "#FF0000", "category": "Không tốt"},
]


def add_aqi_scripts():
    zones_json = json.dumps(AQI_ZONES)
    ui.add_head_html(f'''
    <script>
    if (typeof window.aqiZones === 'undefined') {{
        window.aqiZones = {zones_json};
        window.aqiLayersByMap = {{}};

        window.showAQIOverlay = function(mapId) {{
            var mapObj = window[mapId + '_instance'];
            if (!mapObj) return;
            window.hideAQIOverlay(mapId);
            window.aqiLayersByMap[mapId] = [];

            window.aqiZones.forEach(function(zone) {{
                var circle = L.circle([zone.lat, zone.lng], {{
                    radius: zone.radius,
                    color: zone.color,
                    fillColor: zone.color,
                    fillOpacity: 0.08,
                    weight: 2.5,
                    interactive: false
                }}).addTo(mapObj);

                var textColor = (zone.aqi <= 100) ? '#333' : '#fff';
                var label = L.tooltip({{
                    permanent: true,
                    direction: 'center',
                    className: 'aqi-zone-tooltip',
                    opacity: 1
                }})
                .setLatLng([zone.lat, zone.lng])
                .setContent(
                    '<div style="background:' + zone.color +
                    ';color:' + textColor +
                    ';padding:3px 9px;border-radius:6px;font-weight:bold;font-size:11px;' +
                    'box-shadow:0 1px 4px rgba(0,0,0,0.35);white-space:nowrap;">' +
                    zone.name + ' · AQI ' + zone.aqi + '</div>'
                )
                .addTo(mapObj);

                window.aqiLayersByMap[mapId].push(circle);
                window.aqiLayersByMap[mapId].push(label);
            }});
        }};

        window.hideAQIOverlay = function(mapId) {{
            var mapObj = window[mapId + '_instance'];
            if (!mapObj) return;
            var layers = window.aqiLayersByMap[mapId];
            if (layers) {{
                layers.forEach(function(l) {{ mapObj.removeLayer(l); }});
                window.aqiLayersByMap[mapId] = [];
            }}
        }};
    }}
    </script>
    <style>
    .aqi-zone-tooltip {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}
    .aqi-zone-tooltip:before {{ display: none !important; }}
    </style>
    ''')


def add_aqi_button(map_id: str = 'map'):
    """Nút toggle AQI: 10 vòng tròn cố định theo quận, opacity 8%."""
    add_aqi_scripts()

    aqi_active = {'value': False}

    async def toggle_aqi():
        if aqi_active['value']:
            await ui.run_javascript(f"hideAQIOverlay('{map_id}')")
            aqi_active['value'] = False
            aqi_btn.props('outline')
        else:
            await ui.run_javascript(f"showAQIOverlay('{map_id}')")
            aqi_active['value'] = True
            aqi_btn.props(remove='outline')

    aqi_btn = ui.button('AQI', on_click=toggle_aqi)
    aqi_btn.props('outline rounded-full color=blue').classes('px-4 text-sm font-bold')
    return aqi_btn
