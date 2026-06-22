#!/usr/bin/env python3
import json
import os
import sys

CONFIG_PATH = '/opt/dashboard/config/gifs_config.json'

def load_config():
    """Загружает конфиг гифок"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found. Creating default...")
        default_config = {"gifs": []}
        save_config(default_config)
        return default_config
    except json.JSONDecodeError as e:
        print(f"Error reading config: {e}")
        return {"gifs": []}

def save_config(config):
    """Сохраняет конфиг гифок"""
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("Config saved successfully!")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def list_gifs():
    """Показывает список всех гифок"""
    config = load_config()
    if not config['gifs']:
        print("No GIFs configured.")
        return
    
    print("\n=== Configured GIFs ===")
    for i, gif in enumerate(config['gifs']):
        status = "🟢 ENABLED" if gif['enabled'] else "🔴 DISABLED"
        layer = "🔼 FRONT" if gif.get('zIndex', 5) >= 2000 else "🔽 BACK"
        print(f"{i+1}. {gif['id']} - {status} - {layer}")
        print(f"   URL: {gif['url']}")
        
        # Позиционирование
        pos_info = []
        if gif['position'].get('center_both'):
            pos_info.append("center both")
        elif gif['position'].get('center_x') and gif['position'].get('center_y'):
            pos_info.append("center both")
        else:
            if gif['position'].get('center_x'):
                pos_info.append("center X")
            if gif['position'].get('center_y'):
                pos_info.append("center Y")
            if gif['position'].get('top'):
                pos_info.append(f"top: {gif['position']['top']}")
            if gif['position'].get('left'):
                pos_info.append(f"left: {gif['position']['left']}")
            if gif['position'].get('right'):
                pos_info.append(f"right: {gif['position']['right']}")
            if gif['position'].get('bottom'):
                pos_info.append(f"bottom: {gif['position']['bottom']}")
        
        if gif['position'].get('transform'):
            pos_info.append(f"transform: {gif['position']['transform']}")
            
        print(f"   Position: {', '.join(pos_info)}")
        print(f"   Size: {gif['size']['width']} x {gif['size']['height']}")
        print(f"   Opacity: {gif['opacity']}")
        print(f"   Z-Index: {gif.get('zIndex', 5)}")
        if gif.get('blend_mode'):
            print(f"   Blend Mode: {gif['blend_mode']}")
        if gif.get('filter'):
            print(f"   Filter: {gif['filter']}")
        print()

def add_gif():
    """Добавляет новую гифку"""
    config = load_config()
    
    print("\n=== Add New GIF ===")
    gif_id = input("GIF ID (unique name): ").strip()
    
    # Проверяем уникальность ID
    if any(gif['id'] == gif_id for gif in config['gifs']):
        print(f"Error: GIF with ID '{gif_id}' already exists!")
        return
    
    filename = input("GIF filename (from /opt/dashboard/static/gifs/): ").strip()
    if not filename.endswith('.gif'):
        filename += '.gif'
    
    # Позиционирование с опциями центрирования
    print("\n=== Positioning ===")
    print("Choose positioning method:")
    print("1. Manual positioning (top/left/right/bottom)")
    print("2. Center horizontally")
    print("3. Center vertically") 
    print("4. Center both (perfect center)")
    
    pos_method = input("Choose method (1-4, default 4): ").strip() or "4"
    
    position = {}
    
    if pos_method == "1":
        print("\nManual positioning:")
        position['top'] = input("Top position (e.g., '50px', '10%'): ").strip() or "50px"
        position['left'] = input("Left position: ").strip() or "50px"
        position['right'] = input("Right position (or leave empty): ").strip() or None
        position['bottom'] = input("Bottom position (or leave empty): ").strip() or None
        position['transform'] = input("Transform (e.g., 'rotate(45deg)'): ").strip() or None
    elif pos_method == "2":
        position['center_x'] = True
        position['top'] = input("Top position (e.g., '50px', '10%'): ").strip() or "50px"
        position['transform'] = input("Additional transform (e.g., 'translateY(-50%)'): ").strip() or None
    elif pos_method == "3":
        position['center_y'] = True
        position['left'] = input("Left position (e.g., '50px', '10%'): ").strip() or "50px"
        position['transform'] = input("Additional transform (e.g., 'translateX(-50%)'): ").strip() or None
    elif pos_method == "4":
        position['center_both'] = True
        position['transform'] = input("Additional transform (e.g., 'scale(1.5)'): ").strip() or "scale(1.2)"
    
    # Размер
    print("\n=== Size ===")
    width = input("Width (e.g., '200px', '50%'): ").strip() or "200px"
    height = input("Height: ").strip() or "150px"
    
    # Слой и видимость
    print("\n=== Layer & Appearance ===")
    print("Layer options:")
    print("1. Background (z-index: 5-100)")
    print("2. Middle (z-index: 101-1999)") 
    print("3. Foreground (z-index: 2000+)")
    
    layer_choice = input("Choose layer (1-3, default 3): ").strip() or "3"
    
    if layer_choice == "1":
        zindex = input("Z-Index (5-100, default 50): ").strip()
        zindex = int(zindex) if zindex else 50
    elif layer_choice == "2":
        zindex = input("Z-Index (101-1999, default 500): ").strip()
        zindex = int(zindex) if zindex else 500
    else:  # layer_choice == "3"
        zindex = input("Z-Index (2000+, default 2000): ").strip()
        zindex = int(zindex) if zindex else 2000
    
    # По умолчанию opacity 1.0
    opacity_input = input("Opacity (0.0-1.0, default 1.0): ").strip()
    opacity = float(opacity_input) if opacity_input else 1.0
    
    # Дополнительные эффекты
    print("\n=== Advanced Effects ===")
    blend_modes = ["normal", "multiply", "screen", "overlay", "darken", "lighten", "color-dodge", "color-burn", "hard-light", "soft-light", "difference", "exclusion", "hue", "saturation", "color", "luminosity"]
    print("Available blend modes: " + ", ".join(blend_modes))
    blend_mode = input("Blend mode (leave empty for none): ").strip()
    blend_mode = blend_mode if blend_mode in blend_modes else None
    
    filter_effect = input("CSS filter (e.g., 'brightness(1.2) contrast(1.1)'): ").strip() or None
    
    enabled = input("Enable immediately? (Y/n): ").strip().lower()
    enabled = enabled != 'n' if enabled else True
    
    # Создаем объект гифки
    new_gif = {
        "id": gif_id,
        "url": f"/static/gifs/{filename}",
        "position": {k: v for k, v in position.items() if v is not None},
        "size": {
            "width": width,
            "height": height
        },
        "opacity": opacity,
        "zIndex": zindex,
        "enabled": enabled
    }
    
    if blend_mode:
        new_gif["blend_mode"] = blend_mode
    if filter_effect:
        new_gif["filter"] = filter_effect
    
    config['gifs'].append(new_gif)
    
    if save_config(config):
        print(f"✅ GIF '{gif_id}' added successfully!")
        print("Restart the dashboard to see changes.")

def remove_gif():
    """Удаляет гифку"""
    config = load_config()
    list_gifs()
    
    if not config['gifs']:
        return
    
    try:
        choice = int(input("\nEnter GIF number to remove: ")) - 1
        if 0 <= choice < len(config['gifs']):
            gif_id = config['gifs'][choice]['id']
            del config['gifs'][choice]
            if save_config(config):
                print(f"✅ GIF '{gif_id}' removed successfully!")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Please enter a valid number!")

def toggle_gif():
    """Включает/выключает гифку"""
    config = load_config()
    list_gifs()
    
    if not config['gifs']:
        return
    
    try:
        choice = int(input("\nEnter GIF number to toggle: ")) - 1
        if 0 <= choice < len(config['gifs']):
            gif = config['gifs'][choice]
            gif['enabled'] = not gif['enabled']
            status = "enabled" if gif['enabled'] else "disabled"
            if save_config(config):
                print(f"✅ GIF '{gif['id']}' {status}!")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Please enter a valid number!")

def change_layer():
    """Изменяет слой гифки"""
    config = load_config()
    list_gifs()
    
    if not config['gifs']:
        return
    
    try:
        choice = int(input("\nEnter GIF number to change layer: ")) - 1
        if 0 <= choice < len(config['gifs']):
            gif = config['gifs'][choice]
            print(f"\nCurrent z-index: {gif.get('zIndex', 5)}")
            print("\nLayer options:")
            print("1. Background (z-index: 5-100)")
            print("2. Middle (z-index: 101-1999)") 
            print("3. Foreground (z-index: 2000+)")
            print("4. Custom z-index")
            
            layer_choice = input("Choose option (1-4): ").strip()
            
            if layer_choice == "1":
                gif['zIndex'] = 50
            elif layer_choice == "2":
                gif['zIndex'] = 500
            elif layer_choice == "3":
                gif['zIndex'] = 2000
            elif layer_choice == "4":
                custom_z = input("Enter custom z-index: ").strip()
                if custom_z.isdigit():
                    gif['zIndex'] = int(custom_z)
                else:
                    print("Invalid z-index!")
                    return
            else:
                print("Invalid choice!")
                return
                
            if save_config(config):
                print(f"✅ GIF '{gif['id']}' layer updated to z-index {gif['zIndex']}!")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Please enter a valid number!")

def change_opacity():
    """Изменяет прозрачность гифки"""
    config = load_config()
    list_gifs()
    
    if not config['gifs']:
        return
    
    try:
        choice = int(input("\nEnter GIF number to change opacity: ")) - 1
        if 0 <= choice < len(config['gifs']):
            gif = config['gifs'][choice]
            print(f"\nCurrent opacity: {gif['opacity']}")
            new_opacity = input("New opacity (0.0-1.0): ").strip()
            if new_opacity:
                try:
                    opacity_val = float(new_opacity)
                    if 0.0 <= opacity_val <= 1.0:
                        gif['opacity'] = opacity_val
                        if save_config(config):
                            print(f"✅ GIF '{gif['id']}' opacity updated to {opacity_val}!")
                    else:
                        print("Opacity must be between 0.0 and 1.0!")
                except ValueError:
                    print("Invalid opacity value!")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Please enter a valid number!")

def edit_gif():
    """Редактирует существующую гифку"""
    config = load_config()
    list_gifs()
    
    if not config['gifs']:
        return
    
    try:
        choice = int(input("\nEnter GIF number to edit: ")) - 1
        if 0 <= choice < len(config['gifs']):
            gif = config['gifs'][choice]
            print(f"\nEditing GIF: {gif['id']}")
            print("Leave fields empty to keep current values.")
            
            # Позиционирование
            print("\n=== Positioning ===")
            print("Current position:", gif['position'])
            
            # Очищаем старые позиции центрирования
            for key in ['center_x', 'center_y', 'center_both']:
                if key in gif['position']:
                    del gif['position'][key]
            
            print("Choose positioning method:")
            print("1. Manual positioning (top/left/right/bottom)")
            print("2. Center horizontally")
            print("3. Center vertically") 
            print("4. Center both (perfect center)")
            
            pos_method = input(f"Choose method [current: {list(gif['position'].keys())}]: ").strip()
            
            if pos_method == "1":
                for pos in ['top', 'left', 'right', 'bottom']:
                    current = gif['position'].get(pos)
                    new_val = input(f"{pos.capitalize()} [{current}]: ").strip()
                    if new_val:
                        gif['position'][pos] = new_val
                    elif new_val == "" and pos in gif['position']:
                        del gif['position'][pos]
                
                transform = input(f"Transform [{gif['position'].get('transform', '')}]: ").strip()
                if transform:
                    gif['position']['transform'] = transform
                elif transform == "" and 'transform' in gif['position']:
                    del gif['position']['transform']
                    
            elif pos_method == "2":
                gif['position'] = {'center_x': True}
                top = input("Top position (or leave empty): ").strip()
                if top:
                    gif['position']['top'] = top
                transform = input("Additional transform: ").strip()
                if transform:
                    gif['position']['transform'] = transform
                    
            elif pos_method == "3":
                gif['position'] = {'center_y': True}
                left = input("Left position (or leave empty): ").strip()
                if left:
                    gif['position']['left'] = left
                transform = input("Additional transform: ").strip()
                if transform:
                    gif['position']['transform'] = transform
                    
            elif pos_method == "4":
                gif['position'] = {'center_both': True}
                transform = input("Additional transform: ").strip()
                if transform:
                    gif['position']['transform'] = transform
            
            # Размер
            print("\n=== Size ===")
            width = input(f"Width [{gif['size']['width']}]: ").strip()
            if width:
                gif['size']['width'] = width
            
            height = input(f"Height [{gif['size']['height']}]: ").strip()
            if height:
                gif['size']['height'] = height
            
            # Другие параметры
            print("\n=== Other Settings ===")
            opacity = input(f"Opacity [{gif['opacity']}]: ").strip()
            if opacity:
                gif['opacity'] = float(opacity)
            
            zindex = input(f"Z-Index [{gif.get('zIndex', 5)}]: ").strip()
            if zindex:
                gif['zIndex'] = int(zindex)
            
            # Эффекты
            blend_mode = input(f"Blend mode [{gif.get('blend_mode', 'none')}]: ").strip()
            if blend_mode:
                gif['blend_mode'] = blend_mode
            elif blend_mode == "" and 'blend_mode' in gif:
                del gif['blend_mode']
                
            filter_effect = input(f"Filter [{gif.get('filter', 'none')}]: ").strip()
            if filter_effect:
                gif['filter'] = filter_effect
            elif filter_effect == "" and 'filter' in gif:
                del gif['filter']
            
            enabled = input(f"Enabled [{gif['enabled']}] (Y/n): ").strip().lower()
            if enabled:
                gif['enabled'] = enabled != 'n'
            
            if save_config(config):
                print(f"✅ GIF '{gif['id']}' updated successfully!")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Please enter a valid number!")

def show_help():
    """Показывает справку"""
    print("""
