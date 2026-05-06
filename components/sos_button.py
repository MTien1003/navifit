import httpx
from nicegui import ui

def add_sos_button():
    dialog = ui.dialog()
    
    with dialog, ui.card().classes('w-full max-w-md p-4 bg-white rounded-2xl'):
        with ui.row().classes('items-center justify-between w-full mb-2'):
            ui.label('Liên hệ khẩn cấp / 緊急連絡').classes('text-xl font-bold text-red-600')
            ui.button(icon='close', on_click=dialog.close).props('flat round dense text-color=gray')
        
        ui.label('Chọn kênh hỗ trợ phù hợp với tình huống của bạn').classes('text-gray-500 text-sm mb-4')
        container = ui.column().classes('w-full gap-3')

    async def open_sos():
        container.clear()
        with container:
            ui.spinner(size='lg').classes('self-center')
        dialog.open()
        
        try:
            resp = await httpx.AsyncClient().get('http://127.0.0.1:8081/api/sos/channels')
            if resp.status_code == 200:
                channels = resp.json()
            else:
                channels = []
        except Exception as e:
            print("Error fetching SOS channels:", e)
            channels = []
            
        container.clear()
        ICON_MAP = {"police":"🚔", "hospital":"🏥", "embassy":"🏛️", "other":"📞"}
        
        with container:
            if not channels:
                ui.label('Không thể tải danh sách SOS').classes('text-red-500 text-center w-full')
            
            for ch in channels:
                icon = ICON_MAP.get(ch['type'], '📞')
                with ui.card().classes('w-full p-3 shadow-sm border'):
                    with ui.row().classes('items-center gap-3 w-full flex-nowrap'):
                        ui.label(icon).classes('text-3xl')
                        with ui.column().classes('flex-1 gap-0'):
                            ui.label(ch['name']).classes('font-semibold text-base leading-tight')
                            if ch.get('name_ja'):
                                ui.label(ch['name_ja']).classes('text-gray-400 text-sm')
                            ui.label(ch['phone']).classes('text-blue-600 font-bold text-lg mt-1')
                        with ui.column().classes('gap-2 items-end'):
                            ui.link('📞 Gọi', target=f"tel:{ch['phone']}").classes('bg-green-500 text-white px-3 py-1 rounded-lg text-sm no-underline font-medium hover:bg-green-600')
                            ui.link('💬 Nhắn', target=f"sms:{ch['phone']}").classes('bg-blue-500 text-white px-3 py-1 rounded-lg text-sm no-underline font-medium hover:bg-blue-600')
            
    # Ép z-index cho wrapper sticky để nổi trên Leaflet map
    ui.add_head_html('<style>.q-page-sticky { z-index: 9999 !important; }</style>')

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button('SOS', on_click=open_sos) \
            .classes('rounded-full w-16 h-16 text-white font-bold text-lg shadow-xl hover:scale-110 transition-transform flex items-center justify-center') \
            .style('background: #DC2626; border: none;')
