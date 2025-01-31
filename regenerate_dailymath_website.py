import shutil
import os

def copy_folder_contents(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

if __name__ == "__main__":
    dst_folder = os.getcwd()
    src_folder = os.path.join(dst_folder,'WebsiteGenerator/_site')
    copy_folder_contents(src_folder, dst_folder)
    print(f"Regenerated website")