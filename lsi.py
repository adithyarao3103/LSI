import curses
import os
from pathlib import Path
import subprocess
import platform

filetype_icons = {
    'python': '\ue73c',  # Python file
    'text': '\uf15c',     # Text file
    'java': '\ue738',     # Java file
    'html': '\ue736',     # HTML file
    'css': '\ue749',      # CSS file
    'javascript': '\uf2ee',  # JavaScript file
    'markdown': '\uf48a',  # Markdown file
    'pdf': '\ueaeb',      # PDF file
    'image': '\uf03e',    # Image file (generic)
    'video': '\uf52c',    # Video file
    'audio': '\uf1c7',
    'zip': '\uf0ffa',      # ZIP file
    'git': '\ue702',      # Git repository
    'json': '\ueb0f',     # JSON file
    'xml': '\ue619',      # XML file
    'csv': '\ueefc',      # CSV file
    'folder': '\uea83',   # Folder
    'generic_file': '\uea7b',  # Generic file
}

def get_file_icon(entry_path):
    if entry_path.is_dir():
        return filetype_icons['folder']
    
    # Get the file extension
    extension = entry_path.suffix.lower().lstrip('.')
    
    # Map common extensions to filetype icons
    extension_map = {
        'py': 'python',
        'txt': 'text',
        'java': 'java',
        'html': 'html',
        'css': 'css',
        'js': 'javascript',
        'md': 'markdown',
        'pdf': 'pdf',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image',
        'mp4': 'video',
        'zip': 'zip',
        'git': 'git',
        'json': 'json',
        'xml': 'xml',
        'csv': 'csv',
        'svg': 'image',
        'webp': 'image',
        'mkv': 'video',
        'avi': 'video',
        'mp3': 'audio'
    }
    
    filetype = extension_map.get(extension, 'generic_file')
    return filetype_icons[filetype]

def rgb_to_curses(r, g, b):
    # Convert RGB (0-255) to curses color range (0-1000)
    return (r * 1000 // 255, g * 1000 // 255, b * 1000 // 255)

def hex_to_curses(hex_color):
    """
    Convert hex color code to curses RGB values (0-1000 range)
    Example: '#FF5733' -> (1000, 341, 200)
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB (0-255)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Convert to curses range (0-1000)
    r_curses = int((r / 255) * 1000)
    g_curses = int((g / 255) * 1000)
    b_curses = int((b / 255) * 1000)
    
    return (r_curses, g_curses, b_curses)


def open_file(filepath):
    if platform.system() == 'Windows':
        os.startfile(filepath)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.run(['open', filepath])
    else:  # Linux
        subprocess.run(['xdg-open', filepath])

def interactive_ls(stdscr):
    if not curses.can_change_color():
        return "Your terminal doesn't support custom colors"
    
    curses.start_color()
    
    # Define custom colors
    curses.init_color(10, *hex_to_curses('#2234a8'))  # Light yellow
    curses.init_color(11, *rgb_to_curses(255, 255, 255))    # Warm brown
    
    curses.init_pair(1, 10, curses.COLOR_BLACK)  # Directories
    curses.init_pair(2, 11, curses.COLOR_BLACK)  # Files
    
    curses.curs_set(0)
    current_pos = 0
    current_path = Path('.')
    history = []  # Stack to store directory history
    
    while True:
        entries = sorted([x for x in os.listdir(current_path) if not x.startswith('.')])
        max_y, max_x = stdscr.getmaxyx()
        
        stdscr.clear()
        
        # Show navigation help
        help_text = "↑↓:Navigate | Enter:Open | b:Back | h:History Back | e:Change Dir | q:Quit"
        if len(help_text) <= max_x:
            stdscr.addstr(0, 0, help_text, curses.A_BOLD)
        
        path_str = f"Path: {current_path.resolve()}"
        if len(path_str) > max_x:
            path_str = path_str[:max_x-3] + "..."
        stdscr.addstr(1, 0, path_str, curses.A_BOLD)
        
        visible_entries = max_y - 3  # Account for help text
        start_idx = max(0, current_pos - visible_entries + 1)
        end_idx = min(len(entries), start_idx + visible_entries)
        
        for idx, entry in enumerate(entries[start_idx:end_idx], start_idx):
            y = idx - start_idx + 3  # Start after help and path
            entry_str = entry[:max_x-4] + "..." if len(entry) > max_x-4 else entry
            
            is_dir = (current_path / entry).is_dir()

            #Uncomment one of the two if nerdfont is not installed
            # prefix = "📁 " if is_dir else "📄 "
            # prefix = "■ " if is_dir else "□ "

            #Comment the two lines if nerdfont is not installed
            entry_path = current_path / entry
            prefix = f"{get_file_icon(entry_path)} "

            display_str = f"{prefix}{entry_str}"
            
            if idx == current_pos:
                color_pair = curses.color_pair(1) if is_dir else curses.color_pair(2)
                stdscr.addstr(y, 0, display_str[:max_x], curses.A_REVERSE | color_pair)
            else:
                color_pair = curses.color_pair(1) if is_dir else curses.color_pair(2)
                stdscr.addstr(y, 0, display_str[:max_x], color_pair)
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_pos > 0:
            current_pos -= 1
        elif key == curses.KEY_DOWN and current_pos < len(entries) - 1:
            current_pos += 1
        elif key == ord('\n') and entries:
            selected = current_path / entries[current_pos]
            if selected.is_dir():
                history.append(current_path)
                current_path = selected
                current_pos = 0
            else:
                # Open file with default application
                open_file(selected)
        elif key == ord('b'):
            if current_path != Path('.'):
                history.append(current_path)
                current_path = current_path.parent
                current_pos = 0
        elif key == ord('h'):  # History back
            if history:
                current_path = history.pop()
                current_pos = 0
        elif key == ord('q'):
            break
        elif key == ord('e'):
            return f"CHANGE_DIR:{current_path.resolve()}"

def main():
    result = curses.wrapper(interactive_ls)
    if result and result.startswith("CHANGE_DIR:"):
        print(result)

if __name__ == "__main__":
    main()
