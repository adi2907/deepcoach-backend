#!/bin/bash

# Get repository name and set up output file
REPO_NAME=$(basename "$PWD")
OUTPUT_FILE="${REPO_NAME}_repo_digest.txt"

# Define source code file extensions we want to include
SOURCE_EXTENSIONS="\.(py|ipynb|js|jsx|ts|tsx|vue|java|cpp|hpp|c|h|go|rs|rb|php|cs|scala|kt|swift|m|mm|sh|bash|pl|pm|t|less|html|xml|sql|graphql|md|rst|tex|yaml|yml|json|coffee|dart|r|jl|lua|clj|cljs|ex|exs)$"

# Define common patterns to exclude
EXCLUDE_PATTERNS=(
    # Version control
    ".git"
    "__pycache__"
    
    # Data and binary files
    "*.csv"
    "*.xlsx"
    "*.json"
    "*.log"
    
    # Build and environment
    "node_modules"
    "docker"
    "venv"
    ".env"
    
    # IDE and editor files
    ".vscode"
    ".idea"
    "*.swp"
)

# Helper function to check if a file is binary
is_binary() {
    [ ! -f "$1" ] && return 1
    local mime
    mime=$(file -b --mime "$1")
    case "$mime" in
        *binary*) return 0 ;;
        *charset=binary*) return 0 ;;
        *) return 1 ;;
    esac
}

# Build exclude arguments for find command
build_find_excludes() {
    local excludes=()
    
    # Process predefined exclude patterns
    for pat in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$pat" == *[*?]* ]]; then
            # Pattern contains wildcards - use -name
            excludes+=("-name" "$pat" "-prune" "-o")
        else
            # No wildcards - use -path
            excludes+=("-path" "./$pat" "-prune" "-o")
        fi
    done
    
    # Add patterns from .gitignore if it exists
    if [ -f .gitignore ]; then
        while IFS= read -r pattern; do
            # Skip comments and empty lines
            [[ "$pattern" =~ ^#.*$ || -z "$pattern" ]] && continue
            
            # Clean up pattern: remove trailing and leading slashes
            pattern="${pattern%/}"
            pattern="${pattern#/}"
            [[ -n "$pattern" ]] || continue
            
            # Handle wildcards in gitignore patterns
            if [[ "$pattern" == *[*?]* ]]; then
                excludes+=("-name" "$pattern" "-prune" "-o")
            else
                excludes+=("-path" "./$pattern" "-prune" "-o")
            fi
        done < .gitignore
    fi
    
    printf '%s\n' "${excludes[@]}"
}

# Initialize output file
> "$OUTPUT_FILE"
echo "Repository Source Code Contents" >> "$OUTPUT_FILE"
echo "Generated on: $(date)" >> "$OUTPUT_FILE"
echo "----------------------------------------" >> "$OUTPUT_FILE"

# Initialize counters
total_files=0
included_files=0
excluded_binary=0

echo "Building find command..." >&2

# Build the find command with excludes
mapfile -t FIND_EXCLUDES < <(build_find_excludes)

# Process files using find with proper array expansion
while IFS= read -r -d $'\0' path; do
    ((total_files++))
    echo "Processing: $path"
    
    if [[ "$path" =~ $SOURCE_EXTENSIONS ]]; then
        if ! is_binary "$path"; then
            echo "File: $path" >> "$OUTPUT_FILE"
            echo "----------------------------------------" >> "$OUTPUT_FILE"
            cat "$path" >> "$OUTPUT_FILE"
            echo -e "\n----------------------------------------" >> "$OUTPUT_FILE"
            ((included_files++))
        else
            echo "Skipping binary: $path"
            ((excluded_binary++))
        fi
    else
        echo "Skipping non-source file: $path"
    fi
done < <(find . "${FIND_EXCLUDES[@]}" -type f -print0)

# Print summary
echo -e "\nSummary:"
echo "Total files found: $total_files"
echo "Included in output: $included_files"
echo "Skipped binary files: $excluded_binary"
echo "Output: $OUTPUT_FILE"