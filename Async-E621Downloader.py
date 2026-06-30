import json
import os
import subprocess
import tqdm
import requests
import polars


# downloading content by md5 from static1.e621.net
def download_content(config, db, _in):
    _dwnl_dir = get_value_for_sort(config, "downloading_dir", _in)

    raw_url = "https://static1.e621.net/data/"
    print("[Info] Donwloading content..")

    # vars
    _a_j = get_value_for_sort(config, "aria2_queue_size", _in)
    _a_max = get_value_for_sort(config, "aria2_max_concurred_download", _in)

    _all_ov = get_value_for_sort(config, "allow_overwrite", _in)
    _auto_rename = get_value_for_sort(config, "auto_file_renaming", _in)

    print("[Info] Downloading files..")
    _pather = os.path.join(os.path.split(
        os.path.abspath(__file__))[0], "Temp/md5.txt")
    if (os.path.isfile(_pather)):
        os.remove(_pather)

    with (open(_pather, "w")) as file:
        for _row in db.iter_rows():
            filename = _row[3] + "." + _row[11]
            url = raw_url + _row[3][:2] + "/" + \
                _row[3][2:4] + "/" + filename

            if (os.path.isfile(os.path.join(_dwnl_dir, filename))):
                continue

            file.write(str(url) + "\n")

    subprocess.run([
        "aria2c",
        "--input-file", _pather,
        "--dir", _dwnl_dir,
        "-j", str(_a_j),
        "--max-concurrent-downloads", str(_a_max),
        "--allow-overwrite", str(_all_ov),
        "--auto-file-renaming", str(_auto_rename)
    ])

    print("\n[Info] Downloading loop stage completed!")


# make sorted csv table of content to download
def sorting_content(db_dir, config, _in=int):
    db = polars.read_csv(db_dir)
    _tags = str(get_value_for_sort(config, "tags", _in)
                ).replace(' ', '').split('|')

    _blacklist = str(get_value_for_sort(
        config, "blacklist", _in)).replace(' ', '').split('|')

    _min_i = get_value_for_sort(config, "min_score", _in)
    _use_e = get_value_for_sort(config, "use_explicit", _in)
    _use_q = get_value_for_sort(config, "use_questionable", _in)
    _use_s = get_value_for_sort(config, "use_safe", _in)

    _sort_by = get_value_for_sort(
        config, "sort_by", _in).replace(' ', '').split('|')

    _max_d = get_value_for_sort(config, "max_to_download", _in)
    _min_a = get_value_for_sort(config, "min_id", _in)

    # formats
    _f_swf = get_value_for_sort(config, "format_swf", _in)
    _f_webp = get_value_for_sort(config, "format_webp", _in)
    _f_webm = get_value_for_sort(config, "format_webm", _in)
    _f_mp4 = get_value_for_sort(config, "format_mp4", _in)
    _f_png = get_value_for_sort(config, "format_png", _in)
    _f_jpg = get_value_for_sort(config, "format_jpg", _in)
    _f_gif = get_value_for_sort(config, "format_gif", _in)

    _min_area = get_value_for_sort(config, "min_area", _in)

    # filter
    if _min_a > 0:
        db = db.filter(polars.col("id") >= _min_a)

    for _t in _tags:
        if _t != "":
            db = db.filter(polars.col("tag_string").str.split(
                ' ').list.contains(_t))

    for _bl in _blacklist:
        if _bl != "":
            db = db.filter(polars.col("tag_string").str.split(
                ' ').list.contains(_bl).not_())

    db.filter(polars.col("score") >= _min_i)

    if not _use_e:
        db = db.filter(polars.col("rating") != "e")
    if not _use_q:
        db = db.filter(polars.col("rating") != "q")
    if not _use_s:
        db = db.filter(polars.col("rating") != "s")

    # filter formats
    if not _f_swf:
        db = db.filter(polars.col("file_ext") != "swf")

    if not _f_webp:
        db = db.filter(polars.col("file_ext") != "webp")

    if not _f_webm:
        db = db.filter(polars.col("file_ext") != "webm")

    if not _f_mp4:
        db = db.filter(polars.col("file_ext") != "mp4")

    if not _f_png:
        db = db.filter(polars.col("file_ext") != "png")

    if not _f_jpg:
        db = db.filter(polars.col("file_ext") != "jpg")

    if not _f_gif:
        db = db.filter(polars.col("file_ext") != "gif")

    if _min_area > 0:
        db = db.filter((polars.col("image_width") *
                       polars.col("image_height")) >= _min_area)

    # sorting
    list_values = []
    list_descendings = []
    for _srt in _sort_by:
        if _srt != "":
            if _srt[:1] == "!":
                list_values.append(_srt[1:])
                list_descendings.append(False)
            else:
                list_values.append(_srt)
                list_descendings.append(True)

    if len(list_values) > 0:
        db = db.sort(list_values, descending=list_descendings)

    # Get first n..
    if (_max_d > 0):
        db = db.head(_max_d)

    print(db)

    return db


def get_value_for_sort(config, nval, index):
    if index < len(config[nval]):
        return config[nval][index]
    else:
        return config[nval][0]


# downloading database from  e621.net/db_export/
def download_database(db_dir):
    print("[Info] Downloading database..")

    if not (os.path.isdir(os.path.split(db_dir)[0])):
        os.mkdir(os.path.split(db_dir)[0])

    with (open(db_dir, "wb")) as f:
        # downloading db
        with requests.get(
            "https://static1.e621.net/data/db_export/posts.csv.gz", stream=True
        ) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with tqdm.tqdm(total=total, unit='B', unit_scale=True) as pb:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pb.update(len(chunk))


# loading json configuration
def load_config():
    print("[Info] Trying to get config..")
    if not (os.path.isfile('Config.json')):
        return False

    return json.load(open('Config.json'))


def init():
    db_dir = os.path.join(
        os.path.split(os.path.abspath(__file__))[0], "Temp/posts.csv.gz"
    )

    if (os.path.isfile(db_dir)):
        print("[Ann] Database file is exist!")
        i = input("Redownload database (y/n): ")
        if (i == 'y'):
            download_database(db_dir)
    else:
        download_database(db_dir)

    if not (os.path.isfile(db_dir)):
        print("[Error] Database file is not exist!")
        return

    # variables
    config = load_config()

    # cheching variables
    if not (config):
        print("[Error] Config.json open error!")
        return

    # Making loop for TAGS massive from config
    print("=== DOWNLOADING LOOP ===")
    for i in range(0, len(config["tags"])):
        print(f"[Info] Going loop on tags ({i + 1}/{len(config["tags"])})")
        print("[Info] Soring database..")
        _db = sorting_content(db_dir, config, i)
        download_content(config, _db, i)


if __name__ == "__main__":
    print("==========  - ASYNC-E621DOWNLOADED -  ==========")
    print("Thanks for using my noob script.\nThis is a beta version. Have fun!\n\n")
    init()

# ['id', 'uploader_id', 'created_at', 'md5', 'source', 'rating', 'image_width', 'image_height', 'tag_string', 'locked_tags', 'fav_count', 'file_ext',
# 'parent_id', 'change_seq', 'approver_id', 'file_size', 'comment_count', 'description', 'duration', 'updated_at', 'is_deleted', 'is_pending', 'is_flagged',
# 'score', 'up_score', 'down_score', 'is_rating_locked', 'is_status_locked', 'is_note_locked', 'bg_color', 'last_noted_at', 'last_commented_at']
