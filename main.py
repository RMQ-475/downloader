import flet as ft
import yt_dlp
import os
import random
import string

def main(page: ft.Page):
    page.title = "Sleek Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE)
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    current_video_url = [None]

    # 1. Top Input Section
    url_input = ft.TextField(
        label="Paste video link here...",
        border_radius=12,
        border_color=ft.Colors.DEEP_PURPLE_400,
        focused_border_color=ft.Colors.DEEP_PURPLE_ACCENT,
        suffix_icon=ft.Icons.LINK,
        expand=True,
    )
    
    fetch_btn = ft.IconButton(
        icon=ft.Icons.ARROW_FORWARD_ROUNDED,
        icon_color=ft.Colors.WHITE,
        bgcolor=ft.Colors.DEEP_PURPLE,
        icon_size=24,
        on_click=lambda e: process_link(),
    )

    # 2. Preview Layout
    video_title = ft.Text(
        weight=ft.FontWeight.BOLD, 
        size=16, 
        text_align=ft.TextAlign.CENTER,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS
    )
    download_btn = ft.ElevatedButton(
        content=ft.Text("Download Video"),
        icon=ft.Icons.DOWNLOAD_ROUNDED,
        bgcolor=ft.Colors.DEEP_PURPLE,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: trigger_download(),
    )

    preview_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.VIDEO_LIBRARY, size=50, color=ft.Colors.DEEP_PURPLE_200),
                    ft.Divider(height=10, color=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                    video_title,
                    ft.Container(content=download_btn, margin=ft.Margin.only(top=10)),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=20,
        ),
        visible=False,
        width=400,
    )

    # 3. Status Windows
    loading_indicator = ft.ProgressRing(visible=False, color=ft.Colors.DEEP_PURPLE_ACCENT)
    
    error_banner = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="redaccent400"),
                ft.Text("Could not find or load video. Check the link, bor.", color="white", weight=ft.FontWeight.W_500)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor="#2a0808",
        border=ft.Border.all(1, "red800"),
        border_radius=10,
        padding=12,
        visible=False,
        width=400,
    )

    def process_link():
        if not url_input.value:
            return
        
        error_banner.visible = False
        preview_card.visible = False
        loading_indicator.visible = True
        page.update()

        ydl_opts = {'format': 'best', 'skip_download': True}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url_input.value, download=False)
                title = info.get('title', 'Untitled Video')
                
                current_video_url[0] = url_input.value
                video_title.value = title
                
                download_btn.content = ft.Text("Download Video")
                download_btn.disabled = False
                
                loading_indicator.visible = False
                preview_card.visible = True
        except Exception:
            loading_indicator.visible = False
            error_banner.visible = True
            
        page.update()

    def trigger_download():
        download_btn.content = ft.Text("Downloading...")
        download_btn.disabled = True
        page.update()
        
        rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        
        ydl_opts = {
            # Moved target path directly to standard /sdcard/Movies/ folder to force Instant Gallery Scan
            'outtmpl': f'/sdcard/Movies/%(title).100s_{rand_suffix}.%(ext)s',
            'format': 'best',
            'restrictfilenames': True,
            'windowsfilenames': True,
            'nooverwrites': False, 
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(current_video_url[0], download=True)
                filename = ydl.prepare_filename(info)
            
            try:
                os.system(f'termux-media-scan "{filename}" > /dev/null 2>&1 &')
            except:
                pass
                
            download_btn.content = ft.Text("Saved to Movies! 🚀")
        except Exception as err:
            download_btn.content = ft.Text("Download Failed")
            print(f"Error: {err}")
            
        page.update()

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Private Grabber", size=28, weight=ft.FontWeight.W_800, color=ft.Colors.DEEP_PURPLE_200),
                    ft.Row([url_input, fetch_btn], alignment=ft.MainAxisAlignment.CENTER),
                    loading_indicator,
                    error_banner,
                    preview_card,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            width=450,
        )
    )

if __name__ == "__main__":
    ft.app(target=main, port=8888, view=ft.AppView.WEB_BROWSER)

