import os
moved = 0
logs_dir = ".logs"
trash_dir = "logs trash"
# Loop through all .jsonl files in .logs
for filename in os.listdir(logs_dir):
    if filename.endswith(".jsonl"):
        src_path = os.path.join(logs_dir, filename)
        dst_path = os.path.join(trash_dir, filename)
        try:
            # Read the existing content (if any)
            with open(src_path, 'r', encoding='utf-8') as src_file:
                content = src_file.read()

            # Skip empty files
            if not content.strip():
                continue

            # Append the cleared content into the trash version
            with open(dst_path, 'a', encoding='utf-8') as dst_file:
                dst_file.write(content)
                # Separate entries if needed
                dst_file.write("\n")

            # Clear the original file
            open(src_path, 'w').close()

            print(f"Moved content → {dst_path}")
            moved += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}")

if moved == 0:
    print("No .jsonl files with content found in .logs/")
else:
    print(f"\n✅ Cleared {moved} file(s) and moved their content to '{trash_dir}/'")
