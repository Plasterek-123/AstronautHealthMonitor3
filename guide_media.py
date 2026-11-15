"""Offline Markdown with local photographs and step illustrations."""
import re
from pathlib import Path
import flet as ft
from config import txt,GRAY
def article_controls(markdown,directory):
    controls=[];position=0;root=Path(directory).resolve()
    for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)',markdown):
        before=markdown[position:match.start()]
        if before.strip():controls.append(ft.Markdown(value=before,selectable=True,extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,auto_follow_links=True))
        alt,target=match.groups();path=(root/target).resolve()
        if path.is_relative_to(root) and path.is_file():
            controls.append(ft.Image(src=path.read_text(encoding='utf-8') if path.suffix=='.svg' else path.read_bytes(),height=230,fit=ft.BoxFit.CONTAIN,semantics_label=alt))
            controls.append(txt(alt,11,GRAY))
        else:controls.append(txt(alt,11,GRAY))
        position=match.end()
    if markdown[position:].strip():controls.append(ft.Markdown(value=markdown[position:],selectable=True,extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,auto_follow_links=True))
    return controls
