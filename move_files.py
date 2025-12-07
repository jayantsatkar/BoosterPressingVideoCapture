import os
import shutil
import time
class FileMover:

    @staticmethod
    def move_all(src_root, dest_root, delete_empty=False, days=30):
        """
        Moves all files from src_root to dest_root while preserving folder structure.
        Optionally deletes empty folders.
        """

        age_limit = days * 24 * 60 * 60
        now = time.time()

        # ---- Move all files ----
        for root, dirs, files in os.walk(src_root):
            for file in files:
                src_path = os.path.join(root, file)

                # Get file age
                file_mtime = os.path.getmtime(src_path)
                file_age_seconds = now - file_mtime

                # Skip files not older than X days
                if file_age_seconds < age_limit:
                    continue

                # Relative path (preserve structure)
                rel_path = os.path.relpath(src_path, src_root)
                dest_path = os.path.join(dest_root, rel_path)

                # Create destination folder
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                # Move file
                shutil.move(src_path, dest_path)
                print(f"Moved (>{days} days): {src_path} -> {dest_path}")

        # ---- Delete empty folders if enabled ----
        if delete_empty:
            for root, dirs, files in os.walk(src_root, topdown=False):
                if not dirs and not files:
                    try:
                        os.rmdir(root)
                        print(f"Deleted empty folder: {root}")
                    except Exception as ex:
                        print(ex)


        # After the walk, check if src_root is empty
        try:
            if not os.listdir(src_root):
                os.rmdir(src_root)
                print(f"Deleted root folder: {src_root}")
        except Exception as ex:
            print(ex)


# ------------------ Usage Example ------------------

# FileMover.move_all(
#     src_root="/records",
#     dest_root="Final",
#     delete_empty=True
# )
