import httpx
import json
from nicegui import ui, app

@ui.page('/search')
async def search_page(q: str = '', lat: float = 21.006847, lng: float = 105.843058):
    ui.page_title('NaviFit — Tìm kiếm')

    # Đọc trạng thái filter, đảm bảo luôn là bool
    japanese_filter = bool(app.storage.user.get('japanese_only', False))

    CAT_LABELS = {
        'gym': '🏋️ Phòng gym',
        'park': '🌳 Công viên',
        'pool': '🏊 Hồ bơi',
        'badminton': '🏸 Cầu lông',
    }

    # Lấy dữ liệu ban đầu
    async def fetch_places(japanese_only: bool = False) -> list:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                japanese_str = 'true' if japanese_only else 'false'
                url = f'http://127.0.0.1:8081/api/places/nearby?lat={lat}&lng={lng}&radius=20000&japanese_only={japanese_str}'
                res = await client.get(url)
                res.raise_for_status()
                all_places = res.json()

                if q:
                    q_lower = q.lower()
                    matched = []
                    for p in all_places:
                        if p.get('is_separator'):
                            continue
                        if (q_lower in p.get('name','').lower()
                                or q_lower in (p.get('name_ja') or '').lower()
                                or q_lower in p.get('address','').lower()):
                            matched.append(p)

                    if matched:
                        # Xác định category đầu tiên trong kết quả
                        primary_cat = matched[0].get('category', '')
                        matched_ids = {p['id'] for p in matched}

                        # Lấy các địa điểm cùng category, chưa có trong kết quả
                        similar = [
                            p for p in all_places
                            if not p.get('is_separator')
                            and p.get('category') == primary_cat
                            and p['id'] not in matched_ids
                        ]

                        result = list(matched)
                        if similar:
                            cat_label = CAT_LABELS.get(primary_cat, 'cùng loại')
                            result.append({'is_separator': True, 'label': f'── Địa điểm {cat_label} khác ──'})
                            result.extend(similar)
                        return result
                    return matched  # không có kết quả

                return all_places  # không có query
        except httpx.HTTPStatusError as e:
            ui.notify(f'Lỗi server: {e.response.status_code}', type='negative')
        except httpx.RequestError:
            ui.notify('Không thể kết nối server. Kiểm tra kết nối mạng.', type='negative')
        except Exception as e:
            ui.notify(f'Lỗi: {str(e)}', type='negative')
        return []

    places = await fetch_places(japanese_filter)
    # Chỉ lấy place thực sự (không phải separator) để vẽ map
    real_places = [p for p in places if not p.get('is_separator')]
    places_json = json.dumps(real_places)

    # ── Header ────────────────────────────────────────────────────────────────
    with ui.header().classes('items-center bg-white text-black shadow-md px-4 py-3 justify-between'):
        with ui.row().classes('items-center'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat round dense')
            ui.label('Tìm kiếm').classes('text-xl font-bold ml-2')
        with ui.row().classes('items-center gap-2'):
            from components.aqi_button import add_aqi_button
            add_aqi_button('search-map')

    # ── Layout chính ──────────────────────────────────────────────────────────
    with ui.row().classes('w-full h-[calc(100vh-64px)] m-0 p-0 overflow-hidden flex-nowrap'):

        # ── Cột trái: Danh sách (33%) ─────────────────────────────────────────
        with ui.column().classes('w-1/3 h-full overflow-y-auto p-4 border-r bg-gray-50 flex-shrink-0 gap-0'):

            # Tiêu đề + toggle filter
            ui.label(f'Kết quả: "{q}"' if q else 'Địa điểm xung quanh').classes('text-lg font-bold mb-2')

            with ui.row().classes('items-center gap-2 mb-3'):
                ui.label('Bộ lọc:').classes('text-xs text-gray-500')
                filter_switch = ui.switch('日本語対応のみ', value=japanese_filter).classes('text-xs')

            # Container chứa danh sách kết quả (có thể clear & reload)
            results_container = ui.column().classes('w-full gap-2')

            def render_places(pl: list):
                """Render danh sách places vào results_container"""
                results_container.clear()
                real = [p for p in pl if not p.get('is_separator')]
                with results_container:
                    if not real:
                        with ui.column().classes('items-center p-8 text-gray-400 gap-2 w-full'):
                            ui.label('🔍').classes('text-4xl')
                            ui.label('Không tìm thấy địa điểm nào').classes('font-medium text-gray-500')
                            ui.label('Thử tìm kiếm với từ khóa khác hoặc mở rộng khu vực tìm kiếm').classes('text-sm text-center text-gray-400')
                        return

                    for place in pl:
                        # Separator label
                        if place.get('is_separator'):
                            ui.label(place.get('label', '──')).classes('text-gray-400 text-xs text-center py-1 w-full')
                            continue

                        # Badge tiếng Nhật
                        has_jp = place.get('has_japanese_support', False)
                        badge_text = '日本語対応' if has_jp else '日本語なし'
                        badge_cls = 'bg-blue-100 text-blue-700 border border-blue-200' if has_jp else 'bg-gray-100 text-gray-400'

                        p_id = place['id']
                        p_lat = place['lat']
                        p_lng = place['lng']

                        with ui.card().classes('w-full p-3 cursor-pointer hover:bg-blue-50 hover:shadow-md transition-all rounded-xl') as card:
                            card.on('mouseover', lambda pid=p_id: ui.run_javascript(f'highlightMarker({pid})'))
                            card.on('click', lambda pid=p_id, plat=p_lat, plng=p_lng: [
                                ui.run_javascript(f'highlightMarker({pid})'),
                            ])

                            with ui.row().classes('items-start justify-between gap-2 w-full'):
                                with ui.column().classes('flex-1 gap-0'):
                                    ui.label(place.get('name', '')).classes('font-semibold text-gray-800 leading-tight text-sm')
                                    if place.get('name_ja'):
                                        ui.label(place['name_ja']).classes('text-gray-400 text-xs')
                                    with ui.row().classes('gap-3 mt-1 items-center'):
                                        ui.label(f"📍 {round(place.get('distance', 0)/1000, 1)} km").classes('text-xs text-gray-500')
                                        ui.label(f"⭐ {place.get('rating','N/A')}").classes('text-xs text-yellow-600 font-bold')
                                with ui.column().classes('items-end gap-1 flex-shrink-0'):
                                    ui.badge(badge_text).classes(f'text-xs px-2 py-0.5 rounded-full {badge_cls}')
                                    # Nút xem chi tiết
                                    ui.link('Chi tiết →', target=f'/detail/{p_id}').classes('text-blue-500 text-xs font-medium no-underline hover:underline')

            render_places(places)

            # ── Handler filter switch ──────────────────────────────────────────
            async def on_filter_change(e):
                is_jp = bool(e.args)
                app.storage.user['japanese_only'] = is_jp

                new_places = await fetch_places(is_jp)
                render_places(new_places)

                # Cập nhật markers trên map (chỉ real places)
                new_real = [p for p in new_places if not p.get('is_separator')]
                await ui.run_javascript(f'updateMapMarkers({json.dumps(new_real)})')

            filter_switch.on('update:model-value', on_filter_change)

        # ── Cột phải: Bản đồ (67%) ────────────────────────────────────────────
        with ui.column().classes('w-2/3 h-full p-4 flex-grow relative bg-white'):
            ui.add_head_html('''
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            ''')
            ui.html('<div id="route-info" style="padding:8px 12px;font-size:13px;color:#1565C0;background:#E3F2FD;border-radius:8px;margin-bottom:6px;font-weight:600;">Đang tải bản đồ...</div>')
            ui.html('<div id="search-map" style="height:calc(100vh - 150px);width:100%;border-radius:12px;box-shadow:0 4px 6px -1px rgb(0 0 0 / 0.1);"></div>').classes('w-full')

            ui.add_body_html(f'''
            <script>
            function initSearchMap() {{
                var mapDiv = document.getElementById('search-map');
                if (!mapDiv) {{ setTimeout(initSearchMap, 100); return; }}

                var searchMap = L.map('search-map').setView([{lat}, {lng}], 14);
                window['search-map_instance'] = searchMap;

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap'
                }}).addTo(searchMap);

                window.userLat = {lat};
                window.userLng = {lng};
                window.currentDestLat = null;
                window.currentDestLng = null;

                // Marker vị trí user
                window.userMarker = L.circleMarker([window.userLat, window.userLng], {{
                    radius: 8, color: '#4285F4', fillColor: '#4285F4', fillOpacity: 1, zIndexOffset: 1000
                }}).addTo(searchMap).bindPopup('Vị trí của bạn');

                // Markers địa điểm
                window.markers = {{}};
                window.currentRouteLayer = null;
                window.places = {places_json};

                function addMarkers(places) {{
                    // Xóa markers cũ
                    for (var k in window.markers) {{
                        searchMap.removeLayer(window.markers[k]);
                    }}
                    window.markers = {{}};
                    window.places = places;
                    places.forEach(function(p) {{
                        var color = p.has_japanese_support ? '#1565C0' : '#607D8B';
                        var icon = L.divIcon({{
                            html: `<div style="background:${{color}};width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,.3)"></div>`,
                            iconSize:[12,12], iconAnchor:[6,6], className:''
                        }});
                        window.markers[p.id] = L.marker([p.lat, p.lng], {{icon: icon}})
                            .addTo(searchMap)
                            .bindPopup(`<div style="font-family:sans-serif;min-width:140px">
                                <b>${{p.name}}</b><br>
                                <span style="color:#666;font-size:12px">${{p.name_ja || ''}}</span><br>
                                <span>📍 ${{(p.distance/1000).toFixed(1)}} km · ⭐ ${{p.rating}}</span><br>
                                <a href="/detail/${{p.id}}" style="color:#1976D2;font-weight:bold;font-size:12px">Xem chi tiết →</a>
                            </div>`);
                    }});
                }}
                addMarkers(window.places);

                // Hàm cập nhật markers khi filter thay đổi
                window.updateMapMarkers = function(newPlaces) {{
                    addMarkers(newPlaces);
                    if (newPlaces.length > 0) {{
                        window.drawRoute(newPlaces[0].lat, newPlaces[0].lng);
                    }}
                }};

                // Vẽ route OSRM
                window.drawRoute = async function(destLat, destLng) {{
                    window.currentDestLat = destLat;
                    window.currentDestLng = destLng;
                    if (!destLat || !destLng) return;
                    try {{
                        const url = `https://router.project-osrm.org/route/v1/driving/${{window.userLng}},${{window.userLat}};${{destLng}},${{destLat}}?overview=full&geometries=geojson`;
                        const res = await fetch(url);
                        const data = await res.json();
                        if (data.routes && data.routes[0]) {{
                            const route = data.routes[0];
                            if (window.currentRouteLayer) searchMap.removeLayer(window.currentRouteLayer);
                            window.currentRouteLayer = L.geoJSON(route.geometry, {{
                                style: {{ color: '#1976D2', weight: 4, opacity: 0.85 }}
                            }}).addTo(searchMap);
                            searchMap.fitBounds(window.currentRouteLayer.getBounds(), {{ padding: [40, 40] }});
                            const km = (route.distance / 1000).toFixed(1);
                            const min = Math.round(route.duration / 60);
                            document.getElementById('route-info').innerHTML = `🚗 ${{km}} km &nbsp;·&nbsp; ⏱ ${{min}} phút lái xe`;
                        }}
                    }} catch(e) {{
                        document.getElementById('route-info').innerHTML = 'Lỗi tính đường đi.';
                    }}
                }};

                if (window.places.length > 0) {{
                    window.drawRoute(window.places[0].lat, window.places[0].lng);
                }} else {{
                    document.getElementById('route-info').innerHTML = 'Không có địa điểm để vẽ đường.';
                }}

                // Highlight marker khi hover/click card
                window.highlightMarker = function(placeId) {{
                    if (window.markers[placeId]) {{
                        window.markers[placeId].openPopup();
                        let p = window.places.find(x => x.id === placeId);
                        if (p) window.drawRoute(p.lat, p.lng);
                    }}
                }};

                // Vị trí người dùng cố định tại B1 HUST (không dùng GPS)
                // window.userLat và window.userLng đã được set từ Python f-string ở trên
            }}
            setTimeout(initSearchMap, 100);
            </script>
            ''')

    from components.sos_button import add_sos_button
    add_sos_button()
