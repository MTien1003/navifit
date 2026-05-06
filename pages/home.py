import httpx
from nicegui import ui

@ui.page('/')
async def home_page():
    ui.page_title('NaviFit — Trang chủ')
    # 1. Header cố định
    with ui.header().classes('items-center justify-between bg-white text-black shadow-md px-6 py-3'):
        ui.label('NaviFit').classes('text-3xl font-extrabold text-blue-600 cursor-pointer').on('click', lambda: ui.navigate.to('/'))

        async def handle_search(e):
            q = search_input.value
            if not q:
                return
            lat = await ui.run_javascript('window.currentLat || null')
            lng = await ui.run_javascript('window.currentLng || null')
            if lat and lng:
                ui.navigate.to(f'/search?q={q}&lat={lat}&lng={lng}')
            else:
                ui.navigate.to(f'/search?q={q}')

        import asyncio
        with ui.column().classes('relative w-1/3 gap-0'):
            search_state = {'task': None}

            from services import places_service
            from database import async_session

            async def perform_search(q):
                if not q:
                    suggestions_box.classes(add='hidden')
                    return
                lat, lng = 21.006847, 105.843058  # Default HUST B1
                try:
                    lat_js = await ui.run_javascript('window.currentLat || null', timeout=0.5)
                    lng_js = await ui.run_javascript('window.currentLng || null', timeout=0.5)
                    if lat_js and lng_js:
                        lat, lng = float(lat_js), float(lng_js)
                except Exception:
                    pass

                try:
                    async with async_session() as db:
                        places = await places_service.search_places(db, q, lat, lng)

                        suggestions_list.clear()
                        if places:
                            suggestions_box.classes(remove='hidden')
                            with suggestions_list:
                                for place in places:
                                    with ui.row().classes('w-full items-center p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0').on('click', lambda p_name=place.name: ui.navigate.to(f'/search?q={p_name}&lat=21.006847&lng=105.843058')):
                                        ui.icon('place', color='gray').classes('mr-2 text-xl')
                                        with ui.column().classes('gap-0'):
                                            ui.label(place.name).classes('font-bold text-sm text-black')
                                            ui.label(f"{round(place.distance/1000, 1)} km").classes('text-xs text-gray-500')
                        else:
                            suggestions_box.classes(add='hidden')
                except Exception as e:
                    print("Error autocomplete:", e)
                    suggestions_box.classes(add='hidden')

            async def on_input(e):
                if search_state['task']:
                    search_state['task'].cancel()
                q = e.value
                async def debounced():
                    try:
                        await asyncio.sleep(0.3)
                        await perform_search(q)
                    except asyncio.CancelledError:
                        pass
                search_state['task'] = asyncio.create_task(debounced())

            search_input = ui.input(placeholder='Tìm địa điểm tập luyện...', on_change=on_input).classes('w-full').props('rounded outlined dense clearable')
            search_input.on('keydown.enter', handle_search)

            with ui.card().classes('absolute top-full left-0 w-full z-[9999] p-0 mt-1 shadow-lg bg-white hidden') as suggestions_box:
                suggestions_list = ui.column().classes('w-full gap-0')

        with ui.row().classes('gap-3'):
            from components.aqi_button import add_aqi_button
            add_aqi_button('map')
            ui.button('安全 (An toàn)', on_click=lambda: ui.navigate.to('/safe-area')).props('outline rounded color=green text-color=green')

    # Nhúng Leaflet CSS & JS
    ui.add_head_html('''
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    ''')

    # 2. Bản đồ bằng thẻ div
    ui.html('<div id="map" style="height:80vh;width:100%;z-index:0;border-radius:12px;box-shadow:0 4px 6px -1px rgb(0 0 0 / 0.1);"></div>').classes('w-full px-4 mt-4')

    # 3. Khởi tạo map bằng script
    ui.add_body_html('''
    <script>
    var map = null;

    function initLeaflet() {
        var mapDiv = document.getElementById('map');
        if (!mapDiv) {
            setTimeout(initLeaflet, 100);
            return;
        }

        // Khởi tạo bản đồ với tọa độ trung tâm Hà Nội
        map = L.map('map').setView([21.006847, 105.843058], 15);
        window.map_instance = map;

        // Tile layer OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Icon theo category (dùng string concat, không dùng template literal)
        var CATEGORY_ICON = {
            'gym':       { emoji: '🏋️', bg: '#E3F2FD', border: '#1976D2' },
            'park':      { emoji: '🌳', bg: '#E8F5E9', border: '#388E3C' },
            'pool':      { emoji: '🏊', bg: '#E0F7FA', border: '#0097A7' },
            'badminton': { emoji: '🏸', bg: '#FFF3E0', border: '#F57C00' }
        };

        function makePlaceIcon(category) {
            var cfg = CATEGORY_ICON[category] || { emoji: '📍', bg: '#F5F5F5', border: '#9E9E9E' };
            var html = '<div style="width:36px;height:36px;background:' + cfg.bg +
                       ';border:2.5px solid ' + cfg.border +
                       ';border-radius:50% 50% 50% 0;transform:rotate(-45deg);' +
                       'display:flex;align-items:center;justify-content:center;' +
                       'box-shadow:0 2px 6px rgba(0,0,0,0.25);">' +
                       '<span style="transform:rotate(45deg);font-size:18px;line-height:1;">' +
                       cfg.emoji + '</span></div>';
            return L.divIcon({
                className: '',
                html: html,
                iconSize: [36, 36],
                iconAnchor: [18, 36],
                popupAnchor: [0, -36]
            });
        }

        // Hàm load địa điểm gần đây từ API
        async function fetchNearbyPlaces(lat, lng) {
            try {
                var res = await fetch('/api/places/nearby?lat=' + lat + '&lng=' + lng + '&radius=20000');
                var places = await res.json();
                window.map_places = places;
                places.forEach(function(place) {
                    var icon = makePlaceIcon(place.category);
                    var japanBadge = place.has_japanese_support
                        ? '<span style="background:#E3F2FD;color:#1565C0;border:1px solid #90CAF9;border-radius:4px;padding:2px 6px;font-size:11px;font-weight:bold;">🇯🇵 日本語対応</span>'
                        : '';
                    var popup =
                        '<div style="font-family:sans-serif;min-width:190px;">' +
                        '<h3 style="margin:0 0 3px 0;color:#1a73e8;font-size:15px;font-weight:700;">' + place.name + '</h3>' +
                        (place.name_ja ? '<p style="margin:0 0 6px 0;color:#666;font-size:12px;">' + place.name_ja + '</p>' : '') +
                        '<div style="display:flex;gap:8px;margin-bottom:6px;font-size:13px;">' +
                        '<span>📍 <strong>' + (place.distance / 1000).toFixed(1) + ' km</strong></span>' +
                        '<span>⭐ <strong>' + place.rating + '</strong></span>' +
                        '</div>' +
                        (japanBadge ? '<div style="margin-bottom:8px;">' + japanBadge + '</div>' : '') +
                        '<a href="/detail/' + place.id + '?ulat=' + lat + '&ulng=' + lng + '" ' +
                        'style="display:inline-block;background:#1a73e8;color:#fff;text-decoration:none;' +
                        'font-weight:600;font-size:12px;padding:5px 12px;border-radius:6px;">Xem chi tiết →</a>' +
                        '</div>';
                    L.marker([place.lat, place.lng], { icon: icon })
                        .addTo(map)
                        .bindPopup(popup);
                });
            } catch(e) {
                console.error('Loi load dia diem:', e);
            }
        }

        // Dùng tọa độ Hà Nội làm mặc định (không yêu cầu GPS)
        var defaultLat = 21.006847;
        var defaultLng = 105.843058;
        window.currentLat = defaultLat;
        window.currentLng = defaultLng;

        // Marker chấm xanh vị trí hiện tại
        var userIcon = L.divIcon({
            className: '',
            html: '<div style="width:18px;height:18px;background:#4285F4;border:3px solid white;border-radius:50%;box-shadow:0 2px 8px rgba(66,133,244,0.6);"></div>',
            iconSize: [18, 18],
            iconAnchor: [9, 9]
        });
        L.marker([defaultLat, defaultLng], {icon: userIcon})
            .addTo(map)
            .bindPopup('<b>Vị trí của bạn</b><br><small>Nhà B1 - Đại học Bách khoa Hà Nội</small>')
            .openPopup();

        fetchNearbyPlaces(defaultLat, defaultLng);
    }

    setTimeout(initLeaflet, 100);
    </script>
    ''')

    from components.sos_button import add_sos_button
    add_sos_button()
