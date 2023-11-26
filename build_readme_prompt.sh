#!/bin/bash

# Function to process a file
process_file() {
  file="$1"
  if [ "$file" != "./readme_prompt.txt" ]; then
    echo "Processing: $file"
    echo "### $file" >> readme_prompt.txt
    cat "$file" >> readme_prompt.txt
    echo -e "\n\n" >> readme_prompt.txt
  else
    echo "Skipped: $file (readme_prompt.txt)"
  fi
}

# Function to list all folders and files in the current directory recursively, excluding specified directories
list_files() {
  directory="$1"
  echo "Listing: $directory" >> readme_prompt.txt
  find "$directory" -type d ! -path "./app/data/*" ! -path "./.git/*" -exec echo "  [D] {}" \; -o -type f -exec echo "  [F] {}" \; | grep -v -e './\.git/' -e './app/data/' >> readme_prompt.txt
  echo -e "\n\n" >> readme_prompt.txt
}

# Function to crawl through directories
crawl_directory() {
  directory="$1"
  if [ "$directory" != "./app/data" ]; then
    list_files "$directory"
    for file in "$directory"/*; do
      if [ -d "$file" ]; then
        crawl_directory "$file"
      elif [ -f "$file" ]; then
        case "$file" in
          *.py|Dockerfile|*.sh|.github/workflows/docker-image.yml|.env|*.txt)
            process_file "$file"
            ;;
        esac
      fi
    done
  fi
}

# Clear existing readme_prompt.txt
> readme_prompt.txt

# Start crawling from the current directory
crawl_directory "."

echo "Crawling completed. Results are saved in readme_prompt.txt"
