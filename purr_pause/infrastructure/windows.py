"""Windows overlay integration; original style flags and error behavior."""
import sys


def make_click_through(hwnd: int) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(
            hwnd, -20, style | 0x00000020 | 0x00080000
        )
    except Exception as exc:
        print(f"cat_anim: click-through setup failed: {exc}", file=sys.stderr)
