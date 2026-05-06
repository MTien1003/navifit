import httpx
from nicegui import ui

@ui.page('/sos')
async def sos_page():
    ui.page_title('NaviFit — Liên hệ khẩn cấp')
    ICON_MAP = {"police":"🚔", "hospital":"🏥", "embassy":"🏛️", "other":"📞"}

    with ui.column().classes('max-w-lg mx-auto p-4 gap-4 w-full'):
        # Header
        with ui.row().classes('items-center gap-3 w-full'):
            ui.button('←', on_click=ui.navigate.back).classes('text-gray-500').props('flat round dense')
            ui.label('Liên hệ khẩn cấp / 緊急連絡').classes('text-xl font-bold text-red-600 flex-1')

        ui.label('Chọn kênh hỗ trợ phù hợp với tình huống của bạn').classes('text-gray-500 text-sm')

        # Danh sách kênh
        channels = []
        try:
            resp = await httpx.AsyncClient(timeout=10.0).get('http://127.0.0.1:8081/api/sos/channels')
            resp.raise_for_status()
            channels = resp.json()
        except httpx.HTTPStatusError as e:
            ui.notify(f'Lỗi server: {e.response.status_code}', type='negative')
        except httpx.RequestError:
            ui.notify('Không thể kết nối server. Kiểm tra kết nối mạng.', type='negative')
        except Exception as e:
            print("Error fetching SOS channels:", e)
            ui.notify('Lỗi khi tải danh sách SOS', type='negative')
        
        for ch in channels:
            icon = ICON_MAP.get(ch['type'], '📞')
            with ui.card().classes('w-full p-4 shadow-sm border'):
                with ui.row().classes('items-center gap-3 w-full flex-nowrap'):
                    ui.label(icon).classes('text-3xl')
                    with ui.column().classes('flex-1 gap-0'):
                        ui.label(ch['name']).classes('font-semibold text-base leading-tight')
                        if ch.get('name_ja'):
                            ui.label(ch['name_ja']).classes('text-gray-400 text-sm')
                        ui.label(ch['phone']).classes('text-blue-600 font-bold text-lg mt-1')
                    with ui.column().classes('gap-2 items-end'):
                        ui.link('📞 Gọi', target=f"tel:{ch['phone']}").classes('bg-green-500 text-white px-3 py-1 rounded-lg text-sm no-underline font-medium')
                        ui.link('💬 Nhắn', target=f"sms:{ch['phone']}").classes('bg-blue-500 text-white px-3 py-1 rounded-lg text-sm no-underline font-medium')
