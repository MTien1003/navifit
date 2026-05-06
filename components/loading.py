from nicegui import ui

def show_loading(container, message: str = "Đang tải..."):
    """Hiển thị spinner + message trong container."""
    with container:
        with ui.row().classes('items-center gap-2 text-gray-400 p-4'):
            ui.spinner(size='sm')
            ui.label(message).classes('text-sm')
