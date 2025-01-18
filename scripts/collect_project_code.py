import os
import pathlib
from datetime import datetime

def collect_project_files(project_path: str, output_file: str = "project_contents.txt") -> None:
    """
    Collects content from useful project files and combines them into a single file.
    
    Args:
        project_path: Path to the project root directory
        output_file: Name of the output file
    """
    # File extensions to collect
    useful_extensions = {'.py', '.json', '.yaml', '.yml', '.md', '.env.example'}
    
    # Directories to skip
    skip_dirs = {
        '__pycache__', 
        'venv', 
        '.git', 
        '.pytest_cache', 
        'node_modules',
        'dist',
        'build'
    }
    
    collected_contents = []
    
    def should_process_file(filepath: str) -> bool:
        """Check if the file should be processed based on extension and path."""
        file_ext = pathlib.Path(filepath).suffix
        return (file_ext in useful_extensions and 
                not any(skip_dir in filepath for skip_dir in skip_dirs))
    
    # Add header with timestamp
    collected_contents.append(f"# Project Code Collection\n")
    collected_contents.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Walk through project directory
    for root, dirs, files in os.walk(project_path):
        # Remove unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            if should_process_file(filepath):
                try:
                    # Add file header
                    relative_path = os.path.relpath(filepath, project_path)
                    collected_contents.append(f"\n{'='*80}\n")
                    collected_contents.append(f"File: {relative_path}\n")
                    collected_contents.append(f"{'='*80}\n\n")
                    
                    # Read and add file contents
                    with open(filepath, 'r', encoding='utf-8') as f:
                        collected_contents.append(f.read())
                    
                    collected_contents.append("\n")
                except Exception as e:
                    collected_contents.append(f"Error reading file {filepath}: {str(e)}\n")
    
    # Write everything to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(collected_contents))
    
    print(f"Project contents have been collected in {output_file}")

if __name__ == "__main__":
    # Get the current working directory as default project path
    default_project_path = os.getcwd()
    
    print(f"Using project path: {default_project_path}")
    collect_project_files(default_project_path)