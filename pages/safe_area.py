from nicegui import ui

@ui.page('/safe-area')
async def safe_area_page():
    """Hiển thị bản đồ với các khu vực an toàn, vị trí công an/bệnh viện gần nhất"""
    ui.page_title('NaviFit — Khu vực an toàn')

    # ── Leaflet ────────────────────────────────────────────────────────────────
    ui.add_head_html('''
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
        .safe-legend {
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            padding: 10px 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            font-family: sans-serif;
            font-size: 12px;
            line-height: 1.8;
        }
        .safe-legend i {
            display: inline-block;
            width: 12px; height: 12px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
        }
        </style>
    ''')

    # ── Header ─────────────────────────────────────────────────────────────────
    with ui.header().classes('items-center justify-between bg-white text-black shadow-md px-6 py-3'):
        ui.label('NaviFit').classes('text-3xl font-extrabold text-blue-600 cursor-pointer').on('click', lambda: ui.navigate.to('/'))

        with ui.row().classes('gap-2'):
            # 安全 đang ACTIVE
            ui.button('安全 (An toàn)').props('rounded color=green text-color=white').classes('text-sm px-3')
            # AQI inactive → về home
            ui.button('AQI', on_click=lambda: ui.navigate.to('/')).props('outline rounded color=gray text-color=gray').classes('text-sm px-3')

        with ui.row().classes('gap-2 items-center'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat round dense').tooltip('Quay lại trang chủ')

    # ── Info bar ────────────────────────────────────────────────────────────────
    ui.html('<div id="safe-info" style="padding:8px 16px;font-size:13px;font-weight:600;color:#1B5E20;background:#E8F5E9;border-radius:0;">🛡️ Đang xác định vị trí của bạn...</div>').classes('w-full')

    # ── Bản đồ toàn màn hình ───────────────────────────────────────────────────
    ui.html('<div id="safe-map" style="height:calc(100vh - 112px);width:100%;z-index:0;"></div>').classes('w-full')

    # ── JS: khởi tạo map + markers khu vực an toàn ────────────────────────────
    ui.add_body_html('''
    <script>
    // Dữ liệu an toàn tĩnh: công an, bệnh viện, khu vực an toàn mẫu
    // (Trong sản phẩm thực tế: lấy từ API hoặc Overpass API OpenStreetMap)
    var SAFE_LOCATIONS = [
        {name: "Công an TP Vinh",       name_ja: "ヴィン市警察",       lat: 18.6745, lng: 105.6813, type: "police",   phone: "113"},
        {name: "Công an phường Lê Mao", name_ja: "レーマオ警察",       lat: 18.6692, lng: 105.6850, type: "police",   phone: "0238.382.1031"},
        {name: "Bệnh viện Hữu Nghị Đa Khoa Nghệ An", name_ja: "ゲアン友好病院", lat: 18.6780, lng: 105.6900, type: "hospital", phone: "0238.384.6609"},
        {name: "Bệnh viện 115 Nghệ An", name_ja: "115病院",            lat: 18.6710, lng: 105.6830, type: "hospital", phone: "0238.382.8115"},
        {name: "Bệnh viện Sản Nhi Nghệ An", name_ja: "産婦人科病院",   lat: 18.6760, lng: 105.6950, type: "hospital", phone: "0238.256.9999"},
    ];

    var SAFE_ZONES = [
        {name: "Khu vực Trung tâm Vinh",    lat: 18.6745, lng: 105.6870, radius: 800,  safety: "high"},
        {name: "Công viên Nguyễn Tất Thành", lat: 18.6741, lng: 105.6922, radius: 400,  safety: "high"},
        {name: "Khu vực Sân vận động",      lat: 18.6796, lng: 105.6813, radius: 500,  safety: "medium"},
        {name: "Khu vực Hưng Dũng",         lat: 18.6650, lng: 105.6980, radius: 600,  safety: "medium"},
    ];

    var TYPE_CONFIG = {
        police:   {color: "#1565C0", icon: "🚔", label: "Công an"},
        hospital: {color: "#C62828", icon: "🏥", label: "Bệnh viện"},
    };
    var ZONE_COLOR = {high: "#4CAF50", medium: "#FFC107", low: "#F44336"};

    function initSafeMap() {
        var mapDiv = document.getElementById('safe-map');
        if (!mapDiv || typeof L === 'undefined') {
            setTimeout(initSafeMap, 100);
            return;
        }
        if (mapDiv._leaflet_id) return;

        var safeMap = L.map('safe-map').setView([18.6745, 105.6870], 14);
        window['safe-map_instance'] = safeMap;

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(safeMap);

        // ── Vẽ vùng an toàn ──────────────────────────────────────────────────
        SAFE_ZONES.forEach(function(zone) {
            var color = ZONE_COLOR[zone.safety] || "#4CAF50";
            L.circle([zone.lat, zone.lng], {
                radius: zone.radius,
                color: color, fillColor: color,
                fillOpacity: 0.12, weight: 2, dashArray: '6 4'
            }).addTo(safeMap).bindTooltip(zone.name + ' — ' + (zone.safety === 'high' ? 'An toàn cao' : 'Khá an toàn'), {
                permanent: false, direction: 'top'
            });
        });

        // ── Marker công an / bệnh viện ────────────────────────────────────────
        SAFE_LOCATIONS.forEach(function(loc) {
            var cfg = TYPE_CONFIG[loc.type];
            var icon = L.divIcon({
                html: '<div style="font-size:22px;line-height:1;filter:drop-shadow(0 1px 3px rgba(0,0,0,.4))">' + cfg.icon + '</div>',
                iconSize: [28, 28], iconAnchor: [14, 14], className: ''
            });
            L.marker([loc.lat, loc.lng], {icon: icon})
                .addTo(safeMap)
                .bindPopup(
                    '<div style="font-family:sans-serif;min-width:180px">' +
                    '<b style="color:' + cfg.color + '">' + cfg.icon + ' ' + loc.name + '</b><br>' +
                    (loc.name_ja ? '<span style="color:#888;font-size:12px">' + loc.name_ja + '</span><br>' : '') +
                    '<a href="tel:' + loc.phone + '" style="color:' + cfg.color + ';font-weight:bold;font-size:14px">📞 ' + loc.phone + '</a>' +
                    '</div>'
                );
        });

        // ── Legend ────────────────────────────────────────────────────────────
        var legend = L.control({position: 'bottomleft'});
        legend.onAdd = function() {
            var div = L.DomUtil.create('div', 'safe-legend');
            div.innerHTML =
                '<b style="font-size:13px">Chú thích</b><br>' +
                '<i style="background:#4CAF50"></i> Khu vực an toàn cao<br>' +
                '<i style="background:#FFC107"></i> Khu vực khá an toàn<br>' +
                '<i style="background:#F44336"></i> Cần chú ý<br>' +
                '🚔 Công an &nbsp; 🏥 Bệnh viện';
            return div;
        };
        legend.addTo(safeMap);

        // ── Lấy GPS user ──────────────────────────────────────────────────────
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(pos) {
                var uLat = pos.coords.latitude;
                var uLng = pos.coords.longitude;
                window.userLat = uLat;
                window.userLng = uLng;

                var userIcon = L.divIcon({
                    html: '<div style="background:#4285F4;width:14px;height:14px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,.4)"></div>',
                    iconSize:[14,14], iconAnchor:[7,7], className:''
                });
                L.marker([uLat, uLng], {icon: userIcon, zIndexOffset: 1000})
                    .addTo(safeMap).bindPopup('📍 Vị trí của bạn').openPopup();

                safeMap.setView([uLat, uLng], 15);

                // Tìm nơi gần nhất theo loại
                function nearest(type) {
                    var locs = SAFE_LOCATIONS.filter(l => l.type === type);
                    if (!locs.length) return null;
                    return locs.reduce(function(best, loc) {
                        var d = Math.hypot(loc.lat - uLat, loc.lng - uLng);
                        return (!best || d < best.dist) ? {loc, dist: d} : best;
                    }, null);
                }

                var nearPolice   = nearest('police');
                var nearHospital = nearest('hospital');

                var infoHtml = '🛡️ Khu vực của bạn';
                if (nearPolice)   infoHtml += ' &nbsp;|&nbsp; 🚔 Công an gần nhất: <b>' + nearPolice.loc.name + '</b> (' + nearPolice.loc.phone + ')';
                if (nearHospital) infoHtml += ' &nbsp;|&nbsp; 🏥 Bệnh viện gần nhất: <b>' + nearHospital.loc.name + '</b> (' + nearHospital.loc.phone + ')';
                document.getElementById('safe-info').innerHTML = infoHtml;

            }, function() {
                document.getElementById('safe-info').innerHTML = '⚠️ Không lấy được vị trí GPS. Vui lòng cấp quyền truy cập vị trí.';
            });
        }
    }
    setTimeout(initSafeMap, 100);
    </script>
    ''')

    # ── SOS button ─────────────────────────────────────────────────────────────
    from components.sos_button import add_sos_button
    add_sos_button()
