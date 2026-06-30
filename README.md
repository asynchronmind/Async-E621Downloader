# Async-E621Download

A lightweight Python parser that uses **Polars** for fast data processing and **aria2** for efficient file downloads.

## Usage

1. Edit `Config.json`.

2. Download needed libs:
```bash
python -m pip install requirements.txt
```

3. Run:

```bash
python Async-E621Download.py
```

The parser processes each tag from the `tags` array sequentially and repeats the download/parsing workflow for every tag.

## Configuration

| Option | Description |
|---------|-------------|
| `tags` | List of tags to parse. The parser processes each tag sequentially in a loop. Multiple tags can be combined using `\|` (e.g. `"catgirl \| solo"`). |
| `blacklist` | Tags to exclude from results. Multiple blacklist tags can be combined using `\|` (e.g. `"gore \| animated"`). |
| `ignored_id` | List of ignored posts. It also can be combined using `\|` (e.g. `"000000001 \| 000000002"`). |
| `use_explicit` | Enable explicit content. |
| `use_questionable` | Enable questionable content. |
| `use_safe` | Enable safe content. |
| `format_*` | Enable or disable supported file formats (`swf`, `webp`, `webm`, `mp4`, `png`, `jpg`, `gif`). |
| `min_score` | Minimum post score. Use `-1` to disable filtering. |
| `sort_by` | One or more sort fields separated by `\|` (e.g. `"score \| !id"`). Prefix a field with `!` to sort it in descending order. |
| `max_to_download` | Maximum number of files to download per tag. |
| `min_area` | Minimum image resolution (width × height). |
| `min_id` | Only process posts with an ID greater than or equal to this value. |
| `downloading_dir` | Directory where files are saved. |
| `aria2_queue_size` | aria2 download queue size. |
| `aria2_max_concurred_download` | Maximum concurrent downloads. |
| `allow_overwrite` | Overwrite existing files. |
| `auto_file_renaming` | Automatically rename duplicate files. |
| `posts` | List of posts to download. |
| `download_posts_first` | Set when posts are about to be downloaded. |

The parser iterates through the `tags` array and uses the same index for all other configuration arrays.

If a configuration array does not contain a value for the current index (its length is smaller than the current tag index), the value at **index `0`** is used as the default.

**Example**

```json
{
  "tags": ["catgirl", "landscape", "city"],
  "min_score": [100],
  "sort_by": ["score", "!id"]
}
```