🎭 GIF Manager for Cyber Dashboard

Commands:
  list     - Show all configured GIFs
  add      - Add new GIF
  remove   - Remove GIF
  toggle   - Enable/disable GIF
  layer    - Change GIF layer (z-index)
  opacity  - Change GIF opacity
  edit     - Edit GIF settings
  help     - Show this help

Layer Guide:
  Background: z-index 5-100 (behind content)
  Middle:     z-index 101-1999 (between elements) 
  Foreground: z-index 2000+ (above everything)

Defaults:
  - Opacity: 1.0 (fully visible)
  - Positioning: Center both
  - Layer: Foreground (z-index: 2000)

Examples:
  python3 manage_gifs.py list
  python3 manage_gifs.py add
  python3 manage_gifs.py remove
  python3 manage_gifs.py toggle
  python3 manage_gifs.py layer
  python3 manage_gifs.py opacity
  python3 manage_gifs.py edit
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_gifs()
    elif command == 'add':
        add_gif()
    elif command == 'remove':
        remove_gif()
    elif command == 'toggle':
        toggle_gif()
    elif command == 'layer':
        change_layer()
    elif command == 'opacity':
        change_opacity()
    elif command == 'edit':
        edit_gif()
    elif command == 'help':
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == '__main__':
    main()
