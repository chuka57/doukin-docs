"""Optional diagram render; the normal guide build stays standard-library only."""
import argparse
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', default=shutil.which('chromium'))
    args = parser.parse_args()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium,
                                    args=['--no-sandbox', '--font-render-hinting=none'])
        page = browser.new_page(viewport={'width': 1200, 'height': 1000}, device_scale_factor=2)
        page.set_content((ROOT / 'content/proposal-auth-architecture.html').read_text(encoding='utf-8'))
        page.evaluate('document.fonts.ready')
        page.add_style_tag(content='.canvas,.group,.tile{border-radius:0!important}')
        for theme, suffix in [('light', ''), ('dark', '-dark')]:
            page.evaluate('(theme) => document.documentElement.dataset.theme = theme', theme)
            page.wait_for_timeout(200)
            page.evaluate('Promise.all([...document.images].map(img => img.decode()))')
            page.locator('.canvas').screenshot(path=str(ROOT / f'docs/assets/proposal-auth-architecture{suffix}.png'))
        browser.close()


if __name__ == '__main__':
    main()
