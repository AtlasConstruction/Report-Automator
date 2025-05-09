import os
from pathlib import Path

def print_directory_structure(startpath, max_level=None, current_level=0, exclude_dirs=None):
    """
    Recursively prints the directory structure starting from startpath.
    
    Args:
        startpath (str or Path): The root directory to start from
        max_level (int, optional): Maximum depth to display. None for unlimited.
        current_level (int): Internal use for recursion tracking
        exclude_dirs (list): List of directory names to exclude
    """
    # Default excluded directories
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'refs', 'objects', 'info', 'hooks', 'pack', 'logs']
    
    # Skip if we've reached max depth
    if max_level is not None and current_level > max_level:
        return
    
    # Convert to Path object if it's a string
    startpath = Path(startpath) if isinstance(startpath, str) else startpath
    
    # Skip if the path doesn't exist
    if not startpath.exists():
        print(f"Path does not exist: {startpath}")
        return
    
    # Print the current directory (only for root level)
    if current_level == 0:
        print(f"{startpath.name}/")
    
    # If it's a directory, recurse into it
    if startpath.is_dir():
        try:
            # Get sorted list of items (directories first, then files)
            items = sorted(startpath.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for i, item in enumerate(items):
                # Skip excluded directories
                if item.is_dir() and item.name in exclude_dirs:
                    continue
                
                # Check if this is the last item in the directory
                is_last = i == len(items) - 1
                
                # Create appropriate prefix
                prefix = "    " * current_level + ("└── " if is_last else "├── ")
                
                if item.is_dir():
                    print(f"{prefix}{item.name}/")
                    print_directory_structure(item, max_level, current_level + 1, exclude_dirs)
                else:
                    print(f"{prefix}{item.name}")
        except PermissionError:
            print(f"{'    ' * current_level}└── [Permission denied]")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Print directory structure')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory to scan (default: current directory)')
    parser.add_argument('--max-level', type=int, default=None,
                       help='Maximum depth to display (default: unlimited)')
    parser.add_argument('--exclude', nargs='+', default=None,
                       help='Additional directory names to exclude')
    
    args = parser.parse_args()
    
    print(f"Directory structure of: {os.path.abspath(args.directory)}")
    print_directory_structure(args.directory, args.max_level, exclude_dirs=args.exclude)