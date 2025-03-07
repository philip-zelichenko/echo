import os
import sys
import dmgbuild
import subprocess
from pathlib import Path

def create_dmg():
    print("\n📦 Creating DMG installer...")
    
    # Build the app first
    subprocess.run(["poetry", "run", "python", "scripts/build_app.py"], check=True)
    
    app_path = Path('dist/Echo.app')
    if not app_path.exists():
        print("❌ Error: App bundle not found")
        sys.exit(1)
        
    # Clean any existing DMG
    dmg_path = Path('dist/Echo.dmg')
    if dmg_path.exists():
        dmg_path.unlink()
    
    # DMG settings
    settings = {
        'volume_name': 'Echo',
        'format': 'UDBZ',
        'size': '250M',
        'files': [str(app_path.resolve())],
        'symlinks': {'Applications': '/Applications'},
        'icon_size': 128,
        'window_rect': ((100, 100), (500, 400)),
        'icon_locations': {
            'Echo.app': (125, 175),
            'Applications': (375, 175)
        },
        'background': None
    }
    
    try:
        # Create a temporary settings file
        settings_file = Path('dmg_settings.py')
        with open(settings_file, 'w') as f:
            for key, value in settings.items():
                f.write(f"{key} = {repr(value)}\n")
        
        # Create DMG using the settings file
        dmgbuild.build_dmg(str(dmg_path), 'Echo', settings_file=str(settings_file))
        
        # Clean up settings file
        settings_file.unlink()
        
        print("\n✅ DMG created successfully!")
        print(f"📦 Output: {dmg_path}")
    except Exception as e:
        print(f"\n❌ Error creating DMG: {e}")
        if settings_file.exists():
            settings_file.unlink()
        sys.exit(1)

if __name__ == '__main__':
    create_dmg()